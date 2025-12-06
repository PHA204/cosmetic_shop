// Global function to add product to cart
function addToCart(productId, quantity) {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        showMessage('Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng!', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return;
    }
    
    const cartData = {
        productId: productId,
        quantity: quantity || 1
    };
    
    $.ajax({
        url: '/api/cart/items',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(cartData),
        success: function(response) {
            showMessage('Đã thêm vào giỏ hàng!', 'success');
            
            // Update cart count in navbar
            if (typeof updateCartCount === 'function') {
                updateCartCount();
            }
            
            // Show cart notification with animation
            showCartNotification();
        },
        error: function(xhr) {
            let message = 'Có lỗi xảy ra!';
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                message = xhr.responseJSON.message;
            } else if (xhr.status === 401) {
                message = 'Vui lòng đăng nhập!';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            }
            
            showMessage(message, 'danger');
        }
    });
}

// Check if user is authenticated (simple check for navbar)
function isUserAuthenticated() {
    // Check if cart link exists (only shown to authenticated users)
    return $('#cartLink').length > 0;
}

// Show message alert
function showMessage(message, type) {
    // Remove existing alerts
    $('.alert-notification').remove();
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3 alert-notification" 
             role="alert" style="z-index: 9999; min-width: 300px;">
            <strong>
                ${type === 'success' ? '<i class="bi bi-check-circle"></i>' : 
                  type === 'danger' ? '<i class="bi bi-x-circle"></i>' : 
                  type === 'warning' ? '<i class="bi bi-exclamation-triangle"></i>' : 
                  '<i class="bi bi-info-circle"></i>'}
            </strong>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        $('.alert-notification').fadeOut(300, function() {
            $(this).remove();
        });
    }, 5000);
}

// Show cart notification with icon animation
function showCartNotification() {
    const cartIcon = $('#cartLink i');
    
    if (cartIcon.length > 0) {
        // Add bounce animation
        cartIcon.addClass('animate-bounce');
        
        setTimeout(() => {
            cartIcon.removeClass('animate-bounce');
        }, 1000);
    }
}

// Format currency to Vietnamese Dong
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount) + ' ₫';
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

// Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show scroll to top button
$(window).scroll(function() {
    if ($(this).scrollTop() > 300) {
        $('#scrollTopBtn').fadeIn();
    } else {
        $('#scrollTopBtn').fadeOut();
    }
});

// Add scroll to top button on page load
$(document).ready(function() {
    // Add scroll to top button
    if ($('#scrollTopBtn').length === 0) {
        $('body').append(`
            <button id="scrollTopBtn" 
                    class="btn btn-primary rounded-circle position-fixed" 
                    style="bottom: 20px; right: 20px; width: 50px; height: 50px; display: none; z-index: 1000;"
                    onclick="scrollToTop()">
                <i class="bi bi-arrow-up"></i>
            </button>
        `);
    }
    
    // Add loading indicator styles if not exists
    if ($('#loadingStyles').length === 0) {
        $('head').append(`
            <style id="loadingStyles">
                .animate-bounce {
                    animation: bounce 0.5s ease-in-out;
                }
                
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-10px); }
                }
                
                .product-card {
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                
                .product-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
                }
                
                .category-card {
                    transition: all 0.3s ease;
                }
                
                .category-card:hover {
                    transform: scale(1.05);
                    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
                }
                
                .btn-add-cart {
                    transition: all 0.3s ease;
                }
                
                .btn-add-cart:hover:not(:disabled) {
                    transform: scale(1.05);
                }
                
                .cart-item {
                    transition: opacity 0.3s ease;
                }
                
                .cart-item.removing {
                    opacity: 0.5;
                }
                
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                
                .loading-spinner {
                    width: 3rem;
                    height: 3rem;
                }
            </style>
        `);
    }
});

// Show loading overlay
function showLoading() {
    if ($('#loadingOverlay').length === 0) {
        $('body').append(`
            <div id="loadingOverlay" class="loading-overlay">
                <div class="spinner-border text-light loading-spinner" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
    }
}

// Hide loading overlay
function hideLoading() {
    $('#loadingOverlay').fadeOut(300, function() {
        $(this).remove();
    });
}

// Confirm dialog wrapper
function confirmDialog(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    const temp = $('<input>');
    $('body').append(temp);
    temp.val(text).select();
    document.execCommand('copy');
    temp.remove();
    
    showMessage('Đã copy vào clipboard!', 'success');
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone number (Vietnamese)
function isValidPhone(phone) {
    const re = /^(0|\+84)[0-9]{9,10}$/;
    return re.test(phone);
}

// Format number with thousand separator
function formatNumber(number) {
    return new Intl.NumberFormat('vi-VN').format(number);
}

// Truncate text
function truncateText(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Get query parameter from URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Update URL parameter without reload
function updateQueryParam(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

// Remove URL parameter without reload
function removeQueryParam(param) {
    const url = new URL(window.location);
    url.searchParams.delete(param);
    window.history.pushState({}, '', url);
}

// Initialize tooltips (Bootstrap 5)
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize popovers (Bootstrap 5)
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Handle image load error
function handleImageError(img) {
    img.onerror = null;
    img.src = 'https://via.placeholder.com/300x300?text=No+Image';
}

// Auto-hide alerts after delay
$(document).on('click', '.alert .btn-close', function() {
    $(this).closest('.alert').fadeOut(300, function() {
        $(this).remove();
    });
});

// Prevent double form submission
$('form').on('submit', function() {
    const submitBtn = $(this).find('button[type="submit"]');
    submitBtn.prop('disabled', true);
    
    setTimeout(() => {
        submitBtn.prop('disabled', false);
    }, 3000);
});

// Console log for debugging (remove in production)
console.log('Main.js loaded successfully!');
console.log('Cart functions initialized.');

// Export functions to window for global access
window.addToCart = addToCart;
window.showMessage = showMessage;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.escapeHtml = escapeHtml;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.confirmDialog = confirmDialog;
window.copyToClipboard = copyToClipboard;