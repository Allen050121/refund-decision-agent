package com.example.aftersale.interfaces.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 退款资格校验请求 DTO
 * 文档规定输入格式
 */
@Data
public class RefundEligibilityRequest {

    /**
     * 订单ID
     */
    @NotBlank(message = "订单ID不能为空")
    private String orderId;

    /**
     * 请求用户ID
     */
    @NotBlank(message = "用户ID不能为空")
    private String requesterUserId;

    /**
     * 退款原因码
     */
    private String reasonCode;

    /**
     * 规则版本（可选）
     */
    private Integer ruleVersion;
}