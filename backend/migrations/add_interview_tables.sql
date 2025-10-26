-- 创建面试题表
CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learning_path_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    difficulty VARCHAR(20) DEFAULT 'medium' CHECK(difficulty IN ('easy', 'medium', 'hard')),
    knowledge_points TEXT,  -- SQLite存储JSON为TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_interview_questions_learning_path ON interview_questions(learning_path_id);
CREATE INDEX IF NOT EXISTS idx_interview_questions_category ON interview_questions(category);
CREATE INDEX IF NOT EXISTS idx_interview_questions_difficulty ON interview_questions(difficulty);

-- 创建题目状态表
CREATE TABLE IF NOT EXISTS question_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'not_seen' CHECK(status IN ('not_seen', 'mastered', 'not_mastered')),
    last_reviewed_at TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES interview_questions(id) ON DELETE CASCADE,
    UNIQUE(user_id, question_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_question_statuses_user ON question_statuses(user_id);
CREATE INDEX IF NOT EXISTS idx_question_statuses_question ON question_statuses(question_id);
CREATE INDEX IF NOT EXISTS idx_question_statuses_status ON question_statuses(status);

