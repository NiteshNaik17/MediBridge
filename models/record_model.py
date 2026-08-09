import uuid
from datetime import datetime
from backend.database.mongodb import get_db

class RecordModel:
    @staticmethod
    def create_record(patient_id, hospital_id, document_url, diagnosis, medicines, doctor_notes, date=None, hospital_name="", doctor_name="", document_type="Medical Document", test_results=None):
        db = get_db()
        record_id = f"rec-{uuid.uuid4().hex[:8]}"
        record_data = {
            "record_id": record_id,
            "patient_id": patient_id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "doctor_name": doctor_name,
            "document_url": document_url,
            "document_type": document_type,
            "diagnosis": diagnosis,
            "medicines": medicines if isinstance(medicines, list) else ([medicines] if medicines else []),
            "doctor_notes": doctor_notes,
            "test_results": test_results if test_results else {},
            "date": date if date else datetime.now().strftime("%Y-%m-%d"),
            "verification_status": "Verified",
            "created_at": datetime.now().isoformat()
        }
        db.medical_records.insert_one(record_data)
        return record_data

    @staticmethod
    def get_by_patient(patient_id):
        db = get_db()
        records = db.medical_records.find({"patient_id": patient_id})
        # Sort chronologically (descending for latest records first)
        return sorted(records, key=lambda x: x.get('date', ''), reverse=True)

    @staticmethod
    def get_by_hospital(hospital_id):
        db = get_db()
        records = db.medical_records.find({"hospital_id": hospital_id})
        return sorted(records, key=lambda x: x.get('date', ''), reverse=True)

    @staticmethod
    def get_all():
        db = get_db()
        return db.medical_records.find()
