// Bake with Love - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    // Search Modal
    const searchBtn = document.getElementById('searchBtn');
    const searchModal = document.getElementById('searchModal');
    const searchClose = document.getElementById('searchClose');

    if (searchBtn && searchModal) {
        searchBtn.addEventListener('click', function() {
            searchModal.classList.add('active');
            searchModal.querySelector('input').focus();
        });

        if (searchClose) {
            searchClose.addEventListener('click', function() {
                searchModal.classList.remove('active');
            });
        }

        searchModal.addEventListener('click', function(e) {
            if (e.target === searchModal) {
                searchModal.classList.remove('active');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                searchModal.classList.remove('active');
            }
        });
    }

    // Message Auto-dismiss
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);

        const closeBtn = message.querySelector('.message-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.remove();
            });
        }
    });

    // Add to Cart Animation
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const btn = form.querySelector('button');
            btn.textContent = 'Added!';
            btn.style.background = '#2D8A4E';
            setTimeout(function() {
                btn.textContent = 'Add to Cart';
                btn.style.background = '';
            }, 2000);
        });
    });

    // Quantity Selectors
    document.querySelectorAll('.quantity-form').forEach(function(form) {
        const minusBtn = form.querySelector('.qty-btn.minus, [data-action="decrease"]');
        const plusBtn = form.querySelector('.qty-btn.plus, [data-action="increase"]');
        const input = form.querySelector('.qty-input');

        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', function() {
                const current = parseInt(input.value) || 1;
                if (current > 1) {
                    input.value = current - 1;
                    form.submit();
                }
            });

            plusBtn.addEventListener('click', function() {
                const current = parseInt(input.value) || 1;
                input.value = current + 1;
                form.submit();
            });
        }
    });

    // Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Lazy Loading Images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Category Carousel Scroll
    const carousel = document.querySelector('.categories-carousel');
    if (carousel) {
        let isDown = false;
        let startX;
        let scrollLeft;

        carousel.addEventListener('mousedown', function(e) {
            isDown = true;
            carousel.style.cursor = 'grabbing';
            startX = e.pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
        });

        carousel.addEventListener('mouseleave', function() {
            isDown = false;
            carousel.style.cursor = 'grab';
        });

        carousel.addEventListener('mouseup', function() {
            isDown = false;
            carousel.style.cursor = 'grab';
        });

        carousel.addEventListener('mousemove', function(e) {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });
    }

    // Form Validation Styling
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let valid = true;

            requiredInputs.forEach(function(input) {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = '#C0392B';
                } else {
                    input.style.borderColor = '';
                }
            });
        });
    });

    // Animation on Scroll
    if ('IntersectionObserver' in window) {
        const animateObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.product-card, .category-card, .value-card').forEach(function(el) {
            animateObserver.observe(el);
        });
    }
});

// Utility: Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
