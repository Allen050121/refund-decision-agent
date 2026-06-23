package com.example.aftersale.application.port;

import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.shared.OrderId;
import com.example.aftersale.domain.shared.UserId;

/**
 * 订单查询端口
 * 定义订单查询的接口，由 Infrastructure 层实现
 */
public interface OrderQueryPort {

    /**
     * 查询订单
     *
     * @param orderId 订单ID
     * @param requesterUserId 请求用户ID（用于归属校验）
     * @return 订单领域对象
     * @throws OrderNotFoundException 订单不存在
     * @throws PermissionDeniedException 订单不属于当前用户
     */
    Order findById(OrderId orderId, UserId requesterUserId);

    /**
     * 检查订单是否存在
     */
    boolean existsById(OrderId orderId);
}