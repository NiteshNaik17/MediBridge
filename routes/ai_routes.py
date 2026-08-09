import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from backend.services.ocr_service import MedicalOCRService
from backend.services.ai_summary_service import AISummaryService
from backend.models.record_model import RecordModel

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/extract-doc', methods=['POST'])
def extract_document():
    """
    OCR Medical Document Extraction API:
    1. Upload PDF / Image / Text file
    2. Runs OCR / Text extraction
    3. Detects patient info, diagnosis, medicines, doctor, test results, date
    4. Returns structured JSON for review or auto-filling forms
    """
    if 'file' not in request.files and not request.json:
        return jsonify({"success": False, "message": "No file uploaded or payload provided."}), 400

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected."}), 400

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        relative_url = f"/uploads/medical_documents/{unique_filename}"
        extracted_text = MedicalOCRService.extract_text_from_file(file_path)
    else:
        # Fallback text mode
        extracted_text = request.json.get('text', '')
        relative_url = "/uploads/medical_documents/scanned_report.pdf"

    extracted_data = MedicalOCRService.parse_medical_information(extracted_text)
    extracted_data["document_url"] = relative_url

    # Auto-save to medical records if auto_save parameter set
    auto_save = request.form.get('auto_save', 'false').lower() == 'true'
    patient_id = request.form.get('patient_id', 'pat-201')
    hospital_id = request.form.get('hospital_id', 'hosp-101')

    if auto_save:
        record = RecordModel.create_record(
            patient_id=patient_id,
            hospital_id=hospital_id,
            document_url=relative_url,
            diagnosis=extracted_data.get('diagnosis'),
            medicines=extracted_data.get('medicines'),
            doctor_notes=f"AI Extracted Record. Raw snippet: {extracted_text[:150]}...",
            date=extracted_data.get('date'),
            doctor_name=extracted_data.get('doctor_name'),
            test_results=extracted_data.get('test_results')
        )
        extracted_data["record"] = record

    return jsonify({
        "success": True,
        "message": "Medical document scanned and analyzed by MediBridge AI.",
        "data": extracted_data
    })


@ai_bp.route('/health-summary', methods=['GET', 'POST'])
def generate_summary():
    patient_id = request.args.get('patient_id') or (request.get_json() or {}).get('patient_id', 'pat-201')
    summary = AISummaryService.generate_patient_summary(patient_id)
    return jsonify({
        "success": True,
        "summary": summary
    })
