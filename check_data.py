from modules.data_loader import load_data

def check_dataset():
    print("Проверка структуры данных...")
    df = load_data('Social Media Engagement Dataset.csv')
    
    print("\n=== ИНФОРМАЦИЯ О ДАННЫХ ===")
    print(f"Всего записей: {len(df)}")
    print(f"Всего столбцов: {len(df.columns)}")
    print(f"Столбцы: {df.columns.tolist()}")
    
    print("\n=== ПЕРВЫЕ 3 ЗАПИСИ ===")
    print(df.head(3))
    
    print("\n=== ТИПЫ ДАННЫХ ===")
    print(df.dtypes)

if __name__ == '__main__':
    check_dataset()