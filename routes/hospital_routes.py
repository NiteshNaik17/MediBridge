import uuid
from flask import Blueprint, request, jsonify, session
from backend.models.hospital_model import HospitalModel
from backend.models.patient_model import PatientModel
from backend.models.record_model import RecordModel
from backend.models.user_model import UserModel
from backend.database.mongodb import get_db

hospital_bp = Blueprint('hospital', __name__)

def _get_active_hospital_id():
    h_id = session.get('hospital_id')
    if not h_id:
        user_id = session.get('user_id')
        if user_id:
            u = UserModel.get_by_id(user_id)
            if u and u.get('hospital_id'):
                h_id = u.get('hospital_id')
    if not h_id:
        hospitals = HospitalModel.get_all()
        if hospitals:
            h_id = hospitals[0]['hospital_id']
    return h_id

@hospital_bp.route('/add', methods=['POST'])
def add_hospital():
    data = request.get_json() or {}
    hosp_name = data.get('hospital_name')
    reg_number = data.get('registration_number', 'REG-PENDING')
    address = data.get('address', '')
    departments_str = data.get('departments', '')
    departments = [d.strip() for d in departments_str.split(',') if d.strip()] if isinstance(departments_str, str) else (departments_str or [])

    if not hosp_name:
        return jsonify({"success": False, "message": "Hospital name is required."}), 400

    hosp = HospitalModel.create_hospital(hosp_name, reg_number, address, departments)
    return jsonify({"success": True, "message": "Hospital created successfully.", "hospital": hosp})


@hospital_bp.route('/dashboard', methods=['GET'])
def get_hospital_dashboard():
    hospital_id = request.args.get('hospital_id') or _get_active_hospital_id()

    hospital = HospitalModel.get_by_id(hospital_id) if hospital_id else None
    patients = PatientModel.get_all()
    records = RecordModel.get_by_hospital(hospital_id) if hospital_id else []
    
    db = get_db()
    apts = db.appointments.find({"hospital_id": hospital_id}) if hospital_id else []

    connected_patients = []
    if hospital_id:
        connected_patients = [
            p for p in patients 
            if hospital_id in p.get('connected_hospitals', [])
        ]

    return jsonify({
        "success": True,
        "hospital": hospital,
        "stats": {
            "total_patients": len(connected_patients),
            "total_records": len(records),
            "total_doctors": len(hospital.get('doctor_info', [])) if hospital else 0,
            "total_appointments": len(apts)
        },
        "recent_records": records[:5],
        "appointments": apts,
        "doctors": hospital.get('doctor_info', []) if hospital else []
    })


@hospital_bp.route('/doctors', methods=['GET', 'POST'])
def manage_doctors():
    hospital_id = request.args.get('hospital_id') or _get_active_hospital_id()
    if not hospital_id:
        return jsonify({"success": False, "message": "No hospital active."}), 400

    if request.method == 'GET':
        hospital = HospitalModel.get_by_id(hospital_id)
        return jsonify({"success": True, "doctors": hospital.get('doctor_info', []) if hospital else []})

    elif request.method == 'POST':
        data = request.get_json() or {}
        doc_name = data.get('name')
        specialty = data.get('specialty', 'General Medicine')
        qualification = data.get('qualification', 'MD')

        if not doc_name:
            return jsonify({"success": False, "message": "Doctor name is required."}), 400

        doctor_obj = {
            "doctor_id": f"doc-{uuid.uuid4().hex[:6]}",
            "name": doc_name if doc_name.startswith("Dr.") else f"Dr. {doc_name}",
            "specialty": specialty,
            "qualification": qualification
        }

        HospitalModel.add_doctor(hospital_id, doctor_obj)
        updated_hosp = HospitalModel.get_by_id(hospital_id)
        return jsonify({
            "success": True,
            "message": "Doctor added successfully.",
            "doctors": updated_hosp.get('doctor_info', [])
        })


