// Employee Leave Management System - Client Interactivity

document.addEventListener('DOMContentLoaded', () => {
    // 1. Password Visibility Toggle
    const togglePasswordBtn = document.getElementById('togglePasswordBtn');
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            // Switch eye icon
            if (isPassword) {
                eyeIcon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                `;
            } else {
                eyeIcon.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                `;
            }
        });
    }

    // 2. Client-side Form Validation for Leave Application
    const applyForm = document.getElementById('applyLeaveForm');
    if (applyForm) {
        applyForm.addEventListener('submit', (e) => {
            const daysInput = document.getElementById('days');
            const leaveTypeSelect = document.getElementById('leave_type');
            
            if (daysInput) {
                const days = parseInt(daysInput.value, 10);
                const maxDays = parseInt(daysInput.getAttribute('max'), 10);
                
                if (isNaN(days) || days < 1) {
                    e.preventDefault();
                    alert('Please enter at least 1 day of leave.');
                    daysInput.focus();
                    return false;
                }
                
                if (!isNaN(maxDays) && days > maxDays) {
                    e.preventDefault();
                    alert(`Requested days (${days}) exceeds your available balance (${maxDays} days).`);
                    daysInput.focus();
                    return false;
                }
            }

            if (leaveTypeSelect && !leaveTypeSelect.value) {
                e.preventDefault();
                alert('Please select a leave category.');
                leaveTypeSelect.focus();
                return false;
            }
        });
    }

    // 3. Auto-dismiss flash notifications after 5 seconds
    const flashAlerts = document.querySelectorAll('.flash');
    if (flashAlerts.length > 0) {
        setTimeout(() => {
            flashAlerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 6000);
    }
});
