package com.example.aftersale.interfaces.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 错误响应 DTO
 * 文档规定工具层必须返回标准错误
 */
@Data
@Builder
public class ErrorResponse {

    /**
     * 错误码
     */
    private String errorCode;

    /**
     * 错误消息
     */
    private String message;

    /**
     * 详细信息
     */
    private String details;
}