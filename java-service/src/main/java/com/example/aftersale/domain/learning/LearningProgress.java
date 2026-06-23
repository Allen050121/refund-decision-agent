package com.example.aftersale.domain.learning;

import com.example.aftersale.domain.shared.OrderId;
import com.example.aftersale.domain.shared.UserId;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 学习进度领域模型
 * 用于退款判断的学习进度限制校验
 */
@Getter
public class LearningProgress {

    private final OrderId orderId;
    private final UserId userId;
    private final String courseId;
    private BigDecimal progressPercentage;  // 学习进度百分比
    private int totalVideoDuration;          // 总视频时长（秒）
    private int watchedDuration;             // 已观看时长（秒）
    private LocalDateTime lastLearnedAt;
    private LocalDateTime firstLearnedAt;

    public LearningProgress(OrderId orderId, UserId userId, String courseId,
                            BigDecimal progressPercentage, int totalVideoDuration,
                            int watchedDuration, LocalDateTime lastLearnedAt,
                            LocalDateTime firstLearnedAt) {
        this.orderId = orderId;
        this.userId = userId;
        this.courseId = courseId;
        this.progressPercentage = progressPercentage;
        this.totalVideoDuration = totalVideoDuration;
        this.watchedDuration = watchedDuration;
        this.lastLearnedAt = lastLearnedAt;
        this.firstLearnedAt = firstLearnedAt;
    }

    /**
     * 是否已开始学习
     */
    public boolean hasStartedLearning() {
        return firstLearnedAt != null || watchedDuration > 0;
    }

    /**
     * 学习进度是否超过限制
     * 文档规定：学习进度超过30%后不支持退款（除特殊情况）
     */
    public boolean exceedsLimit(BigDecimal maxPercentage) {
        return progressPercentage.compareTo(maxPercentage) > 0;
    }

    /**
     * 学习进度是否超过默认限制（30%）
     */
    public boolean exceedsDefaultLimit() {
        return exceedsLimit(BigDecimal.valueOf(30));
    }

    /**
     * 获取进度百分比
     */
    public BigDecimal getProgressPercentage() {
        return progressPercentage;
    }

    /**
     * 获取进度百分比（整数）
     */
    public int getProgressPercentageInt() {
        return progressPercentage.intValue();
    }
}