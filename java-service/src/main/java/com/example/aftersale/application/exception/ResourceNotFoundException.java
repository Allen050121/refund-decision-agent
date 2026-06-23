package com.example.aftersale.application.exception;

import com.example.aftersale.domain.shared.ErrorCode;

/**
 * 资源不存在异常
 */
public class ResourceNotFoundException extends BusinessException {

    public ResourceNotFoundException(String resourceType, String resourceId) {
        super(ErrorCode.RESOURCE_NOT_FOUND,
                String.format("%s不存在: %s", resourceType, resourceId));
    }
}