package com.example.aftersale.domain.shared;

import java.math.BigDecimal;

/**
 * 金额值对象
 * 使用整数分表示金额，禁止使用浮点数
 * 文档规定：金额使用整数分或 BigDecimal，禁止浮点数
 */
public record Money(int cents) {

    public Money {
        if (cents < 0) {
            throw new IllegalArgumentException("金额不能为负数");
        }
    }

    /**
     * 从分创建金额
     */
    public static Money ofCents(int cents) {
        return new Money(cents);
    }

    /**
     * 从元创建金额（自动转换为分）
     * 注意：仅用于测试或展示，业务逻辑必须使用分
     */
    public static Money ofYuan(BigDecimal yuan) {
        return new Money(yuan.multiply(BigDecimal.valueOf(100)).intValue());
    }

    /**
     * 获取金额（分）
     */
    public int getCents() {
        return cents;
    }

    /**
     * 获取金额（元），用于展示
     */
    public BigDecimal getYuan() {
        return BigDecimal.valueOf(cents).divide(BigDecimal.valueOf(100));
    }

    /**
     * 金额相加
     */
    public Money add(Money other) {
        return new Money(this.cents + other.cents);
    }

    /**
     * 金额相减（结果不能为负）
     */
    public Money subtract(Money other) {
        int result = this.cents - other.cents;
        if (result < 0) {
            throw new IllegalArgumentException("相减后金额不能为负数");
        }
        return new Money(result);
    }

    /**
     * 比较金额大小
     */
    public boolean isGreaterThan(Money other) {
        return this.cents > other.cents;
    }

    /**
     * 比较金额大小
     */
    public boolean isLessThan(Money other) {
        return this.cents < other.cents;
    }

    /**
     * 格式化显示（如 "199.00元"）
     */
    public String display() {
        return String.format("%.2f元", getYuan().doubleValue());
    }
}