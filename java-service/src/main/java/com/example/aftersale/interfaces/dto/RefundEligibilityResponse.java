package com.example.aftersale.interfaces.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * 退款资格校验响应 DTO
 * 文档规定输出格式
 */
@Data
@Builder
public class RefundEligibilityResponse {

    /**
     * 是否可退款
     */
    private Boolean eligible;

    /**
     * 决策代码
     */
    private String decisionCode;

    /**
     * 最大可退金额（分）
     */
    private Integer maxRefundAmount;

    /**
     * 是否需要人工审批
     */
    private Boolean approvalRequired;

    /**
     * 审批原因
     */
    private String approvalReason;

    /**
     * 证据列表
     */
    private List<String> evidence;

    /**
     * 适用的规则引用
     */
    private String ruleCitation;

    /**
     * 风险等级
     */
    private String riskLevel;
}