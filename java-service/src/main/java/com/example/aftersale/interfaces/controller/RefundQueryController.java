package com.example.aftersale.interfaces.controller;

import com.example.aftersale.application.service.RefundQueryService;
import com.example.aftersale.domain.course.Course;
import com.example.aftersale.domain.learning.LearningProgress;
import com.example.aftersale.domain.order.Order;
import com.example.aftersale.domain.refund.RefundEligibilityResult;
import com.example.aftersale.interfaces.dto.CourseStatusResponse;
import com.example.aftersale.interfaces.dto.LearningProgressResponse;
import com.example.aftersale.interfaces.dto.OrderResponse;
import com.example.aftersale.interfaces.dto.RefundEligibilityRequest;
import com.example.aftersale.interfaces.dto.RefundEligibilityResponse;
import com.example.aftersale.interfaces.dto.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 退款查询控制器
 * 提供文档规定的三个只读工具接口
 */
@Slf4j
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
    @Operation(summary = "查询订单", description = "根据订单 ID 查询订单信息，需要验证用户归属")
    @GetMapping("/orders/{orderId}")
    public Result<OrderResponse> getOrder(
            @Parameter(description = "订单 ID") @PathVariable @NotBlank String orderId,
            @Parameter(description = "请求用户 ID") @RequestParam @NotBlank String requesterUserId) {

        log.info(" 查询订单 | orderId={} | requesterUserId={}", orderId, requesterUserId);

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

        log.info("   返回：{}", response);

        return Result.success(response);
    }

    /**
     * 查询学习进度
     * 文档工具：get_learning_progress(order_id, requester_user_id)
     */
    @Operation(summary = "查询学习进度", description = "查询订单关联的学习进度")
    @GetMapping("/learning/{orderId}")
    public Result<LearningProgressResponse> getLearningProgress(
            @Parameter(description = "订单 ID") @PathVariable @NotBlank String orderId,
            @Parameter(description = "请求用户 ID") @RequestParam @NotBlank String requesterUserId) {

        log.info(" 查询学习进度 | orderId={} | requesterUserId={}", orderId, requesterUserId);

        LearningProgress progress = refundQueryService.getLearningProgress(orderId, requesterUserId);

        if (progress == null) {
            LearningProgressResponse response = LearningProgressResponse.builder()
                    .orderId(orderId)
                    .progressPercentage(0.0)
                    .exceedsLimit(false)
                    .build();
            log.info("   返回：{}", response);
            return Result.success(response);
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

        log.info("   返回：{}", response);

        return Result.success(response);
    }

    /**
     * 查询课程状态
     * 文档工具：get_course_status(course_id)
     */
    @Operation(summary = "查询课程状态", description = "查询课程的可用状态信息")
    @GetMapping("/courses/{courseId}/status")
    public Result<CourseStatusResponse> getCourseStatus(
            @Parameter(description = "课程 ID") @PathVariable @NotBlank String courseId) {

        log.info(" 查询课程状态 | courseId={}", courseId);

        Course course = refundQueryService.getCourseStatus(courseId);

        CourseStatusResponse response = CourseStatusResponse.builder()
                .courseId(course.getCourseId())
                .name(course.getName())
                .status(course.getStatus().name())
                .isAvailable(course.isAvailable())
                .unavailableReason(course.getUnavailableReason())
                .isPromotional(course.isPromotional())
                .build();

        log.info("   返回：{}", response);

        return Result.success(response);
    }

    /**
     * 检查退款资格
     * 文档工具：check_eligibility(order_id, requester_user_id, reason_code)
     */
    @Operation(summary = "退款资格校验", description = "根据订单、用户和退款原因计算确定性退款资格")
    @PostMapping("/refund/check-eligibility")
    public Result<RefundEligibilityResponse> checkEligibility(
            @Valid @RequestBody RefundEligibilityRequest request) {

        log.info(" 检查退款资格 | orderId={} | requesterUserId={} | reasonCode={}",
                request.getOrderId(), request.getRequesterUserId(), request.getReasonCode());

        RefundEligibilityResult result = refundQueryService.checkEligibility(
                request.getOrderId(),
                request.getRequesterUserId(),
                request.getReasonCode(),
                0
        );

        RefundEligibilityResponse response = RefundEligibilityResponse.builder()
                .eligible(result.isEligible())
                .decisionCode(result.getDecisionCode())
                .maxRefundAmount(result.getMaxRefundAmount().getCents())
                .approvalRequired(result.isApprovalRequired())
                .approvalReason(result.getApprovalReason())
                .evidence(result.getEvidence())
                .ruleCitation(result.getAppliedRule() != null ? result.getAppliedRule().citation() : null)
                .riskLevel(result.getRiskLevel())
                .build();

        log.info("   返回：{}", response);

        return Result.success(response);
    }
}
