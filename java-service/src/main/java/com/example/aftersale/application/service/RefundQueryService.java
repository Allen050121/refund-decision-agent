package com.example.aftersale.application.service;

import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.refund.RefundEligibilityResult;

/**
 * 退款查询业务接口
 * 定义业务行为，便于扩展和测试
 */
public interface RefundQueryService {

    /**
     * 查询订单信息
     * 文档工具：get_order(order_id, requester_user_id)
     *
     * @param orderId 订单ID
     * @param requesterUserId 请求用户ID
     * @return 订单领域对象
     */
    Order getOrder(String orderId, String requesterUserId);

    /**
     * 查询学习进度
     * 文档工具：get_learning_progress(order_id, requester_user_id)
     *
     * @param orderId 订单ID
     * @param requesterUserId 请求用户ID
     * @return 学习进度（可能为null表示未开始学习）
     */
    LearningProgress getLearningProgress(String orderId, String requesterUserId);

    /**
     * 查询课程状态
     * 文档工具：get_course_status(course_id)
     *
     * @param courseId 课程ID
     * @return 课程领域对象
     */
    Course getCourseStatus(String courseId);

    /**
     * 检查退款资格
     * 文档工具：check_eligibility(order_id, requester_user_id, reason_code)
     *
     * @param orderId 订单ID
     * @param requesterUserId 请求用户ID
     * @param reasonCodeStr 退款原因码
     * @param abnormalRefundCount 用户异常退款次数
     * @return 退款资格校验结果
     */
    RefundEligibilityResult checkEligibility(String orderId, String requesterUserId,
                                               String reasonCodeStr, int abnormalRefundCount);
}