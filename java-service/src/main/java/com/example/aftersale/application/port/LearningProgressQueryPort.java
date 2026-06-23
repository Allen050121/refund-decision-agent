package com.example.aftersale.application.port;

import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.shared.OrderId;
import com.example.aftersale.domain.shared.UserId;

/**
 * 学习进度查询端口
 */
public interface LearningProgressQueryPort {

    /**
     * 查询学习进度
     *
     * @param orderId 订单ID
     * @param requesterUserId 请求用户ID
     * @return 学习进度领域对象（可能为null表示未开始学习）
     */
    LearningProgress findByOrderId(OrderId orderId, UserId requesterUserId);
}