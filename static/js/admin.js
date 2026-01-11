// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Message Auto-dismiss
    const messages = document.querySelectorAll('.admin-message');
    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);

        const closeBtn = message.querySelector('.message-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                message.remove();
            });
        }
    });

    // Auto-generate slug from name
    const nameInput = document.querySelector('#id_name');
    const slugInput = document.querySelector('#id_slug');

    if (nameInput && slugInput && !slugInput.value) {
        nameInput.addEventListener('input', function () {
            const slug = this.value
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/(^-|-$)/g, '');
            slugInput.value = slug;
        });
    }

    // Confirm Delete Actions
    document.querySelectorAll('[data-confirm]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // Table Row Hover Effect
    document.querySelectorAll('.admin-table tbody tr').forEach(function (row) {
        row.style.transition = 'background 0.2s ease';
    });

    // Sidebar Active State Highlight
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // File Input Preview
    document.querySelectorAll('input[type="file"]').forEach(function (input) {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const preview = document.createElement('img');
                preview.style.maxWidth = '150px';
                preview.style.marginTop = '10px';
                preview.style.borderRadius = '8px';

                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);

                const existingPreview = input.parentElement.querySelector('.file-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }

                preview.classList.add('file-preview');
                input.parentElement.appendChild(preview);
            }
        });
    });

    // Select All Checkbox
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(function (checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }

    // Search Form Auto-submit
    const searchInput = document.querySelector('.search-form input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                searchInput.form.submit();
            }, 800);
        });
    }
});
