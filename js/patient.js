/* ==========================================================================
   MEDIBRIDGE AI - PATIENT PORTAL SCRIPT
   ========================================================================== */

let currentPatientData = null;

function getLoggedInPatientId() {
  const userStr = localStorage.getItem('medibridge_user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      if (user && user.patient_id) {
        return user.patient_id;
      }
    } catch (e) {}
  }
  return 'pat-201'; // Default fallback demo patient if not logged in
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('/patient/')) {
    loadPatientDashboard();
  }
});

async function loadPatientDashboard() {
  const patientId = getLoggedInPatientId();

  try {
    const res = await fetch(`/api/patient/dashboard?patient_id=${patientId}`);
    const data = await res.json();

    if (!data.success) return;

    const pat = data.patient;
    currentPatientData = pat;
    const summary = data.summary;

    if (!pat) return;

    // Sidebar User Badge
    if (document.getElementById('pat-name')) document.getElementById('pat-name').textContent = pat.name;
    if (document.getElementById('pat-health-id')) document.getElementById('pat-health-id').textContent = pat.health_id;
    if (document.getElementById('sidebar-avatar')) {
      const initials = pat.name ? pat.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0,2) : 'PT';
      document.getElementById('sidebar-avatar').textContent = initials;
    }

    // Dashboard Quick Metrics
    if (document.getElementById('pat-blood-group')) document.getElementById('pat-blood-group').textContent = pat.blood_group || 'N/A';
    if (document.getElementById('pat-age-gender')) document.getElementById('pat-age-gender').textContent = `${pat.age || '30'} Y/O (${pat.gender || 'N/A'})`;
    
    // Allergies Badge Render on Dashboard
    const allergiesContainer = document.getElementById('pat-allergies-list');
    if (allergiesContainer) {
      if (pat.allergies && pat.allergies.length > 0) {
        allergiesContainer.innerHTML = pat.allergies.map(a => `<span class="badge badge-danger">${a}</span>`).join(' ');
      } else {
        allergiesContainer.innerHTML = `<span class="badge badge-info">No known allergies</span>`;
      }
    }

    // Health Profile Page Specific Elements (`profile.html`)
    if (document.getElementById('prof-header-name')) document.getElementById('prof-header-name').textContent = pat.name;
    if (document.getElementById('prof-header-health-id')) document.getElementById('prof-header-health-id').textContent = pat.health_id;
    if (document.getElementById('prof-full-name')) document.getElementById('prof-full-name').textContent = pat.name;
    if (document.getElementById('prof-health-id')) document.getElementById('prof-health-id').textContent = pat.health_id;
    if (document.getElementById('prof-age-gender')) document.getElementById('prof-age-gender').textContent = `${pat.age || '30'} Y/O (${pat.gender || 'N/A'})`;
    if (document.getElementById('prof-blood-group')) document.getElementById('prof-blood-group').textContent = pat.blood_group || 'N/A';
    if (document.getElementById('prof-email')) document.getElementById('prof-email').textContent = pat.email || 'Registered Patient';
    if (document.getElementById('prof-phone')) document.getElementById('prof-phone').textContent = pat.phone || 'N/A';
    
    const profAllergies = document.getElementById('prof-allergies-list');
    if (profAllergies) {
      if (pat.allergies && pat.allergies.length > 0) {
        profAllergies.innerHTML = pat.allergies.map(a => `<span class="badge badge-danger" style="margin-right: 4px;">${a}</span>`).join('');
      } else {
        profAllergies.innerHTML = `<span class="badge badge-info">No known allergies</span>`;
      }
    }

    const profEmergency = document.getElementById('prof-emergency-contact');
    if (profEmergency) {
      const ec = pat.emergency_contact || {};
      if (ec.name && ec.name !== 'N/A') {
        profEmergency.textContent = `${ec.name} (${ec.relationship || 'Contact'}): ${ec.phone || 'N/A'}`;
      } else {
        profEmergency.innerHTML = `<span style="color: var(--text-muted);">Not added yet. Click "Edit Profile" to set.</span>`;
      }
    }

    // AI Summary Render (Dashboard)
    const aiSummaryBox = document.getElementById('ai-summary-container');
    if (aiSummaryBox && summary) {
      aiSummaryBox.innerHTML = `
        <div class="ai-banner">
          <h3><i class="fa-solid fa-brain"></i> MediBridge AI Health Summary</h3>
          <p style="font-size: 1.05rem; opacity: 0.95;">${summary.summary_text}</p>
          <div class="ai-banner-content">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
              <div>
                <strong style="color: #ffffff;"><i class="fa-solid fa-stethoscope"></i> Diagnoses</strong>
                <p style="font-size: 0.85rem; margin-top: 4px;">${summary.previous_conditions.join(', ') || 'None'}</p>
              </div>
              <div>
                <strong style="color: #ffffff;"><i class="fa-solid fa-pills"></i> Current Medication</strong>
                <p style="font-size: 0.85rem; margin-top: 4px;">${summary.current_medication.join(', ') || 'None'}</p>
              </div>
              <div>
                <strong style="color: #ffffff;"><i class="fa-solid fa-calendar-check"></i> Last Hospital Visit</strong>
                <p style="font-size: 0.85rem; margin-top: 4px;">${summary.last_hospital_visit}</p>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Load Timeline if on Timeline Page
    if (window.location.pathname.includes('timeline.html')) {
      loadTimelineData(patientId);
    }

    // Load Emergency Card if on Emergency Page
    if (window.location.pathname.includes('emergency.html')) {
      loadEmergencyPass(patientId);
    }

    // Load Hospital Connections if on Profile Page
    if (window.location.pathname.includes('profile.html')) {
      loadHospitalConnections(patientId);
    }

  } catch (err) {
    console.error('Error fetching patient dashboard:', err);
  }
}

function openEditProfileModal() {
  const modal = document.getElementById('edit-profile-modal');
  if (modal) {
    modal.classList.add('active');
    if (currentPatientData) {
      if (document.getElementById('edit-name')) document.getElementById('edit-name').value = currentPatientData.name || '';
      if (document.getElementById('edit-age')) document.getElementById('edit-age').value = currentPatientData.age || 30;
      if (document.getElementById('edit-gender')) document.getElementById('edit-gender').value = currentPatientData.gender || 'Male';
      if (document.getElementById('edit-blood')) document.getElementById('edit-blood').value = currentPatientData.blood_group || 'A-Positive (A+)';
      if (document.getElementById('edit-allergies')) document.getElementById('edit-allergies').value = (currentPatientData.allergies || []).join(', ');
      
      const ec = currentPatientData.emergency_contact || {};
      if (document.getElementById('edit-em-name')) document.getElementById('edit-em-name').value = (ec.name && ec.name !== 'N/A') ? ec.name : '';
      if (document.getElementById('edit-em-relation')) document.getElementById('edit-em-relation').value = (ec.relationship && ec.relationship !== 'Contact') ? ec.relationship : '';
      if (document.getElementById('edit-em-phone')) document.getElementById('edit-em-phone').value = (ec.phone && ec.phone !== 'N/A') ? ec.phone : '';
    }
  }
}

function closeEditProfileModal() {
  const modal = document.getElementById('edit-profile-modal');
  if (modal) modal.classList.remove('active');
}

async function saveProfileUpdates(e) {
  e.preventDefault();
  const patientId = getLoggedInPatientId();

  const name = document.getElementById('edit-name').value;
  const age = document.getElementById('edit-age').value;
  const gender = document.getElementById('edit-gender').value;
  const blood_group = document.getElementById('edit-blood').value;
  const allergiesStr = document.getElementById('edit-allergies').value;
  const allergies = allergiesStr ? allergiesStr.split(',').map(s => s.trim()) : [];
  
  const emergency_contact = {
    name: document.getElementById('edit-em-name').value || 'N/A',
    relationship: document.getElementById('edit-em-relation').value || 'Contact',
    phone: document.getElementById('edit-em-phone').value || 'N/A'
  };

  try {
    const res = await fetch(`/api/patient/profile?patient_id=${patientId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        age: parseInt(age) || 30,
        gender,
        blood_group,
        allergies,
        emergency_contact
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Profile and Emergency Contact updated successfully!', 'success');
      closeEditProfileModal();
      loadPatientDashboard();
    }
  } catch (err) {
    showToast('Failed to update profile.', 'error');
  }
}

