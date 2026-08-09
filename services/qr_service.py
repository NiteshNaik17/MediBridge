import io
import base64
from backend.services.pdf_service import get_lan_ip

class QRService:
    @staticmethod
    def generate_emergency_qr(patient_data, host_url=None):
        """
        Generates QR code encoding the direct PDF file URL using LAN IP (or host_url).
        When scanned by any mobile phone camera, it opens the PDF document directly.
        """
        patient_id = patient_data.get('patient_id', 'pat-201')
        
        if not host_url or 'localhost' in host_url or '127.0.0.1' in host_url:
            lan_ip = get_lan_ip()
            host_url = f"http://{lan_ip}:5000"

        # Direct scannable URL to the PDF file
        target_pdf_url = f"{host_url}/api/patient/emergency-pdf-file?patient_id={patient_id}"

        try:
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(target_pdf_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#ef4444", back_color="white")
            
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"python qrcode library notice ({e}); generating URL payload.")
            encoded_payload = base64.b64encode(target_pdf_url.encode('utf-8')).decode('utf-8')
            return f"data:text/plain;base64,{encoded_payload}"
