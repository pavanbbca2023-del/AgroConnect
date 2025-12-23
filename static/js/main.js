// AgroConnect - SAFE JavaScript (Django Friendly)

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initFormValidation();
    initPhoneFormatting();
    initPriceCalculator();
    initFormEnhancements();
    initWasteProductFilters();
});

// ================= INITIALIZATION =================

function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Add CSRF token validation warning
        const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (!csrfToken && (form.method === 'POST' || form.method === 'post')) {
            console.warn('CSRF token missing for form submission');
        }

        form.addEventListener('submit', function (e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });

    // Live validation
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearError(input));
    });
}

function initWasteProductFilters() {
    // Auto-submit filter form when crop type changes
    const cropTypeSelect = document.querySelector('select[name="crop_type"]');
    if (cropTypeSelect) {
        cropTypeSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }

    // Card animation
    const productCards = document.querySelectorAll('.card');
    productCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ================= VALIDATION =================

function validateForm(form) {
    let valid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            valid = false;
        }
    });

    return valid;
}

function validateField(field) {
    if (!field) return false;

    const value = field.value.trim();
    const name = field.name;

    clearError(field);

    if (field.hasAttribute('required') && value === '') {
        showError(field, 'This field is required');
        return false;
    }

    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showError(field, 'Enter valid email');
            return false;
        }
    }

    if (name === 'phone' && value) {
        const phoneRegex = /^[6-9]\d{9}$/;
        if (!phoneRegex.test(value)) {
            showError(field, 'Enter valid 10 digit phone number');
            return false;
        }
    }

    if (name === 'password1' && value.length < 8) {
        showError(field, 'Password must be at least 8 characters');
        return false;
    }

    if (name === 'password2') {
        const p1 = field.form ? field.form.querySelector('input[name="password1"]') : null;
        if (p1 && value !== p1.value) {
            showError(field, 'Passwords do not match');
            return false;
        }
    }

    if (name === 'farm_size' && value) {
        const num = parseFloat(value);
        if (isNaN(num) || num <= 0) {
            showError(field, 'Enter valid farm size');
            return false;
        }
    }

    return true;
}

// ================= ERRORS =================

function showError(field, message) {
    if (!field || !field.parentElement) return;

    field.classList.add('is-invalid');

    let errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentElement.appendChild(errorDiv);
    }

    errorDiv.textContent = sanitizeText(message);
}

function clearError(field) {
    if (!field || !field.parentElement) return;

    field.classList.remove('is-invalid');
    const errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) errorDiv.remove();
}

// ================= PHONE =================

function initPhoneFormatting() {
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 10) value = value.substring(0, 10);
            this.value = value;
        });
    });
}

// ================= PRICE CALCULATOR =================

function getPricePerTon() {
    const paragraphs = document.querySelectorAll('p');
    for (let p of paragraphs) {
        if (p && p.textContent.includes("Price per ton:")) {
            const match = p.textContent.match(/₹(\d+(?:\.\d+)?)/);
            return match ? parseFloat(match[1]) : 0;
        }
    }
    return 0;
}

function initPriceCalculator() {
    const quantityInput = document.querySelector('input[name="quantity_ordered"]');
    const priceElement = document.querySelector('#totalPrice');
    const orderQuantityElement = document.getElementById('orderQuantity');

    if (quantityInput && priceElement) {
        const pricePerTon = getPricePerTon();

        quantityInput.addEventListener('input', function () {
            const quantity = parseFloat(this.value) || 0;
            const total = quantity * pricePerTon;

            if (orderQuantityElement) {
                orderQuantityElement.textContent = sanitizeText(quantity.toString());
            }
            priceElement.textContent = sanitizeText(total.toFixed(2));
        });
    }
}

// ================= FORM ENHANCEMENTS =================

function initFormEnhancements() {
    // Submit button loading
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.dataset.originalText = button.textContent || 'Submit';
        button.addEventListener('click', function () {
            const form = this.closest('form');
            if (form && validateForm(form)) {
                this.disabled = true;
                this.textContent = 'Processing...';
                setTimeout(() => {
                    this.disabled = false;
                    this.textContent = this.dataset.originalText || 'Submit';
                }, 5000);
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Character counter
    const descriptionFields = document.querySelectorAll('textarea[name="description"], textarea[name="notes"]');
    descriptionFields.forEach(field => {
        if (!field.parentNode) return;
        const maxLength = parseInt(field.getAttribute('maxlength')) || 500;
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';

        const countSpan = document.createElement('span');
        countSpan.className = 'char-count';
        countSpan.textContent = '0';

        counter.appendChild(countSpan);
        counter.appendChild(document.createTextNode(`/${maxLength} characters`));
        field.parentNode.appendChild(counter);

        field.addEventListener('input', function () {
            const count = this.value.length;
            countSpan.textContent = count.toString();
            countSpan.style.color = count > maxLength * 0.9 ? '#dc3545' : '#6c757d';
        });
    });
}

// ================= UTILITY FUNCTIONS =================

function sanitizeText(text) {
    if (typeof text !== 'string') text = String(text);
    return text.replace(/[<>"'&]/g, function (match) {
        const escapeMap = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        };
        return escapeMap[match];
    });
}

function showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';

    const messageText = document.createTextNode(sanitizeText(message));
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close';
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');

    alert.appendChild(messageText);
    alert.appendChild(closeButton);

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alert, container.firstChild);

    setTimeout(() => {
        if (alert.parentNode) alert.remove();
    }, 5000);
}

function confirmAction(message, callback) {
    // Simple fallback modal using Bootstrap if available
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header"><h5 class="modal-title">Confirm Action</h5></div>
                <div class="modal-body"><p class="confirm-message"></p></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary confirm-btn">Confirm</button>
                </div>
            </div>
        </div>
    `;
    const messageElement = modal.querySelector('.confirm-message');
    messageElement.textContent = sanitizeText(message);

    const confirmBtn = modal.querySelector('.confirm-btn');
    confirmBtn.addEventListener('click', () => {
        callback();
        modal.remove();
    });

    document.body.appendChild(modal);

    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        modal.addEventListener('hidden.bs.modal', () => modal.remove());
    } else {
        if (window.confirm(sanitizeText(message))) callback();
        modal.remove();
    }
}

// ================= EXPORT =================

window.AgroConnect = {
    validateForm,
    validateField,
    showSuccessMessage,
    confirmAction,
    sanitizeText
};
// ================= END OF FILE =================