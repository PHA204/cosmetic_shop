// ==========================================
// CUSTOM JAVASCRIPT - Cosmetic Shop
// File: src/main/resources/static/js/main.js
// ==========================================

$(document).ready(function() {
    
    // ========== Initialize Tooltips ==========
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ========== Auto-hide Alerts ==========
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // ========== Confirm Delete ==========
    $('.btn-delete').on('click', function(e) {
        if (!confirm('Bạn có chắc chắn muốn xóa?')) {
            e.preventDefault();
        }
    });
    
    // ========== Add to Cart Animation ==========
    $('.btn-add-cart').on('click', function() {
        var btn = $(this);
        var originalText = btn.html();
        
        btn.html('<i class="bi bi-check-circle"></i> Đã thêm!');
        btn.prop('disabled', true);
        
        setTimeout(function() {
            btn.html(originalText);
            btn.prop('disabled', false);
        }, 2000);
    });
    
    // ========== Quantity Counter ==========
    $('.quantity-minus').on('click', function() {
        var input = $(this).siblings('input');
        var value = parseInt(input.val());
        if (value > 1) {
            input.val(value - 1);
            updateCartItem(input);
        }
    });
    
    $('.quantity-plus').on('click', function() {
        var input = $(this).siblings('input');
        var value = parseInt(input.val());
        var max = parseInt(input.attr('max')) || 999;
        if (value < max) {
            input.val(value + 1);
            updateCartItem(input);
        }
    });
    
    // ========== Update Cart Item ==========
    function updateCartItem(input) {
        var itemId = input.data('item-id');
        var quantity = input.val();
        
        // TODO: Gửi AJAX request để update cart
        console.log('Update cart item:', itemId, 'quantity:', quantity);
    }
    
    // ========== Search Bar ==========
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            var keyword = $(this).val();
            if (keyword.trim()) {
                window.location.href = '/products?search=' + encodeURIComponent(keyword);
            }
        }
    });
    
    // ========== Image Preview ==========
    $('#imageInput').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('#imagePreview').attr('src', e.target.result).show();
            }
            reader.readAsDataURL(file);
        }
    });
    
    // ========== Loading Overlay ==========
    function showLoading() {
        $('body').append('<div class="spinner-overlay"><div class="spinner-border text-light" role="status"></div></div>');
    }
    
    function hideLoading() {
        $('.spinner-overlay').remove();
    }
    
    // ========== AJAX Form Submit ==========
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        
        showLoading();
        
        var form = $(this);
        var url = form.attr('action');
        var method = form.attr('method') || 'POST';
        var data = form.serialize();
        
        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(response) {
                hideLoading();
                showMessage('Thành công!', 'success');
                // Reload hoặc redirect
                setTimeout(function() {
                    location.reload();
                }, 1000);
            },
            error: function(xhr) {
                hideLoading();
                var message = xhr.responseJSON ? xhr.responseJSON.message : 'Có lỗi xảy ra!';
                showMessage(message, 'danger');
            }
        });
    });
    
    // ========== Show Message ==========
    function showMessage(message, type) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert" style="z-index: 9999;">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>';
        
        $('body').append(alertHtml);
        
        setTimeout(function() {
            $('.alert').fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    }
    
    // ========== Format Currency ==========
    function formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    }
    
    // ========== Update Cart Badge ==========
    function updateCartBadge() {
        // TODO: Gọi API để lấy số lượng items trong cart
        $.get('/api/cart/count', function(data) {
            $('.cart-badge').text(data);
        });
    }
    
    // ========== Smooth Scroll ==========
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });
    
    // ========== Back to Top Button ==========
    var backToTopButton = $('<button class="btn btn-primary btn-floating position-fixed bottom-0 end-0 m-3" style="display: none; z-index: 999;">' +
        '<i class="bi bi-arrow-up"></i>' +
        '</button>');
    
    $('body').append(backToTopButton);
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTopButton.fadeIn();
        } else {
            backToTopButton.fadeOut();
        }
    });
    
    backToTopButton.on('click', function() {
        $('html, body').animate({scrollTop: 0}, 600);
        return false;
    });
    
    // ========== Dark Mode Toggle (Optional) ==========
    $('#darkModeToggle').on('click', function() {
        $('body').toggleClass('dark-mode');
        localStorage.setItem('darkMode', $('body').hasClass('dark-mode'));
    });
    
    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        $('body').addClass('dark-mode');
    }
});

// ========== Global Functions ==========

// Add to Cart Function
function addToCart(productId, quantity) {
    $.ajax({
        url: '/api/cart/items',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            productId: productId,
            quantity: quantity || 1
        }),
        success: function(response) {
            showMessage('Đã thêm vào giỏ hàng!', 'success');
            updateCartBadge();
        },
        error: function(xhr) {
            var message = xhr.responseJSON ? xhr.responseJSON.message : 'Có lỗi xảy ra!';
            showMessage(message, 'danger');
        }
    });
}

// Remove from Cart Function
function removeFromCart(itemId) {
    if (!confirm('Bạn có chắc muốn xóa sản phẩm này?')) {
        return;
    }
    
    $.ajax({
        url: '/api/cart/items/' + itemId + '?confirm=true',
        method: 'DELETE',
        success: function(response) {
            showMessage('Đã xóa khỏi giỏ hàng!', 'success');
            location.reload();
        },
        error: function(xhr) {
            var message = xhr.responseJSON ? xhr.responseJSON.message : 'Có lỗi xảy ra!';
            showMessage(message, 'danger');
        }
    });
}