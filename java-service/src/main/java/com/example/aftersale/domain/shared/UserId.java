package com.example.aftersale.domain.shared;

/**
 * 用户ID值对象
 * 用于封装用户业务ID，避免原始类型滥用
 */
public record UserId(String value) {

    public UserId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("用户ID不能为空");
        }
        if (!value.startsWith("U")) {
            throw new IllegalArgumentException("用户ID格式错误，应以U开头");
        }
    }

    public static UserId of(String value) {
        return new UserId(value);
    }
}