async function loadTimelineData(patientId) {
  const container = document.getElementById('timeline-container');
  if (!container) return;
  patientId = patientId || getLoggedInPatientId();

  try {
    const res = await fetch(`/api/patient/timeline?patient_id=${patientId}`);
    const data = await res.json();

    if (!data.success || !data.timeline || Object.keys(data.timeline).length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 3rem 1rem;">
          <i class="fa-solid fa-folder-open" style="font-size: 3rem; color: var(--text-light); margin-bottom: 1rem;"></i>
          <h3>No Medical Records Found</h3>
          <p class="text-muted">Upload your medical documents or visit a partner hospital to start your timeline.</p>
          <a href="/patient/upload.html" class="btn btn-primary" style="margin-top: 1rem;">Upload Document</a>
        </div>
      `;
      return;
    }

    let html = '';
    const years = Object.keys(data.timeline).sort().reverse();

    years.forEach(year => {
      html += `
        <div class="timeline-year-group">
          <div class="timeline-year-badge">${year}</div>
          ${data.timeline[year].map(r => `
            <div class="timeline-item">
              <div class="timeline-card">
                <div class="timeline-meta">
                  <span><i class="fa-solid fa-hospital"></i> ${r.hospital_name || 'Hospital'}</span>
                  <span><i class="fa-regular fa-calendar"></i> ${r.date}</span>
                </div>
                <h4 style="color: var(--primary-500); margin-bottom: 6px;">${r.diagnosis}</h4>
                <p style="font-size: 0.9rem; color: var(--text-dark);"><strong>Doctor:</strong> ${r.doctor_name || 'Dr. Aris Thorne'}</p>
                <p style="font-size: 0.9rem; color: var(--text-muted); margin-top: 6px;">${r.doctor_notes || ''}</p>
                ${r.medicines && r.medicines.length ? `
                  <div style="margin-top: 10px;">
                    <strong style="font-size: 0.85rem;"><i class="fa-solid fa-prescription-bottle-medical"></i> Prescribed Medicines:</strong>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px;">
                      ${r.medicines.map(m => `<span class="badge badge-info">${m}</span>`).join('')}
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      `;
    });

    container.innerHTML = html;
  } catch (err) {
    console.error('Timeline error:', err);
  }
}

async function loadEmergencyPass(patientId) {
  const container = document.getElementById('emergency-pass-wrapper');
  if (!container) return;
  patientId = patientId || getLoggedInPatientId();

  try {
    const res = await fetch(`/api/patient/emergency?patient_id=${patientId}`);
    const data = await res.json();

    if (data.success && data.emergency_card) {
      const card = data.emergency_card;
      const ec = card.emergency_contact || {};
      const ecDisplay = (ec.name && ec.name !== 'N/A') ? `${ec.name} (${ec.relationship || 'Contact'}): ${ec.phone || 'N/A'}` : 'Not specified';
      
      const condList = (card.important_conditions && card.important_conditions.length > 0) ? card.important_conditions.join(', ') : 'None recorded';

      container.innerHTML = `
        <div class="emergency-card-container">
          <div class="emergency-header">
            <span><i class="fa-solid fa-truck-medical"></i> EMERGENCY HEALTH PASS</span>
            <span>MEDIBRIDGE AI</span>
          </div>
          <div class="emergency-body">
            <div>
              <h3 style="font-size: 1.5rem; color: var(--text-dark);">${card.name}</h3>
              <p style="font-weight: 800; color: var(--primary-500); margin-bottom: 0.8rem;">Health ID: ${card.health_id}</p>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.8rem;">
                <div>
                  <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">BLOOD GROUP</span>
                  <span class="badge badge-danger" style="font-size: 0.95rem; padding: 4px 10px;">${card.blood_group}</span>
                </div>
                <div>
                  <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">AGE & GENDER</span>
                  <span style="font-weight: 700; font-size: 0.9rem;">${card.age || 30} Y/O (${card.gender || 'N/A'})</span>
                </div>
              </div>

              <div style="margin-bottom: 0.8rem;">
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">KNOWN ALLERGIES</span>
                <p style="font-weight: 700; color: #dc2626; font-size: 0.9rem;">${(card.allergies && card.allergies.length) ? card.allergies.join(', ') : 'None'}</p>
              </div>

              <div style="margin-bottom: 0.8rem;">
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">CONDITIONS & DISEASES</span>
                <p style="font-weight: 700; color: #d97706; font-size: 0.85rem;">${condList}</p>
              </div>

              <div style="margin-bottom: 0.8rem;">
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">EMERGENCY CONTACT</span>
                <p style="font-weight: 700; font-size: 0.9rem;">${ecDisplay}</p>
              </div>
            </div>

            <div style="text-align: center;">
              <div class="emergency-qr">
                <img src="${card.qr_code}" alt="Emergency QR Code" />
              </div>
              <span style="font-size: 0.75rem; color: var(--text-muted); margin-top: 6px; display: block;">Scan QR Code to open scannable Emergency PDF</span>
              
              <a href="/api/patient/emergency-pdf-file?patient_id=${card.patient_id}" target="_blank" class="btn btn-primary btn-sm" style="margin-top: 10px; width: 100%;">
                <i class="fa-solid fa-file-pdf"></i> Download / View Emergency PDF File
              </a>
            </div>
          </div>
        </div>
      `;
    }
  } catch (err) {
    console.error('Emergency Card load error:', err);
  }
}

async function loadHospitalConnections(patientId) {
  const container = document.getElementById('hospital-connections-list');
  if (!container) return;
  patientId = patientId || getLoggedInPatientId();

  try {
    const res = await fetch(`/api/patient/connections?patient_id=${patientId}`);
    const data = await res.json();

    if (data.success && data.hospitals) {
      container.innerHTML = data.hospitals.map(h => `
        <div class="card" style="margin-bottom: 1rem; padding: 1.2rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h4 style="color: var(--primary-500);">${h.hospital_name}</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted);">${h.address}</p>
            <div style="display: flex; gap: 6px; margin-top: 6px;">
              ${(h.departments || []).map(d => `<span class="badge badge-info">${d}</span>`).join('')}
            </div>
          </div>
          <div>
            ${h.connected ? 
              `<button class="btn btn-secondary btn-sm" disabled><i class="fa-solid fa-link"></i> Authorized</button>` : 
              `<button class="btn btn-primary btn-sm" onclick="connectHospital('${h.hospital_id}')"><i class="fa-solid fa-user-plus"></i> Grant Access</button>`}
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Connections error:', err);
  }
}

async function connectHospital(hospital_id) {
  const patientId = getLoggedInPatientId();
  try {
    const res = await fetch(`/api/patient/connections?patient_id=${patientId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hospital_id })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Hospital authorization granted successfully!', 'success');
      loadHospitalConnections(patientId);
    }
  } catch (err) {
    showToast('Failed to connect hospital.', 'error');
  }
}
