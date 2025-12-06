package com.example.cosmetic_shop.controller;

import com.example.cosmetic_shop.service.CategoryService;
import com.example.cosmetic_shop.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
@RequiredArgsConstructor
public class WebController {
    
    private final ProductService productService;
    private final CategoryService categoryService;
    
    // ========== PUBLIC PAGES ==========
    
    @GetMapping("/")
    public String home(Model model) {
        return "index";
    }
    
    @GetMapping("/login")
    public String login() {
        return "login";
    }
    
    @GetMapping("/register")
    public String register() {
        return "register";
    }
    
    @GetMapping("/products")
    public String products(
            @RequestParam(required = false) String search,
            @RequestParam(required = false) Long category,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "12") int size,
            Model model) {
        
        Pageable pageable = PageRequest.of(page, size);
        
        if (search != null && !search.isEmpty()) {
            model.addAttribute("products", productService.searchProducts(search, pageable));
            model.addAttribute("searchKeyword", search);
        } else if (category != null) {
            model.addAttribute("products", productService.getProductsByCategory(category, pageable));
            model.addAttribute("selectedCategory", category);
        } else {
            model.addAttribute("products", productService.getAllActiveProducts(pageable));
        }
        
        model.addAttribute("categories", categoryService.getAllCategories());
        
        return "products";
    }
    
    @GetMapping("/products/{id}")
    public String productDetail(@PathVariable Long id, Model model) {
        try {
            model.addAttribute("product", productService.getProductById(id));
            // Optional: Load related products
            // model.addAttribute("relatedProducts", ...);
            return "product-detail";
        } catch (Exception e) {
            return "redirect:/products?error=product-not-found";
        }
    }
    
    @GetMapping("/categories")
    public String categories(Model model) {
        model.addAttribute("categories", categoryService.getAllCategories());
        return "categories";
    }
    
    // ========== AUTHENTICATED PAGES ==========
    
    @GetMapping("/cart")
    public String cart() {
        return "cart";
    }
    
    @GetMapping("/checkout")
    public String checkout() {
        return "checkout";
    }
    
    @GetMapping("/orders")
    public String orders() {
        return "orders";
    }
    
    @GetMapping("/orders/{id}")
    public String orderDetail(@PathVariable Long id, Model model) {
        model.addAttribute("orderId", id);
        return "order-detail";
    }
    
    @GetMapping("/profile")
    public String profile() {
        return "profile";
    }
    
    // ========== ADMIN PAGES ==========
    
    @GetMapping("/admin")
    public String adminDashboard() {
        return "admin/dashboard";
    }
    
    @GetMapping("/admin/products")
    public String adminProducts() {
        return "admin/products";
    }
    
    @GetMapping("/admin/orders")
    public String adminOrders() {
        return "admin/orders";
    }
    
    @GetMapping("/admin/users")
    public String adminUsers() {
        return "admin/users";
    }
    
    @GetMapping("/admin/categories")
    public String adminCategories() {
        return "admin/categories";
    }
}