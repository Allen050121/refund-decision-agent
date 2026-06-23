package com.example.aftersale.domain.shared;

/**
 * 退款原因码枚举
 * 对应文档定义的6类退款场景
 */
public enum ReasonCode {

    /**
     * 重复购买
     */
    DUPLICATE_PURCHASE,

    /**
     * 课程无法观看
     */
    COURSE_UNAVAILABLE,

    /**
     * 无理由退款（购买后未学习且处于退款期内）
     */
    NO_REASON,

    /**
     * 已学习超过规定比例
     */
    EXCEEDED_PROGRESS_LIMIT,

    /**
     * 超过退款有效期
     */
    EXPIRED_REFUND_WINDOW,

    /**
     * 其他原因
     */
    GENERAL,

    /**
     * 促销课程限制
     */
    PROMOTIONAL_RESTRICTION
}