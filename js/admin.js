/* ==========================================================================
   MEDIBRIDGE AI - ADMIN PORTAL SCRIPT
   ========================================================================== */

let allAdminDoctors = [];

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('/admin/dashboard.html')) {
    loadAdminDashboard();
  } else if (window.location.pathname.includes('/admin/hospitals.html')) {
    loadAdminHospitalsPage();
  } else if (window.location.pathname.includes('/admin/users.html')) {
    loadAdminUsersPage();
  }
});

async function loadAdminDashboard() {
  try {
    const res = await fetch('/api/admin/dashboard');
    const data = await res.json();

    if (!data.success) return;

    if (document.getElementById('stat-admin-hospitals')) {
      document.getElementById('stat-admin-hospitals').textContent = data.stats.total_hospitals;
    }
    if (document.getElementById('stat-admin-approved')) {
      document.getElementById('stat-admin-approved').textContent = data.stats.approved_hospitals;
    }
    if (document.getElementById('stat-admin-pending')) {
      document.getElementById('stat-admin-pending').textContent = data.stats.pending_hospitals;
    }
    if (document.getElementById('stat-admin-patients')) {
      document.getElementById('stat-admin-patients').textContent = data.stats.total_patients;
    }

  } catch (err) {
    console.error('Admin dashboard error:', err);
  }
}

async function loadAdminHospitalsPage() {
  const tbody = document.getElementById('admin-hospitals-tbody');
  const docTbody = document.getElementById('admin-doctors-tbody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/admin/hospitals');
    const data = await res.json();

    if (data.success && data.hospitals) {
      // Populate Hospital Select in Add Doctor Modal & Filter Select
      const hospSelect = document.getElementById('admin_doc_hosp_id');
      const hospFilter = document.getElementById('admin-hosp-filter');

      if (hospSelect) {
        hospSelect.innerHTML = data.hospitals.map(h => `<option value="${h.hospital_id}">${h.hospital_name} (${h.hospital_id})</option>`).join('');
      }

      if (hospFilter) {
        let filterHtml = `<option value="all">-- All Hospitals (Show All Doctors) --</option>`;
        filterHtml += data.hospitals.map(h => `<option value="${h.hospital_id}">${h.hospital_name} (${h.hospital_id})</option>`).join('');
        hospFilter.innerHTML = filterHtml;
      }

      if (data.hospitals.length > 0) {
        tbody.innerHTML = data.hospitals.map(h => `
          <tr>
            <td><strong style="color: var(--primary-500);">${h.hospital_id}</strong></td>
            <td><strong>${h.hospital_name}</strong></td>
            <td>${h.registration_number || 'N/A'}</td>
            <td>${h.address || 'N/A'}</td>
            <td><span class="badge badge-info">${(h.doctor_info || []).length} Doctors</span></td>
            <td>
              <span class="badge ${h.verification_status === 'Approved' ? 'badge-success' : (h.verification_status === 'Pending' ? 'badge-warning' : 'badge-danger')}">
                ${h.verification_status}
              </span>
            </td>
            <td style="white-space: nowrap;">
              <div style="display: inline-flex; align-items: center; gap: 8px;">
                ${h.verification_status !== 'Approved' ? 
                  `<button onclick="updateHospStatus('${h.hospital_id}', 'Approved')" class="btn btn-primary btn-sm"><i class="fa-solid fa-check"></i> Approve</button>` : 
                  `<button onclick="updateHospStatus('${h.hospital_id}', 'Pending')" class="btn btn-outline btn-sm">Revoke</button>`
                }
                <button onclick="deleteHospitalRecord('${h.hospital_id}')" class="btn btn-outline btn-sm" style="color: #ef4444; border-color: #ef4444;"><i class="fa-solid fa-trash"></i> Delete</button>
              </div>
            </td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              No hospitals registered yet. Click <strong>"Add Hospital with ID"</strong> to register a hospital.
            </td>
          </tr>
        `;
      }
    }

    // Load Doctors Table
    if (docTbody) {
      const docRes = await fetch('/api/admin/doctors');
      const docData = await docRes.json();
      if (docData.success && docData.doctors) {
        allAdminDoctors = docData.doctors;
        filterDoctorsByHospital();
      }
    }
  } catch (err) {
    console.error('Error loading hospitals:', err);
  }
}

