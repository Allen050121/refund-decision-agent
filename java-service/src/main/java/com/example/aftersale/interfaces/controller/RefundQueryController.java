package com.example.aftersale.interfaces.controller;

import com.example.aftersale.application.service.RefundQueryService;
import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.interfaces.dto.CourseStatusResponse;
import com.example.aftersale.interfaces.dto.LearningProgressResponse;
import com.example.aftersale.interfaces.dto.OrderResponse;
import com.example.aftersale.interfaces.dto.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 退款查询控制器
 * 提供文档规定的三个只读工具接口
 */
@Validated
@Tag(name = "退款查询", description = "退款判断所需的业务数据查询接口")
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class RefundQueryController {

    private final RefundQueryService refundQueryService;

    /**
     * 查询订单
     * 文档工具：get_order(order_id, requester_user_id)
     */
    @Operation(summary = "查询订单", description = "根据订单ID查询订单信息，需要验证用户归属")
    @GetMapping("/orders/{orderId}")
    public Result<OrderResponse> getOrder(
            @Parameter(description = "订单ID") @PathVariable @NotBlank String orderId,
            @Parameter(description = "请求用户ID") @RequestParam @NotBlank String requesterUserId) {

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

        return Result.success(response);
    }

    /**
     * 查询学习进度
     * 文档工具：get_learning_progress(order_id, requester_user_id)
     */
    @Operation(summary = "查询学习进度", description = "查询订单关联的学习进度")
    @GetMapping("/learning/{orderId}")
    public Result<LearningProgressResponse> getLearningProgress(
            @Parameter(description = "订单ID") @PathVariable @NotBlank String orderId,
            @Parameter(description = "请求用户ID") @RequestParam @NotBlank String requesterUserId) {

        LearningProgress progress = refundQueryService.getLearningProgress(orderId, requesterUserId);

        if (progress == null) {
            return Result.success(LearningProgressResponse.builder()
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

        return Result.success(response);
    }

    /**
     * 查询课程状态
     * 文档工具：get_course_status(course_id)
     */
    @Operation(summary = "查询课程状态", description = "查询课程的可用状态信息")
    @GetMapping("/courses/{courseId}/status")
    public Result<CourseStatusResponse> getCourseStatus(
            @Parameter(description = "课程ID") @PathVariable @NotBlank String courseId) {

        Course course = refundQueryService.getCourseStatus(courseId);

        CourseStatusResponse response = CourseStatusResponse.builder()
                .courseId(course.getCourseId())
                .name(course.getName())
                .status(course.getStatus().name())
                .isAvailable(course.isAvailable())
                .unavailableReason(course.getUnavailableReason())
                .isPromotional(course.isPromotional())
                .build();

        return Result.success(response);
    }
}