import psycopg2
from modules.data_storage import get_db_config

def test_connection():
    config = get_db_config()
    try:
        conn = psycopg2.connect(
            host=config['host'],
            database=config['name'],
            user=config['user'],
            password=config['password']
        )
        print('Успешное подключение к PostgreSQL!')
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f'Версия PostgreSQL: {db_version[0]}')
        cur.close()
        conn.close()
    except Exception as e:
        print(f'Ошибка подключения: {e}')

if __name__ == "__main__":
    test_connection()