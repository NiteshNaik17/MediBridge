import io
import socket

def get_lan_ip():
    """ Returns the laptop's LAN IP address (e.g. 192.168.x.x or 10.x.x.x) so mobile phones can connect """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class EmergencyPDFService:
    @staticmethod
    def generate_pdf_bytes(card):
        name = card.get('name', 'Patient')
        health_id = card.get('health_id', 'MB-0000-0000')
        age = card.get('age', 30)
        gender = card.get('gender', 'N/A')
        blood = card.get('blood_group', 'N/A')
        
        allergies = ", ".join(card.get('allergies', [])) if card.get('allergies') else "None recorded"
        conditions = ", ".join(card.get('important_conditions', [])) if card.get('important_conditions') else "None recorded"
        meds = ", ".join(card.get('medications', [])) if card.get('medications') else "None recorded"
        
        ec = card.get('emergency_contact', {})
        ec_name = ec.get('name', 'N/A')
        ec_rel = ec.get('relationship', 'Contact')
        ec_phone = ec.get('phone', 'N/A')

        lines = [
            "MEDIBRIDGE AI - EMERGENCY CRITICAL MEDICAL PROFILE",
            "==================================================================",
            f"PATIENT FULL NAME : {name}",
            f"DIGITAL HEALTH ID : {health_id}",
            f"AGE & GENDER      : {age} Y/O ({gender})",
            f"BLOOD GROUP       : {blood}",
            "------------------------------------------------------------------",
            "SEVERE KNOWN ALLERGIES:",
            f"  {allergies}",
            "",
            "CHRONIC CONDITIONS / DISEASES / DIAGNOSES:",
            f"  {conditions}",
            "",
            "ACTIVE PRESCRIBED MEDICATIONS:",
            f"  {meds}",
            "------------------------------------------------------------------",
            "EMERGENCY CONTACT PERSON:",
            f"  {ec_name} ({ec_rel}): {ec_phone}",
            "==================================================================",
            "Verified by MediBridge AI Centralized Digital Healthcare Ecosystem"
        ]

        text_ops = ["BT", "/F1 11 Tf", "14 TL", "40 750 Td"]
        for line in lines:
            escaped = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            text_ops.append(f"({escaped}) Tj T*")
        text_ops.append("ET")

        stream_data = "\n".join(text_ops).encode('latin-1')

        objects = []
        objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        objects.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        objects.append("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")
        objects.append("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
        
        obj5_header = f"5 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode('latin-1')
        obj5_footer = "\nendstream\nendobj\n".encode('latin-1')

        pdf_bytes = bytearray(b"%PDF-1.4\n")
        offsets = []

        for obj in objects[:4]:
            offsets.append(len(pdf_bytes))
            pdf_bytes.extend(obj.encode('latin-1'))
        
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj5_header)
        pdf_bytes.extend(stream_data)
        pdf_bytes.extend(obj5_footer)

        startxref = len(pdf_bytes)
        pdf_bytes.extend(b"xref\n0 6\n0000000000 65535 f \n")
        for off in offsets:
            pdf_bytes.extend(f"{off:010d} 00000 n \n".encode('latin-1'))

        pdf_bytes.extend(f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n".encode('latin-1'))
        return bytes(pdf_bytes)
