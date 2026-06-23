package com.example.aftersale.interfaces.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * 订单响应 DTO
 * 文档规定：最小字段返回
 */
@Data
@Builder
public class OrderResponse {

    /**
     * 订单ID
     */
    private String orderId;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 课程ID
     */
    private String courseId;

    /**
     * 金额（分）
     */
    private Integer amount;

    /**
     * 订单状态
     */
    private String status;

    /**
     * 是否已退款
     */
    private Boolean hasRefunded;

    /**
     * 支付时间
     */
    private String paidAt;

    /**
     * 最大可退金额（分）
     */
    private Integer maxRefundAmount;
}