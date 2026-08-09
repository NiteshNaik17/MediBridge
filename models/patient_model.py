from backend.database.mongodb import get_db

class PatientModel:
    @staticmethod
    def get_all():
        db = get_db()
        return db.patients.find()

    @staticmethod
    def get_by_id(patient_id):
        db = get_db()
        pat = db.patients.find_one({"patient_id": patient_id})
        if not pat:
            pat = db.patients.find_one({"user_id": patient_id})
        return pat

    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        pat = db.patients.find_one({"user_id": user_id})
        if not pat:
            pat = db.patients.find_one({"patient_id": user_id})
        return pat

    @staticmethod
    def create_patient_with_id(patient_id, user_id, name, age, gender, blood_group, allergies=None, emergency_contact=None, important_conditions=None):
        db = get_db()
        num_str = str(patient_id).replace('usr-', '').replace('pat-', '')
        health_id = f"MB-{num_str}-4112"

        patient_data = {
            "patient_id": patient_id,
            "user_id": user_id,
            "name": name,
            "age": int(age) if str(age).isdigit() else 30,
            "gender": gender,
            "blood_group": blood_group,
            "health_id": health_id,
            "allergies": allergies or [],
            "important_conditions": important_conditions or [],
            "emergency_contact": emergency_contact or {
                "name": "N/A",
                "relationship": "Contact",
                "phone": "N/A"
            },
            "connected_hospitals": [],
            "created_at": "2026-08-07T12:00:00"
        }

        db.patients.insert_one(patient_data)
        return patient_data

    @staticmethod
    def create_patient(user_id, name, age, gender, blood_group, allergies=None, emergency_contact=None, important_conditions=None):
        db = get_db()
        pat_count = db.patients.count_documents({})
        next_num = 1001 + pat_count
        patient_id = f"usr-{next_num}"
        while db.patients.find_one({"patient_id": patient_id}):
            next_num += 1
            patient_id = f"usr-{next_num}"
        return PatientModel.create_patient_with_id(patient_id, user_id, name, age, gender, blood_group, allergies, emergency_contact, important_conditions)

    @staticmethod
    def update_profile(patient_id, update_data):
        db = get_db()
        db.patients.update_one(
            {"patient_id": patient_id},
            {"$set": update_data}
        )
        return PatientModel.get_by_id(patient_id)

    @staticmethod
    def add_hospital_connection(patient_id, hospital_id):
        db = get_db()
        patient = PatientModel.get_by_id(patient_id)
        if patient:
            connected = patient.get('connected_hospitals', [])
            if hospital_id not in connected:
                connected.append(hospital_id)
                db.patients.update_one(
                    {"patient_id": patient_id},
                    {"$set": {"connected_hospitals": connected}}
                )
            return True
        return False
