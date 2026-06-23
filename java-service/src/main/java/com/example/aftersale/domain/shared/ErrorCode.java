package com.example.aftersale.domain.shared;

/**
 * 标准错误码枚举
 * 文档规定工具层必须返回标准错误
 */
public enum ErrorCode {

    /**
     * 资源不存在
     */
    RESOURCE_NOT_FOUND,

    /**
     * 权限拒绝（订单不属于当前用户）
     */
    PERMISSION_DENIED,

    /**
     * 参数校验错误
     */
    VALIDATION_ERROR,

    /**
     * 依赖服务超时
     */
    DEPENDENCY_TIMEOUT,

    /**
     * 依赖服务不可用
     */
    DEPENDENCY_UNAVAILABLE,

    /**
     * 规则冲突
     */
    RULE_CONFLICT,

    /**
     * 信息不足
     */
    INSUFFICIENT_INFO
}