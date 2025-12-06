package com.example.cosmetic_shop.exception;

import com.example.cosmetic_shop.dto.ApiResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    
    // ============================================
    // Custom Exceptions
    // ============================================
    
    // Xử lý ResourceNotFoundException (404)
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponse> handleResourceNotFoundException(
            ResourceNotFoundException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // Xử lý BadRequestException (400)
    @ExceptionHandler(BadRequestException.class)
    public ResponseEntity<ApiResponse> handleBadRequestException(
            BadRequestException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // Xử lý UnauthorizedException (401)
    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ApiResponse> handleUnauthorizedException(
            UnauthorizedException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // Xử lý ConfirmationRequiredException (400)
    @ExceptionHandler(ConfirmationRequiredException.class)
    public ResponseEntity<ApiResponse> handleConfirmationRequiredException(
            ConfirmationRequiredException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // ============================================
    // Spring Security Exceptions
    // ============================================
    
    // Xử lý Authentication Exception (401)
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ApiResponse> handleAuthenticationException(
            AuthenticationException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Xác thực thất bại: " + ex.getMessage()));
    }
    
    // Xử lý Bad Credentials (401)
    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ApiResponse> handleBadCredentialsException(
            BadCredentialsException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Username hoặc password không đúng!"));
    }
    
    // Xử lý Access Denied (403)
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse> handleAccessDeniedException(
            AccessDeniedException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(ApiResponse.error("Bạn không có quyền truy cập!"));
    }
    
    // ============================================
    // Validation Exceptions
    // ============================================
    
    // Xử lý Validation Errors (400)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse> handleValidationException(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(new ApiResponse(false, "Dữ liệu không hợp lệ!", errors));
    }
    
    // Xử lý IllegalArgumentException (400)
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponse> handleIllegalArgumentException(
            IllegalArgumentException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // ============================================
    // Generic Exception Handler
    // ============================================
    
    // Xử lý Runtime Exception (400)
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ApiResponse> handleRuntimeException(
            RuntimeException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getMessage()));
    }
    
    // Xử lý tất cả các Exception còn lại (500)
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse> handleGlobalException(
            Exception ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("Lỗi server: " + ex.getMessage()));
    }
}