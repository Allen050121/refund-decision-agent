-- 创建数据库
CREATE DATABASE IF NOT EXISTS refund_agent
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE refund_agent;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64) NOT NULL UNIQUE COMMENT '用户业务ID',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    email VARCHAR(150) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    abnormal_refund_count INT NOT NULL DEFAULT 0 COMMENT '异常退款次数（用于风险评估）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. 课程表
-- ============================================
-- 文档要求：课程状态查询 get_course_status(course_id)
-- 需要跟踪课程是否可用
CREATE TABLE IF NOT EXISTS courses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(64) NOT NULL UNIQUE COMMENT '课程业务ID',
    name VARCHAR(200) NOT NULL COMMENT '课程名称',
    price INT NOT NULL COMMENT '价格（分）- 禁止浮点数',
    category VARCHAR(50) COMMENT '分类',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE, UNAVAILABLE',
    unavailable_reason VARCHAR(200) COMMENT '不可用原因（用于退款判断）',
    is_promotional BOOLEAN DEFAULT FALSE COMMENT '是否促销课程（有特殊退款限制）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. 订单表
-- ============================================
-- 文档要求：订单归属校验、订单状态
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(64) NOT NULL UNIQUE COMMENT '订单业务ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    course_id VARCHAR(64) NOT NULL COMMENT '课程ID',
    amount INT NOT NULL COMMENT '金额（分）- 禁止浮点数',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, PAID, REFUNDED, CANCELLED',
    paid_at DATETIME COMMENT '支付时间',
    refunded_at DATETIME COMMENT '退款完成时间',
    refund_amount INT COMMENT '已退款金额（分）',
    has_refunded BOOLEAN DEFAULT FALSE COMMENT '是否已退款（用于退款历史校验）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_course_user (course_id, user_id)  -- 用于重复购买检测
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. 学习进度表
-- ============================================
-- 文档要求：学习进度限制校验
CREATE TABLE IF NOT EXISTS learning_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(64) NOT NULL COMMENT '订单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    course_id VARCHAR(64) NOT NULL COMMENT '课程ID',
    progress_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '学习进度百分比',
    total_video_duration INT DEFAULT 0 COMMENT '总视频时长（秒）',
    watched_duration INT DEFAULT 0 COMMENT '已观看时长（秒）',
    last_learned_at DATETIME COMMENT '最后学习时间',
    first_learned_at DATETIME COMMENT '首次学习时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_order_user (order_id, user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_progress (progress_percentage)  -- 用于进度限制查询
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. 退款规则表（RAG 知识库元数据）
-- ============================================
-- 文档要求：规则必须有 ruleId, version, effectiveFrom, effectiveTo, scenario, riskLevel
CREATE TABLE IF NOT EXISTS refund_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_id VARCHAR(64) NOT NULL COMMENT '规则ID，如 REFUND-2026-003',
    version INT NOT NULL DEFAULT 1 COMMENT '规则版本',
    scenario VARCHAR(50) NOT NULL COMMENT '适用场景: COURSE_UNAVAILABLE, DUPLICATE_PURCHASE, NO_REASON 等',
    title VARCHAR(200) NOT NULL COMMENT '规则标题',
    content TEXT NOT NULL COMMENT '规则原文内容',
    effective_from DATE NOT NULL COMMENT '生效日期',
    effective_to DATE COMMENT '失效日期（NULL 表示持续生效）',
    risk_level VARCHAR(20) NOT NULL DEFAULT 'LOW' COMMENT '风险等级: LOW, MEDIUM, HIGH',
    approval_threshold_amount INT COMMENT '需要审批的金额阈值（分）',
    max_refund_days INT COMMENT '最大退款天数',
    max_progress_percentage DECIMAL(5,2) COMMENT '最大学习进度限制',
    content_hash VARCHAR(64) COMMENT '内容哈希，用于变更检测',
    source VARCHAR(100) COMMENT '规则来源',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否当前激活版本',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_verified_at DATETIME COMMENT '最后验证时间',
    UNIQUE KEY uk_rule_version (rule_id, version),
    INDEX idx_scenario (scenario),
    INDEX idx_effective (effective_from, effective_to),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 6. 系统配置表
-- ============================================
-- 文档要求：人工审批金额阈值等配置
CREATE TABLE IF NOT EXISTS system_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value VARCHAR(500) NOT NULL COMMENT '配置值',
    config_type VARCHAR(20) NOT NULL DEFAULT 'STRING' COMMENT '类型: STRING, INT, DECIMAL, BOOLEAN',
    description VARCHAR(200) COMMENT '配置说明',
    effective_from DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生效时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 7. 工单表
