USE refund_agent;

-- 插入测试用户
INSERT INTO users (user_id, username, email, phone) VALUES
('U1001', '张三', 'zhangsan@example.com', '13800138001'),
('U1002', '李四', 'lisi@example.com', '13800138002'),
('U1003', '王五', 'wangwu@example.com', '13800138003');

-- 插入测试课程
INSERT INTO courses (course_id, name, price, category, status) VALUES
('C2001', 'Java 高级编程', 19900, '编程开发', 'ACTIVE'),
('C2002', 'Python 数据分析', 24900, '数据科学', 'ACTIVE'),
('C2003', 'React 前端开发', 17900, '前端开发', 'ACTIVE'),
('C2004', '机器学习入门', 29900, '人工智能', 'ACTIVE');

-- 插入测试订单
INSERT INTO orders (order_id, user_id, course_id, amount, status, paid_at) VALUES
('O20260622001', 'U1001', 'C2001', 19900, 'PAID', '2026-06-21 10:00:00'),
('O20260622002', 'U1001', 'C2002', 24900, 'PAID', '2026-06-20 15:30:00'),
('O20260622003', 'U1002', 'C2003', 17900, 'PAID', '2026-06-19 09:15:00'),
('O20260622004', 'U1003', 'C2004', 29900, 'PENDING', NULL),
('O20260622005', 'U1002', 'C2001', 19900, 'PAID', '2026-06-18 14:20:00');

-- 插入学习进度
INSERT INTO learning_progress (order_id, user_id, course_id, progress_percentage, last_learned_at) VALUES
('O20260622001', 'U1001', 'C2001', 0.00, NULL),
('O20260622002', 'U1001', 'C2002', 45.50, '2026-06-21 20:00:00'),
('O20260622003', 'U1002', 'C2003', 80.00, '2026-06-21 18:30:00'),
('O20260622005', 'U1002', 'C2001', 15.00, '2026-06-20 10:00:00');
