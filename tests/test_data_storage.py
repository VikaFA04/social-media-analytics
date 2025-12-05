import os
import sys
import psycopg2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from modules.data_storage import get_db_config, save_to_database, load_from_database

def test_database_connection():
    """Тест подключения к базе данных"""
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['name'],
        user=config['user'],
        password=config['password']
    )
    assert conn.closed == 0, "Подключение к БД не установлено"
    conn.close()

def test_save_and_load_data():
    """Тест сохранения и загрузки данных"""
    # Создаем тестовый DataFrame
    df = pd.DataFrame({
        'post_id': ['test1', 'test2'],
        'text_content': ['Test content 1', 'Test content 2'],
        'platform': ['Test', 'Test'],
        'timestamp': ['2024-01-01', '2024-01-02']
    })
    
    # Получаем конфигурацию БД
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['name'],
        user=config['user'],
        password=config['password']
    )
    
    # Создаем тестовую таблицу
    create_query = """
    CREATE TABLE IF NOT EXISTS test_table (
        post_id VARCHAR(100) PRIMARY KEY,
        text_content TEXT,
        platform VARCHAR(50),
        timestamp TIMESTAMP
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()
    
    # Сохраняем в БД
    save_to_database(df, table_name='test_table')
    
    # Загружаем обратно
    df_loaded = load_from_database(table_name='test_table')
    
    # Проверяем, что данные совпадают
    assert len(df_loaded) >= 2, "Данные не сохранены в БД"
    assert 'test1' in df_loaded['post_id'].values
    assert 'test2' in df_loaded['post_id'].values
    
    # Очищаем тестовую таблицу
    with conn.cursor() as cur:
        cur.execute("DELETE FROM test_table WHERE post_id IN ('test1', 'test2')")
        cur.execute("DROP TABLE IF EXISTS test_table")
    conn.commit()
    conn.close()