-- ============================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id VARCHAR(64) NOT NULL UNIQUE COMMENT '工单业务ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    order_id VARCHAR(64) COMMENT '订单ID',
    content TEXT NOT NULL COMMENT '工单内容',
    intent VARCHAR(50) COMMENT '意图: REFUND_REQUEST, GENERAL_INQUIRY 等',
    reason_code VARCHAR(50) COMMENT '原因码: COURSE_UNAVAILABLE 等',
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT '状态: OPEN, PROCESSING, RESOLVED, CLOSED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 8. Agent 任务表
-- ============================================
-- 文档要求的状态定义：task_id, user_id, intent, reason_code, order_id, order_snapshot,
-- learning_progress, retrieved_rules, eligibility_result, decision, approval, errors, budget
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(64) NOT NULL UNIQUE COMMENT '任务业务ID',
    ticket_id VARCHAR(64) NOT NULL COMMENT '工单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    order_id VARCHAR(64) COMMENT '订单ID',

    -- 状态与意图
    intent VARCHAR(50) COMMENT '意图类型',
    reason_code VARCHAR(50) COMMENT '原因代码',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, PROCESSING, COMPLETED, FAILED, WAITING_APPROVAL',

    -- 业务快照（用于审计）
    order_snapshot JSON COMMENT '订单信息快照',
    learning_progress_snapshot JSON COMMENT '学习进度快照',
    retrieved_rules JSON COMMENT '检索到的规则列表',
    eligibility_result JSON COMMENT '资格校验结果',

    -- 决策结果
    decision VARCHAR(50) COMMENT '决策: REFUND_RECOMMENDED, REFUND_REJECTED, NEED_MORE_INFORMATION 等',
    decision_code VARCHAR(50) COMMENT '决策代码: COURSE_SERVICE_FAILURE 等',
    suggested_amount INT COMMENT '建议退款金额（分）',
    confidence DECIMAL(3,2) COMMENT '置信度',
    rule_citations JSON COMMENT '规则引用列表，如 ["REFUND-2026-003@v3"]',
    warnings JSON COMMENT '警告信息列表',

    -- 审批信息
    approval_required BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approval_status VARCHAR(20) COMMENT '审批状态: PENDING, APPROVED, REJECTED',
    approved_by VARCHAR(64) COMMENT '审批人',
    approved_at DATETIME COMMENT '审批时间',
    approval_amount INT COMMENT '审批通过的金额（分）',

    -- 错误与追踪
    error_type VARCHAR(50) COMMENT '错误类型: VALIDATION_ERROR, PERMISSION_DENIED 等',
    error_message TEXT COMMENT '错误信息',

    -- Token 与成本（可观测性）
    token_input INT COMMENT '输入Token数',
    token_output INT COMMENT '输出Token数',
    token_total INT COMMENT '总Token数',
    model_cost DECIMAL(10,4) COMMENT '模型成本（美元）',
    model_name VARCHAR(50) COMMENT '使用的模型',

    -- 时间追踪
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间',

    INDEX idx_task_id (task_id),
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_decision (decision)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 9. 退款申请表
-- ============================================
-- 文档要求：退款幂等校验
CREATE TABLE IF NOT EXISTS refund_requests (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    refund_id VARCHAR(64) NOT NULL UNIQUE COMMENT '退款业务ID',
    order_id VARCHAR(64) NOT NULL COMMENT '订单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    task_id VARCHAR(64) COMMENT 'Agent任务ID',
    idempotency_key VARCHAR(64) NOT NULL UNIQUE COMMENT '幂等键（防止重复退款）',

    reason_code VARCHAR(50) NOT NULL COMMENT '退款原因',
    requested_amount INT NOT NULL COMMENT '申请金额（分）',
    approved_amount INT COMMENT '批准金额（分）',
    max_eligible_amount INT COMMENT '最大可退金额（分）- 来自Java校验',

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, APPROVED, REJECTED, COMPLETED',
    approval_required BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',

    -- 审批信息
    approved_by VARCHAR(64) COMMENT '审批人',
    approved_at DATETIME COMMENT '审批时间',
    rejection_reason VARCHAR(200) COMMENT '拒绝原因',

    -- 规则引用
    applied_rule_id VARCHAR(64) COMMENT '应用的规则ID',
    applied_rule_version INT COMMENT '应用的规则版本',

    -- 时间追踪
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间',

    INDEX idx_refund_id (refund_id),
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_idempotency_key (idempotency_key),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 10. Outbox 事件表（可靠消息投递）
-- ============================================
CREATE TABLE IF NOT EXISTS outbox_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_id VARCHAR(64) NOT NULL UNIQUE COMMENT '事件ID',
    aggregate_type VARCHAR(50) NOT NULL COMMENT '聚合根类型: AgentTask, RefundRequest 等',
    aggregate_id VARCHAR(64) NOT NULL COMMENT '聚合根ID',
    event_type VARCHAR(50) NOT NULL COMMENT '事件类型: TASK_CREATED, TASK_COMPLETED 等',
    payload JSON NOT NULL COMMENT '事件数据',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, SENT, FAILED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME COMMENT '发送时间',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    INDEX idx_event_id (event_id),
    INDEX idx_aggregate (aggregate_type, aggregate_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 11. 退款历史表（用于风险评估）
-- ============================================
-- 文档要求：用户存在多次异常退款记录
CREATE TABLE IF NOT EXISTS refund_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    refund_id VARCHAR(64) NOT NULL COMMENT '退款ID',
    order_id VARCHAR(64) NOT NULL COMMENT '订单ID',
    amount INT NOT NULL COMMENT '退款金额（分）',
    reason_code VARCHAR(50) NOT NULL COMMENT '退款原因',
    is_abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常退款',
    abnormal_type VARCHAR(50) COMMENT '异常类型: FREQUENT, HIGH_AMOUNT, SUSPICIOUS 等',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_abnormal (is_abnormal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;