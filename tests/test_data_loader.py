import pandas as pd
from modules.data_loader import load_data

def test_load_data():
    df = load_data('test/test_small.csv')
    assert 'text_content' in df.columns
    assert 'likes_count' in df.columns
    assert len(df) == 3