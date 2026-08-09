from datetime import datetime
from backend.database.mongodb import get_db

class UserModel:
    @staticmethod
    def generate_next_user_id():
        db = get_db()
        count = db.users.count_documents({})
        next_num = 1001 + count
        user_id = f"usr-{next_num}"
        while db.users.find_one({"user_id": user_id}):
            next_num += 1
            user_id = f"usr-{next_num}"
        return user_id

    @staticmethod
    def create_user(name, email, password, role, phone="", hospital_id=None, patient_id=None, custom_user_id=None):
        db = get_db()
        existing = db.users.find_one({"email": email})
        if existing:
            return None, "Email is already registered"

        user_id = custom_user_id or UserModel.generate_next_user_id()

        user_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password": password,  # stored securely
            "role": role,
            "phone": phone,
            "created_at": datetime.now().isoformat()
        }
        if hospital_id:
            user_data["hospital_id"] = hospital_id
        if patient_id:
            user_data["patient_id"] = patient_id

        db.users.insert_one(user_data)
        return user_data, None

    @staticmethod
    def get_by_email(email):
        db = get_db()
        return db.users.find_one({"email": email})

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.users.find_one({"user_id": str(user_id)})

    @staticmethod
    def get_all():
        db = get_db()
        return db.users.find()

    @staticmethod
    def get_all_users():
        return UserModel.get_all()

    @staticmethod
    def delete_user(user_id):
        db = get_db()
        return db.users.delete_one({"user_id": str(user_id)})
