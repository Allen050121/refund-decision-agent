package com.example.aftersale.interfaces.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 课程状态响应 DTO
 */
@Data
@Builder
public class CourseStatusResponse {

    private String courseId;
    private String name;
    private String status;
    private Boolean isAvailable;
    private String unavailableReason;
    private Boolean isPromotional;
}