package com.example.cosmetic_shop.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CartResponse {
    
    private Long cartId;
    private List<CartItemResponse> items;
    private Integer totalItems;
    private Double totalAmount;
}