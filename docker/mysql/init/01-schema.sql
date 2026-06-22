-- 创建数据库和用户
CREATE DATABASE IF NOT EXISTS refund_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'refund_user'@'%' IDENTIFIED BY 'refund_pass';
GRANT ALL PRIVILEGES ON refund_agent.* TO 'refund_user'@'%';
FLUSH PRIVILEGES;

USE refund_agent;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64) NOT NULL UNIQUE COMMENT '用户业务ID',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    email VARCHAR(150) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 课程表
CREATE TABLE IF NOT EXISTS courses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(64) NOT NULL UNIQUE COMMENT '课程业务ID',
    name VARCHAR(200) NOT NULL COMMENT '课程名称',
    price INT NOT NULL COMMENT '价格（分）',
    category VARCHAR(50) COMMENT '分类',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(64) NOT NULL UNIQUE COMMENT '订单业务ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    course_id VARCHAR(64) NOT NULL COMMENT '课程ID',
    amount INT NOT NULL COMMENT '金额（分）',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, PAID, REFUNDED, CANCELLED',
    paid_at DATETIME COMMENT '支付时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学习进度表
CREATE TABLE IF NOT EXISTS learning_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(64) NOT NULL COMMENT '订单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    course_id VARCHAR(64) NOT NULL COMMENT '课程ID',
    progress_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '学习进度百分比',
    last_learned_at DATETIME COMMENT '最后学习时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_order_user (order_id, user_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 工单表
CREATE TABLE IF NOT EXISTS support_tickets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id VARCHAR(64) NOT NULL UNIQUE COMMENT '工单业务ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    order_id VARCHAR(64) COMMENT '订单ID',
    content TEXT NOT NULL COMMENT '工单内容',
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT '状态: OPEN, PROCESSING, RESOLVED, CLOSED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Agent 任务表
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(64) NOT NULL UNIQUE COMMENT '任务业务ID',
    ticket_id VARCHAR(64) NOT NULL COMMENT '工单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, PROCESSING, COMPLETED, FAILED, WAITING_APPROVAL',
    intent VARCHAR(50) COMMENT '意图类型',
    reason_code VARCHAR(50) COMMENT '原因代码',
    decision VARCHAR(50) COMMENT '决策结果',
    suggested_amount INT COMMENT '建议退款金额（分）',
    confidence DECIMAL(3,2) COMMENT '置信度',
    error_message TEXT COMMENT '错误信息',
    token_usage INT COMMENT 'Token使用量',
    cost DECIMAL(10,4) COMMENT '成本（美元）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间',
    INDEX idx_task_id (task_id),
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 退款申请表
CREATE TABLE IF NOT EXISTS refund_requests (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    refund_id VARCHAR(64) NOT NULL UNIQUE COMMENT '退款业务ID',
    order_id VARCHAR(64) NOT NULL COMMENT '订单ID',
    user_id VARCHAR(64) NOT NULL COMMENT '用户ID',
    task_id VARCHAR(64) COMMENT 'Agent任务ID',
    reason_code VARCHAR(50) NOT NULL COMMENT '退款原因',
    amount INT NOT NULL COMMENT '申请金额（分）',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, APPROVED, REJECTED, COMPLETED',
    approval_required BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approved_by VARCHAR(64) COMMENT '审批人',
    approved_at DATETIME COMMENT '审批时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_refund_id (refund_id),
    INDEX idx_order_id (order_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Outbox 事件表
CREATE TABLE IF NOT EXISTS outbox_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_id VARCHAR(64) NOT NULL UNIQUE COMMENT '事件ID',
    aggregate_type VARCHAR(50) NOT NULL COMMENT '聚合根类型',
    aggregate_id VARCHAR(64) NOT NULL COMMENT '聚合根ID',
    event_type VARCHAR(50) NOT NULL COMMENT '事件类型',
    payload JSON NOT NULL COMMENT '事件数据',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING, SENT, FAILED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME COMMENT '发送时间',
    INDEX idx_event_id (event_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
