CREATE TABLE IF NOT EXISTS social_media_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE,
    timestamp TIMESTAMP,
    day_of_week VARCHAR(20),
    platform VARCHAR(50),
    user_id VARCHAR(100),
    location VARCHAR(200),
    language VARCHAR(50),
    text_content TEXT,
    hashtags TEXT,
    mentions TEXT,
    keywords TEXT,
    topic_category VARCHAR(100),
    sentiment_score NUMERIC(3,2),
    sentiment_label VARCHAR(20),
    emotion_type VARCHAR(50),
    toxicity_score NUMERIC(3,2),
    likes_count INTEGER,
    shares_count INTEGER,
    comments_count INTEGER,
    impressions INTEGER,
    engagement_rate NUMERIC(8,4),
    brand_name VARCHAR(200),
    product_name VARCHAR(200),
    campaign_name VARCHAR(200),
    campaign_phase VARCHAR(100),
    user_past_sentiment_avg NUMERIC(3,2),
    user_engagement_growth NUMERIC(8,4),
    buzz_change_rate NUMERIC(8,4),
    text_clean TEXT,
    text_lemmatized TEXT,
    num_hashtags INTEGER,
    text_length INTEGER,
    hour INTEGER,
    is_viral BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX idx_post_id ON social_media_posts(post_id);
CREATE INDEX idx_platform_date ON social_media_posts(platform, timestamp);
CREATE INDEX idx_sentiment ON social_media_posts(sentiment_label);
CREATE INDEX idx_user_id ON social_media_posts(user_id);