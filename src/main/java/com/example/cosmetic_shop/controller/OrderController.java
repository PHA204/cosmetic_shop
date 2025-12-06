package com.example.cosmetic_shop.controller;

import com.example.cosmetic_shop.dto.ApiResponse;
import com.example.cosmetic_shop.dto.OrderRequest;
import com.example.cosmetic_shop.dto.OrderResponse;
import com.example.cosmetic_shop.entity.Order;
import com.example.cosmetic_shop.service.OrderService;
import com.example.cosmetic_shop.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class OrderController {
    
    private final OrderService orderService;
    private final UserService userService;
    
    // Lấy userId từ Authentication
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new RuntimeException("Vui lòng đăng nhập!");
        }
        
        String username = authentication.getName();
        return userService.getUserIdByUsername(username);
    }
    
    // POST /api/orders - Đặt hàng
    @PostMapping
    public ResponseEntity<ApiResponse> createOrder(@RequestBody OrderRequest request) {
        try {
            Long userId = getCurrentUserId();
            Order order = orderService.createOrder(userId, request);
            
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Đặt hàng thành công!", 
                            new Object() {
                                public final Long orderId = order.getId();
                                public final Double totalAmount = order.getTotalAmount();
                            }));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/orders?page=0&size=10 - Lấy danh sách đơn hàng của user
    @GetMapping
    public ResponseEntity<ApiResponse> getMyOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        try {
            Long userId = getCurrentUserId();
            Pageable pageable = PageRequest.of(page, size);
            Page<OrderResponse> orders = orderService.getOrdersByUserId(userId, pageable);
            return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đơn hàng thành công!", orders));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/orders/{id} - Chi tiết đơn hàng
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse> getOrderById(@PathVariable Long id) {
        try {
            Long userId = getCurrentUserId();
            OrderResponse order = orderService.getOrderResponse(id, userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy thông tin đơn hàng thành công!", order));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // PUT /api/orders/{id}/cancel?confirm=true - Hủy đơn hàng
    @PutMapping("/{id}/cancel")
    public ResponseEntity<ApiResponse> cancelOrder(
            @PathVariable Long id,
            @RequestParam(required = false, defaultValue = "false") boolean confirm) {
        try {
            Long userId = getCurrentUserId();
            orderService.cancelOrder(id, userId, confirm);
            return ResponseEntity.ok(ApiResponse.success("Hủy đơn hàng thành công!"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/orders/count - Đếm số đơn hàng của user
    @GetMapping("/count")
    public ResponseEntity<ApiResponse> countMyOrders() {
        try {
            Long userId = getCurrentUserId();
            long count = orderService.countUserOrders(userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy số lượng đơn hàng thành công!", count));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/orders/total-spending - Tổng chi tiêu của user
    @GetMapping("/total-spending")
    public ResponseEntity<ApiResponse> getTotalSpending() {
        try {
            Long userId = getCurrentUserId();
            Double total = orderService.calculateUserTotalSpending(userId);
            return ResponseEntity.ok(ApiResponse.success("Lấy tổng chi tiêu thành công!", total));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // =============== ADMIN ENDPOINTS ===============
    
    // GET /api/orders/admin/all?page=0&size=10 - Lấy tất cả đơn hàng (Admin)
    @GetMapping("/admin/all")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getAllOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        try {
            Pageable pageable = PageRequest.of(page, size);
            Page<OrderResponse> orders = orderService.getAllOrders(pageable);
            return ResponseEntity.ok(ApiResponse.success("Lấy tất cả đơn hàng thành công!", orders));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // GET /api/orders/admin/status/{status}?page=0&size=10 - Lấy đơn theo status (Admin)
    @GetMapping("/admin/status/{status}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getOrdersByStatus(
            @PathVariable String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        try {
            Order.OrderStatus orderStatus = Order.OrderStatus.valueOf(status.toUpperCase());
            Pageable pageable = PageRequest.of(page, size);
            Page<OrderResponse> orders = orderService.getOrdersByStatus(orderStatus, pageable);
            return ResponseEntity.ok(ApiResponse.success("Lấy đơn hàng theo trạng thái thành công!", orders));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error("Trạng thái không hợp lệ! (PENDING, CONFIRMED, SHIPPING, DELIVERED, CANCELLED)"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // PUT /api/orders/admin/{id}/status - Cập nhật trạng thái đơn hàng (Admin)
    @PutMapping("/admin/{id}/status")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> updateOrderStatus(
            @PathVariable Long id,
            @RequestParam String status) {
        try {
            Order.OrderStatus orderStatus = Order.OrderStatus.valueOf(status.toUpperCase());
            Order order = orderService.updateOrderStatus(id, orderStatus);
            return ResponseEntity.ok(ApiResponse.success("Cập nhật trạng thái đơn hàng thành công!", order));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error("Trạng thái không hợp lệ! (PENDING, CONFIRMED, SHIPPING, DELIVERED, CANCELLED)"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
}