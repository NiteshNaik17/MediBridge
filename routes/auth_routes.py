from flask import Blueprint, request, jsonify, session
from backend.models.user_model import UserModel
from backend.models.hospital_model import HospitalModel
from backend.models.patient_model import PatientModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'patient')  # 'patient' or 'hospital'
    phone = data.get('phone', '')

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email and password are required."}), 400

    hospital_id = None
    patient_id = None
    user_id = UserModel.generate_next_user_id()

    if role == 'hospital':
        doc_id_num = data.get('doctor_id_number') or user_id
        hosp_input = (data.get('hospital_id') or data.get('hospital_name') or '').strip()
        specialty = data.get('specialty', 'General Medicine')
        qualification = data.get('qualification', 'MD')

        if not hosp_input:
            return jsonify({"success": False, "message": "Hospital ID is required for Doctor Registration."}), 400

        # Validate Hospital ID against database
        hospital = HospitalModel.get_by_id(hosp_input)
        if not hospital:
            all_hosps = HospitalModel.get_all()
            matched = [
                h for h in all_hosps 
                if h['hospital_id'].lower() == hosp_input.lower() or h['hospital_name'].lower() == hosp_input.lower()
            ]
            if matched:
                hospital = matched[0]

        if not hospital:
            return jsonify({
                "success": False, 
                "message": f"Invalid Hospital ID '{hosp_input}'. No hospital found matching this ID. Please enter a valid Hospital ID added by Admin (e.g. hosp-101 or hosp-102)."
            }), 400

        hospital_id = hospital['hospital_id']

        # Add doctor entry to hospital profile with matching Doctor ID
        doctor_obj = {
            "doctor_id": doc_id_num,
            "name": name if name.startswith("Dr.") else f"Dr. {name}",
            "specialty": specialty,
            "qualification": qualification
        }
        HospitalModel.add_doctor(hospital_id, doctor_obj)

    elif role == 'patient':
        patient_id = user_id
        age = data.get('age', 30)
        gender = data.get('gender', 'Male')
        blood_group = data.get('blood_group', 'O+')
        allergies = data.get('allergies', [])
        emergency_contact = data.get('emergency_contact', {})
        important_conditions = data.get('important_conditions', [])

        pat = PatientModel.create_patient_with_id(
            patient_id, user_id, name, age, gender, blood_group, 
            allergies, emergency_contact, important_conditions
        )

    user_data, error = UserModel.create_user(
        name=name,
        email=email,
        password=password,
        role=role,
        phone=phone,
        hospital_id=hospital_id,
        patient_id=patient_id,
        custom_user_id=user_id
    )

    if error:
        return jsonify({"success": False, "message": error}), 400

    if role == 'patient' and patient_id:
        PatientModel.update_profile(patient_id, {"user_id": user_data['user_id']})

    session['user_id'] = user_data['user_id']
    session['role'] = user_data['role']
    if hospital_id:
        session['hospital_id'] = hospital_id

    return jsonify({
        "success": True,
        "message": f"Account created successfully as {role.capitalize()}.",
        "user": user_data
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    expected_role = data.get('role')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = UserModel.get_by_email(email)
    if not user or user.get('password') != password:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    if expected_role and user.get('role') != expected_role:
        return jsonify({"success": False, "message": f"Account is registered as {user.get('role').capitalize()}, not {expected_role.capitalize()}."}), 403

    session['user_id'] = user['user_id']
    session['role'] = user['role']

    profile_data = {}
    if user['role'] == 'hospital' and user.get('hospital_id'):
        session['hospital_id'] = user['hospital_id']
        profile_data['hospital'] = HospitalModel.get_by_id(user['hospital_id'])
    elif user['role'] == 'patient' and user.get('patient_id'):
        profile_data['patient'] = PatientModel.get_by_id(user['patient_id'])

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": user,
        "profile": profile_data
    })


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "authenticated": False}), 401

    user = UserModel.get_by_id(user_id)
    if not user:
        return jsonify({"success": False, "authenticated": False}), 401

    profile_data = {}
    if user['role'] == 'hospital' and user.get('hospital_id'):
        profile_data['hospital'] = HospitalModel.get_by_id(user['hospital_id'])
    elif user['role'] == 'patient' and user.get('patient_id'):
        profile_data['patient'] = PatientModel.get_by_id(user['patient_id'])

    return jsonify({
        "success": True,
        "authenticated": True,
        "user": user,
        "profile": profile_data
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})
