package com.example.aftersale.application.exception;

import com.example.aftersale.domain.shared.ErrorCode;

/**
 * 业务异常基类
 */
public class BusinessException extends RuntimeException {

    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }
}