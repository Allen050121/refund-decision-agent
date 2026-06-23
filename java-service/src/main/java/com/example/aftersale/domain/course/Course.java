package com.example.aftersale.domain.course;

import com.example.aftersale.domain.shared.CourseStatus;
import com.example.aftersale.domain.shared.Money;
import lombok.Getter;

/**
 * 课程领域模型
 * 用于课程状态查询和退款判断
 */
@Getter
public class Course {

    private final String courseId;
    private final String name;
    private final Money price;
    private final String category;
    private CourseStatus status;
    private String unavailableReason;
    private boolean isPromotional;

    public Course(String courseId, String name, Money price, String category,
                  CourseStatus status, String unavailableReason, boolean isPromotional) {
        this.courseId = courseId;
        this.name = name;
        this.price = price;
        this.category = category;
        this.status = status;
        this.unavailableReason = unavailableReason;
        this.isPromotional = isPromotional;
    }

    /**
     * 课程是否可用
     */
    public boolean isAvailable() {
        return status == CourseStatus.ACTIVE;
    }

    /**
     * 课程是否不可用（如视频服务故障）
     */
    public boolean isUnavailable() {
        return status == CourseStatus.UNAVAILABLE;
    }

    /**
     * 是否为促销课程
     * 文档规定：促销课程有特殊退款限制
     */
    public boolean isPromotional() {
        return isPromotional;
    }

    /**
     * 获取不可用原因
     */
    public String getUnavailableReason() {
        return unavailableReason;
    }

    /**
     * 是否支持无理由退款
     * 促销课程不支持无理由退款
     */
    public boolean supportsNoReasonRefund() {
        return !isPromotional;
    }
}