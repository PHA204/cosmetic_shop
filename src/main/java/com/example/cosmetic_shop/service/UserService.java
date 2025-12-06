package com.example.cosmetic_shop.service;

import com.example.cosmetic_shop.dto.LoginRequest;
import com.example.cosmetic_shop.dto.RegisterRequest;
import com.example.cosmetic_shop.dto.JwtResponse;
import com.example.cosmetic_shop.entity.User;
import com.example.cosmetic_shop.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    
    // Đăng ký user mới
    @Transactional
    public User registerUser(RegisterRequest request) {
        // Kiểm tra username đã tồn tại
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Username đã tồn tại!");
        }
        
        // Kiểm tra email đã tồn tại
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email đã tồn tại!");
        }
        
        // Tạo user mới
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setFullName(request.getFullName());
        user.setPhone(request.getPhone());
        user.setAddress(request.getAddress());
        user.setRole(User.UserRole.USER);
        
        return userRepository.save(user);
    }
    
    // Đăng nhập
    public JwtResponse loginUser(LoginRequest request) {
        // Tìm user
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("Username hoặc password không đúng!"));
        
        // Kiểm tra password
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Username hoặc password không đúng!");
        }
        
        // Tạo JWT token
        String token = jwtTokenProvider.generateToken(user.getUsername(), user.getRole().name());
        
        return new JwtResponse(token, user.getId(), user.getUsername(), 
                             user.getEmail(), user.getRole().name());
    }
    
    // Lấy user theo username
    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy user!"));
    }
    
    // Lấy user theo ID
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy user!"));
    }
    
    // Kiểm tra user có phải admin không
    public boolean isAdmin(String username) {
        User user = getUserByUsername(username);
        return user.getRole() == User.UserRole.ADMIN;
    }
}