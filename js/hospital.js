/* ==========================================================================
   MEDIBRIDGE AI - HOSPITAL PORTAL SCRIPT
   ========================================================================== */

function getLoggedInHospitalId() {
  const userStr = localStorage.getItem('medibridge_user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      if (user && user.hospital_id) {
        return user.hospital_id;
      }
    } catch (e) {}
  }
  return '';
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('/hospital/')) {
    loadHospitalDashboard();
  }
});

async function loadHospitalDashboard() {
  const hospId = getLoggedInHospitalId();
  const url = hospId ? `/api/hospitals/dashboard?hospital_id=${hospId}` : '/api/hospitals/dashboard';

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (!data.success) return;

    const hosp = data.hospital;
    if (hosp) {
      if (document.getElementById('hosp-header-title')) document.getElementById('hosp-header-title').textContent = hosp.hospital_name || 'Hospital Clinical Overview';
      if (document.getElementById('hosp-header-sub')) document.getElementById('hosp-header-sub').textContent = `${hosp.hospital_name} • ${hosp.address || 'Hospital Digital Records Portal'}`;
      if (document.getElementById('hosp-sidebar-name')) document.getElementById('hosp-sidebar-name').textContent = hosp.hospital_name || 'Hospital Portal';
      if (document.getElementById('hosp-sidebar-avatar')) {
        const initials = hosp.hospital_name ? hosp.hospital_name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0,2) : 'HP';
        document.getElementById('hosp-sidebar-avatar').textContent = initials;
      }
    }

    // Update Dashboard Metrics
    const totalPats = document.getElementById('stat-total-patients');
    const totalRecs = document.getElementById('stat-total-records');
    const totalDocs = document.getElementById('stat-total-doctors');
    const totalApts = document.getElementById('stat-total-appointments');

    if (totalPats) totalPats.textContent = data.stats.total_patients;
    if (totalRecs) totalRecs.textContent = data.stats.total_records;
    if (totalDocs) totalDocs.textContent = data.stats.total_doctors;
    if (totalApts) totalApts.textContent = data.stats.total_appointments;

    // Render Doctors Table
    const doctorsTbody = document.getElementById('doctors-tbody');
    if (doctorsTbody) {
      if (data.doctors && data.doctors.length > 0) {
        doctorsTbody.innerHTML = data.doctors.map(d => `
          <tr>
            <td><strong>${d.name}</strong></td>
            <td><span class="badge badge-info">${d.specialty}</span></td>
            <td>${d.qualification || 'MD'}</td>
            <td><span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Active Staff</span></td>
          </tr>
        `).join('');
      } else {
        doctorsTbody.innerHTML = `
          <tr>
            <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              No doctors registered under this hospital yet.
            </td>
          </tr>
        `;
      }
    }

    // Render Recent Records Table
    const recentTbody = document.getElementById('recent-records-tbody');
    if (recentTbody) {
      if (data.recent_records && data.recent_records.length > 0) {
        recentTbody.innerHTML = data.recent_records.map(r => `
          <tr>
            <td><strong>${r.record_id}</strong></td>
            <td>${r.doctor_name || 'Attending Doctor'}</td>
            <td><span class="badge badge-info">${r.document_type || 'Prescription'}</span></td>
            <td>${r.diagnosis}</td>
            <td>${r.date}</td>
            <td><span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> ${r.verification_status}</span></td>
          </tr>
        `).join('');
      } else {
        recentTbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              No medical records uploaded yet. Click <strong>"Upload & AI Scan Report"</strong> to add patient records.
            </td>
          </tr>
        `;
      }
    }

    // Render Appointments Table
    const aptsTbody = document.getElementById('appointments-tbody');
    if (aptsTbody) {
      if (data.appointments && data.appointments.length > 0) {
        aptsTbody.innerHTML = data.appointments.map(a => `
          <tr>
            <td><strong>${a.patient_name}</strong></td>
            <td>${a.doctor}</td>
            <td>${a.department || 'General Medicine'}</td>
            <td>${a.date} at ${a.time || '10:00 AM'}</td>
            <td><span class="badge badge-warning">${a.status}</span></td>
          </tr>
        `).join('');
      } else {
        aptsTbody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              No consultations scheduled yet.
            </td>
          </tr>
        `;
      }
    }

    // Load dynamic patient select list
    loadPatientSelectList();

  } catch (err) {
    console.error('Error loading hospital dashboard data:', err);
  }
}

