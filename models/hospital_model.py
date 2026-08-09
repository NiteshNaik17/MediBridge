import uuid
from backend.database.mongodb import get_db

class HospitalModel:
    @staticmethod
    def get_all():
        db = get_db()
        return db.hospitals.find()

    @staticmethod
    def get_by_id(hospital_id):
        db = get_db()
        return db.hospitals.find_one({"hospital_id": hospital_id})

    @staticmethod
    def create_hospital(hospital_name, registration_number, address, departments=None):
        hospital_id = f"hosp-{uuid.uuid4().hex[:6]}"
        return HospitalModel.create_hospital_with_id(hospital_id, hospital_name, registration_number, address, departments)

    @staticmethod
    def create_hospital_with_id(hospital_id, hospital_name, registration_number, address, departments=None):
        db = get_db()
        hospital_data = {
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "registration_number": registration_number,
            "address": address,
            "verification_status": "Approved",
            "departments": departments or ["General Medicine", "Emergency"],
            "doctor_info": [],
            "created_at": "2026-08-07T12:00:00"
        }
        db.hospitals.insert_one(hospital_data)
        return hospital_data

    @staticmethod
    def add_doctor(hospital_id, doctor_obj):
        db = get_db()
        hospital = HospitalModel.get_by_id(hospital_id)
        if hospital:
            doctors = hospital.get('doctor_info', [])
            # Avoid duplicates
            if not any(d.get('doctor_id') == doctor_obj.get('doctor_id') for d in doctors):
                doctors.append(doctor_obj)
                db.hospitals.update_one(
                    {"hospital_id": hospital_id},
                    {"$set": {"doctor_info": doctors}}
                )
            return True
        return False

    @staticmethod
    def update_status(hospital_id, status):
        db = get_db()
        return db.hospitals.update_one(
            {"hospital_id": hospital_id},
            {"$set": {"verification_status": status}}
        )
