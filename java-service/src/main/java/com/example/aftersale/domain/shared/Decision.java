package com.example.aftersale.domain.shared;

/**
 * 退款决策枚举
 * 文档规定：decision 必须来自固定枚举
 */
public enum Decision {

    /**
     * 建议退款
     */
    REFUND_RECOMMENDED,

    /**
     * 拒绝退款
     */
    REFUND_REJECTED,

    /**
     * 需要更多信息
     */
    NEED_MORE_INFORMATION,

    /**
     * 需要人工审批
     */
    WAITING_APPROVAL,

    /**
     * 人工审批通过
     */
    APPROVED,

    /**
     * 人工审批拒绝
     */
    REJECTED
}