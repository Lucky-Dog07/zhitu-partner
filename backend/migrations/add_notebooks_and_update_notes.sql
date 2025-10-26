-- 笔记系统数据库迁移脚本
-- 创建 notebooks 表和更新 notes 表

-- 1. 创建 notebooks 表
CREATE TABLE IF NOT EXISTS notebooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    icon VARCHAR(50) DEFAULT '📚',
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_notebooks_user_id ON notebooks(user_id);
CREATE INDEX IF NOT EXISTS idx_notebooks_is_default ON notebooks(is_default);

-- 3. 为 notes 表添加新字段
ALTER TABLE notes ADD COLUMN notebook_id INTEGER;
ALTER TABLE notes ADD COLUMN learning_path_id INTEGER;
ALTER TABLE notes ADD COLUMN editor_mode VARCHAR(20) DEFAULT 'markdown';

-- 4. 为所有现有用户创建默认笔记本
INSERT INTO notebooks (user_id, name, description, icon, is_default)
SELECT DISTINCT user_id, '面试笔记', '记录面试题目和解析', '📚', 1
FROM users
WHERE user_id NOT IN (SELECT user_id FROM notebooks WHERE name = '面试笔记');

INSERT INTO notebooks (user_id, name, description, icon, is_default)
SELECT DISTINCT user_id, '错题本', '记录错题和薄弱知识点', '📝', 1
FROM users
WHERE user_id NOT IN (SELECT user_id FROM notebooks WHERE name = '错题本');

INSERT INTO notebooks (user_id, name, description, icon, is_default)
SELECT DISTINCT user_id, '学习笔记', '记录学习路线和知识点', '📖', 1
FROM users
WHERE user_id NOT IN (SELECT user_id FROM notebooks WHERE name = '学习笔记');

INSERT INTO notebooks (user_id, name, description, icon, is_default)
SELECT DISTINCT user_id, '日常笔记', '记录日常想法和总结', '📅', 1
FROM users
WHERE user_id NOT IN (SELECT user_id FROM notebooks WHERE name = '日常笔记');

-- 5. 将现有笔记关联到默认的"日常笔记"笔记本
UPDATE notes
SET notebook_id = (
    SELECT id FROM notebooks
    WHERE notebooks.user_id = notes.user_id
    AND notebooks.name = '日常笔记'
    LIMIT 1
)
WHERE notebook_id IS NULL;

