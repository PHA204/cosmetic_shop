package com.example.cosmetic_shop.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse {
    
    private boolean success;
    private String message;
    private Object data;
    
    // Constructor cho response thành công với data
    public ApiResponse(String message, Object data) {
        this.success = true;
        this.message = message;
        this.data = data;
    }
    
    // Constructor cho response thành công không có data
    public ApiResponse(String message) {
        this.success = true;
        this.message = message;
        this.data = null;
    }
    
    // Constructor cho response lỗi
    public static ApiResponse error(String message) {
        return new ApiResponse(false, message, null);
    }
    
    // Constructor cho response thành công
    public static ApiResponse success(String message) {
        return new ApiResponse(true, message, null);
    }
    
    // Constructor cho response thành công với data
    public static ApiResponse success(String message, Object data) {
        return new ApiResponse(true, message, data);
    }
}