package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Product;
import com.example.cosmetic_shop.entity.Category;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    // Tìm tất cả sản phẩm active (phân trang)
    Page<Product> findByIsActiveTrue(Pageable pageable);
    
    // Tìm sản phẩm theo category (phân trang)
    Page<Product> findByCategoryAndIsActiveTrue(Category category, Pageable pageable);
    
    // Tìm sản phẩm theo category ID (phân trang)
    Page<Product> findByCategoryIdAndIsActiveTrue(Long categoryId, Pageable pageable);
    
    // Tìm kiếm sản phẩm theo tên (phân trang)
    Page<Product> findByNameContainingIgnoreCaseAndIsActiveTrue(String name, Pageable pageable);
    
    // Tìm kiếm sản phẩm theo tên hoặc mô tả
    @Query("SELECT p FROM Product p WHERE (LOWER(p.name) LIKE LOWER(CONCAT('%', :keyword, '%')) " +
           "OR LOWER(p.description) LIKE LOWER(CONCAT('%', :keyword, '%'))) AND p.isActive = true")
    Page<Product> searchProducts(@Param("keyword") String keyword, Pageable pageable);
    
    // Lấy top sản phẩm mới nhất
    List<Product> findTop10ByIsActiveTrueOrderByCreatedAtDesc();
    
    // Đếm số sản phẩm theo category
    long countByCategoryAndIsActiveTrue(Category category);
    
    // Kiểm tra sản phẩm có tồn tại và active không
    boolean existsByIdAndIsActiveTrue(Long id);
}