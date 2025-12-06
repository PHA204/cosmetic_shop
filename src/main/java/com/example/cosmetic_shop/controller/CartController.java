package com.example.cosmetic_shop.controller;

import com.example.cosmetic_shop.dto.ApiResponse;
import com.example.cosmetic_shop.dto.CartItemRequest;
import com.example.cosmetic_shop.dto.CartResponse;
import com.example.cosmetic_shop.dto.UpdateQuantityRequest;
import com.example.cosmetic_shop.exception.UnauthorizedException;
import com.example.cosmetic_shop.service.CartService;
import com.example.cosmetic_shop.service.UserService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/cart")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CartController {
    
    private final CartService cartService;
    private final UserService userService;
    // Lấy userId từ Authentication
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new UnauthorizedException("Vui lòng đăng nhập!");
        }
        String username = authentication.getName();
        return userService.getUserIdByUsername(username);
    }
    
    // GET /api/cart - Lấy giỏ hàng
    @GetMapping
    public ResponseEntity<ApiResponse> getCart() {
        try {
            Long userId = getCurrentUserId();
            CartResponse cart = cartService.getCartResponse(userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy giỏ hàng thành công!", cart));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // POST /api/cart/items - Thêm sản phẩm vào giỏ
    @PostMapping("/items")
    public ResponseEntity<ApiResponse> addItemToCart(@RequestBody CartItemRequest request) {
        try {
            Long userId = getCurrentUserId();
            cartService.addItemToCart(userId, request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Thêm vào giỏ hàng thành công!"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // PUT /api/cart/items/{itemId} - Cập nhật số lượng
    @PutMapping("/items/{itemId}")
    public ResponseEntity<ApiResponse> updateCartItem(
            @PathVariable Long itemId,
            @RequestBody UpdateQuantityRequest request) {
        try {
            Long userId = getCurrentUserId();
            cartService.updateCartItem(userId, itemId, request.getQuantity());
            return ResponseEntity.ok(ApiResponse.success("Cập nhật giỏ hàng thành công!"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // DELETE /api/cart/items/{itemId}?confirm=true - Xóa khỏi giỏ
    @DeleteMapping("/items/{itemId}")
    public ResponseEntity<ApiResponse> removeCartItem(
            @PathVariable Long itemId,
            @RequestParam(required = false, defaultValue = "false") boolean confirm) {
        try {
            Long userId = getCurrentUserId();
            cartService.removeCartItem(userId, itemId, confirm);
            return ResponseEntity.ok(ApiResponse.success("Xóa sản phẩm khỏi giỏ hàng thành công!"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // DELETE /api/cart - Xóa toàn bộ giỏ hàng
    @DeleteMapping
    public ResponseEntity<ApiResponse> clearCart() {
        try {
            Long userId = getCurrentUserId();
            cartService.clearCart(userId);
            return ResponseEntity.ok(ApiResponse.success("Xóa giỏ hàng thành công!"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/cart/count - Đếm số items trong giỏ
    @GetMapping("/count")
    public ResponseEntity<ApiResponse> getCartItemCount() {
        try {
            Long userId = getCurrentUserId();
            long count = cartService.getCartItemCount(userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy số lượng items thành công!", count));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/cart/total - Tính tổng tiền giỏ hàng
    @GetMapping("/total")
    public ResponseEntity<ApiResponse> getCartTotal() {
        try {
            Long userId = getCurrentUserId();
            double total = cartService.getCartTotal(userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy tổng tiền thành công!", total));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
}