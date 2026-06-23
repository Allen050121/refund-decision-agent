package com.example.aftersale.infrastructure.persistence.adapter;

import com.example.aftersale.application.exception.ResourceNotFoundException;
import com.example.aftersale.application.port.CourseQueryPort;
import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.shared.CourseStatus;
import com.example.aftersale.domain.shared.Money;
import com.example.aftersale.infrastructure.persistence.entity.CourseEntity;
import com.example.aftersale.infrastructure.persistence.repository.CourseJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * 课程查询端口实现
 */
@Component
@RequiredArgsConstructor
public class CourseQueryAdapter implements CourseQueryPort {

    private final CourseJpaRepository courseJpaRepository;

    @Override
    public Course findById(String courseId) {
        CourseEntity entity = courseJpaRepository.findByCourseId(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("课程", courseId));

        return toDomain(entity);
    }

    @Override
    public boolean isAvailable(String courseId) {
        return courseJpaRepository.findByCourseId(courseId)
                .map(entity -> "ACTIVE".equals(entity.getStatus()))
                .orElse(false);
    }

    /**
     * 将 JPA 实体转换为领域对象
     */
    private Course toDomain(CourseEntity entity) {
        return new Course(
                entity.getCourseId(),
                entity.getName(),
                Money.ofCents(entity.getPrice()),
                entity.getCategory(),
                CourseStatus.valueOf(entity.getStatus()),
                entity.getUnavailableReason(),
                entity.getIsPromotional() != null ? entity.getIsPromotional() : false
        );
    }
}