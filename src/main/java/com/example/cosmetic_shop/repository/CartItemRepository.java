package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Cart;
import com.example.cosmetic_shop.entity.CartItem;
import com.example.cosmetic_shop.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CartItemRepository extends JpaRepository<CartItem, Long> {
    
    // Tìm tất cả items trong giỏ hàng
    List<CartItem> findByCart(Cart cart);
    
    // Tìm tất cả items theo cart ID
    List<CartItem> findByCartId(Long cartId);
    
    // Tìm cart item theo cart và product
    Optional<CartItem> findByCartAndProduct(Cart cart, Product product);
    
    // Tìm cart item theo cart ID và product ID
    Optional<CartItem> findByCartIdAndProductId(Long cartId, Long productId);
    
    // Xóa tất cả items trong giỏ hàng
    void deleteByCart(Cart cart);
    
    // Xóa tất cả items theo cart ID
    void deleteByCartId(Long cartId);
    
    // Đếm số lượng items trong giỏ
    long countByCart(Cart cart);
    
    // Đếm số lượng items theo cart ID
    long countByCartId(Long cartId);
    
    // Tính tổng tiền trong giỏ hàng
    @Query("SELECT SUM(ci.quantity * ci.product.price) FROM CartItem ci WHERE ci.cart.id = :cartId")
    Double calculateCartTotal(@Param("cartId") Long cartId);
}