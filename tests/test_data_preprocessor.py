import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from modules.data_preprocessor import clean_text, lemmatize_text, preprocess_data

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)  # ← ДОБАВЬТЕ ЭТУ СТРОКУ — заменяет множественные пробелы на один
    return text.lower().strip()

def test_lemmatize_text():
    """Тест лемматизации (упрощённый)"""
    text = "running and jumps"
    lemmatized = lemmatize_text(text)
    # Проверяем, что слова приведены к основе (может отличаться в зависимости от модели)
    assert 'run' in lemmatized or 'jump' in lemmatized, f"Лемматизация не сработала: {lemmatized}"

def test_preprocess_data():
    """Тест полной предобработки"""
    df = pd.DataFrame({
        'text_content': ['I love this! 😍'],
        'hashtags': ['#love'],
        'timestamp': ['2024-01-01 10:00:00']
    })
    
    df_processed = preprocess_data(df, lemmatize=False)
    
    assert 'text_clean' in df_processed.columns
    assert 'num_hashtags' in df_processed.columns
    assert 'post_date' in df_processed.columns
    assert df_processed.iloc[0]['text_clean'] == 'i love this'
    assert df_processed.iloc[0]['num_hashtags'] == 1