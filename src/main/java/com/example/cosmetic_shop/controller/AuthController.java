package com.example.cosmetic_shop.controller;

import com.example.cosmetic_shop.dto.ApiResponse;
import com.example.cosmetic_shop.dto.JwtResponse;
import com.example.cosmetic_shop.dto.LoginRequest;
import com.example.cosmetic_shop.dto.RegisterRequest;
import com.example.cosmetic_shop.entity.User;
import com.example.cosmetic_shop.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {
    
    private final UserService userService;
    
    // POST /api/auth/register
    @PostMapping("/register")
    public ResponseEntity<ApiResponse> register(@RequestBody RegisterRequest request) {
        try {
            User user = userService.registerUser(request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Đăng ký thành công!", user.getId()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
    
    // POST /api/auth/login
    @PostMapping("/login")
    public ResponseEntity<ApiResponse> login(@RequestBody LoginRequest request) {
        try {
            JwtResponse jwtResponse = userService.loginUser(request);
            return ResponseEntity.ok(ApiResponse.success("Đăng nhập thành công!", jwtResponse));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }
}