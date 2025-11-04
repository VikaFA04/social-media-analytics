import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from jinja2 import Template
from weasyprint import HTML
import os

def create_sentiment_chart(df: pd.DataFrame):
    fig = px.histogram(
        df,
        x='platform',
        color='sentiment_label',
        title='Распределение тональности по платформам',
        labels={'platform': 'Платформа', 'count': 'Количество постов'},
        color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'gray'}
    )
    return fig

def create_engagement_trend(df: pd.DataFrame):
    daily_engagement = df.groupby(df['post_date'].dt.date)['engagement_score'].mean().reset_index()
    fig = px.line(
        daily_engagement,
        x='post_date',
        y='engagement_score',
        title='Средняя вовлечённость по времени',
        labels={'post_date': 'Дата', 'engagement_score': 'Средний engagement'}
    )
    return fig

def create_wordcloud(df: pd.DataFrame, max_words: int = 100):
    all_text = ' '.join(df['text_clean'].dropna().tolist())
    if len(all_text.strip()) == 0:
        return None
    
    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        max_words=max_words,
        colormap='viridis'
    ).generate(all_text)
    
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Облако слов')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{img_str}"

def generate_html_report(df: pd.DataFrame, output_path: str = "report.html"):
    sentiment_fig = create_sentiment_chart(df)
    trend_fig = create_engagement_trend(df)
    wordcloud_img = create_wordcloud(df)
    
    sentiment_html = sentiment_fig.to_html(full_html=False, include_plotlyjs='cdn')
    trend_html = trend_fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Шаблон отчёта
    template_str = """
    <html>
    <head>
        <title>Отчёт по анализу социальных медиа</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1, h2 { color: #2c3e50; }
            .chart { margin: 30px 0; }
            .stats { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Отчёт по анализу социальных медиа</h1>
        
        <div class="stats">
            <h3>Основные статистики</h3>
            <p>Всего постов: {{ total_posts }}</p>
            <p>Позитивных: {{ positive_pct }}%</p>
            <p>Негативных: {{ negative_pct }}%</p>
            <p>Вирусных постов: {{ viral_pct }}%</p>
        </div>
        
        <div class="chart">
            <h2>Распределение тональности по платформам</h2>
            {{ sentiment_chart | safe }}
        </div>
        
        <div class="chart">
            <h2>Динамика вовлечённости</h2>
            {{ trend_chart | safe }}
        </div>
        
        {% if wordcloud %}
        <div class="chart">
            <h2>Облако слов</h2>
            <img src="{{ wordcloud }}" alt="Word Cloud" style="width: 100%; max-width: 800px;">
        </div>
        {% endif %}
    </body>
    </html>
    """
    
    template = Template(template_str)
    
    # Статистики
    total_posts = len(df)
    positive_pct = round((df['sentiment_label'] == 'positive').sum() / total_posts * 100, 1)
    negative_pct = round((df['sentiment_label'] == 'negative').sum() / total_posts * 100, 1)
    viral_pct = round(df['is_viral'].sum() / total_posts * 100, 1)
    
    html_content = template.render(
        total_posts=total_posts,
        positive_pct=positive_pct,
        negative_pct=negative_pct,
        viral_pct=viral_pct,
        sentiment_chart=sentiment_html,
        trend_chart=trend_html,
        wordcloud=wordcloud_img
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f'HTML-отчёт сохранён: {output_path}')
    return output_path

def export_to_pdf(html_path: str, pdf_path: str = "report.pdf"):

    HTML(html_path).write_pdf(pdf_path)
    print(f'PDF-отчёт сохранён: {pdf_path}')

def export_to_excel(df: pd.DataFrame, excel_path: str = "report.xlsx"):

    df.to_excel(excel_path, index=False)
    print(f'Excel-отчёт сохранён: {excel_path}')

def generate_reports(df: pd.DataFrame, output_dir: str = "."):

    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "report.html")
    pdf_path = os.path.join(output_dir, "report.pdf")
    excel_path = os.path.join(output_dir, "data.xlsx")
    
    generate_html_report(df, html_path)
    export_to_pdf(html_path, pdf_path)
    export_to_excel(df, excel_path)
    
    print('Все отчёты успешно сгенерированы')
