// MindMarket JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Price input formatting
    const priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Search form enhancement
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchForm.submit();
                }
            });
        }
    }

    // Bid amount suggestions
    const bidAmountInput = document.querySelector('input[name="amount"]');
    if (bidAmountInput) {
        const minAmount = parseFloat(bidAmountInput.getAttribute('min'));
        
        // Add suggested bid buttons
        const suggestedAmounts = [
            minAmount + 5,
            minAmount + 10,
            minAmount + 25,
            minAmount + 50
        ];

        const container = bidAmountInput.parentElement.parentElement;
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'mt-2';
        suggestionsDiv.innerHTML = '<small class="text-muted">Quick bid amounts:</small><br>';

        suggestedAmounts.forEach(function(amount) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-outline-secondary btn-sm me-2 mt-1';
            button.textContent = '$' + amount.toFixed(2);
            button.addEventListener('click', function() {
                bidAmountInput.value = amount.toFixed(2);
            });
            suggestionsDiv.appendChild(button);
        });

        container.appendChild(suggestionsDiv);
    }

    // Confirmation dialogs for critical actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Loading states for forms
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.classList.add('loading');
            button.disabled = true;
            
            // Re-enable after 5 seconds as failsafe
            setTimeout(function() {
                button.classList.remove('loading');
                button.disabled = false;
            }, 5000);
        });
    });

    // Character counter for text areas
    const textAreas = document.querySelectorAll('textarea[maxlength]');
    textAreas.forEach(function(textarea) {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        const counter = document.createElement('small');
        counter.className = 'text-muted float-end';
        textarea.parentElement.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = remaining + ' characters remaining';
            
            if (remaining < 50) {
                counter.className = 'text-warning float-end';
            } else if (remaining < 20) {
                counter.className = 'text-danger float-end';
            } else {
                counter.className = 'text-muted float-end';
            }
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-refresh for dashboard
    if (window.location.pathname.includes('dashboard')) {
        // Refresh page every 5 minutes to show new bids/updates
        setTimeout(function() {
            window.location.reload();
        }, 300000); // 5 minutes
    }

    // Filter form auto-submit
    const filterSelects = document.querySelectorAll('#category, #sort');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Mobile menu improvements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const icon = this.querySelector('.navbar-toggler-icon');
            icon.style.transform = icon.style.transform === 'rotate(180deg)' ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    }

    // Copy idea URL functionality
    const shareButtons = document.querySelectorAll('.share-idea');
    shareButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            navigator.clipboard.writeText(window.location.href).then(function() {
                // Show success message
                const toast = document.createElement('div');
                toast.className = 'toast-container position-fixed top-0 end-0 p-3';
                toast.innerHTML = `
                    <div class="toast show" role="alert">
                        <div class="toast-body">
                            Link copied to clipboard!
                        </div>
                    </div>
                `;
                document.body.appendChild(toast);
                
                setTimeout(function() {
                    toast.remove();
                }, 3000);
            });
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    cards.forEach(function(card) {
        observer.observe(card);
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Export functions for use in other scripts
window.MindMarket = {
    formatCurrency: formatCurrency,
    formatDate: formatDate
};
