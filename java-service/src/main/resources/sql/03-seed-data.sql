-- 测试数据插入
USE refund_agent;

-- ============================================
-- 1. 系统配置
-- ============================================
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('APPROVAL_THRESHOLD_AMOUNT', '50000', 'INT', '人工审批金额阈值（分）'),
('MAX_REFUND_DAYS_NO_REASON', '7', 'INT', '无理由退款最大天数'),
('MAX_PROGRESS_PERCENTAGE', '30.00', 'DECIMAL', '最大学习进度百分比限制'),
('ABNORMAL_REFUND_THRESHOLD', '3', 'INT', '异常退款次数阈值'),
('MODEL_COST_LIMIT', '1.0', 'DECIMAL', '单任务模型成本上限（美元）');

-- ============================================
-- 2. 退款规则（RAG 知识库）
-- ============================================
INSERT INTO refund_rules (rule_id, version, scenario, title, content, effective_from, effective_to, risk_level, approval_threshold_amount, max_refund_days, max_progress_percentage, is_active) VALUES
('REFUND-2026-001', 1, 'NO_REASON', '无理由退款规则',
 '用户在购买课程后7天内，且学习进度未超过30%，可申请无理由退款。退款金额为订单实付金额。',
 '2026-01-01', NULL, 'LOW', NULL, 7, 30.00, TRUE),

('REFUND-2026-002', 2, 'DUPLICATE_PURCHASE', '重复购买退款规则',
 '用户在同一课程有多个有效订单时，可申请退还重复购买的订单。需保留最早购买的订单。退款金额为订单实付金额。',
 '2026-01-01', NULL, 'LOW', NULL, NULL, NULL, TRUE),

('REFUND-2026-003', 3, 'COURSE_UNAVAILABLE', '课程无法观看退款规则',
 '课程因技术故障无法正常观看，经核实后可全额退款。需确认课程状态为UNAVAILABLE。退款金额为订单实付金额。',
 '2026-06-01', NULL, 'MEDIUM', 50000, NULL, NULL, TRUE),

('REFUND-2026-004', 1, 'EXCEEDED_PROGRESS', '超出学习进度限制',
 '用户学习进度超过30%后，除课程无法正常播放等特殊情况外，不支持退款。',
 '2026-01-01', NULL, 'HIGH', 50000, NULL, 30.00, TRUE),

('REFUND-2026-005', 1, 'EXPIRED_WINDOW', '超过退款有效期',
 '超过无理由退款有效期（7天）且不符合特殊退款条件（如课程故障）的订单，不支持退款。',
 '2026-01-01', NULL, 'HIGH', NULL, 7, NULL, TRUE),

('REFUND-2026-006', 1, 'PROMOTIONAL_COURSE', '促销课程特殊限制',
 '促销课程购买后不支持无理由退款，仅支持因课程无法正常播放等技术问题导致的退款。',
 '2026-01-01', NULL, 'MEDIUM', 30000, NULL, NULL, TRUE);

-- ============================================
-- 3. 测试用户
-- ============================================
INSERT INTO users (user_id, username, email, phone, abnormal_refund_count) VALUES
('U1001', '张三', 'zhangsan@example.com', '13800138001', 0),
('U1002', '李四', 'lisi@example.com', '13800138002', 1),
('U1003', '王五', 'wangwu@example.com', '13800138003', 0),
('U1004', '赵六', 'zhaoliu@example.com', '13800138004', 3);  -- 异常退款用户

-- ============================================
-- 4. 测试课程
-- ============================================
INSERT INTO courses (course_id, name, price, category, status, is_promotional, unavailable_reason) VALUES
('C2001', 'Java 高级编程', 19900, '编程开发', 'ACTIVE', FALSE, NULL),
('C2002', 'Python 数据分析', 24900, '数据科学', 'ACTIVE', FALSE, NULL),
('C2003', 'React 前端开发', 17900, '前端开发', 'UNAVAILABLE', FALSE, '视频服务故障'),  -- 课程不可用
('C2004', '机器学习入门', 29900, '人工智能', 'ACTIVE', TRUE, NULL),  -- 促销课程
('C2005', 'Spring Boot 实战', 15900, '编程开发', 'ACTIVE', FALSE, NULL);

-- ============================================
-- 5. 测试订单（覆盖各类场景）
-- ============================================
-- 正常订单（可退款）
INSERT INTO orders (order_id, user_id, course_id, amount, status, paid_at, has_refunded) VALUES
('O20260622001', 'U1001', 'C2001', 19900, 'PAID', '2026-06-21 10:00:00', FALSE),  -- 新订单，未学习
('O20260622002', 'U1001', 'C2002', 24900, 'PAID', '2026-06-20 15:30:00', FALSE),  -- 学习进度45%
('O20260622003', 'U1002', 'C2003', 17900, 'PAID', '2026-06-19 09:15:00', FALSE),  -- 课程不可用
('O20260622005', 'U1002', 'C2001', 19900, 'PAID', '2026-06-18 14:20:00', FALSE),  -- 学习进度15%（重复购买检测）

-- 促销课程订单（特殊限制）
('O20260622006', 'U1003', 'C2004', 29900, 'PAID', '2026-06-22 08:00:00', FALSE),  -- 促销课程

-- 已退款订单
('O20260622007', 'U1004', 'C2005', 15900, 'REFUNDED', '2026-06-10 10:00:00', TRUE),  -- 已退款

-- 超过有效期订单
('O20260622008', 'U1001', 'C2005', 15900, 'PAID', '2026-05-01 10:00:00', FALSE),  -- 超过7天

-- 待支付订单
('O20260622009', 'U1003', 'C2001', 19900, 'PENDING', NULL, FALSE);  -- 未支付

-- ============================================
-- 6. 学习进度
-- ============================================
INSERT INTO learning_progress (order_id, user_id, course_id, progress_percentage, total_video_duration, watched_duration, first_learned_at, last_learned_at) VALUES
('O20260622001', 'U1001', 'C2001', 0.00, 3600, 0, NULL, NULL),  -- 未学习
('O20260622002', 'U1001', 'C2002', 45.50, 7200, 3276, '2026-06-20 16:00:00', '2026-06-21 20:00:00'),  -- 超过30%
('O20260622003', 'U1002', 'C2003', 10.00, 5400, 540, '2026-06-19 10:00:00', '2026-06-19 12:00:00'),  -- 课程不可用但学了10%
('O20260622005', 'U1002', 'C2001', 15.00, 3600, 540, '2026-06-18 15:00:00', '2026-06-20 10:00:00'),  -- 重复购买检测
('O20260622006', 'U1003', 'C2004', 5.00, 9000, 450, '2026-06-22 09:00:00', '2026-06-22 11:00:00');  -- 促销课程

-- ============================================
-- 7. 退款历史（用于风险评估）
-- ============================================
INSERT INTO refund_history (user_id, refund_id, order_id, amount, reason_code, is_abnormal, abnormal_type) VALUES
('U1002', 'R001', 'O20260101001', 10000, 'NO_REASON', FALSE, NULL),
('U1004', 'R002', 'O20260201001', 50000, 'NO_REASON', TRUE, 'FREQUENT'),
('U1004', 'R003', 'O20260301001', 30000, 'COURSE_UNAVAILABLE', TRUE, 'FREQUENT'),
('U1004', 'R004', 'O20260401001', 20000, 'NO_REASON', TRUE, 'FREQUENT');