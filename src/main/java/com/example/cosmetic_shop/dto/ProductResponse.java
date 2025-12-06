package com.example.cosmetic_shop.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductResponse {
    
    private Long id;
    private String name;
    private String description;
    private Double price;
    private String image;
    private Integer stock;
    private String categoryName;
    private Long categoryId;
    private Boolean isActive;
    private LocalDateTime createdAt;
}