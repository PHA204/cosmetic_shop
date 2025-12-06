package com.example.cosmetic_shop.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "orders")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Order {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
    
    @Column(name = "total_amount", nullable = false)
    private Double totalAmount;
    
    @Column(nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.PENDING;
    
    @Column(name = "shipping_address", nullable = false, columnDefinition = "TEXT")
    private String shippingAddress;
    
    @Column(nullable = false, length = 15)
    private String phone;
    
    @Column(columnDefinition = "TEXT")
    private String note;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    public enum OrderStatus {
        PENDING,      // Chờ xác nhận
        CONFIRMED,    // Đã xác nhận
        SHIPPING,     // Đang giao
        DELIVERED,    // Đã giao
        CANCELLED     // Đã hủy
    }
}