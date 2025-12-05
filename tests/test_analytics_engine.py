import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from modules.analytics_engine import analyze_sentiment, calculate_engagement, detect_trends

def test_analyze_sentiment():
    """Тест анализа тональности на известных фразах"""
    df = pd.DataFrame({
        'text_clean': [
            'I love this product!',      # Должно быть positive
            'This is terrible',          # Должно быть negative
            'Just an average day'        # Должно быть neutral
        ]
    })
    
    df = analyze_sentiment(df)
    
    assert df.iloc[0]['sentiment_label'] == 'positive'
    assert df.iloc[1]['sentiment_label'] == 'negative'
    assert df.iloc[2]['sentiment_label'] == 'neutral'
    
    # Проверка, что score для positive > 0.5
    assert df.iloc[0]['sentiment_score'] > 0.5
    # Проверка, что score для negative < -0.5
    assert df.iloc[1]['sentiment_score'] < -0.4

def test_calculate_engagement():
    """Тест расчёта вовлечённости"""
    df = pd.DataFrame({
        'likes_count': [100],
        'comments_count': [50],
        'shares_count': [25]
    })
    
    df = calculate_engagement(df)
    
    assert 'engagement_score' in df.columns
    assert df.iloc[0]['engagement_score'] == 175.0

def test_detect_trends():
    """Тест выявления трендов"""
    df = pd.DataFrame({
        'post_date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'engagement_score': [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
    })
    
    df = detect_trends(df)
    
    assert 'rolling_mean_engagement' in df.columns
    assert 'z_score' in df.columns
    assert 'is_anomaly' in df.columns
    
    # Последнее значение должно иметь высокий z-score
    assert df.iloc[-1]['z_score'] > 1.0