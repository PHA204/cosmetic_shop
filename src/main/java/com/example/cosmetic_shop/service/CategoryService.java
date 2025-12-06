package com.example.cosmetic_shop.service;

import com.example.cosmetic_shop.dto.CategoryRequest;
import com.example.cosmetic_shop.entity.Category;
import com.example.cosmetic_shop.repository.CategoryRepository;
import com.example.cosmetic_shop.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CategoryService {
    
    private final CategoryRepository categoryRepository;
    private final ProductRepository productRepository;
    
    // Lấy tất cả danh mục
    public List<Category> getAllCategories() {
        return categoryRepository.findAll();
    }
    
    // Lấy category theo ID
    public Category getCategoryById(Long id) {
        return categoryRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy danh mục!"));
    }
    
    // Tạo category mới (Admin)
    @Transactional
    public Category createCategory(CategoryRequest request) {
        // Kiểm tra tên đã tồn tại
        if (categoryRepository.existsByName(request.getName())) {
            throw new RuntimeException("Tên danh mục đã tồn tại!");
        }
        
        Category category = new Category();
        category.setName(request.getName());
        category.setDescription(request.getDescription());
        
        return categoryRepository.save(category);
    }
    
    // Cập nhật category (Admin)
    @Transactional
    public Category updateCategory(Long id, CategoryRequest request) {
        Category category = getCategoryById(id);
        
        // Kiểm tra tên mới có trùng với category khác không
        if (!category.getName().equals(request.getName()) && 
            categoryRepository.existsByName(request.getName())) {
            throw new RuntimeException("Tên danh mục đã tồn tại!");
        }
        
        category.setName(request.getName());
        category.setDescription(request.getDescription());
        
        return categoryRepository.save(category);
    }
    
    // Xóa category (Admin) - Có xác nhận
    @Transactional
    public void deleteCategory(Long id, boolean confirm) {
        if (!confirm) {
            throw new RuntimeException("Vui lòng xác nhận xóa danh mục bằng cách thêm ?confirm=true");
        }
        
        Category category = getCategoryById(id);
        
        // Kiểm tra có sản phẩm nào thuộc category này không
        long productCount = productRepository.countByCategoryAndIsActiveTrue(category);
        if (productCount > 0) {
            throw new RuntimeException("Không thể xóa danh mục vì còn " + productCount + " sản phẩm!");
        }
        
        categoryRepository.delete(category);
    }
}