package com.example.aftersale.interfaces.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 学习进度响应 DTO
 */
@Data
@Builder
public class LearningProgressResponse {

    /**
     * 订单ID
     */
    private String orderId;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 课程ID
     */
    private String courseId;

    /**
     * 学习进度百分比
     */
    private Double progressPercentage;

    /**
     * 总视频时长（秒）
     */
    private Integer totalVideoDuration;

    /**
     * 已观看时长（秒）
     */
    private Integer watchedDuration;

    /**
     * 是否超过默认限制（30%）
     */
    private Boolean exceedsLimit;
}