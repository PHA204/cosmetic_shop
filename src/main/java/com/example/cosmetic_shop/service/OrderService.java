package com.example.cosmetic_shop.service;

import com.example.cosmetic_shop.dto.OrderRequest;
import com.example.cosmetic_shop.dto.OrderItemResponse;
import com.example.cosmetic_shop.dto.OrderResponse;
import com.example.cosmetic_shop.entity.*;
import com.example.cosmetic_shop.repository.CartItemRepository;
import com.example.cosmetic_shop.repository.OrderItemRepository;
import com.example.cosmetic_shop.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final CartService cartService;
    private final CartItemRepository cartItemRepository;
    private final ProductService productService;
    private final UserService userService;
    
    // Tạo đơn hàng từ giỏ hàng
    @Transactional
    public Order createOrder(Long userId, OrderRequest request) {
        User user = userService.getUserById(userId);
        Cart cart = cartService.getCartByUserId(userId);
        List<CartItem> cartItems = cartItemRepository.findByCartId(cart.getId());
        
        if (cartItems.isEmpty()) {
            throw new RuntimeException("Giỏ hàng trống!");
        }
        
        // Tính tổng tiền
        double totalAmount = cartItems.stream()
                .mapToDouble(item -> item.getProduct().getPrice() * item.getQuantity())
                .sum();
        
        // Tạo đơn hàng
        Order order = new Order();
        order.setUser(user);
        order.setTotalAmount(totalAmount);
        order.setStatus(Order.OrderStatus.PENDING);
        order.setShippingAddress(request.getShippingAddress());
        order.setPhone(request.getPhone());
        order.setNote(request.getNote());
        
        order = orderRepository.save(order);
        
        // Tạo order items từ cart items
        for (CartItem cartItem : cartItems) {
            OrderItem orderItem = new OrderItem();
            orderItem.setOrder(order);
            orderItem.setProduct(cartItem.getProduct());
            orderItem.setQuantity(cartItem.getQuantity());
            orderItem.setPrice(cartItem.getProduct().getPrice());
            orderItemRepository.save(orderItem);
            
            // Giảm tồn kho
            productService.decreaseStock(cartItem.getProduct().getId(), cartItem.getQuantity());
        }
        
        // Xóa giỏ hàng sau khi đặt hàng thành công
        cartService.clearCart(userId);
        
        return order;
    }
    
    // Lấy danh sách đơn hàng của user (phân trang)
    public Page<OrderResponse> getOrdersByUserId(Long userId, Pageable pageable) {
        return orderRepository.findByUserId(userId, pageable)
                .map(this::convertToResponse);
    }
    
    // Lấy chi tiết đơn hàng
    public Order getOrderById(Long orderId) {
        return orderRepository.findById(orderId)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy đơn hàng!"));
    }
    
    // Lấy đơn hàng với response đầy đủ
    public OrderResponse getOrderResponse(Long orderId, Long userId) {
        Order order = getOrderById(orderId);
        
        // Kiểm tra quyền truy cập
        if (!order.getUser().getId().equals(userId)) {
            throw new RuntimeException("Không có quyền xem đơn hàng này!");
        }
        
        return convertToResponse(order);
    }
    
    // Lấy order items
    public List<OrderItemResponse> getOrderItems(Long orderId) {
        List<OrderItem> items = orderItemRepository.findByOrderId(orderId);
        return items.stream()
                .map(this::convertToOrderItemResponse)
                .collect(Collectors.toList());
    }
    
    // Hủy đơn hàng - Có xác nhận
    @Transactional
    public void cancelOrder(Long orderId, Long userId, boolean confirm) {
        if (!confirm) {
            throw new RuntimeException("Vui lòng xác nhận hủy đơn hàng bằng cách thêm ?confirm=true");
        }
        
        Order order = getOrderById(orderId);
        
        // Kiểm tra quyền
        if (!order.getUser().getId().equals(userId)) {
            throw new RuntimeException("Không có quyền hủy đơn hàng này!");
        }
        
        // Chỉ được hủy đơn ở trạng thái PENDING hoặc CONFIRMED
        if (order.getStatus() != Order.OrderStatus.PENDING && 
            order.getStatus() != Order.OrderStatus.CONFIRMED) {
            throw new RuntimeException("Không thể hủy đơn hàng ở trạng thái: " + order.getStatus());
        }
        
        // Hoàn lại tồn kho
        List<OrderItem> items = orderItemRepository.findByOrderId(orderId);
        for (OrderItem item : items) {
            productService.increaseStock(item.getProduct().getId(), item.getQuantity());
        }
        
        // Cập nhật trạng thái
        order.setStatus(Order.OrderStatus.CANCELLED);
        orderRepository.save(order);
    }
    
    // Cập nhật trạng thái đơn hàng (Admin)
    @Transactional
    public Order updateOrderStatus(Long orderId, Order.OrderStatus status) {
        Order order = getOrderById(orderId);
        order.setStatus(status);
        return orderRepository.save(order);
    }
    
    // Lấy tất cả đơn hàng (Admin)
    public Page<OrderResponse> getAllOrders(Pageable pageable) {
        return orderRepository.findAll(pageable)
                .map(this::convertToResponse);
    }
    
    // Lấy đơn hàng theo status (Admin)
    public Page<OrderResponse> getOrdersByStatus(Order.OrderStatus status, Pageable pageable) {
        return orderRepository.findByStatus(status, pageable)
                .map(this::convertToResponse);
    }
    
    // Đếm số đơn hàng của user
    public long countUserOrders(Long userId) {
        return orderRepository.countByUserId(userId);
    }
    
    // Tính tổng chi tiêu của user
    public Double calculateUserTotalSpending(Long userId) {
        Double total = orderRepository.calculateUserTotalSpending(userId, Order.OrderStatus.DELIVERED);
        return total != null ? total : 0.0;
    }
    
    // Convert Order to Response
    private OrderResponse convertToResponse(Order order) {
        OrderResponse response = new OrderResponse();
        response.setId(order.getId());
        response.setUserId(order.getUser().getId());
        response.setUsername(order.getUser().getUsername());
        
        List<OrderItemResponse> items = orderItemRepository.findByOrderId(order.getId())
                .stream()
                .map(this::convertToOrderItemResponse)
                .collect(Collectors.toList());
        
        response.setItems(items);
        response.setTotalAmount(order.getTotalAmount());
        response.setStatus(order.getStatus().name());
        response.setShippingAddress(order.getShippingAddress());
        response.setPhone(order.getPhone());
        response.setNote(order.getNote());
        response.setCreatedAt(order.getCreatedAt());
        response.setUpdatedAt(order.getUpdatedAt());
        
        return response;
    }
    
    // Convert OrderItem to Response
    private OrderItemResponse convertToOrderItemResponse(OrderItem item) {
        OrderItemResponse response = new OrderItemResponse();
        response.setId(item.getId());
        response.setProductId(item.getProduct().getId());
        response.setProductName(item.getProduct().getName());
        response.setProductImage(item.getProduct().getImage());
        response.setQuantity(item.getQuantity());
        response.setPrice(item.getPrice());
        response.setSubTotal(item.getSubTotal());
        return response;
    }
}