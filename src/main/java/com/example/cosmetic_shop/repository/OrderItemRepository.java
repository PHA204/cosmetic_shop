package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Order;
import com.example.cosmetic_shop.entity.OrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {
    
    // Tìm tất cả items trong đơn hàng
    List<OrderItem> findByOrder(Order order);
    
    // Tìm tất cả items theo order ID
    List<OrderItem> findByOrderId(Long orderId);
    
    // Tìm items theo product ID
    List<OrderItem> findByProductId(Long productId);
    
    // Đếm số lượng items trong đơn hàng
    long countByOrder(Order order);
    
    // Đếm số lượng items theo order ID
    long countByOrderId(Long orderId);
    
    // Tính tổng tiền của đơn hàng
    @Query("SELECT SUM(oi.quantity * oi.price) FROM OrderItem oi WHERE oi.order.id = :orderId")
    Double calculateOrderTotal(@Param("orderId") Long orderId);
    
    // Thống kê sản phẩm bán chạy nhất
    @Query("SELECT oi.product.id, oi.product.name, SUM(oi.quantity) as totalSold " +
           "FROM OrderItem oi GROUP BY oi.product.id, oi.product.name ORDER BY totalSold DESC")
    List<Object[]> findBestSellingProducts();
}