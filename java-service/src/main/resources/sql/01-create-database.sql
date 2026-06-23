-- 创建数据库
CREATE DATABASE IF NOT EXISTS refund_agent
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权（可选，如果需要单独用户）
-- CREATE USER IF NOT EXISTS 'refund_user'@'%' IDENTIFIED BY 'refund_pass';
-- GRANT ALL PRIVILEGES ON refund_agent.* TO 'refund_user'@'%';
-- FLUSH PRIVILEGES;