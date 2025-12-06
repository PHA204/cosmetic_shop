package com.example.cosmetic_shop.exception;

public class ConfirmationRequiredException extends RuntimeException {
    
    public ConfirmationRequiredException(String action) {
        super(String.format("Vui lòng xác nhận %s bằng cách thêm ?confirm=true", action));
    }
}