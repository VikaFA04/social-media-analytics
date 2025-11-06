import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import yaml

def get_db_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['database']

def create_table_if_not_exists(conn):
    create_query = """
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
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

def save_to_database(df: pd.DataFrame, table_name: str = 'social_media_posts'):
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],  # добавим порт
        database=config['name'],
        user=config['user'],
        password=config['password']
    )

    create_table_if_not_exists(conn)

    # Список колонок из вашей таблицы (кроме id и created_at)
    all_columns = [
        'post_id', 'timestamp', 'day_of_week', 'platform', 'user_id',
        'location', 'language', 'text_content', 'hashtags', 'mentions',
        'keywords', 'topic_category', 'sentiment_score', 'sentiment_label',
        'emotion_type', 'toxicity_score', 'likes_count', 'shares_count',
        'comments_count', 'impressions', 'engagement_rate', 'brand_name',
        'product_name', 'campaign_name', 'campaign_phase', 'user_past_sentiment_avg',
        'user_engagement_growth', 'buzz_change_rate', 'text_clean',
        'text_lemmatized', 'num_hashtags', 'text_length', 'hour', 'is_viral'
    ]
    
    # Оставляем только те колонки, которые есть в DataFrame
    available_columns = [col for col in all_columns if col in df.columns]
    
    # Подготавливаем данные
    data = df[available_columns].where(pd.notnull(df), None).values.tolist()

    # INSERT запрос с обработкой конфликтов по post_id
    insert_query = f"""
    INSERT INTO {table_name} ({', '.join(available_columns)})
    VALUES %s
    ON CONFLICT (post_id) DO UPDATE SET
    {', '.join([f"{col}=EXCLUDED.{col}" for col in available_columns if col != 'post_id'])}
    """

    with conn.cursor() as cur:
        execute_values(cur, insert_query, data)
    conn.commit()
    conn.close()

    print(f'Сохранено {len(df)} записей в таблицу {table_name}')

def load_from_database(table_name: str = 'social_media_posts') -> pd.DataFrame:
    """Загружает данные из PostgreSQL"""
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],  # добавим порт
        database=config['name'],
        user=config['user'],
        password=config['password']
    )
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, conn)
    conn.close()
    return df