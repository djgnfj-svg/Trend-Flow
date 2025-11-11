-- Trend-Flow Database Schema
-- 트렌드 수집 및 AI 분석 시스템

-- ====================================
-- 1. Sources 테이블 - 트렌드 소스 관리
-- ====================================
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,        -- 'github', 'product_hunt', 'google_trends'
    category VARCHAR(50),                     -- 'tech', 'general', 'startup'
    url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 기본 소스 데이터 삽입
INSERT INTO sources (name, category, url, is_active) VALUES
    ('github_trending', 'tech', 'https://github.com/trending', TRUE),
    ('product_hunt', 'startup', 'https://www.producthunt.com/', TRUE),
    ('google_trends_kr', 'general', 'https://trends.google.com/trends/?geo=KR', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ====================================
-- 2. Trends 테이블 - 원본 트렌드 데이터
-- ====================================
CREATE TABLE IF NOT EXISTS trends (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    category VARCHAR(100),                    -- 원본 카테고리 (있는 경우)
    rank INTEGER,                             -- 순위 (있는 경우)
    metadata JSONB,                           -- 추가 정보 (별 개수, 언어, 포크 수 등)
    collected_at TIMESTAMP DEFAULT NOW(),     -- 수집 시각
    collected_date DATE DEFAULT CURRENT_DATE, -- 수집 날짜 (중복 방지용)
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_trend_per_day UNIQUE(source_id, title, collected_date)
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_trends_source_id ON trends(source_id);
CREATE INDEX IF NOT EXISTS idx_trends_collected_at ON trends(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_title ON trends USING gin(to_tsvector('english', title));

-- ====================================
-- 3. Analyzed Trends 테이블 - AI 분석 결과
-- ====================================
CREATE TABLE IF NOT EXISTS analyzed_trends (
    id SERIAL PRIMARY KEY,
    trend_id INTEGER REFERENCES trends(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,                    -- AI 생성 요약
    category VARCHAR(100),                    -- AI가 분류한 카테고리
    problems TEXT[],                          -- 발견된 문제점들
    keywords TEXT[],                          -- 추출된 키워드
    sentiment VARCHAR(20),                    -- 'positive', 'neutral', 'negative'
    importance_score INTEGER CHECK (importance_score >= 1 AND importance_score <= 10),
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_analysis_per_trend UNIQUE(trend_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_analyzed_trends_trend_id ON analyzed_trends(trend_id);
CREATE INDEX IF NOT EXISTS idx_analyzed_trends_importance ON analyzed_trends(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_analyzed_trends_category ON analyzed_trends(category);

-- ====================================
-- 4. Solutions 테이블 - 솔루션 아이디어
-- ====================================
CREATE TABLE IF NOT EXISTS solutions (
    id SERIAL PRIMARY KEY,
    analyzed_trend_id INTEGER REFERENCES analyzed_trends(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    feasibility VARCHAR(20) CHECK (feasibility IN ('high', 'medium', 'low')),
    estimated_effort VARCHAR(20),             -- '1주', '1개월', '3개월' 등
    target_audience TEXT,                     -- 타겟 사용자
    tech_stack TEXT[],                        -- 추천 기술 스택
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_solutions_analyzed_trend_id ON solutions(analyzed_trend_id);
CREATE INDEX IF NOT EXISTS idx_solutions_feasibility ON solutions(feasibility);

-- ====================================
-- 유용한 뷰 (View) 생성
-- ====================================

-- 최신 트렌드 요약 뷰
CREATE OR REPLACE VIEW v_latest_trends AS
SELECT
    t.id,
    t.title,
    t.description,
    t.url,
    s.name as source_name,
    s.category as source_category,
    t.rank,
    t.collected_at,
    at.summary,
    at.importance_score,
    at.category as ai_category,
    at.keywords,
    COUNT(sol.id) as solution_count
FROM trends t
JOIN sources s ON t.source_id = s.id
LEFT JOIN analyzed_trends at ON at.trend_id = t.id
LEFT JOIN solutions sol ON sol.analyzed_trend_id = at.id
GROUP BY t.id, s.name, s.category, at.id
ORDER BY t.collected_at DESC, at.importance_score DESC NULLS LAST;

-- 일별 트렌드 통계 뷰
CREATE OR REPLACE VIEW v_daily_stats AS
SELECT
    DATE(t.collected_at) as date,
    s.name as source_name,
    COUNT(t.id) as trend_count,
    COUNT(at.id) as analyzed_count,
    COUNT(sol.id) as solution_count,
    AVG(at.importance_score) as avg_importance
FROM trends t
JOIN sources s ON t.source_id = s.id
LEFT JOIN analyzed_trends at ON at.trend_id = t.id
LEFT JOIN solutions sol ON sol.analyzed_trend_id = at.id
GROUP BY DATE(t.collected_at), s.name
ORDER BY date DESC;

-- ====================================
-- 함수: 트렌드 중복 체크
-- ====================================
CREATE OR REPLACE FUNCTION check_duplicate_trend(
    p_source_id INTEGER,
    p_title TEXT,
    p_collected_date DATE
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM trends
        WHERE source_id = p_source_id
          AND title = p_title
          AND DATE(collected_at) = p_collected_date
    );
END;
$$ LANGUAGE plpgsql;

-- ====================================
-- 트리거: updated_at 자동 업데이트
-- ====================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ====================================
-- 권한 설정 (Airflow 사용자용)
-- ====================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO airflow;

-- ====================================
-- 완료 메시지
-- ====================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Trend-Flow Database Schema Created!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables: sources, trends, analyzed_trends, solutions';
    RAISE NOTICE 'Views: v_latest_trends, v_daily_stats';
    RAISE NOTICE 'Ready to collect and analyze trends!';
    RAISE NOTICE '========================================';
END $$;
