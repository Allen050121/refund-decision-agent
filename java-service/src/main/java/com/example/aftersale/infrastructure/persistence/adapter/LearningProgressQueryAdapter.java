package com.example.aftersale.infrastructure.persistence.adapter;

import com.example.aftersale.application.port.LearningProgressQueryPort;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.shared.OrderId;
import com.example.aftersale.domain.shared.UserId;
import com.example.aftersale.infrastructure.persistence.entity.LearningProgressEntity;
import com.example.aftersale.infrastructure.persistence.repository.LearningProgressJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

/**
 * 学习进度查询端口实现
 */
@Component
@RequiredArgsConstructor
public class LearningProgressQueryAdapter implements LearningProgressQueryPort {

    private final LearningProgressJpaRepository learningProgressJpaRepository;

    @Override
    public LearningProgress findByOrderId(OrderId orderId, UserId requesterUserId) {
        // 可以根据订单ID查询，不需要额外校验用户（因为订单已经校验过了）
        return learningProgressJpaRepository.findByOrderId(orderId.value())
                .map(this::toDomain)
                .orElse(null);  // 未开始学习返回 null
    }

    /**
     * 将 JPA 实体转换为领域对象
     */
    private LearningProgress toDomain(LearningProgressEntity entity) {
        return new LearningProgress(
                OrderId.of(entity.getOrderId()),
                UserId.of(entity.getUserId()),
                entity.getCourseId(),
                entity.getProgressPercentage() != null ? entity.getProgressPercentage() : BigDecimal.ZERO,
                entity.getTotalVideoDuration() != null ? entity.getTotalVideoDuration() : 0,
                entity.getWatchedDuration() != null ? entity.getWatchedDuration() : 0,
                entity.getLastLearnedAt(),
                entity.getFirstLearnedAt()
        );
    }
}