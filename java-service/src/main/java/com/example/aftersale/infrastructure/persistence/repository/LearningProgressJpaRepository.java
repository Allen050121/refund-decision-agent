package com.example.aftersale.infrastructure.persistence.repository;

import com.example.aftersale.infrastructure.persistence.entity.LearningProgressEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface LearningProgressJpaRepository extends JpaRepository<LearningProgressEntity, Long> {

    Optional<LearningProgressEntity> findByOrderId(String orderId);

    Optional<LearningProgressEntity> findByOrderIdAndUserId(String orderId, String userId);
}