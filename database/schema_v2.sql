-- Pain Point Finder Database Schema V2
-- SaaS/Micro Service 아이디어 발굴 시스템

-- ====================================
-- 1. Sources 테이블 - 데이터 소스 관리
-- ====================================
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,        -- 'product_hunt', 'reddit', 'indie_hackers'
    category VARCHAR(50),                     -- 'product', 'community', 'maker'
    url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_collected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 기본 소스 데이터
INSERT INTO sources (name, category, url, is_active) VALUES
    ('product_hunt', 'product', 'https://www.producthunt.com/', TRUE),
    ('reddit_sideproject', 'community', 'https://reddit.com/r/SideProject', TRUE),
    ('reddit_entrepreneur', 'community', 'https://reddit.com/r/Entrepreneur', TRUE),
    ('reddit_startups', 'community', 'https://reddit.com/r/startups', TRUE),
    ('reddit_saas', 'community', 'https://reddit.com/r/SaaS', TRUE),
    ('indie_hackers', 'maker', 'https://www.indiehackers.com/', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ====================================
-- 2. Raw Content 테이블 - 원본 데이터
-- ====================================
CREATE TABLE IF NOT EXISTS raw_contents (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    content_type VARCHAR(50),                 -- 'post', 'comment', 'product'
    title TEXT,
    body TEXT,                                -- 본문
    author VARCHAR(255),
    url TEXT,
    external_id VARCHAR(255),                 -- 소스별 고유 ID
    metadata JSONB,                           -- 추가 정보 (votes, comments, etc.)
    collected_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_content UNIQUE(source_id, external_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_raw_contents_source ON raw_contents(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_contents_collected ON raw_contents(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_contents_type ON raw_contents(content_type);

-- ====================================
-- 3. Pain Points 테이블 - 추출된 문제점
-- ====================================
CREATE TABLE IF NOT EXISTS pain_points (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES raw_contents(id) ON DELETE CASCADE,

    -- Pain Point 상세 정보
    problem_statement TEXT NOT NULL,          -- 문제 설명 (1-2문장)
    problem_detail TEXT,                      -- 상세 설명
    affected_users TEXT,                      -- 영향받는 사용자 (예: "소상공인", "개발자")
    frequency VARCHAR(50),                    -- 'daily', 'weekly', 'monthly', 'occasional'
    severity VARCHAR(50),                     -- 'critical', 'high', 'medium', 'low'

    -- 시장 정보
    market_size VARCHAR(50),                  -- 'large', 'medium', 'small', 'niche'
    willingness_to_pay VARCHAR(50),           -- 'high', 'medium', 'low', 'unknown'
    existing_solutions TEXT[],                -- 기존 솔루션들
    solution_gaps TEXT,                       -- 기존 솔루션의 부족한 점

    -- 메타데이터
    keywords TEXT[],                          -- 키워드 추출
    category VARCHAR(100),                    -- AI가 분류한 카테고리
    confidence_score DECIMAL(3,2),            -- 0.00 ~ 1.00

    -- Vector 임베딩 (RAG용)
    embedding vector(1536),                   -- OpenAI embedding

    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_pain_point UNIQUE(content_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_pain_points_content ON pain_points(content_id);
CREATE INDEX IF NOT EXISTS idx_pain_points_severity ON pain_points(severity);
CREATE INDEX IF NOT EXISTS idx_pain_points_category ON pain_points(category);
CREATE INDEX IF NOT EXISTS idx_pain_points_confidence ON pain_points(confidence_score DESC);

-- Vector 검색을 위한 인덱스 (pgvector 확장 필요)
-- CREATE INDEX IF NOT EXISTS idx_pain_points_embedding ON pain_points
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ====================================
-- 4. SaaS Ideas 테이블 - 생성된 아이디어
-- ====================================
CREATE TABLE IF NOT EXISTS saas_ideas (
    id SERIAL PRIMARY KEY,
    pain_point_id INTEGER REFERENCES pain_points(id) ON DELETE CASCADE,

    -- 아이디어 기본 정보
    title VARCHAR(255) NOT NULL,
    tagline VARCHAR(500),                     -- 한 줄 설명
    description TEXT NOT NULL,                -- 상세 설명

    -- 비즈니스 모델
    business_model VARCHAR(50),               -- 'subscription', 'freemium', 'one-time', 'usage-based'
    pricing_model TEXT,                       -- 가격 전략 설명
    estimated_monthly_revenue VARCHAR(50),    -- '$0-$1K', '$1K-$10K', '$10K-$50K', '$50K+'

    -- 기술 스택
    tech_stack TEXT[],                        -- ['React', 'Node.js', 'PostgreSQL']
    complexity VARCHAR(50),                   -- 'simple', 'moderate', 'complex'
    estimated_dev_time VARCHAR(50),           -- '1주', '1개월', '3개월', '6개월+'

    -- MVP 정의
    mvp_features TEXT[],                      -- 최소 기능 목록
    mvp_description TEXT,                     -- MVP 설명

    -- 시장 검증
    target_audience TEXT,                     -- 타겟 고객
    go_to_market_strategy TEXT,               -- GTM 전략
    competition_level VARCHAR(50),            -- 'low', 'medium', 'high'
    differentiation TEXT,                     -- 차별화 포인트

    -- 점수
    feasibility_score INTEGER CHECK (feasibility_score >= 1 AND feasibility_score <= 10),
    market_score INTEGER CHECK (market_score >= 1 AND market_score <= 10),
    overall_score INTEGER CHECK (overall_score >= 1 AND overall_score <= 10),

    -- 메타데이터
    tags TEXT[],
    similar_products TEXT[],                  -- 유사 제품/서비스

    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_saas_ideas_pain_point ON saas_ideas(pain_point_id);
CREATE INDEX IF NOT EXISTS idx_saas_ideas_overall_score ON saas_ideas(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_saas_ideas_feasibility ON saas_ideas(feasibility_score DESC);
CREATE INDEX IF NOT EXISTS idx_saas_ideas_market ON saas_ideas(market_score DESC);
CREATE INDEX IF NOT EXISTS idx_saas_ideas_created ON saas_ideas(created_at DESC);

-- ====================================
-- 5. Market Validation 테이블 - 시장 검증
-- ====================================
CREATE TABLE IF NOT EXISTS market_validation (
    id SERIAL PRIMARY KEY,
    saas_idea_id INTEGER REFERENCES saas_ideas(id) ON DELETE CASCADE,

    -- 검증 지표
    search_volume INTEGER,                    -- 월 검색량 (Google Trends)
    trend_direction VARCHAR(20),              -- 'rising', 'stable', 'declining'

    -- 경쟁사 분석
    competitor_count INTEGER,
    top_competitors JSONB,                    -- [{name, url, pricing, users}]
    market_saturation VARCHAR(50),            -- 'low', 'medium', 'high'

    -- 사용자 관심도
    reddit_mentions INTEGER,                  -- Reddit 언급 수
    twitter_mentions INTEGER,                 -- Twitter 언급 수 (선택)
    producthunt_similar INTEGER,              -- 유사 제품 수

    -- 검증 결과
    validation_score INTEGER CHECK (validation_score >= 1 AND validation_score <= 10),
    recommendation TEXT,                      -- AI 추천 사항

    validated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_validation UNIQUE(saas_idea_id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_validation_idea ON market_validation(saas_idea_id);
CREATE INDEX IF NOT EXISTS idx_validation_score ON market_validation(validation_score DESC);

-- ====================================
-- 6. Vector Embeddings 테이블 (ChromaDB 대신 PostgreSQL 사용 시)
-- ====================================
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES raw_contents(id) ON DELETE CASCADE,
    chunk_index INTEGER,                      -- 긴 텍스트를 나눈 경우 순서
    chunk_text TEXT,                          -- 임베딩된 텍스트
    embedding vector(1536),                   -- OpenAI embedding
    metadata JSONB,                           -- 추가 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_content_chunk UNIQUE(content_id, chunk_index)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_embeddings_content ON embeddings(content_id);
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ====================================
-- 유용한 뷰 (View) 생성
-- ====================================

-- 최고 점수 아이디어 뷰
CREATE OR REPLACE VIEW v_top_ideas AS
SELECT
    si.id,
    si.title,
    si.tagline,
    si.overall_score,
    si.feasibility_score,
    si.market_score,
    si.business_model,
    si.estimated_monthly_revenue,
    si.estimated_dev_time,
    pp.problem_statement,
    pp.affected_users,
    pp.severity,
    s.name as source_name,
    mv.validation_score,
    si.created_at
FROM saas_ideas si
JOIN pain_points pp ON si.pain_point_id = pp.id
JOIN raw_contents rc ON pp.content_id = rc.id
JOIN sources s ON rc.source_id = s.id
LEFT JOIN market_validation mv ON mv.saas_idea_id = si.id
ORDER BY si.overall_score DESC, mv.validation_score DESC NULLS LAST;

-- Pain Point 통계 뷰
CREATE OR REPLACE VIEW v_pain_point_stats AS
SELECT
    s.name as source_name,
    pp.category,
    pp.severity,
    COUNT(*) as pain_point_count,
    AVG(pp.confidence_score) as avg_confidence,
    COUNT(si.id) as idea_count
FROM pain_points pp
JOIN raw_contents rc ON pp.content_id = rc.id
JOIN sources s ON rc.source_id = s.id
LEFT JOIN saas_ideas si ON si.pain_point_id = pp.id
GROUP BY s.name, pp.category, pp.severity
ORDER BY pain_point_count DESC;

-- 일별 수집 통계
CREATE OR REPLACE VIEW v_daily_collection_stats AS
SELECT
    DATE(rc.collected_at) as date,
    s.name as source_name,
    COUNT(DISTINCT rc.id) as content_count,
    COUNT(DISTINCT pp.id) as pain_point_count,
    COUNT(DISTINCT si.id) as idea_count
FROM raw_contents rc
JOIN sources s ON rc.source_id = s.id
LEFT JOIN pain_points pp ON pp.content_id = rc.id
LEFT JOIN saas_ideas si ON si.pain_point_id = pp.id
GROUP BY DATE(rc.collected_at), s.name
ORDER BY date DESC;

-- ====================================
-- 함수: 유사 Pain Point 검색 (RAG)
-- ====================================
-- pgvector 확장 설치 필요: CREATE EXTENSION IF NOT EXISTS vector;

CREATE OR REPLACE FUNCTION search_similar_pain_points(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id INTEGER,
    problem_statement TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pp.id,
        pp.problem_statement,
        1 - (pp.embedding <=> query_embedding) as similarity
    FROM pain_points pp
    WHERE 1 - (pp.embedding <=> query_embedding) > match_threshold
    ORDER BY pp.embedding <=> query_embedding
    LIMIT match_count;
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
-- pgvector 확장 설치 안내
-- ====================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Pain Point Finder Database Schema V2 Created!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables:';
    RAISE NOTICE '  - sources (데이터 소스)';
    RAISE NOTICE '  - raw_contents (원본 데이터)';
    RAISE NOTICE '  - pain_points (Pain Point 분석)';
    RAISE NOTICE '  - saas_ideas (SaaS 아이디어)';
    RAISE NOTICE '  - market_validation (시장 검증)';
    RAISE NOTICE '  - embeddings (Vector 임베딩)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views:';
    RAISE NOTICE '  - v_top_ideas';
    RAISE NOTICE '  - v_pain_point_stats';
    RAISE NOTICE '  - v_daily_collection_stats';
    RAISE NOTICE '';
    RAISE NOTICE 'Vector 검색을 사용하려면:';
    RAISE NOTICE '  CREATE EXTENSION IF NOT EXISTS vector;';
    RAISE NOTICE '========================================';
END $$;
