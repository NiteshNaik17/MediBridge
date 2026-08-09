# MediBridge AI - Full-Stack Centralized Healthcare Platform

MediBridge AI is a state-of-the-art healthcare ecosystem connecting multiple hospitals, patients, and administrators through a unified digital medical record platform.

## Key Features
- **Hospital / Doctor Portal**: Manage patient profiles, review medical records, upload diagnostic lab reports/prescriptions with AI auto-fill, and schedule consultations.
- **Patient Portal**: Unique Digital Health ID generation (`MB-XXXX-XXXX`), interactive multi-year chronological medical timeline, AI-generated health history summary, and emergency digital pass with printable QR code.
- **AI Module**: Optical Character Recognition (OCR) and Natural Language Information Extraction for PDF/image medical reports, automatic timeline updates, and clinical risk summaries.
- **Admin Portal**: Institutional verification approval workflow for registered hospitals, user management, and system-wide analytics.
- **Dual Database Architecture**: Connects seamlessly to MongoDB via PyMongo with an out-of-the-box in-memory fallback database pre-seeded with realistic sample data.

---

## Folder Structure
```text
MediBridge-AI/
├── frontend/
│   ├── index.html          # Public Landing Page
│   ├── login.html          # Multi-role Login Page
│   ├── register.html       # Hospital & Patient Signup Page
│   ├── hospital/           # Hospital Portal Pages
│   ├── patient/            # Patient Portal Pages
│   ├── admin/              # System Admin Pages
│   ├── css/                # Design token & dashboard styles
│   └── js/                 # Auth, Hospital, Patient & Admin scripts
├── backend/
│   ├── app.py              # Flask Server Entry Point
│   ├── config.py           # Configuration File
│   ├── requirements.txt    # Python Dependencies
│   ├── database/           # MongoDB Connection & Mock Engine
│   ├── models/             # User, Hospital, Patient & Record Models
│   ├── routes/             # RESTful API Endpoints
│   ├── services/           # OCR Engine, AI Summarizer & QR Code Generator
│   └── uploads/            # Medical Document Storage
├── .env                    # Environment Variables
└── README.md
```

---

## Local Setup & Quickstart

1. **Clone & Navigate into the project folder**:
   ```bash
   cd MediBridge-AI
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python backend/app.py
   ```

4. **Open in Web Browser**:
   Navigate to `http://localhost:5000`

---

## Demo Credentials

You can log in directly using the following pre-seeded credentials:

- **Patient Portal**:
  - Email: `sarah.connor@example.com`
  - Password: `patient123`
- **Hospital Portal**:
  - Email: `contact@apollohealth.org`
  - Password: `hospital123`
- **System Admin**:
  - Email: `admin@medibridge.ai`
  - Password: `admin123`

---

## Render Deployment Instructions

1. **Create Web Service on Render**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `gunicorn backend.app:app`
2. **Environment Variables**:
   - `SECRET_KEY`: (Set a strong secret)
   - `MONGO_URI`: (Optional MongoDB Atlas Connection URL)
   - `PORT`: 10000 (Render default)
