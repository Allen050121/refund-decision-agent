package com.example.aftersale.domain.refund;

import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.shared.*;
import com.example.aftersale.infrastructure.config.RefundProperties;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 退款资格校验领域服务
 * 文档规定：退款资格由 Java 领域服务计算，不由模型判断
 *
 * 关键边界：
 * - 金额使用整数分，禁止浮点数
 * - 校验订单归属、订单状态、退款历史和规则版本
 * - Agent 只能获取建议上限，不能自行决定最终退款金额
 */
@Service
@RequiredArgsConstructor
public class RefundEligibilityService {

    private final RefundProperties refundProperties;

    /**
     * 校验退款资格
     */
    public RefundEligibilityResult checkEligibility(
            Order order,
            LearningProgress progress,
            Course course,
            ReasonCode reasonCode,
            UserId requesterUserId,
            int abnormalRefundCount,
            LocalDateTime now) {

        List<String> evidence = new ArrayList<>();

        // 1. 订单归属校验（必须由 Java 保证）
        if (!order.belongsTo(requesterUserId)) {
            return RefundEligibilityResult.notEligible("PERMISSION_DENIED", "订单不属于当前用户");
        }

        // 2. 订单状态校验
        if (!order.isPaid()) {
            return RefundEligibilityResult.notEligible("ORDER_NOT_PAID", "订单未支付");
        }
        evidence.add("ORDER_PAID");

        if (order.isRefunded()) {
            return RefundEligibilityResult.notEligible("ALREADY_REFUNDED", "订单已退款");
        }

        // 3. 根据退款原因码进行校验
        RefundEligibilityResult result = checkByReasonCode(order, progress, course,
                reasonCode, evidence, now);

        // 4. 风险检查：异常退款记录
        if (result.isEligible() && abnormalRefundCount >= refundProperties.getAbnormalRefundThreshold()) {
            return RefundEligibilityResult.needsApproval(
                    result.getDecisionCode(),
                    result.getMaxRefundAmount(),
                    "用户存在多次异常退款记录",
                    evidence
            );
        }

        // 5. 金额超过阈值需要审批
        if (result.isEligible() && !result.isApprovalRequired()
                && result.getMaxRefundAmount().isGreaterThan(Money.ofCents(refundProperties.getApprovalThresholdAmount()))) {
            return RefundEligibilityResult.needsApproval(
                    result.getDecisionCode(),
                    result.getMaxRefundAmount(),
                    "退款金额超过阈值",
                    evidence
            );
        }

        return result;
    }

    private RefundEligibilityResult checkByReasonCode(
            Order order, LearningProgress progress, Course course,
            ReasonCode reasonCode, List<String> evidence, LocalDateTime now) {

        switch (reasonCode) {
            case COURSE_UNAVAILABLE:
                return checkCourseUnavailable(order, course, evidence);
            case DUPLICATE_PURCHASE:
                return checkDuplicatePurchase(order, evidence);
            case NO_REASON:
                return checkNoReasonRefund(order, progress, course, evidence, now);
            case EXCEEDED_PROGRESS_LIMIT:
                return RefundEligibilityResult.notEligible("EXCEEDED_PROGRESS", "学习进度超过限制");
            case EXPIRED_REFUND_WINDOW:
                return RefundEligibilityResult.notEligible("EXPIRED_WINDOW", "超过退款有效期");
            case PROMOTIONAL_RESTRICTION:
                return RefundEligibilityResult.notEligible("PROMOTIONAL_LIMIT", "促销课程不支持无理由退款");
            default:
                return checkGeneralRefund(order, progress, evidence, now);
        }
    }

    private RefundEligibilityResult checkCourseUnavailable(Order order, Course course, List<String> evidence) {
        if (course == null) {
            return RefundEligibilityResult.notEligible("COURSE_INFO_MISSING", "缺少课程信息");
        }

        if (!course.isUnavailable()) {
            return RefundEligibilityResult.notEligible("COURSE_AVAILABLE", "课程状态正常，不支持此原因退款");
        }

        evidence.add("COURSE_UNAVAILABLE");
        evidence.add("COURSE_REASON: " + course.getUnavailableReason());

        return new RefundEligibilityResult(
                true, "COURSE_SERVICE_FAILURE", order.getMaxRefundAmount(),
                false, null, evidence, null, "MEDIUM"
        );
    }

    private RefundEligibilityResult checkDuplicatePurchase(Order order, List<String> evidence) {
        evidence.add("DUPLICATE_PURCHASE_CHECKED");

        return new RefundEligibilityResult(
                true, "DUPLICATE_PURCHASE_REFUND", order.getMaxRefundAmount(),
                false, null, evidence, null, "LOW"
        );
    }

    private RefundEligibilityResult checkNoReasonRefund(
            Order order, LearningProgress progress, Course course,
            List<String> evidence, LocalDateTime now) {

        if (course != null && course.isPromotional()) {
            return RefundEligibilityResult.notEligible("PROMOTIONAL_LIMIT", "促销课程不支持无理由退款");
        }

        long daysSincePayment = order.daysSincePayment(now);
        if (daysSincePayment > refundProperties.getMaxRefundDaysNoReason()) {
            evidence.add("EXPIRED_DAYS: " + daysSincePayment);
            return RefundEligibilityResult.notEligible("EXPIRED_WINDOW",
                    "超过无理由退款有效期（" + refundProperties.getMaxRefundDaysNoReason() + "天）");
        }
        evidence.add("WITHIN_REFUND_WINDOW");

        BigDecimal maxProgress = BigDecimal.valueOf(refundProperties.getMaxProgressPercentage());
        if (progress != null && progress.exceedsLimit(maxProgress)) {
            evidence.add("PROGRESS: " + progress.getProgressPercentageInt() + "%");
            return RefundEligibilityResult.notEligible("EXCEEDED_PROGRESS",
                    "学习进度超过限制（" + maxProgress + "%）");
        }
        evidence.add("PROGRESS_WITHIN_LIMIT");

        return new RefundEligibilityResult(
                true, "NO_REASON_REFUND", order.getMaxRefundAmount(),
                false, null, evidence, null, "LOW"
        );
    }

    private RefundEligibilityResult checkGeneralRefund(
            Order order, LearningProgress progress,
            List<String> evidence, LocalDateTime now) {

        long daysSincePayment = order.daysSincePayment(now);
        if (daysSincePayment > refundProperties.getMaxRefundDaysNoReason()) {
            return RefundEligibilityResult.notEligible("EXPIRED_WINDOW", "超过退款有效期");
        }
        evidence.add("WITHIN_WINDOW");

        BigDecimal maxProgress = BigDecimal.valueOf(refundProperties.getMaxProgressPercentage());
        if (progress != null && progress.exceedsLimit(maxProgress)) {
            return RefundEligibilityResult.notEligible("EXCEEDED_PROGRESS", "学习进度超过限制");
        }
        evidence.add("PROGRESS_OK");

        return RefundEligibilityResult.needsApproval(
                "GENERAL_REFUND",
                order.getMaxRefundAmount(),
                "需要人工确认退款原因",
                evidence
        );
    }
}