import uuid
from datetime import datetime

def _clean_doc(doc):
    if not doc:
        return doc
    d = dict(doc)
    if '_id' in d:
        d['_id'] = str(d['_id'])
    return d

class InMemoryCollection:
    def __init__(self, initial_data=None):
        self._data = list(initial_data) if initial_data else []

    def find(self, query=None, projection=None):
        if not query:
            return [_clean_doc(doc) for doc in self._data]
        results = []
        for doc in self._data:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(_clean_doc(doc))
        return results

    def find_one(self, query=None):
        results = self.find(query)
        return results[0] if results else None

    def insert_one(self, document):
        doc = dict(document)
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        self._data.append(doc)
        class InsertResult:
            inserted_id = doc['_id']
        return InsertResult()

    def update_one(self, query, update):
        target = self.find_one(query)
        if target:
            for index, item in enumerate(self._data):
                if item.get('_id') == target.get('_id'):
                    if '$set' in update:
                        for k, v in update['$set'].items():
                            self._data[index][k] = v
                    return True
        return False

    def delete_one(self, query):
        target = self.find_one(query)
        if target:
            self._data = [doc for doc in self._data if doc.get('_id') != target.get('_id')]
            return True
        return False

    def count_documents(self, query=None):
        return len(self.find(query))


class MongoCollectionWrapper:
    """ Wraps a PyMongo collection to ensure all returned docs have string _id """
    def __init__(self, collection):
        self._col = collection

    def find(self, query=None):
        raw = self._col.find(query or {})
        return [_clean_doc(d) for d in raw]

    def find_one(self, query=None):
        raw = self._col.find_one(query or {})
        return _clean_doc(raw) if raw else None

    def insert_one(self, document):
        return self._col.insert_one(document)

    def update_one(self, query, update):
        return self._col.update_one(query, update)

    def delete_one(self, query):
        return self._col.delete_one(query)

    def count_documents(self, query=None):
        return self._col.count_documents(query or {})


class DatabaseManager:
    def __init__(self):
        self.is_mongo = False
        self.db = None
        self._init_db()

    def _init_db(self):
        try:
            import pymongo
            from backend.config import Config
            client = pymongo.MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
            client.server_info()
            raw_db = client.get_database()
            
            class MongoWrapperDB:
                def __init__(self, db):
                    self.users = MongoCollectionWrapper(db.users)
                    self.hospitals = MongoCollectionWrapper(db.hospitals)
                    self.patients = MongoCollectionWrapper(db.patients)
                    self.medical_records = MongoCollectionWrapper(db.medical_records)
                    self.appointments = MongoCollectionWrapper(db.appointments)

            self.db = MongoWrapperDB(raw_db)
            self.is_mongo = True
            print("Connected successfully to MongoDB server with ObjectId auto-serializer.")
            
            # Ensure Admin user exists with user_id usr-1001
            admin_user = self.db.users.find_one({"role": "admin"})
            if not admin_user:
                self.db.users.insert_one({
                    "user_id": "usr-1001",
                    "name": "Platform Administrator",
                    "email": "admin@gmail.com",
                    "password": "admin123",
                    "role": "admin",
                    "phone": "+1-800-555-0199",
                    "created_at": datetime.now().isoformat()
                })
            else:
                self.db.users.update_one({"role": "admin"}, {"$set": {"email": "admin@gmail.com", "user_id": "usr-1001"}})

        except Exception as e:
            print(f"MongoDB connection notice ({e}). Running in resilient fallback mode.")
            self.db = self._create_in_memory_db()

    def _create_in_memory_db(self):
        users_seed = [
            {
                "_id": "usr-1001",
                "user_id": "usr-1001",
                "name": "Platform Administrator",
                "email": "admin@gmail.com",
                "password": "admin123",
                "role": "admin",
                "phone": "+1-800-555-0199",
                "created_at": "2024-01-10T10:00:00"
            }
        ]

        hospitals_seed = [
            {
                "_id": "hosp-101",
                "hospital_id": "hosp-101",
                "hospital_name": "Apollo General Hospital",
                "registration_number": "REG-HOSP-2026-9082",
                "address": "104 Healthcare Boulevard, Suite 300, Metro City",
                "verification_status": "Approved",
                "departments": ["Cardiology", "Neurology", "Endocrinology"],
                "doctor_info": [],
                "created_at": "2024-01-15T09:00:00"
            },
            {
                "_id": "hosp-102",
                "hospital_id": "hosp-102",
                "hospital_name": "St. Jude Medical Center",
                "registration_number": "REG-HOSP-2026-4410",
                "address": "782 St. Jude Lane, Westside",
                "verification_status": "Approved",
                "departments": ["Pulmonology", "General Medicine"],
                "doctor_info": [],
                "created_at": "2024-02-01T11:00:00"
            }
        ]

        patients_seed = []
        medical_records_seed = []
        appointments_seed = []

        class InMemDB:
            def __init__(self):
                self.users = InMemoryCollection(users_seed)
                self.hospitals = InMemoryCollection(hospitals_seed)
                self.patients = InMemoryCollection(patients_seed)
                self.medical_records = InMemoryCollection(medical_records_seed)
                self.appointments = InMemoryCollection(appointments_seed)

        return InMemDB()

db_manager = DatabaseManager()

def get_db():
    return db_manager.db
