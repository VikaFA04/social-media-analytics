import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import threading
import os
import sys
import webbrowser

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import load_data
from modules.data_preprocessor import preprocess_data
from modules.data_storage import save_to_database
from modules.analytics_engine import run_full_analysis
from modules.visualization import generate_reports

class SocialMediaAnalyticsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Аналитическая система социальных медиа')
        self.root.geometry('1000x700')
        self.root.resizable(True, True)

        # Цветовая тема
        self.bg_color = '#f0f4f8'
        self.button_color = '#3a86ff'
        self.button_hover_color = '#2a75e6'
        self.text_color = "#3f4d5c"
        self.frame_color = '#ffffff'
        self.highlight_color = '#8ecae6'

        self.root.configure(bg=self.bg_color)

        # Шрифты
        self.title_font = font.Font(family='Arial', size=16, weight='bold')
        self.header_font = font.Font(family='Arial', size=12, weight='bold')
        self.normal_font = font.Font(family='Arial', size=10)
        self.small_font = font.Font(family='Arial', size=9)

        self.file_path = None
        self.df = None

        self.create_widgets()

    def create_widgets(self):
        # Стиль для ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', padding=[12, 6], font=self.normal_font)
        style.map('TNotebook.Tab', background=[('selected', self.button_color)], foreground=[('selected', 'white')])

        # Создаем вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка 1: Загрузка данных
        self.tab_upload = tk.Frame(self.notebook, bg=self.frame_color, padx=20, pady=20)
        self.notebook.add(self.tab_upload, text='Загрузка данных')

        # Вкладка 2: Анализ
        self.tab_analysis = tk.Frame(self.notebook, bg=self.frame_color, padx=20, pady=20)
        self.notebook.add(self.tab_analysis, text='Анализ')

        # Вкладка 3: Графики
        self.tab_charts = tk.Frame(self.notebook, bg=self.frame_color, padx=20, pady=20)
        self.notebook.add(self.tab_charts, text='Графики')

        # Вкладка 4: Отчёты
        self.tab_reports = tk.Frame(self.notebook, bg=self.frame_color, padx=20, pady=20)
        self.notebook.add(self.tab_reports, text='Отчёты')

        # === ВКЛАДКА 1: ЗАГРУЗКА ===
        self.setup_upload_tab()

        # === ВКЛАДКА 2: АНАЛИЗ ===
        self.setup_analysis_tab()

        # === ВКЛАДКА 3: ГРАФИКИ ===
        self.setup_charts_tab()

        # === ВКЛАДКА 4: ОТЧЁТЫ ===
        self.setup_reports_tab()

    def setup_upload_tab(self):
        title_label = tk.Label(self.tab_upload, text='Загрузка данных', font=self.title_font, bg=self.frame_color, fg=self.text_color)
        title_label.pack(pady=(0, 20))

        instruction_label = tk.Label(self.tab_upload, text='Выберите CSV-файл с данными для анализа', font=self.normal_font, bg=self.frame_color, fg=self.text_color)
        instruction_label.pack(pady=(0, 20))

        self.select_button = tk.Button(
            self.tab_upload,
            text='Выбрать файл',
            command=self.select_file,
            bg=self.button_color,
            fg='white',
            font=self.normal_font,
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        self.select_button.pack(pady=10)
        self.select_button.bind('<Enter>', lambda e: self.select_button.config(bg=self.button_hover_color))
        self.select_button.bind('<Leave>', lambda e: self.select_button.config(bg=self.button_color))

        self.file_label = tk.Label(self.tab_upload, text='Файл не выбран', font=self.normal_font, bg=self.frame_color, fg='gray')
        self.file_label.pack(pady=(10, 30))

        # Прогресс-бар
        progress_frame = tk.Frame(self.tab_upload, bg=self.frame_color)
        progress_frame.pack(fill='x', pady=(0, 20))

        self.progress_label = tk.Label(progress_frame, text='Прогресс:', font=self.normal_font, bg=self.frame_color, fg=self.text_color)
        self.progress_label.pack(anchor='w')

        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill='x', pady=(5, 0))

        # Лог выполнения
        log_frame = tk.LabelFrame(self.tab_upload, text='Лог выполнения', font=self.header_font, bg=self.frame_color, fg=self.text_color)
        log_frame.pack(fill='both', expand=True, pady=(20, 0))

        self.log_text = tk.Text(log_frame, height=8, state='disabled', wrap='word', font=self.small_font)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log_text.pack(side='left', fill='both', expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)

    def setup_analysis_tab(self):
        title_label = tk.Label(self.tab_analysis, text='Анализ данных', font=self.title_font, bg=self.frame_color, fg=self.text_color)
        title_label.pack(pady=(0, 20))

        self.analyze_button = tk.Button(
            self.tab_analysis,
            text='Запустить анализ',
            command=self.start_analysis,
            bg=self.button_color,
            fg='white',
            font=self.normal_font,
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.analyze_button.pack(pady=20)
        self.analyze_button.bind('<Enter>', lambda e: self.analyze_button.config(bg=self.button_hover_color))
        self.analyze_button.bind('<Leave>', lambda e: self.analyze_button.config(bg=self.button_color))

        # Результаты анализа
        result_frame = tk.LabelFrame(self.tab_analysis, text='Результаты анализа', font=self.header_font, bg=self.frame_color, fg=self.text_color)
        result_frame.pack(fill='both', expand=True, pady=(20, 0))

        self.result_text = tk.Label(result_frame, text='Анализ не выполнен', font=self.normal_font, bg=self.frame_color, fg='gray', justify='left', anchor='nw')
        self.result_text.pack(padx=20, pady=20, fill='both', expand=True)

    def setup_charts_tab(self):
        title_label = tk.Label(self.tab_charts, text='Визуализация данных', font=self.title_font, bg=self.frame_color, fg=self.text_color)
        title_label.pack(pady=(0, 20))

        # Создаем фрейм для графиков
        charts_container = tk.Frame(self.tab_charts, bg=self.frame_color)
        charts_container.pack(fill='both', expand=True)

        # Создаем холст для прокрутки
        canvas = tk.Canvas(charts_container, bg=self.frame_color)
        scrollbar = ttk.Scrollbar(charts_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.frame_color)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Фреймы для графиков
        self.sentiment_frame = tk.Frame(scrollable_frame, bg=self.frame_color, relief='groove', borderwidth=1)
        self.sentiment_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.trend_frame = tk.Frame(scrollable_frame, bg=self.frame_color, relief='groove', borderwidth=1)
        self.trend_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.wordcloud_frame = tk.Frame(scrollable_frame, bg=self.frame_color, relief='groove', borderwidth=1)
        self.wordcloud_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Заголовки графиков
        tk.Label(self.sentiment_frame, text='Распределение тональности по платформам', font=self.header_font, bg=self.frame_color, fg=self.text_color).pack(pady=(10, 5))
        tk.Label(self.trend_frame, text='Динамика вовлечённости по времени', font=self.header_font, bg=self.frame_color, fg=self.text_color).pack(pady=(10, 5))
        tk.Label(self.wordcloud_frame, text='Облако слов', font=self.header_font, bg=self.frame_color, fg=self.text_color).pack(pady=(10, 5))

        # Плейсхолдеры для графиков
        self.sentiment_canvas = None
        self.trend_canvas = None
        self.wordcloud_canvas = None

        # Сообщение о необходимости анализа
        message = 'После выполнения анализа здесь появятся графики'
        tk.Label(self.sentiment_frame, text=message, font=self.small_font, bg=self.frame_color, fg='gray').pack(pady=20)
        tk.Label(self.trend_frame, text=message, font=self.small_font, bg=self.frame_color, fg='gray').pack(pady=20)
        tk.Label(self.wordcloud_frame, text=message, font=self.small_font, bg=self.frame_color, fg='gray').pack(pady=20)

    def setup_reports_tab(self):
        title_label = tk.Label(self.tab_reports, text='Отчёты', font=self.title_font, bg=self.frame_color, fg=self.text_color)
        title_label.pack(pady=(0, 20))

        instruction_label = tk.Label(self.tab_reports, text='После анализа вы можете открыть сгенерированные отчёты', font=self.normal_font, bg=self.frame_color, fg=self.text_color)
        instruction_label.pack(pady=(0, 20))

        buttons_frame = tk.Frame(self.tab_reports, bg=self.frame_color)
        buttons_frame.pack(pady=20)

        self.html_button = tk.Button(
            buttons_frame,
            text='Открыть HTML-отчёт',
            command=self.open_html_report,
            bg=self.button_color,
            fg='white',
            font=self.normal_font,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.html_button.pack(side='left', padx=10)
        self.html_button.bind('<Enter>', lambda e: self.html_button.config(bg=self.button_hover_color))
        self.html_button.bind('<Leave>', lambda e: self.html_button.config(bg=self.button_color))

        self.excel_button = tk.Button(
            buttons_frame,
            text='Открыть Excel-отчёт',
            command=self.open_excel_report,
            bg=self.button_color,
            fg='white',
            font=self.normal_font,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.excel_button.pack(side='left', padx=10)
        self.excel_button.bind('<Enter>', lambda e: self.excel_button.config(bg=self.button_hover_color))
        self.excel_button.bind('<Leave>', lambda e: self.excel_button.config(bg=self.button_color))

        info_label = tk.Label(self.tab_reports, text='Отчёты сохраняются в папку "reports"', font=self.small_font, bg=self.frame_color, fg='gray')
        info_label.pack(pady=(30, 0))

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        self.root.update()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title='Выберите CSV-файл',
            filetypes=[('CSV files', '*.csv')]
        )
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f'Выбран файл: {filename}', fg=self.text_color)
            self.analyze_button.config(state='normal')
            self.log(f'Файл выбран: {filename}')

    def start_analysis(self):
        if not self.file_path:
            messagebox.showerror('Ошибка', 'Сначала выберите файл!')
            return

        self.set_controls_state('disabled')
        self.progress['value'] = 0
        self.result_text.config(text='Анализ выполняется...', fg='blue')

        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def run_analysis(self):
        try:
            self.log('Загрузка данных...')
            self.progress['value'] = 10
            df = load_data(self.file_path)

            self.log('Предобработка данных...')
            self.progress['value'] = 30
            df = preprocess_data(df, lemmatize=True)

            self.log('Сохранение в базу данных...')
            self.progress['value'] = 40
            save_to_database(df)

            self.log('Запуск полного анализа...')
            self.progress['value'] = 50
            df = run_full_analysis(df)

            self.log('Сохранение результатов анализа...')
            self.progress['value'] = 70
            save_to_database(df)

            self.log('Генерация отчетов...')
            self.progress['value'] = 90
            generate_reports(df, output_dir='reports')

            self.progress['value'] = 100
            self.df = df

            # Обновляем результаты
            self.update_results()
            self.update_charts()

            self.html_button.config(state='normal')
            self.excel_button.config(state='normal')

            self.log('Анализ завершен успешно!')

        except Exception as e:
            error_msg = f'Ошибка: {str(e)}'
            self.log(error_msg)
            messagebox.showerror('Ошибка', f'Произошла ошибка:\n{str(e)}')
            self.result_text.config(text='Ошибка при анализе', fg='red')

        finally:
            self.set_controls_state('normal')

    def update_results(self):
        total_posts = len(self.df)
        positive_pct = round((self.df['sentiment_label'] == 'positive').sum() / total_posts * 100, 1)
        negative_pct = round((self.df['sentiment_label'] == 'negative').sum() / total_posts * 100, 1)
        neutral_pct = round((self.df['sentiment_label'] == 'neutral').sum() / total_posts * 100, 1)
        viral_pct = round(self.df['is_viral'].sum() / total_posts * 100, 1)

        result_str = (
            f'Общее количество постов: {total_posts}\n\n'
            f'Позитивных: {positive_pct}%\n'
            f'Нейтральных: {neutral_pct}%\n'
            f'Негативных: {negative_pct}%\n\n'
            f'Вирусных постов: {viral_pct}%'
        )
        self.result_text.config(text=result_str, fg=self.text_color)

    def update_charts(self):
        if self.df is None:
            return

        # Очищаем старые графики
        for widget in self.sentiment_frame.winfo_children():
            if isinstance(widget, tk.Canvas) or isinstance(widget, tk.Frame):
                if widget != self.sentiment_frame.winfo_children()[0]:  # Не удаляем заголовок
                    widget.destroy()

        for widget in self.trend_frame.winfo_children():
            if isinstance(widget, tk.Canvas) or isinstance(widget, tk.Frame):
                if widget != self.trend_frame.winfo_children()[0]:
                    widget.destroy()

        for widget in self.wordcloud_frame.winfo_children():
            if isinstance(widget, tk.Canvas) or isinstance(widget, tk.Frame):
                if widget != self.wordcloud_frame.winfo_children()[0]:
                    widget.destroy()

        # График 1: Распределение тональности по платформам
        fig1 = Figure(figsize=(8, 4), dpi=100)
        ax1 = fig1.add_subplot(111)

        platform_sentiment = self.df.groupby(['platform', 'sentiment_label']).size().unstack(fill_value=0)
        platform_sentiment.plot(kind='bar', stacked=True, ax=ax1, color=['#2ecc71', '#95a5a6', '#e74c3c'])
        ax1.set_title('Распределение тональности по платформам', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Платформа', fontsize=10)
        ax1.set_ylabel('Количество постов', fontsize=10)
        ax1.legend(title='Тональность')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)

        canvas1 = FigureCanvasTkAgg(fig1, master=self.sentiment_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # График 2: Динамика вовлечённости
        fig2 = Figure(figsize=(8, 4), dpi=100)
        ax2 = fig2.add_subplot(111)

        daily_engagement = self.df.groupby(self.df['post_date'].dt.date)['engagement_score'].mean()
        ax2.plot(daily_engagement.index, daily_engagement.values, marker='o', linewidth=2, color=self.button_color)
        ax2.set_title('Средняя вовлечённость по времени', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Дата', fontsize=10)
        ax2.set_ylabel('Средний engagement', fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.7)
        fig2.autofmt_xdate()

        canvas2 = FigureCanvasTkAgg(fig2, master=self.trend_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # График 3: Облако слов
        fig3 = Figure(figsize=(8, 4), dpi=100)
        ax3 = fig3.add_subplot(111)

        all_text = ' '.join(self.df['text_clean'].dropna().tolist())
        if len(all_text.strip()) > 0:
            wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100, colormap='viridis').generate(all_text)
            ax3.imshow(wordcloud, interpolation='bilinear')
            ax3.axis('off')
            ax3.set_title('Облако слов из текстов постов', fontsize=12, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'Недостаточно текстовых данных', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
            ax3.axis('off')

        canvas3 = FigureCanvasTkAgg(fig3, master=self.wordcloud_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def set_controls_state(self, state):
        self.select_button.config(state=state)
        if self.file_path:
            self.analyze_button.config(state='normal' if state == 'normal' else 'disabled')
        else:
            self.analyze_button.config(state='disabled')

        if state == 'normal' and self.df is not None:
            self.html_button.config(state='normal')
            self.excel_button.config(state='normal')

    def open_html_report(self):
        html_path = os.path.abspath('reports/report.html')
        if os.path.exists(html_path):
            webbrowser.open('file://' + html_path)
        else:
            messagebox.showerror('Ошибка', 'HTML-отчет не найден. Запустите анализ.')

    def open_excel_report(self):
        excel_path = os.path.abspath('reports/data.xlsx')
        if os.path.exists(excel_path):
            if sys.platform == 'win32':
                os.startfile(excel_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{excel_path}"')
            else:
                os.system(f'xdg-open "{excel_path}"')
        else:
            messagebox.showerror('Ошибка', 'Excel-отчет не найден. Запустите анализ.')

if __name__ == '__main__':
    root = tk.Tk()
    app = SocialMediaAnalyticsGUI(root)
    root.mainloop()
    