async function loadPatientSelectList() {
  const select = document.getElementById('select-patient');
  if (!select) return;

  try {
    const res = await fetch('/api/hospitals/patients');
    const data = await res.json();
    if (data.success && data.patients && data.patients.length > 0) {
      select.innerHTML = data.patients.map(p => 
        `<option value="${p.patient_id}">${p.name} (${p.health_id || 'MB-PATIENT'})</option>`
      ).join('');
    } else {
      select.innerHTML = `<option value="">No patients found</option>`;
    }
  } catch (e) {}
}

// Open Record Upload & AI Scanning Modal
function openUploadModal() {
  loadPatientSelectList();
  const modal = document.getElementById('upload-modal');
  if (modal) modal.classList.add('active');
}

function closeModal() {
  const modal = document.getElementById('upload-modal');
  if (modal) modal.classList.remove('active');
}

// Trigger OCR Scanning on File Selection
async function scanMedicalDocument() {
  const fileInput = document.getElementById('medical-file');
  const previewBox = document.getElementById('ocr-preview-results');
  const scanBtn = document.getElementById('scan-btn');

  if (!fileInput || !fileInput.files[0]) {
    showToast('Please select a PDF or Image file to scan.', 'error');
    return;
  }

  const selectedPatientId = document.getElementById('select-patient')?.value || 'pat-201';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('patient_id', selectedPatientId);

  if (scanBtn) scanBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Scanning Document with AI...';

  try {
    const res = await fetch('/api/ai/extract-doc', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();

    if (result.success && result.data) {
      showToast('Document analyzed successfully by OCR engine!', 'success');
      const d = result.data;

      // Auto-fill fields
      if (document.getElementById('diagnosis')) document.getElementById('diagnosis').value = d.diagnosis;
      if (document.getElementById('doctor_name')) document.getElementById('doctor_name').value = d.doctor_name;
      if (document.getElementById('medicines')) document.getElementById('medicines').value = d.medicines.join(', ');
      if (document.getElementById('date')) document.getElementById('date').value = d.date;

      if (previewBox) {
        previewBox.style.display = 'block';
        previewBox.innerHTML = `
          <div class="ai-banner-content" style="background: var(--primary-50); border-color: var(--primary-200); color: var(--text-dark);">
            <h4 style="color: var(--primary-500);"><i class="fa-solid fa-wand-magic-sparkles"></i> AI Extracted Data Preview</h4>
            <p><strong>Patient Detected:</strong> ${d.patient_name}</p>
            <p><strong>Diagnosis:</strong> ${d.diagnosis}</p>
            <p><strong>Medicines:</strong> ${d.medicines.join(', ')}</p>
            <p><strong>Doctor:</strong> ${d.doctor_name}</p>
          </div>
        `;
      }
    } else {
      showToast(result.message || 'Scanning failed.', 'error');
    }
  } catch (err) {
    showToast('OCR Processing error.', 'error');
  } finally {
    if (scanBtn) scanBtn.innerHTML = '<i class="fa-solid fa-file-medical"></i> Scan with AI OCR';
  }
}

// Save Record Submission
async function submitHospitalRecord(e) {
  e.preventDefault();
  const hospId = getLoggedInHospitalId();
  const patient_id = document.getElementById('select-patient')?.value;
  const diagnosis = document.getElementById('diagnosis').value;
  const doctor_name = document.getElementById('doctor_name').value || 'Doctor';
  const medicines = document.getElementById('medicines').value.split(',').map(m => m.trim());
  const doctor_notes = document.getElementById('doctor_notes').value;
  const date = document.getElementById('date').value;

  if (!patient_id) {
    showToast('Please select a patient to assign this record.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/hospitals/records', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id,
        hospital_id: hospId,
        doctor_name,
        diagnosis,
        medicines,
        doctor_notes,
        date
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Record saved to Patient Central Record!', 'success');
      closeModal();
      loadHospitalDashboard();
    }
  } catch (err) {
    showToast('Failed to save medical record.', 'error');
  }
}
