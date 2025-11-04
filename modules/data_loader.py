import pandas as pd
import os

def load_data(file_path: str) -> pd.DataFrame:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Файл {file_path} не найден')

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Поддерживаются только .csv и .json")

    required_columns = ['text', 'platform', 'date', 'likes', 'comments']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют обязательные столбцы: {missing}")

    print(f'агружено {len(df)} записей из {file_path}')
    return df
