document.addEventListener('DOMContentLoaded', () => {
  // 🌗 Theme Switching
  const toggleInput = document.getElementById('mode');
  const applyTheme = (isLight) => {
    document.documentElement.classList.toggle('light', isLight);
    document.documentElement.classList.toggle('dark', !isLight);
    localStorage.setItem('mode', isLight ? 'light' : 'dark');
  };
  
  // on toggle
  toggleInput.addEventListener('change', () => {
    applyTheme(toggleInput.checked);
  });
  
  // on load
  const storedMode = localStorage.getItem('mode') === 'light';
  toggleInput.checked = storedMode;
  applyTheme(storedMode);

  // 🛡️ Form Validation
  const form          = document.querySelector('form');
  const userIdInput   = document.getElementById('user_id');
  const passwordInput = document.getElementById('password');
  const roleSelect    = document.getElementById('role');

  form.addEventListener('submit', (e) => {
    let isValid = true;
    // clear old errors
    document.querySelectorAll('.error-message').forEach(el => el.remove());

    // 1) Password strength
    const pwRe = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
    if (!pwRe.test(passwordInput.value)) {
      showError(passwordInput,
        'Password must be 8+ chars, include uppercase, lowercase, digit & special char.'
      );
      isValid = false;
    }

    // 2) Role‐based ID rules
    const idRules = {
      faculty: {
        pattern: /^\d{4}0000$/,
        message: "Faculty ID must be 8 digits and end in '0000'."
      },
      student: {
        pattern: /^\d{4}(202[2-8])$/,
        message: "Student ID must be 8 digits and end with a year between 2022–2028."
      }
    };

    const role = roleSelect.value;
    const rule = idRules[role];
    if (!rule) {
      showError(userIdInput, 'Please select Student or Faculty.');
      isValid = false;
    } else if (!rule.pattern.test(userIdInput.value)) {
      showError(userIdInput, rule.message);
      isValid = false;
    }

    if (!isValid) e.preventDefault();
  });
});

// 🔔 Inline error helper
function showError(input, message) {
  const span = document.createElement('span');
  span.className      = 'error-message';
  span.style.color    = 'red';
  span.style.fontSize = '0.9em';
  span.textContent    = message;
  input.insertAdjacentElement('afterend', span);
}