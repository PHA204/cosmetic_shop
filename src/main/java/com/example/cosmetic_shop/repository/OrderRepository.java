 package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Order;
import com.example.cosmetic_shop.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    // Tìm tất cả đơn hàng của user (phân trang)
    Page<Order> findByUser(User user, Pageable pageable);
    
    // Tìm tất cả đơn hàng theo user ID (phân trang)
    Page<Order> findByUserId(Long userId, Pageable pageable);
    
    // Tìm đơn hàng theo user ID, sắp xếp theo ngày tạo mới nhất
    List<Order> findByUserIdOrderByCreatedAtDesc(Long userId);
    
    // Tìm đơn hàng theo status
    Page<Order> findByStatus(Order.OrderStatus status, Pageable pageable);
    
    // Tìm đơn hàng theo user và status
    Page<Order> findByUserIdAndStatus(Long userId, Order.OrderStatus status, Pageable pageable);
    
    // Tìm đơn hàng trong khoảng thời gian
    @Query("SELECT o FROM Order o WHERE o.createdAt BETWEEN :startDate AND :endDate ORDER BY o.createdAt DESC")
    List<Order> findOrdersBetweenDates(@Param("startDate") LocalDateTime startDate, 
                                       @Param("endDate") LocalDateTime endDate);
    
    // Đếm số đơn hàng của user
    long countByUserId(Long userId);
    
    // Đếm số đơn hàng theo status
    long countByStatus(Order.OrderStatus status);
    
    // Tính tổng doanh thu
    @Query("SELECT SUM(o.totalAmount) FROM Order o WHERE o.status = :status")
    Double calculateTotalRevenue(@Param("status") Order.OrderStatus status);
    
    // Tính tổng doanh thu của user
    @Query("SELECT SUM(o.totalAmount) FROM Order o WHERE o.user.id = :userId AND o.status = :status")
    Double calculateUserTotalSpending(@Param("userId") Long userId, @Param("status") Order.OrderStatus status);
}