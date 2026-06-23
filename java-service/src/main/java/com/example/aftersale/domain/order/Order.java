package com.example.aftersale.domain.order;

import com.example.aftersale.domain.shared.*;
import lombok.Getter;

import java.time.LocalDateTime;

/**
 * 订单领域聚合根
 * 封装订单相关的业务规则和状态
 */
@Getter
public class Order {

    private final OrderId orderId;
    private final UserId userId;
    private final String courseId;
    private final Money amount;
    private OrderStatus status;
    private LocalDateTime paidAt;
    private LocalDateTime refundedAt;
    private Money refundedAmount;
    private boolean hasRefunded;

    public Order(OrderId orderId, UserId userId, String courseId, Money amount,
                 OrderStatus status, LocalDateTime paidAt, LocalDateTime refundedAt,
                 Money refundedAmount, boolean hasRefunded) {
        this.orderId = orderId;
        this.userId = userId;
        this.courseId = courseId;
        this.amount = amount;
        this.status = status;
        this.paidAt = paidAt;
        this.refundedAt = refundedAt;
        this.refundedAmount = refundedAmount;
        this.hasRefunded = hasRefunded;
    }

    /**
     * 校验订单归属
     * 文档规定：必须校验订单归属，不信任 Python 传入的结论
     */
    public boolean belongsTo(UserId requesterUserId) {
        return this.userId.equals(requesterUserId);
    }

    /**
     * 订单是否已支付
     */
    public boolean isPaid() {
        return status == OrderStatus.PAID;
    }

    /**
     * 订单是否已退款
     */
    public boolean isRefunded() {
        return status == OrderStatus.REFUNDED || hasRefunded;
    }

    /**
     * 订单是否可退款（状态检查）
     */
    public boolean canRefund() {
        return isPaid() && !isRefunded();
    }

    /**
     * 获取最大可退金额
     * 文档规定：Agent 只能获取建议上限，不能自行决定最终退款金额
     */
    public Money getMaxRefundAmount() {
        if (!canRefund()) {
            return Money.ofCents(0);
        }
        // 已退部分金额时，剩余可退金额为原金额减已退金额
        if (refundedAmount != null) {
            return amount.subtract(refundedAmount);
        }
        return amount;
    }

    /**
     * 获取支付后经过的天数
     */
    public long daysSincePayment(LocalDateTime now) {
        if (paidAt == null) {
            return -1;  // 未支付
        }
        return java.time.Duration.between(paidAt, now).toDays();
    }
}