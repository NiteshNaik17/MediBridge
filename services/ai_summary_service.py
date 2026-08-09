from backend.models.record_model import RecordModel
from backend.models.patient_model import PatientModel

class AISummaryService:
    @staticmethod
    def generate_patient_summary(patient_id):
        patient = PatientModel.get_by_id(patient_id)
        if not patient:
            return {
                "patient_name": "Unknown",
                "previous_conditions": [],
                "current_medication": [],
                "recent_reports": [],
                "last_hospital_visit": "None",
                "summary_text": "No patient record found."
            }

        records = RecordModel.get_by_patient(patient_id)

        # Aggregate diagnoses
        diagnoses = set()
        if patient.get("important_conditions"):
            for cond in patient["important_conditions"]:
                diagnoses.add(cond)

        medications = set()
        recent_reports = []
        last_visit = "No visits recorded"

        if records:
            last_visit = records[0].get('date', 'Unknown')
            for r in records:
                if r.get('diagnosis'):
                    diagnoses.add(r['diagnosis'])
                if r.get('medicines'):
                    for med in r['medicines']:
                        medications.add(med)
                
                recent_reports.append({
                    "title": r.get('document_type', 'Medical Report'),
                    "date": r.get('date', ''),
                    "hospital": r.get('hospital_name', 'Hospital')
                })

        summary_narrative = (
            f"Patient {patient.get('name')} ({patient.get('age')} Y/O {patient.get('gender')}) has "
            f"{len(diagnoses)} documented medical condition(s) including {', '.join(list(diagnoses)[:3]) if diagnoses else 'none'}. "
            f"Currently prescribed {len(medications)} active medication(s). "
            f"Last registered medical consultation was on {last_visit}."
        )

        return {
            "patient_name": patient.get("name"),
            "health_id": patient.get("health_id"),
            "blood_group": patient.get("blood_group"),
            "allergies": patient.get("allergies", []),
            "previous_conditions": list(diagnoses),
            "current_medication": list(medications),
            "recent_reports": recent_reports[:5], # top 5
            "last_hospital_visit": last_visit,
            "summary_text": summary_narrative
        }