@hospital_bp.route('/patients', methods=['GET', 'POST'])
def manage_patients():
    if request.method == 'GET':
        query = request.args.get('q', '').lower()
        patients = PatientModel.get_all()
        if query:
            patients = [
                p for p in patients 
                if query in p.get('name', '').lower() or query in p.get('health_id', '').lower()
            ]
        return jsonify({"success": True, "patients": patients})

    elif request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        blood_group = data.get('blood_group')
        allergies = data.get('allergies', [])
        emergency_contact = data.get('emergency_contact', {})

        if not name or not age or not blood_group:
            return jsonify({"success": False, "message": "Patient name, age, and blood group are required."}), 400

        patient = PatientModel.create_patient(
            user_id=f"usr-{name.lower().replace(' ', '')}",
            name=name,
            age=age,
            gender=gender,
            blood_group=blood_group,
            allergies=allergies,
            emergency_contact=emergency_contact
        )
        return jsonify({"success": True, "message": "Patient profile created successfully.", "patient": patient}), 201


@hospital_bp.route('/records', methods=['GET', 'POST'])
def manage_records():
    hospital_id = request.args.get('hospital_id') or _get_active_hospital_id()
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        if patient_id:
            records = RecordModel.get_by_patient(patient_id)
        else:
            records = RecordModel.get_by_hospital(hospital_id) if hospital_id else []
        return jsonify({"success": True, "records": records})

    elif request.method == 'POST':
        data = request.get_json() or {}
        patient_id = data.get('patient_id')
        hosp_id = data.get('hospital_id') or hospital_id
        
        hospital_obj = HospitalModel.get_by_id(hosp_id) if hosp_id else None
        hospital_name = hospital_obj.get('hospital_name', 'Hospital') if hospital_obj else 'Hospital'

        doctor_name = data.get('doctor_name', 'Doctor')
        document_url = data.get('document_url', '/uploads/medical_documents/prescription.pdf')
        document_type = data.get('document_type', 'Prescription')
        diagnosis = data.get('diagnosis')
        medicines = data.get('medicines', [])
        doctor_notes = data.get('doctor_notes', '')
        date = data.get('date')
        test_results = data.get('test_results', {})

        if not patient_id or not diagnosis:
            return jsonify({"success": False, "message": "Patient ID and Diagnosis are required."}), 400

        rec = RecordModel.create_record(
            patient_id=patient_id,
            hospital_id=hosp_id,
            document_url=document_url,
            diagnosis=diagnosis,
            medicines=medicines,
            doctor_notes=doctor_notes,
            date=date,
            hospital_name=hospital_name,
            doctor_name=doctor_name,
            document_type=document_type,
            test_results=test_results
        )
        return jsonify({"success": True, "message": "Medical record uploaded and saved successfully.", "record": rec}), 201


@hospital_bp.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    db = get_db()
    hospital_id = request.args.get('hospital_id') or _get_active_hospital_id()
    if request.method == 'GET':
        apts = db.appointments.find({"hospital_id": hospital_id}) if hospital_id else []
        return jsonify({"success": True, "appointments": apts})

    elif request.method == 'POST':
        data = request.get_json() or {}
        patient_id = data.get('patient_id')
        patient_name = data.get('patient_name', 'Patient')
        hosp_id = data.get('hospital_id') or hospital_id
        doctor = data.get('doctor', 'Doctor')
        date = data.get('date')
        time = data.get('time', '10:00 AM')
        reason = data.get('reason', 'General Consultation')

        apt = {
            "appointment_id": f"apt-{uuid.uuid4().hex[:8]}",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "hospital_id": hosp_id,
            "doctor": doctor,
            "date": date,
            "time": time,
            "reason": reason,
            "status": "Confirmed"
        }
        db.appointments.insert_one(apt)
        return jsonify({"success": True, "message": "Appointment scheduled.", "appointment": apt})
