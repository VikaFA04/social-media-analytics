# modules/data_loader.py
import pandas as pd
from sqlalchemy import create_engine
from .data_storage import get_db_config
from .data_preprocessor import preprocess_data  # ← Импортируем preprocess_data из соседнего модуля

def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    
    # Переименование колонок под структуру таблицы в PostgreSQL
    column_mapping = {
        'Post ID': 'post_id',
        'Timestamp': 'timestamp',
        'Day of Week': 'day_of_week',
        'Platform': 'platform',
        'User ID': 'user_id',
        'Location': 'location',
        'Language': 'language',
        'Text Content': 'text_content',
        'Hashtags': 'hashtags',
        'Mentions': 'mentions',
        'Likes Count': 'likes_count',
        'Shares Count': 'shares_count',
        'Comments Count': 'comments_count',
        'Impressions': 'impressions',
        'Engagement Rate': 'engagement_rate',
        'Brand Name': 'brand_name',
        'Product Name': 'product_name',
        'Campaign Name': 'campaign_name',
        'Campaign Phase': 'campaign_phase'
    }
    df = df.rename(columns=column_mapping)
    
    required_columns = list(column_mapping.values())
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют обязательные столбцы: {missing}")

    print(f"Загружено {len(df)} записей из {file_path}")
    return df

def data_loader():
    config = get_db_config()
    
    engine = create_engine(
        f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['name']}"
    )
    
    print("Загрузка данных из CSV...")
    df = load_data('data/social_media_data.csv')
    
    print("Предобработка данных...")
    df_processed = preprocess_data(df)
    
    print("Сохранение в базу данных...")
    # Сохраняем с заменой всей таблицы (if_exists='replace')
    df_processed.to_sql('social_media_posts', engine, if_exists='replace', index=False)
    
    print(f'Успешно загружено {len(df_processed)} записей в PostgreSQL')

if __name__ == '__main__':
    data_loader()