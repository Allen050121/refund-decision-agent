package com.example.aftersale.domain.refund;

import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.shared.CourseStatus;
import com.example.aftersale.domain.shared.Money;
import com.example.aftersale.domain.shared.OrderId;
import com.example.aftersale.domain.shared.OrderStatus;
import com.example.aftersale.domain.shared.ReasonCode;
import com.example.aftersale.domain.shared.UserId;
import com.example.aftersale.infrastructure.config.RefundProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

class RefundEligibilityServiceTest {

    private static final LocalDateTime NOW = LocalDateTime.of(2026, 6, 23, 10, 0);

    private RefundEligibilityService service;

    @BeforeEach
    void setUp() {
        RefundProperties properties = new RefundProperties();
        properties.setApprovalThresholdAmount(50_000);
        properties.setMaxRefundDaysNoReason(7);
        properties.setMaxProgressPercentage(30.0);
        properties.setAbnormalRefundThreshold(3);
        service = new RefundEligibilityService(properties);
    }

    @Test
    void courseUnavailableAllowsFullRefund() {
        Order order = paidOrder("O20260622003", "U1002", "C2003", 17_900, NOW.minusDays(4));
        Course course = course("C2003", CourseStatus.UNAVAILABLE, false);
        LearningProgress progress = progress(order, BigDecimal.TEN);

        RefundEligibilityResult result = service.checkEligibility(
                order, progress, course, ReasonCode.COURSE_UNAVAILABLE, new UserId("U1002"), 1, NOW);

        assertThat(result.isEligible()).isTrue();
        assertThat(result.isApprovalRequired()).isFalse();
        assertThat(result.getDecisionCode()).isEqualTo("COURSE_SERVICE_FAILURE");
        assertThat(result.getMaxRefundAmount().getCents()).isEqualTo(17_900);
        assertThat(result.getEvidence()).contains("ORDER_PAID", "COURSE_UNAVAILABLE");
    }

    @Test
    void noReasonWithinWindowAndProgressLimitAllowsRefund() {
        Order order = paidOrder("O20260622001", "U1001", "C2001", 19_900, NOW.minusDays(2));
        Course course = course("C2001", CourseStatus.ACTIVE, false);
        LearningProgress progress = progress(order, BigDecimal.ZERO);

        RefundEligibilityResult result = service.checkEligibility(
                order, progress, course, ReasonCode.NO_REASON, new UserId("U1001"), 0, NOW);

        assertThat(result.isEligible()).isTrue();
        assertThat(result.isApprovalRequired()).isFalse();
        assertThat(result.getDecisionCode()).isEqualTo("NO_REASON_REFUND");
        assertThat(result.getMaxRefundAmount().getCents()).isEqualTo(19_900);
        assertThat(result.getEvidence()).contains("WITHIN_REFUND_WINDOW", "PROGRESS_WITHIN_LIMIT");
    }

    @Test
    void noReasonRejectsWhenLearningProgressExceedsLimit() {
        Order order = paidOrder("O20260622002", "U1001", "C2002", 24_900, NOW.minusDays(3));
        Course course = course("C2002", CourseStatus.ACTIVE, false);
        LearningProgress progress = progress(order, BigDecimal.valueOf(45.5));

        RefundEligibilityResult result = service.checkEligibility(
                order, progress, course, ReasonCode.NO_REASON, new UserId("U1001"), 0, NOW);

        assertThat(result.isEligible()).isFalse();
        assertThat(result.getDecisionCode()).isEqualTo("EXCEEDED_PROGRESS");
        assertThat(result.getMaxRefundAmount().getCents()).isZero();
    }

    @Test
    void rejectsOrderOwnedByAnotherUser() {
        Order order = paidOrder("O20260622003", "U1002", "C2003", 17_900, NOW.minusDays(4));

        RefundEligibilityResult result = service.checkEligibility(
                order, null, null, ReasonCode.NO_REASON, new UserId("U1001"), 0, NOW);

        assertThat(result.isEligible()).isFalse();
        assertThat(result.getDecisionCode()).isEqualTo("PERMISSION_DENIED");
    }

    @Test
    void rejectsUnpaidOrder() {
        Order order = new Order(
                new OrderId("O20260622009"),
                new UserId("U1003"),
                "C2001",
                Money.ofCents(19_900),
                OrderStatus.PENDING,
                null,
                null,
                null,
                false
        );

        RefundEligibilityResult result = service.checkEligibility(
                order, null, null, ReasonCode.NO_REASON, new UserId("U1003"), 0, NOW);

        assertThat(result.isEligible()).isFalse();
        assertThat(result.getDecisionCode()).isEqualTo("ORDER_NOT_PAID");
    }

    @Test
    void eligibleRefundRequiresApprovalForAbnormalRefundUser() {
        Order order = paidOrder("O20260622001", "U1004", "C2001", 19_900, NOW.minusDays(2));
        Course course = course("C2001", CourseStatus.ACTIVE, false);
        LearningProgress progress = progress(order, BigDecimal.ZERO);

        RefundEligibilityResult result = service.checkEligibility(
                order, progress, course, ReasonCode.NO_REASON, new UserId("U1004"), 3, NOW);

        assertThat(result.isEligible()).isTrue();
        assertThat(result.isApprovalRequired()).isTrue();
        assertThat(result.getDecisionCode()).isEqualTo("NO_REASON_REFUND");
        assertThat(result.getMaxRefundAmount().getCents()).isEqualTo(19_900);
    }

    private static Order paidOrder(String orderId, String userId, String courseId, int amount, LocalDateTime paidAt) {
        return new Order(
                new OrderId(orderId),
                new UserId(userId),
                courseId,
                Money.ofCents(amount),
                OrderStatus.PAID,
                paidAt,
                null,
                null,
                false
        );
    }

    private static Course course(String courseId, CourseStatus status, boolean promotional) {
        return new Course(
                courseId,
                courseId + " demo course",
                Money.ofCents(19_900),
                "demo",
                status,
                status == CourseStatus.UNAVAILABLE ? "video service outage" : null,
                promotional
        );
    }

    private static LearningProgress progress(Order order, BigDecimal percentage) {
        return new LearningProgress(
                order.getOrderId(),
                order.getUserId(),
                order.getCourseId(),
                percentage,
                3600,
                percentage.signum() == 0 ? 0 : 1200,
                percentage.signum() == 0 ? null : NOW.minusDays(1),
                percentage.signum() == 0 ? null : NOW.minusDays(2)
        );
    }
}