function filterDoctorsByHospital() {
  const docTbody = document.getElementById('admin-doctors-tbody');
  const filterSelect = document.getElementById('admin-hosp-filter');
  if (!docTbody) return;

  const selectedHospId = filterSelect ? filterSelect.value : 'all';

  let filteredDocs = allAdminDoctors;
  if (selectedHospId && selectedHospId !== 'all') {
    filteredDocs = allAdminDoctors.filter(d => d.hospital_id === selectedHospId);
  }

  if (filteredDocs && filteredDocs.length > 0) {
    docTbody.innerHTML = filteredDocs.map(d => `
      <tr>
        <td><strong>${d.doctor_id}</strong></td>
        <td><strong>${d.name}</strong></td>
        <td><span class="badge badge-info">${d.specialty}</span></td>
        <td>${d.qualification || 'MD'}</td>
        <td><strong style="color: var(--primary-500);">${d.hospital_id}</strong></td>
        <td>${d.hospital_name}</td>
        <td style="white-space: nowrap;">
          <button onclick="deleteDoctorRecord('${d.hospital_id}', '${d.doctor_id}')" class="btn btn-outline btn-sm" style="color: #ef4444; border-color: #ef4444;">
            <i class="fa-solid fa-user-minus"></i> Remove
          </button>
        </td>
      </tr>
    `).join('');
  } else {
    docTbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
          No doctors registered under ${selectedHospId === 'all' ? 'any hospital' : 'selected hospital (' + selectedHospId + ')'}.
        </td>
      </tr>
    `;
  }
}

// Add Hospital Modal Handlers
function openAddHospitalAdminModal() {
  const modal = document.getElementById('admin-hosp-modal');
  if (modal) modal.classList.add('active');
}

function closeAddHospitalAdminModal() {
  const modal = document.getElementById('admin-hosp-modal');
  if (modal) modal.classList.remove('active');
}

async function submitAdminNewHospital(e) {
  e.preventDefault();
  const hospital_id = document.getElementById('admin_hosp_id').value;
  const hospital_name = document.getElementById('admin_hosp_name').value;
  const registration_number = document.getElementById('admin_hosp_reg').value;
  const address = document.getElementById('admin_hosp_address').value;

  try {
    const res = await fetch('/api/admin/hospitals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hospital_id, hospital_name, registration_number, address })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message, 'success');
      closeAddHospitalAdminModal();
      document.getElementById('admin-add-hosp-form').reset();
      loadAdminHospitalsPage();
    } else {
      showToast(data.message || 'Failed to add hospital.', 'error');
    }
  } catch (err) {
    showToast('Failed to add hospital.', 'error');
  }
}

// Add Doctor Modal Handlers
function openAdminAddDoctorModal() {
  const modal = document.getElementById('admin-doc-modal');
  if (modal) modal.classList.add('active');
}

function closeAdminAddDoctorModal() {
  const modal = document.getElementById('admin-doc-modal');
  if (modal) modal.classList.remove('active');
}

async function submitAdminNewDoctor(e) {
  e.preventDefault();
  const hospital_id = document.getElementById('admin_doc_hosp_id').value;
  const doctor_id = document.getElementById('admin_doc_id').value;
  const name = document.getElementById('admin_doc_name').value;
  const specialty = document.getElementById('admin_doc_specialty').value;
  const qualification = document.getElementById('admin_doc_qual').value;

  try {
    const res = await fetch('/api/admin/doctors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hospital_id, doctor_id, name, specialty, qualification })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message, 'success');
      closeAdminAddDoctorModal();
      document.getElementById('admin-add-doc-form').reset();
      loadAdminHospitalsPage();
    } else {
      showToast(data.message || 'Failed to add doctor.', 'error');
    }
  } catch (err) {
    showToast('Failed to add doctor.', 'error');
  }
}

async function updateHospStatus(hospital_id, status) {
  try {
    const res = await fetch(`/api/admin/hospitals/${hospital_id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message, 'success');
      loadAdminHospitalsPage();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast('Status update failed.', 'error');
  }
}

async function deleteHospitalRecord(hospital_id) {
  if (!confirm(`Are you sure you want to delete hospital '${hospital_id}'?`)) return;

  try {
    const res = await fetch(`/api/admin/hospitals/${hospital_id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      loadAdminHospitalsPage();
    }
  } catch (err) {
    showToast('Failed to delete hospital.', 'error');
  }
}

async function deleteDoctorRecord(hospital_id, doctor_id) {
  if (!confirm(`Are you sure you want to remove doctor '${doctor_id}'?`)) return;

  try {
    const res = await fetch(`/api/admin/doctors?hospital_id=${hospital_id}&doctor_id=${doctor_id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      loadAdminHospitalsPage();
    }
  } catch (err) {
    showToast('Failed to remove doctor.', 'error');
  }
}

async function loadAdminUsersPage() {
  const tbody = document.getElementById('admin-users-tbody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/admin/users');
    const data = await res.json();

    if (data.success && data.users) {
      if (data.users.length > 0) {
        tbody.innerHTML = data.users.map(u => `
          <tr>
            <td><strong>${u.user_id}</strong></td>
            <td><strong>${u.name}</strong></td>
            <td>${u.email}</td>
            <td><span class="badge ${u.role === 'admin' ? 'badge-danger' : (u.role === 'hospital' ? 'badge-info' : 'badge-success')}">${u.role.toUpperCase()}</span></td>
            <td>${u.phone || 'N/A'}</td>
            <td style="white-space: nowrap;">
              ${u.role !== 'admin' ? 
                `<button onclick="deleteUserAccount('${u.user_id}')" class="btn btn-outline btn-sm" style="color: #ef4444; border-color: #ef4444;"><i class="fa-solid fa-trash"></i> Remove Account</button>` : 
                `<span class="badge badge-info">Superuser</span>`
              }
            </td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
              No registered users found.
            </td>
          </tr>
        `;
      }
    }
  } catch (err) {
    console.error('Users load error:', err);
  }
}

async function deleteUserAccount(user_id) {
  if (!confirm(`Are you sure you want to remove user account ${user_id}?`)) return;

  try {
    const res = await fetch(`/api/admin/users?user_id=${user_id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      loadAdminUsersPage();
    }
  } catch (err) {
    showToast('Failed to delete user.', 'error');
  }
}
