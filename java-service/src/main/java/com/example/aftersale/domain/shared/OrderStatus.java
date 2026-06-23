package com.example.aftersale.domain.shared;

/**
 * 订单状态枚举
 */
public enum OrderStatus {

    /**
     * 待支付
     */
    PENDING,

    /**
     * 已支付
     */
    PAID,

    /**
     * 已退款
     */
    REFUNDED,

    /**
     * 已取消
     */
    CANCELLED
}