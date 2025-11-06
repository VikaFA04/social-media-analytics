# check_columns.py
from modules.data_loader import load_data

def check_columns():
    df = load_data("data/social_media_data.csv")
    print("Столбцы в ваших данных:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"Всего столбцов: {len(df.columns)}")
    print(f"Всего записей: {len(df)}")

if __name__ == "__main__":
    check_columns()