package com.example.aftersale.domain.shared;

/**
 * 课程状态枚举
 */
public enum CourseStatus {

    /**
     * 正常可用
     */
    ACTIVE,

    /**
     * 未激活
     */
    INACTIVE,

    /**
     * 不可用（如视频服务故障）
     */
    UNAVAILABLE
}