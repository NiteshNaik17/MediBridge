import uuid
from flask import Blueprint, request, jsonify, session
from backend.models.hospital_model import HospitalModel
from backend.models.patient_model import PatientModel
from backend.models.record_model import RecordModel
from backend.models.user_model import UserModel
from backend.database.mongodb import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
def get_admin_dashboard():
    hospitals = HospitalModel.get_all()
    patients = PatientModel.get_all()
    
    # Calculate total registered doctors across all hospitals
    total_doctors = sum(len(h.get('doctor_info', [])) for h in hospitals)
    
    pending_hospitals = [h for h in hospitals if h.get('verification_status') == 'Pending']
    approved_hospitals = [h for h in hospitals if h.get('verification_status') == 'Approved']

    return jsonify({
        "success": True,
        "stats": {
            "total_hospitals": len(hospitals),
            "approved_hospitals": len(approved_hospitals),
            "pending_hospitals": len(pending_hospitals),
            "total_doctors": total_doctors,
            "total_patients": len(patients)
        },
        "hospitals": hospitals,
        "recent_users": UserModel.get_all_users()[:10]
    })


@admin_bp.route('/hospitals', methods=['GET', 'POST'])
def manage_admin_hospitals():
    if request.method == 'GET':
        hospitals = HospitalModel.get_all()
        return jsonify({"success": True, "hospitals": hospitals})

    elif request.method == 'POST':
        data = request.get_json() or {}
        hospital_id = data.get('hospital_id')
        hospital_name = data.get('hospital_name')
        reg_number = data.get('registration_number', 'REG-APPROVED')
        address = data.get('address', '')

        if not hospital_id or not hospital_name:
            return jsonify({"success": False, "message": "Hospital ID and Hospital Name are required."}), 400

        # Check if Hospital ID already exists
        existing = HospitalModel.get_by_id(hospital_id)
        if existing:
            return jsonify({"success": False, "message": f"Hospital ID '{hospital_id}' already exists."}), 400

        hosp = HospitalModel.create_hospital_with_id(hospital_id, hospital_name, reg_number, address, [])
        return jsonify({
            "success": True, 
            "message": f"Hospital '{hospital_name}' registered with Hospital ID '{hospital_id}' successfully.",
            "hospital": hosp
        })


@admin_bp.route('/hospitals/<hospital_id>/status', methods=['PUT'])
def update_hospital_status(hospital_id):
    data = request.get_json() or {}
    status = data.get('status')
    if not status or status not in ['Approved', 'Rejected', 'Pending']:
        return jsonify({"success": False, "message": "Valid status required."}), 400

    success = HospitalModel.update_status(hospital_id, status)
    if success:
        return jsonify({"success": True, "message": f"Hospital status updated to {status}."})
    return jsonify({"success": False, "message": "Hospital not found."}), 404


@admin_bp.route('/hospitals/<hospital_id>', methods=['DELETE'])
def delete_hospital(hospital_id):
    db = get_db()
    db.hospitals.delete_one({"hospital_id": hospital_id})
    return jsonify({"success": True, "message": f"Hospital '{hospital_id}' deleted successfully."})


@admin_bp.route('/doctors', methods=['GET', 'POST', 'DELETE'])
def manage_admin_doctors():
    if request.method == 'GET':
        hospitals = HospitalModel.get_all()
        all_doctors = []
        for h in hospitals:
            for d in h.get('doctor_info', []):
                doc_copy = dict(d)
                doc_copy['hospital_id'] = h['hospital_id']
                doc_copy['hospital_name'] = h['hospital_name']
                all_doctors.append(doc_copy)
        return jsonify({"success": True, "doctors": all_doctors})

    elif request.method == 'POST':
        data = request.get_json() or {}
        hospital_id = data.get('hospital_id')
        doctor_id = data.get('doctor_id') or f"doc-{uuid.uuid4().hex[:6]}"
        name = data.get('name')
        specialty = data.get('specialty', 'General Medicine')
        qualification = data.get('qualification', 'MD')

        if not hospital_id or not name:
            return jsonify({"success": False, "message": "Hospital ID and Doctor Name are required."}), 400

        hospital = HospitalModel.get_by_id(hospital_id)
        if not hospital:
            return jsonify({"success": False, "message": f"Hospital ID '{hospital_id}' not found."}), 404

        doctor_obj = {
            "doctor_id": doctor_id,
            "name": name if name.startswith("Dr.") else f"Dr. {name}",
            "specialty": specialty,
            "qualification": qualification
        }
        HospitalModel.add_doctor(hospital_id, doctor_obj)
        return jsonify({"success": True, "message": f"Doctor {name} registered to hospital '{hospital_id}' successfully."})

    elif request.method == 'DELETE':
        hospital_id = request.args.get('hospital_id')
        doctor_id = request.args.get('doctor_id')

        if not hospital_id or not doctor_id:
            return jsonify({"success": False, "message": "Hospital ID and Doctor ID required."}), 400

        db = get_db()
        hosp = HospitalModel.get_by_id(hospital_id)
        if hosp:
            updated_doctors = [d for d in hosp.get('doctor_info', []) if d.get('doctor_id') != doctor_id]
            db.hospitals.update_one({"hospital_id": hospital_id}, {"$set": {"doctor_info": updated_doctors}})
            return jsonify({"success": True, "message": "Doctor profile removed successfully."})
        return jsonify({"success": False, "message": "Hospital not found."}), 404


@admin_bp.route('/users', methods=['GET', 'DELETE'])
def manage_users():
    if request.method == 'GET':
        users = UserModel.get_all_users()
        return jsonify({"success": True, "users": users})
    elif request.method == 'DELETE':
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "User ID required."}), 400
        UserModel.delete_user(user_id)
        return jsonify({"success": True, "message": "User account removed."})
