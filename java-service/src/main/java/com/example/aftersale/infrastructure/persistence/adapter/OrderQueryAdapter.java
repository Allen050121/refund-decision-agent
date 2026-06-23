package com.example.aftersale.infrastructure.persistence.adapter;

import com.example.aftersale.application.exception.PermissionDeniedException;
import com.example.aftersale.application.exception.ResourceNotFoundException;
import com.example.aftersale.application.port.OrderQueryPort;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.shared.*;
import com.example.aftersale.infrastructure.persistence.entity.OrderEntity;
import com.example.aftersale.infrastructure.persistence.repository.OrderJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * 订单查询端口实现
 */
@Component
@RequiredArgsConstructor
public class OrderQueryAdapter implements OrderQueryPort {

    private final OrderJpaRepository orderJpaRepository;

    @Override
    public Order findById(OrderId orderId, UserId requesterUserId) {
        OrderEntity entity = orderJpaRepository.findByOrderId(orderId.value())
                .orElseThrow(() -> new ResourceNotFoundException("订单", orderId.value()));

        // 订单归属校验
        if (!entity.getUserId().equals(requesterUserId.value())) {
            throw new PermissionDeniedException("订单", orderId.value(), requesterUserId.value());
        }

        return toDomain(entity);
    }

    @Override
    public boolean existsById(OrderId orderId) {
        return orderJpaRepository.existsByOrderId(orderId.value());
    }

    /**
     * 将 JPA 实体转换为领域对象
     */
    private Order toDomain(OrderEntity entity) {
        return new Order(
                OrderId.of(entity.getOrderId()),
                UserId.of(entity.getUserId()),
                entity.getCourseId(),
                Money.ofCents(entity.getAmount()),
                OrderStatus.valueOf(entity.getStatus()),
                entity.getPaidAt(),
                entity.getRefundedAt(),
                entity.getRefundAmount() != null ? Money.ofCents(entity.getRefundAmount()) : null,
                entity.getHasRefunded() != null ? entity.getHasRefunded() : false
        );
    }
}