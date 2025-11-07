import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from bertopic import BERTopic
from keybert import KeyBERT
import yaml

# Загрузка ресурсов
nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(df):
    sia = SentimentIntensityAnalyzer()
    
    def get_sentiment(text):
        if not isinstance(text, str) or len(text.strip()) == 0:
            return 0.0, 'neutral'
        scores = sia.polarity_scores(text)
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        return compound, label

    df[['sentiment_score', 'sentiment_label']] = df['text_clean'].apply(
        lambda x: pd.Series(get_sentiment(x))
    )
    print('Анализ тональности завершен')
    return df

def analyze_topics(df, n_topics=8):
    valid_texts = df[df['text_clean'].str.len() > 0]['text_clean'].tolist()
    valid_indices = df[df['text_clean'].str.len() > 0].index.tolist()
    
    if len(valid_texts) == 0:
        df['topic_id'] = -1
        df['topic_name'] = 'No topics'
        df['keywords'] = ''
        return df

    topic_model = BERTopic(language='english', nr_topics=n_topics)
    topics, _ = topic_model.fit_transform(valid_texts)
    
    topic_info = topic_model.get_topic_info()
    topic_map = {-1: "Noise"}
    for _, row in topic_info.iterrows():
        if row['Topic'] != -1:
            topic_map[row['Topic']] = row['Name']
    
    kw_model = KeyBERT()
    def extract_keywords(text, top_n=3):
        if not isinstance(text, str) or len(text.strip()) == 0:
            return ""
        keywords = kw_model.extract_keywords(text, top_n=top_n)
        return ', '.join([kw[0] for kw in keywords]) if keywords else ''

    temp_df = pd.DataFrame({'topic_id': topics}, index=valid_indices)
    df.loc[valid_indices, 'topic_id'] = temp_df['topic_id']
    df['topic_name'] = df['topic_id'].map(topic_map)
    df['keywords'] = df['text_clean'].apply(lambda x: extract_keywords(x, top_n=3))

    print('Тематический анализ завершен')
    return df

def calculate_engagement(df, viral_multiplier=1.5):
    df['likes_count'] = df['likes_count'].fillna(0)
    df['comments_count'] = df['comments_count'].fillna(0)
    df['shares_count'] = df['shares_count'].fillna(0)
    
    df['engagement_score'] = df['likes_count'] + df['comments_count'] + df['shares_count']
    
    median_engagement = df['engagement_score'].median()
    df['is_viral'] = df['engagement_score'] > (median_engagement * viral_multiplier)
    
    print('Расчет метрик вовлеченности завершен')
    return df

def detect_trends(df, z_score_threshold=2.5):
    df = df.sort_values('post_date').reset_index(drop=True)
    df['rolling_mean_engagement'] = df['engagement_score'].rolling(window=7, min_periods=1).mean()
    mean_eng = df['engagement_score'].mean()
    std_eng = df['engagement_score'].std()
    df['z_score'] = (df['engagement_score'] - mean_eng) / std_eng if std_eng > 0 else 0
    df['is_anomaly'] = df['z_score'].abs() > z_score_threshold
    print('Анализ трендов и аномалий завершен')
    return df

def run_full_analysis(df):
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Опциональная проверка обязательных колонок (раскомментируйте при необходимости)
    # required_cols = ['text_clean', 'likes_count', 'comments_count', 'shares_count', 'post_date']
    # missing = [col for col in required_cols if col not in df.columns]
    # if missing:
    #     raise ValueError('Отсутствуют необходимые колонки для анализа: ' + str(missing))
    
    df = analyze_sentiment(df)
    if config['topic_modeling']['enabled']:
        df = analyze_topics(df, n_topics=config['topic_modeling']['n_topics'])
    df = calculate_engagement(df, viral_multiplier=config['engagement']['viral_multiplier'])
    df = detect_trends(df, z_score_threshold=config['trends']['z_score_threshold'])
    
    return df