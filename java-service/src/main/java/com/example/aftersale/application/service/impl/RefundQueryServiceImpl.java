package com.example.aftersale.application.service.impl;

import com.example.aftersale.application.exception.PermissionDeniedException;
import com.example.aftersale.application.exception.ResourceNotFoundException;
import com.example.aftersale.application.port.CourseQueryPort;
import com.example.aftersale.application.port.LearningProgressQueryPort;
import com.example.aftersale.application.port.OrderQueryPort;
import com.example.aftersale.application.service.RefundQueryService;
import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.refund.RefundEligibilityResult;
import com.example.aftersale.domain.refund.RefundEligibilityService;
import com.example.aftersale.domain.shared.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * 退款查询业务实现
 * 实现业务接口，协调各查询端口完成退款判断
 */
@Service
@RequiredArgsConstructor
public class RefundQueryServiceImpl implements RefundQueryService {

    private final OrderQueryPort orderQueryPort;
    private final LearningProgressQueryPort learningProgressQueryPort;
    private final CourseQueryPort courseQueryPort;
    private final RefundEligibilityService refundEligibilityService;

    /**
     * 查询订单信息
     * 文档工具：get_order(order_id, requester_user_id)
     */
    @Override
    public Order getOrder(String orderId, String requesterUserId) {
        OrderId orderIdVo = OrderId.of(orderId);
        UserId userIdVo = UserId.of(requesterUserId);

        try {
            return orderQueryPort.findById(orderIdVo, userIdVo);
        } catch (ResourceNotFoundException e) {
            throw new ResourceNotFoundException("订单", orderId);
        } catch (PermissionDeniedException e) {
            throw new PermissionDeniedException("订单", orderId, requesterUserId);
        }
    }

    /**
     * 查询学习进度
     * 文档工具：get_learning_progress(order_id, requester_user_id)
     */
    @Override
    public LearningProgress getLearningProgress(String orderId, String requesterUserId) {
        OrderId orderIdVo = OrderId.of(orderId);
        UserId userIdVo = UserId.of(requesterUserId);

        return learningProgressQueryPort.findByOrderId(orderIdVo, userIdVo);
    }

    /**
     * 查询课程状态
     * 文档工具：get_course_status(course_id)
     */
    @Override
    public Course getCourseStatus(String courseId) {
        try {
            return courseQueryPort.findById(courseId);
        } catch (ResourceNotFoundException e) {
            throw new ResourceNotFoundException("课程", courseId);
        }
    }

    /**
     * 检查退款资格
     * 文档工具：check_eligibility(order_id, requester_user_id, reason_code)
     */
    @Override
    public RefundEligibilityResult checkEligibility(
            String orderId,
            String requesterUserId,
            String reasonCodeStr,
            int abnormalRefundCount) {

        // 获取业务数据
        Order order = getOrder(orderId, requesterUserId);
        LearningProgress progress = getLearningProgress(orderId, requesterUserId);
        Course course = getCourseStatus(order.getCourseId());

        // 解析原因码
        ReasonCode reasonCode = parseReasonCode(reasonCodeStr);

        // 调用领域服务进行资格校验
        return refundEligibilityService.checkEligibility(
                order, progress, course, reasonCode,
                UserId.of(requesterUserId), abnormalRefundCount,
                LocalDateTime.now()
        );
    }

    /**
     * 解析原因码
     */
    private ReasonCode parseReasonCode(String reasonCodeStr) {
        if (reasonCodeStr == null || reasonCodeStr.isBlank()) {
            return ReasonCode.GENERAL;
        }
        try {
            return ReasonCode.valueOf(reasonCodeStr);
        } catch (IllegalArgumentException e) {
            return ReasonCode.GENERAL;
        }
    }
}