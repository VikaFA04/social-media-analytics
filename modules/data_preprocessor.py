# modules/data_preprocessor.py
import re
import pandas as pd
from datetime import datetime
import nltk
from nltk.corpus import stopwords
import spacy

nltk.download('stopwords', quiet=True)
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

STOP_WORDS = set(stopwords.words('english'))

def clean_text(text: str) -> str:

    if not isinstance(text, str):
        return ''
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().strip()

def lemmatize_text(text: str) -> str:
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc if token.is_alpha and token.text not in STOP_WORDS])

def preprocess_data(df: pd.DataFrame, lemmatize: bool = True) -> pd.DataFrame:
    df = df.copy()
    
    # Используем 'text_content' — имя после переименования в data_loader.py
    df['text_clean'] = df['text_content'].apply(clean_text)

    if lemmatize:
        df['text_lemmatized'] = df['text_clean'].apply(lemmatize_text)
    df['num_hashtags'] = df['hashtags'].str.count('#') if 'hashtags' in df.columns else 0
    df['text_length'] = df['text_clean'].str.len()
    df['post_date'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['post_date'].dt.day_name()
    df['hour'] = df['post_date'].dt.hour

    print(f'Предобработано {len(df)} записей')
    return df
