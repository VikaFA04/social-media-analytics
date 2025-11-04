import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import yaml

def get_db_config():
    with open('../config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['database']

def create_table_if_not_exists(conn):
    create_query = """
    CREATE TABLE IF NOT EXISTS social_media_posts (
        id SERIAL PRIMARY KEY,
        text TEXT,
        text_clean TEXT,
        text_lemmatized TEXT,
        platform VARCHAR(50),
        post_date TIMESTAMP,
        likes INTEGER,
        comments INTEGER,
        shares INTEGER,
        num_hashtags INTEGER,
        text_length INTEGER,
        day_of_week VARCHAR(20),
        hour INTEGER,
        sentiment_score NUMERIC(5,4),
        sentiment_label VARCHAR(20),
        topic_id INTEGER,
        topic_name TEXT,
        keywords TEXT,
        engagement_score NUMERIC(10,2),
        is_viral BOOLEAN,
        rolling_mean_engagement NUMERIC(10,2),
        z_score NUMERIC(6,3),
        is_anomaly BOOLEAN,
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
        database=config['name'],
        user=config['user'],
        password=config['password']
    )

    create_table_if_not_exists(conn)

    # Подготавливаем данные
    columns = [
        'text', 'text_clean', 'text_lemmatized', 'platform', 'post_date',
        'likes', 'comments', 'shares', 'num_hashtags', 'text_length',
        'day_of_week', 'hour'
    ]
    # Добавляем колонки аналитики, если они есть
    optional_cols = [
        'sentiment_score', 'sentiment_label', 'topic_id', 'topic_name', 'keywords',
        'engagement_score', 'is_viral', 'rolling_mean_engagement', 'z_score', 'is_anomaly'
    ]
    for col in optional_cols:
        if col in df.columns:
            columns.append(col)

    data = df[columns].where(pd.notnull(df), None).values.tolist()

    insert_query = f"""
    INSERT INTO {table_name} ({', '.join(columns)})
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
    {', '.join([f"{col}=EXCLUDED.{col}" for col in columns if col != 'id'])}
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
        database=config['name'],
        user=config['user'],
        password=config['password']
    )
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
