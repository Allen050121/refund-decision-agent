package com.example.aftersale.infrastructure.persistence.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 课程 JPA 实体
 */
@Data
@Entity
@Table(name = "courses")
public class CourseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "course_id", unique = true, nullable = false, length = 64)
    private String courseId;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false)
    private Integer price;  // 价格（分）

    @Column(length = 50)
    private String category;

    @Column(nullable = false, length = 20)
    private String status;

    @Column(name = "unavailable_reason", length = 200)
    private String unavailableReason;

    @Column(name = "is_promotional")
    private Boolean isPromotional;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}