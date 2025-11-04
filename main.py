from modules.data_loader import load_data
from modules.data_preprocessor import preprocess_data
from modules.data_storage import save_to_database, load_from_database
from modules.analytics_engine import run_full_analysis
from modules.visualization import generate_reports
import os

def main():
    print('Запуск аналитической системы для социальных медиа')
    file_path = "data/social_media_data.csv"
    df = load_data(file_path)
    df = preprocess_data(df, lemmatize=True)
    save_to_database(df)
    df = run_full_analysis(df)
    save_to_database(df)
    generate_reports(df, output_dir="reports")

if __name__ == "__main__":
    main()
