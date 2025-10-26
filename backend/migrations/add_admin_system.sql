-- 添加管理系统相关表和字段
-- 执行时间：2025-10-26

-- 1. 扩展users表
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
ALTER TABLE users ADD COLUMN last_login_at DATETIME;

-- 2. 创建system_configs表
CREATE TABLE IF NOT EXISTS system_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description VARCHAR(500),
    category VARCHAR(50) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_configs_key ON system_configs(key);
CREATE INDEX idx_system_configs_category ON system_configs(category);

-- 3. 创建operation_logs表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER,
    details JSON,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

CREATE INDEX idx_operation_logs_admin_id ON operation_logs(admin_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);

-- 4. 插入默认系统配置
INSERT INTO system_configs (key, value, description, category) VALUES
('openai_api_key', '""', 'OpenAI API密钥', 'api_keys'),
('openai_api_base', '"https://api.qingyuntop.top/v1"', 'OpenAI API基础URL', 'api_keys'),
('n8n_webhook_url', '""', 'n8n Webhook URL', 'n8n'),
('n8n_api_key', '""', 'n8n API密钥', 'n8n'),
('system_name', '"职途伴侣"', '系统名称', 'system'),
('max_learning_paths_per_user', '10', '每个用户最大学习路线数', 'system');

-- 5. 创建管理员账号（密码：admin123，需要在Python中用bcrypt加密）
-- 这一步在Python代码中执行，确保密码正确加密

