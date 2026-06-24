package com.example.aftersale.domain.refund;

import com.example.aftersale.domain.shared.Money;
import com.example.aftersale.domain.shared.RuleVersion;
import lombok.Data;

import java.util.List;

/**
 * 退款资格校验结果
 * 文档规定：退款资格由 Java 领域服务计算，不由模型判断
 */
@Data
public class RefundEligibilityResult {

    private final boolean eligible;
    private final String decisionCode;
    private final Money maxRefundAmount;
    private final boolean approvalRequired;
    private final String approvalReason;
    private final List<String> evidence;
    private final RuleVersion appliedRule;
    private final String riskLevel;

    public RefundEligibilityResult(boolean eligible, String decisionCode, Money maxRefundAmount,
                                     boolean approvalRequired, String approvalReason,
                                     List<String> evidence, RuleVersion appliedRule, String riskLevel) {
        this.eligible = eligible;
        this.decisionCode = decisionCode;
        this.maxRefundAmount = maxRefundAmount;
        this.approvalRequired = approvalRequired;
        this.approvalReason = approvalReason;
        this.evidence = evidence;
        this.appliedRule = appliedRule;
        this.riskLevel = riskLevel;
    }

    public boolean isEligible() {
        return eligible;
    }

    public boolean isApprovalRequired() {
        return approvalRequired;
    }

    public static RefundEligibilityResult notEligible(String decisionCode, String reason) {
        return new RefundEligibilityResult(
                false, decisionCode, Money.ofCents(0),
                false, reason, List.of(), null, null
        );
    }

    public static RefundEligibilityResult needsApproval(String decisionCode, Money maxAmount,
                                                          String reason, List<String> evidence) {
        return new RefundEligibilityResult(
                true, decisionCode, maxAmount,
                true, reason, evidence, null, null
        );
    }
}