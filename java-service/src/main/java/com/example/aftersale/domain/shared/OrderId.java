package com.example.aftersale.domain.shared;

/**
 * 订单ID值对象
 * 用于封装订单业务ID
 */
public record OrderId(String value) {

    public OrderId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("订单ID不能为空");
        }
        if (!value.startsWith("O")) {
            throw new IllegalArgumentException("订单ID格式错误，应以O开头");
        }
    }

    public static OrderId of(String value) {
        return new OrderId(value);
    }
}