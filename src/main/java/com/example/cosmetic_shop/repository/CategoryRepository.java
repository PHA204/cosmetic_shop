package com.example.cosmetic_shop.repository;

import com.example.cosmetic_shop.entity.Category;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {
    
    // Tìm category theo tên
    Optional<Category> findByName(String name);
    
    // Kiểm tra tên category đã tồn tại chưa
    boolean existsByName(String name);
}