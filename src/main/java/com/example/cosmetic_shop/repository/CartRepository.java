package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Cart;
import com.example.cosmetic_shop.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CartRepository extends JpaRepository<Cart, Long> {
    
    // Tìm giỏ hàng theo user
    Optional<Cart> findByUser(User user);
    
    // Tìm giỏ hàng theo user ID
    Optional<Cart> findByUserId(Long userId);
    
    // Kiểm tra user đã có giỏ hàng chưa
    boolean existsByUserId(Long userId);
}