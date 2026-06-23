package com.example.aftersale.interfaces.controller;

import com.example.aftersale.application.exception.BusinessException;
import com.example.aftersale.application.service.RefundQueryService;
import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.interfaces.dto.CourseStatusResponse;
import com.example.aftersale.interfaces.dto.ErrorResponse;
import com.example.aftersale.interfaces.dto.LearningProgressResponse;
import com.example.aftersale.interfaces.dto.OrderResponse;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 退款查询控制器
 * 提供文档规定的三个只读工具接口
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class RefundQueryController {

    private final RefundQueryService refundQueryService;

    /**
     * 查询订单
     * 文档工具：get_order(order_id, requester_user_id)
     */
    @GetMapping("/orders/{orderId}")
    public ResponseEntity<OrderResponse> getOrder(
            @PathVariable @NotBlank String orderId,
            @RequestParam @NotBlank String requesterUserId) {

        Order order = refundQueryService.getOrder(orderId, requesterUserId);

        OrderResponse response = OrderResponse.builder()
                .orderId(order.getOrderId().value())
                .userId(order.getUserId().value())
                .courseId(order.getCourseId())
                .amount(order.getAmount().getCents())
                .status(order.getStatus().name())
                .hasRefunded(order.isRefunded())
                .paidAt(order.getPaidAt() != null ? order.getPaidAt().toString() : null)
                .maxRefundAmount(order.getMaxRefundAmount().getCents())
                .build();

        return ResponseEntity.ok(response);
    }

    /**
     * 查询学习进度
     * 文档工具：get_learning_progress(order_id, requester_user_id)
     */
    @GetMapping("/learning/{orderId}")
    public ResponseEntity<LearningProgressResponse> getLearningProgress(
            @PathVariable @NotBlank String orderId,
            @RequestParam @NotBlank String requesterUserId) {

        LearningProgress progress = refundQueryService.getLearningProgress(orderId, requesterUserId);

        if (progress == null) {
            return ResponseEntity.ok(LearningProgressResponse.builder()
                    .orderId(orderId)
                    .progressPercentage(0.0)
                    .exceedsLimit(false)
                    .build());
        }

        LearningProgressResponse response = LearningProgressResponse.builder()
                .orderId(progress.getOrderId().value())
                .userId(progress.getUserId().value())
                .courseId(progress.getCourseId())
                .progressPercentage(progress.getProgressPercentage().doubleValue())
                .totalVideoDuration(progress.getTotalVideoDuration())
                .watchedDuration(progress.getWatchedDuration())
                .exceedsLimit(progress.exceedsDefaultLimit())
                .build();

        return ResponseEntity.ok(response);
    }

    /**
     * 查询课程状态
     * 文档工具：get_course_status(course_id)
     */
    @GetMapping("/courses/{courseId}/status")
    public ResponseEntity<CourseStatusResponse> getCourseStatus(
            @PathVariable @NotBlank String courseId) {

        Course course = refundQueryService.getCourseStatus(courseId);

        CourseStatusResponse response = CourseStatusResponse.builder()
                .courseId(course.getCourseId())
                .name(course.getName())
                .status(course.getStatus().name())
                .isAvailable(course.isAvailable())
                .unavailableReason(course.getUnavailableReason())
                .isPromotional(course.isPromotional())
                .build();

        return ResponseEntity.ok(response);
    }

    /**
     * 异常处理
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        ErrorResponse response = ErrorResponse.builder()
                .errorCode(e.getErrorCode().name())
                .message(e.getMessage())
                .build();

        // 根据错误码返回不同的 HTTP 状态
        return switch (e.getErrorCode()) {
            case RESOURCE_NOT_FOUND -> ResponseEntity.status(404).body(response);
            case PERMISSION_DENIED -> ResponseEntity.status(403).body(response);
            case VALIDATION_ERROR -> ResponseEntity.status(400).body(response);
            default -> ResponseEntity.status(500).body(response);
        };
    }
}