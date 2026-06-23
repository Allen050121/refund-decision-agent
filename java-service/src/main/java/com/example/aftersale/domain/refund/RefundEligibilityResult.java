package com.example.aftersale.domain.refund;

import com.example.aftersale.domain.shared.*;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

/**
 * 退款资格校验结果
 * 文档规定：退款资格由 Java 领域服务计算，不由模型判断
 */
@Getter
@Builder
public class RefundEligibilityResult {

    /**
     * 是否可退款
     */
    private final boolean eligible;

    /**
     * 决策代码（如 COURSE_SERVICE_FAILURE）
     */
    private final String decisionCode;

    /**
     * 最大可退金额（分）
     * 文档规定：Agent 只能获取建议上限
     */
    private final Money maxRefundAmount;

    /**
     * 是否需要人工审批
     */
    private final boolean approvalRequired;

    /**
     * 审批原因
     */
    private final String approvalReason;

    /**
     * 证据列表
     * 文档规定：每个确定性结论都有有效证据
     */
    private final List<String> evidence;

    /**
     * 适用的规则版本
     */
    private final RuleVersion appliedRule;

    /**
     * 风险等级
     */
    private final String riskLevel;

    /**
     * 创建不可退款结果
     */
    public static RefundEligibilityResult notEligible(String decisionCode, String reason) {
        return RefundEligibilityResult.builder()
                .eligible(false)
                .decisionCode(decisionCode)
                .maxRefundAmount(Money.ofCents(0))
                .approvalRequired(false)
                .approvalReason(reason)
                .evidence(List.of())
                .build();
    }

    /**
     * 创建需要审批的结果
     */
    public static RefundEligibilityResult needsApproval(String decisionCode, Money maxAmount,
                                                          String reason, List<String> evidence) {
        return RefundEligibilityResult.builder()
                .eligible(true)
                .decisionCode(decisionCode)
                .maxRefundAmount(maxAmount)
                .approvalRequired(true)
                .approvalReason(reason)
                .evidence(evidence)
                .build();
    }
}