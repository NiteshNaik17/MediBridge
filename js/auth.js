/* ==========================================================================
   MEDIBRIDGE AI - AUTHENTICATION & SESSION SCRIPT
   ========================================================================== */

const API_BASE = '/api';

// Toast Notification Helper
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation'}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// Global Auth state loader
document.addEventListener('DOMContentLoaded', () => {
  initAuthUI();
});

function initAuthUI() {
  // Login / Register Role Tab Switcher
  const tabs = document.querySelectorAll('.auth-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      tabs.forEach(t => t.classList.remove('active'));
      const targetBtn = e.target.closest('.auth-tab');
      if (targetBtn) targetBtn.classList.add('active');

      const role = targetBtn ? targetBtn.getAttribute('data-role') : 'patient';
      const roleInput = document.getElementById('auth-role');
      if (roleInput) roleInput.value = role;

      // Adjust register fields if on register page
      const hospFields = document.getElementById('hospital-register-fields');
      const patFields = document.getElementById('patient-register-fields');
      const docIdInput = document.getElementById('doctor_id_num');
      const hospIdInput = document.getElementById('hosp_id_input');

      if (hospFields && patFields) {
        if (role === 'hospital') {
          hospFields.style.display = 'block';
          patFields.style.display = 'none';
          if (docIdInput) docIdInput.setAttribute('required', 'true');
          if (hospIdInput) hospIdInput.setAttribute('required', 'true');
        } else {
          hospFields.style.display = 'none';
          patFields.style.display = 'block';
          if (docIdInput) docIdInput.removeAttribute('required');
          if (hospIdInput) hospIdInput.removeAttribute('required');
        }
      }
    });
  });

  // Login Form Submission
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const role = document.getElementById('auth-role')?.value || 'patient';

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, role })
        });
        const data = await res.json();

        if (data.success) {
          showToast(data.message, 'success');
          localStorage.setItem('medibridge_user', JSON.stringify(data.user));
          setTimeout(() => {
            if (data.user.role === 'hospital') {
              window.location.href = '/hospital/dashboard.html';
            } else if (data.user.role === 'admin') {
              window.location.href = '/admin/dashboard.html';
            } else {
              window.location.href = '/patient/dashboard.html';
            }
          }, 800);
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Connection error. Please ensure backend server is running.', 'error');
      }
    });
  }

  // Registration Form Submission
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const role = document.getElementById('auth-role')?.value || 'patient';
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password')?.value;
      const phone = document.getElementById('phone')?.value || '';

      if (confirmPassword && password !== confirmPassword) {
        showToast('Password and Confirm Password do not match!', 'error');
        return;
      }

      const payload = { name, email, password, role, phone };

      if (role === 'hospital') {
        payload.doctor_id_number = document.getElementById('doctor_id_num')?.value || '';
        payload.hospital_id = document.getElementById('hosp_id_input')?.value || '';
        payload.specialty = document.getElementById('doc_specialty')?.value || 'General Medicine';
        payload.qualification = document.getElementById('doc_qualification')?.value || 'MD';
        payload.hospital_name = document.getElementById('hosp_id_input')?.value || `${name}'s Medical Center`;
      } else {
        payload.age = document.getElementById('age')?.value || 30;
        payload.gender = document.getElementById('gender')?.value || 'Male';
        payload.blood_group = document.getElementById('blood_group')?.value || 'O+';
        const allergiesStr = document.getElementById('allergies')?.value || '';
        payload.allergies = allergiesStr ? allergiesStr.split(',').map(s => s.trim()) : [];
        
        payload.emergency_contact = {
          name: document.getElementById('emergency_name')?.value || 'N/A',
          relationship: document.getElementById('emergency_relation')?.value || 'Contact',
          phone: document.getElementById('emergency_phone')?.value || 'N/A'
        };
      }

      try {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
          showToast(data.message, 'success');
          if (data.user) {
            localStorage.setItem('medibridge_user', JSON.stringify(data.user));
          }
          setTimeout(() => {
            if (role === 'hospital') {
              window.location.href = '/hospital/dashboard.html';
            } else if (role === 'patient') {
              window.location.href = '/patient/dashboard.html';
            } else {
              window.location.href = '/login.html';
            }
          }, 1000);
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Registration failed. Check system logs.', 'error');
      }
    });
  }
}

// Logout helper
async function logoutUser() {
  try {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
  } catch (e) {}
  localStorage.removeItem('medibridge_user');
  window.location.href = '/login.html';
}
