package com.example.cosmetic_shop.service;

import com.example.cosmetic_shop.dto.ProductRequest;
import com.example.cosmetic_shop.dto.ProductResponse;
import com.example.cosmetic_shop.entity.Category;
import com.example.cosmetic_shop.entity.Product;
import com.example.cosmetic_shop.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProductService {
    
    private final ProductRepository productRepository;
    private final CategoryService categoryService;
    
    // Lấy tất cả sản phẩm active (phân trang)
    public Page<ProductResponse> getAllActiveProducts(Pageable pageable) {
        return productRepository.findByIsActiveTrue(pageable)
                .map(this::convertToResponse);
    }
    
    // Lấy sản phẩm theo category
    public Page<ProductResponse> getProductsByCategory(Long categoryId, Pageable pageable) {
        return productRepository.findByCategoryIdAndIsActiveTrue(categoryId, pageable)
                .map(this::convertToResponse);
    }
    
    // Tìm kiếm sản phẩm
    public Page<ProductResponse> searchProducts(String keyword, Pageable pageable) {
        return productRepository.searchProducts(keyword, pageable)
                .map(this::convertToResponse);
    }
    
    // Lấy top 10 sản phẩm mới
    public List<ProductResponse> getNewProducts() {
        return productRepository.findTop10ByIsActiveTrueOrderByCreatedAtDesc()
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    // Lấy sản phẩm theo ID
    public Product getProductById(Long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy sản phẩm!"));
    }
    
    // Tạo sản phẩm mới (Admin)
    @Transactional
    public Product createProduct(ProductRequest request) {
        Category category = categoryService.getCategoryById(request.getCategoryId());
        
        Product product = new Product();
        product.setName(request.getName());
        product.setDescription(request.getDescription());
        product.setPrice(request.getPrice());
        product.setImage(request.getImage());
        product.setStock(request.getStock());
        product.setCategory(category);
        product.setIsActive(true);
        
        return productRepository.save(product);
    }
    
    // Cập nhật sản phẩm (Admin)
    @Transactional
    public Product updateProduct(Long id, ProductRequest request) {
        Product product = getProductById(id);
        Category category = categoryService.getCategoryById(request.getCategoryId());
        
        product.setName(request.getName());
        product.setDescription(request.getDescription());
        product.setPrice(request.getPrice());
        product.setImage(request.getImage());
        product.setStock(request.getStock());
        product.setCategory(category);
        
        return productRepository.save(product);
    }
    
    // Xóa sản phẩm (Admin) - Soft delete với xác nhận
    @Transactional
    public void deleteProduct(Long id, boolean confirm) {
        if (!confirm) {
            throw new RuntimeException("Vui lòng xác nhận xóa sản phẩm bằng cách thêm ?confirm=true");
        }
        
        Product product = getProductById(id);
        product.setIsActive(false); // Soft delete
        productRepository.save(product);
    }
    
    // Kiểm tra tồn kho
    public boolean checkStock(Long productId, int quantity) {
        Product product = getProductById(productId);
        return product.getStock() >= quantity;
    }
    
    // Giảm tồn kho
    @Transactional
    public void decreaseStock(Long productId, int quantity) {
        Product product = getProductById(productId);
        
        if (product.getStock() < quantity) {
            throw new RuntimeException("Không đủ hàng trong kho!");
        }
        
        product.setStock(product.getStock() - quantity);
        productRepository.save(product);
    }
    
    // Tăng tồn kho (khi hủy đơn)
    @Transactional
    public void increaseStock(Long productId, int quantity) {
        Product product = getProductById(productId);
        product.setStock(product.getStock() + quantity);
        productRepository.save(product);
    }
    
    // Convert Entity to Response DTO
    private ProductResponse convertToResponse(Product product) {
        ProductResponse response = new ProductResponse();
        response.setId(product.getId());
        response.setName(product.getName());
        response.setDescription(product.getDescription());
        response.setPrice(product.getPrice());
        response.setImage(product.getImage());
        response.setStock(product.getStock());
        response.setCategoryName(product.getCategory().getName());
        response.setCategoryId(product.getCategory().getId());
        response.setIsActive(product.getIsActive());
        response.setCreatedAt(product.getCreatedAt());
        return response;
    }
}