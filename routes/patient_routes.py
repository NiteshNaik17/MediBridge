from io import BytesIO
from flask import Blueprint, request, jsonify, session, send_file
from backend.models.patient_model import PatientModel
from backend.models.record_model import RecordModel
from backend.models.hospital_model import HospitalModel
from backend.models.user_model import UserModel
from backend.services.ai_summary_service import AISummaryService
from backend.services.qr_service import QRService
from backend.services.pdf_service import EmergencyPDFService

patient_bp = Blueprint('patient', __name__)

def _attach_user_info(patient_dict):
    if not patient_dict:
        return patient_dict
    pat = dict(patient_dict)
    user_id = pat.get('user_id')
    if user_id:
        u = UserModel.get_by_id(user_id)
        if u:
            pat['email'] = u.get('email', '')
            pat['phone'] = u.get('phone', '')
    return pat

@patient_bp.route('/dashboard', methods=['GET'])
def get_patient_dashboard():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        user_id = session.get('user_id')
        if user_id:
            patient = PatientModel.get_by_user_id(user_id)
            if patient:
                patient_id = patient['patient_id']
    
    if not patient_id:
        patient_id = 'pat-201'  # Default fallback patient Sarah Connor

    raw_patient = PatientModel.get_by_id(patient_id)
    patient = _attach_user_info(raw_patient)
    records = RecordModel.get_by_patient(patient_id)
    summary = AISummaryService.generate_patient_summary(patient_id)

    return jsonify({
        "success": True,
        "patient": patient,
        "summary": summary,
        "recent_records": records[:5],
        "stats": {
            "total_records": len(records),
            "connected_hospitals": len(patient.get('connected_hospitals', [])) if patient else 0
        }
    })


@patient_bp.route('/profile', methods=['GET', 'PUT'])
def handle_profile():
    patient_id = request.args.get('patient_id', 'pat-201')
    if request.method == 'GET':
        raw_patient = PatientModel.get_by_id(patient_id)
        patient = _attach_user_info(raw_patient)
        return jsonify({"success": True, "patient": patient})

    elif request.method == 'PUT':
        data = request.get_json() or {}
        PatientModel.update_profile(patient_id, data)
        updated = _attach_user_info(PatientModel.get_by_id(patient_id))
        return jsonify({"success": True, "message": "Profile updated successfully.", "patient": updated})


@patient_bp.route('/timeline', methods=['GET'])
def get_health_timeline():
    patient_id = request.args.get('patient_id', 'pat-201')
    records = RecordModel.get_by_patient(patient_id)

    # Organize timeline by Year
    timeline = {}
    for r in records:
        date_str = r.get('date', '2026-01-01')
        year = date_str.split('-')[0] if '-' in date_str else '2026'
        if year not in timeline:
            timeline[year] = []
        timeline[year].append(r)

    return jsonify({
        "success": True,
        "patient_id": patient_id,
        "timeline": timeline,
        "records": records
    })


@patient_bp.route('/emergency', methods=['GET'])
def get_emergency_card():
    patient_id = request.args.get('patient_id', 'pat-201')
    patient = PatientModel.get_by_id(patient_id)
    if not patient:
        return jsonify({"success": False, "message": "Patient not found"}), 404

    # Aggregate diagnoses & active medications
    records = RecordModel.get_by_patient(patient_id)
    diagnoses = set(patient.get('important_conditions', []))
    medications = set()

    for r in records:
        if r.get('diagnosis'):
            diagnoses.add(r['diagnosis'])
        if r.get('medicines'):
            for m in r['medicines']:
                medications.add(m)

    host_url = request.host_url.rstrip('/')
    qr_code_data = QRService.generate_emergency_qr(patient, host_url=host_url)

    return jsonify({
        "success": True,
        "emergency_card": {
            "patient_id": patient.get('patient_id'),
            "name": patient.get('name'),
            "health_id": patient.get('health_id'),
            "age": patient.get('age', 30),
            "gender": patient.get('gender', 'N/A'),
            "blood_group": patient.get('blood_group'),
            "allergies": patient.get('allergies', []),
            "important_conditions": list(diagnoses),
            "medications": list(medications),
            "emergency_contact": patient.get('emergency_contact', {}),
            "qr_code": qr_code_data
        }
    })


@patient_bp.route('/emergency-pdf-file', methods=['GET'])
def get_emergency_pdf_file():
    """ Returns direct downloadable / viewable PDF binary file for cross-device mobile scanners """
    patient_id = request.args.get('patient_id', 'pat-201')
    patient = PatientModel.get_by_id(patient_id)
    if not patient:
        return jsonify({"success": False, "message": "Patient not found"}), 404

    records = RecordModel.get_by_patient(patient_id)
    diagnoses = set(patient.get('important_conditions', []))
    medications = set()

    for r in records:
        if r.get('diagnosis'):
            diagnoses.add(r['diagnosis'])
        if r.get('medicines'):
            for m in r['medicines']:
                medications.add(m)

    card = {
        "patient_id": patient.get('patient_id'),
        "name": patient.get('name'),
        "health_id": patient.get('health_id'),
        "age": patient.get('age', 30),
        "gender": patient.get('gender', 'N/A'),
        "blood_group": patient.get('blood_group'),
        "allergies": patient.get('allergies', []),
        "important_conditions": list(diagnoses),
        "medications": list(medications),
        "emergency_contact": patient.get('emergency_contact', {})
    }

    pdf_bytes = EmergencyPDFService.generate_pdf_bytes(card)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f"Emergency_Pass_{patient.get('name', 'Patient').replace(' ', '_')}.pdf"
    )


@patient_bp.route('/connections', methods=['GET', 'POST'])
def handle_hospital_connections():
    patient_id = request.args.get('patient_id', 'pat-201')
    if request.method == 'GET':
        all_hospitals = HospitalModel.get_all()
        patient = PatientModel.get_by_id(patient_id)
        connected_ids = patient.get('connected_hospitals', []) if patient else []

        hospitals_with_status = []
        for h in all_hospitals:
            h_copy = dict(h)
            h_copy['connected'] = h['hospital_id'] in connected_ids
            hospitals_with_status.append(h_copy)

        return jsonify({"success": True, "hospitals": hospitals_with_status})

    elif request.method == 'POST':
        data = request.get_json() or {}
        hospital_id = data.get('hospital_id')
        if not hospital_id:
            return jsonify({"success": False, "message": "Hospital ID required."}), 400

        PatientModel.add_hospital_connection(patient_id, hospital_id)
        return jsonify({"success": True, "message": "Hospital connection authorized successfully."})
