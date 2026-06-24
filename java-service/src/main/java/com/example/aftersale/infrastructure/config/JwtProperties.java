package com.example.aftersale.infrastructure.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * JWT 配置属性
 * 使用 @ConfigurationProperties 替代 @Value，更清晰且支持校验
 */
@Data
@Component
@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {

    /**
     * JWT 密钥
     */
    private String secret;

    /**
     * Token 有效期（毫秒），默认24小时
     */
    private Long expiration = 86400000L;

    /**
     * Token 前缀
     */
    private String tokenPrefix = "Bearer ";

    /**
     * Authorization Header 名称
     */
    private String header = "Authorization";
}