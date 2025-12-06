package com.example.cosmetic_shop.service;

import com.example.cosmetic_shop.dto.CartItemRequest;
import com.example.cosmetic_shop.dto.CartItemResponse;
import com.example.cosmetic_shop.dto.CartResponse;
import com.example.cosmetic_shop.entity.Cart;
import com.example.cosmetic_shop.entity.CartItem;
import com.example.cosmetic_shop.entity.Product;
import com.example.cosmetic_shop.entity.User;
import com.example.cosmetic_shop.repository.CartItemRepository;
import com.example.cosmetic_shop.repository.CartRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CartService {
    
    private final CartRepository cartRepository;
    private final CartItemRepository cartItemRepository;
    private final ProductService productService;
    private final UserService userService;
    
    // Lấy hoặc tạo giỏ hàng cho user
    @Transactional
    public Cart getCartByUserId(Long userId) {
        return cartRepository.findByUserId(userId)
                .orElseGet(() -> {
                    User user = userService.getUserById(userId);
                    Cart cart = new Cart();
                    cart.setUser(user);
                    return cartRepository.save(cart);
                });
    }
    
    // Lấy giỏ hàng với response đầy đủ
    public CartResponse getCartResponse(Long userId) {
        Cart cart = getCartByUserId(userId);
        List<CartItem> items = cartItemRepository.findByCartId(cart.getId());
        
        List<CartItemResponse> itemResponses = items.stream()
                .map(this::convertToCartItemResponse)
                .collect(Collectors.toList());
        
        double totalAmount = items.stream()
                .mapToDouble(item -> item.getProduct().getPrice() * item.getQuantity())
                .sum();
        
        CartResponse response = new CartResponse();
        response.setCartId(cart.getId());
        response.setItems(itemResponses);
        response.setTotalItems(items.size());
        response.setTotalAmount(totalAmount);
        
        return response;
    }
    
    // Thêm sản phẩm vào giỏ
    @Transactional
    public void addItemToCart(Long userId, CartItemRequest request) {
        Cart cart = getCartByUserId(userId);
        Product product = productService.getProductById(request.getProductId());
        
        // Kiểm tra tồn kho
        if (!productService.checkStock(product.getId(), request.getQuantity())) {
            throw new RuntimeException("Không đủ hàng trong kho!");
        }
        
        // Kiểm tra sản phẩm đã có trong giỏ chưa
        CartItem existingItem = cartItemRepository
                .findByCartIdAndProductId(cart.getId(), product.getId())
                .orElse(null);
        
        if (existingItem != null) {
            // Cập nhật số lượng
            int newQuantity = existingItem.getQuantity() + request.getQuantity();
            if (!productService.checkStock(product.getId(), newQuantity)) {
                throw new RuntimeException("Không đủ hàng trong kho!");
            }
            existingItem.setQuantity(newQuantity);
            cartItemRepository.save(existingItem);
        } else {
            // Thêm mới
            CartItem cartItem = new CartItem();
            cartItem.setCart(cart);
            cartItem.setProduct(product);
            cartItem.setQuantity(request.getQuantity());
            cartItemRepository.save(cartItem);
        }
    }
    
    // Cập nhật số lượng sản phẩm trong giỏ
    @Transactional
    public void updateCartItem(Long userId, Long itemId, int quantity) {
        CartItem cartItem = cartItemRepository.findById(itemId)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy sản phẩm trong giỏ hàng!"));
        
        // Kiểm tra cart item có thuộc user không
        if (!cartItem.getCart().getUser().getId().equals(userId)) {
            throw new RuntimeException("Không có quyền thao tác!");
        }
        
        // Kiểm tra tồn kho
        if (!productService.checkStock(cartItem.getProduct().getId(), quantity)) {
            throw new RuntimeException("Không đủ hàng trong kho!");
        }
        
        cartItem.setQuantity(quantity);
        cartItemRepository.save(cartItem);
    }
    
    // Xóa sản phẩm khỏi giỏ - Có xác nhận
    @Transactional
    public void removeCartItem(Long userId, Long itemId, boolean confirm) {
        if (!confirm) {
            throw new RuntimeException("Vui lòng xác nhận xóa sản phẩm bằng cách thêm ?confirm=true");
        }
        
        CartItem cartItem = cartItemRepository.findById(itemId)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy sản phẩm trong giỏ hàng!"));
        
        // Kiểm tra cart item có thuộc user không
        if (!cartItem.getCart().getUser().getId().equals(userId)) {
            throw new RuntimeException("Không có quyền thao tác!");
        }
        
        cartItemRepository.delete(cartItem);
    }
    
    // Xóa toàn bộ giỏ hàng
    @Transactional
    public void clearCart(Long userId) {
        Cart cart = getCartByUserId(userId);
        cartItemRepository.deleteByCartId(cart.getId());
    }
    
    // Tính tổng tiền giỏ hàng
    public double getCartTotal(Long userId) {
        Cart cart = getCartByUserId(userId);
        return cartItemRepository.calculateCartTotal(cart.getId());
    }
    
    // Đếm số lượng items trong giỏ
    public long getCartItemCount(Long userId) {
        Cart cart = getCartByUserId(userId);
        return cartItemRepository.countByCartId(cart.getId());
    }
    
    // Convert CartItem to Response
    private CartItemResponse convertToCartItemResponse(CartItem item) {
        CartItemResponse response = new CartItemResponse();
        response.setId(item.getId());
        response.setProductId(item.getProduct().getId());
        response.setProductName(item.getProduct().getName());
        response.setProductImage(item.getProduct().getImage());
        response.setProductPrice(item.getProduct().getPrice());
        response.setQuantity(item.getQuantity());
        response.setSubTotal(item.getSubTotal());
        return response;
    }
}