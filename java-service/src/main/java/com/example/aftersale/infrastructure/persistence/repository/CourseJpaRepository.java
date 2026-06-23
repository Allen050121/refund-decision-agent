package com.example.aftersale.infrastructure.persistence.repository;

import com.example.aftersale.infrastructure.persistence.entity.CourseEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CourseJpaRepository extends JpaRepository<CourseEntity, Long> {

    Optional<CourseEntity> findByCourseId(String courseId);

    boolean existsByCourseId(String courseId);
}