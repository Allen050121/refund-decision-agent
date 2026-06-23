package com.example.aftersale.application.port;

import com.example.aftersale.domain.course.Course;

/**
 * 课程查询端口
 */
public interface CourseQueryPort {

    /**
     * 查询课程状态
     *
     * @param courseId 课程ID
     * @return 课程领域对象
     * @throws CourseNotFoundException 课程不存在
     */
    Course findById(String courseId);

    /**
     * 检查课程是否可用
     */
    boolean isAvailable(String courseId);
}