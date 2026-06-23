package com.example.aftersale.application.exception;

import com.example.aftersale.domain.shared.ErrorCode;

/**
 * 权限拒绝异常
 * 文档规定：权限失败立即终止，不重试
 */
public class PermissionDeniedException extends BusinessException {

    public PermissionDeniedException(String message) {
        super(ErrorCode.PERMISSION_DENIED, message);
    }

    public PermissionDeniedException(String resourceType, String resourceId, String userId) {
        super(ErrorCode.PERMISSION_DENIED,
                String.format("%s %s 不属于用户 %s", resourceType, resourceId, userId));
    }
}