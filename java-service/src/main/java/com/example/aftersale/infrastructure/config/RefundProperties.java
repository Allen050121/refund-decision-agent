package com.example.aftersale.infrastructure.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 退款系统配置属性
 * 从 application.yml 读取退款相关的配置
 */
@Data
@Component
@ConfigurationProperties(prefix = "refund")
public class RefundProperties {

    /**
     * 人工审批金额阈值（分）
     */
    private Integer approvalThresholdAmount = 50000;

    /**
     * 无理由退款最大天数
     */
    private Integer maxRefundDaysNoReason = 7;

    /**
     * 最大学习进度百分比限制
     */
    private Double maxProgressPercentage = 30.0;

    /**
     * 异常退款次数阈值（用户超过此次数需要人工审批）
     */
    private Integer abnormalRefundThreshold = 3;

    /**
     * 单任务模型成本上限（美元）
     */
    private Double modelCostLimit = 1.0;
}