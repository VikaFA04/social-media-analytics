import os
import sys
import tkinter as tk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
import threading
import time

# Импортируем GUI
from gui import SocialMediaAnalyticsGUI

class TestGUI:
    @classmethod
    def setup_class(cls):
        """Создаем экземпляр GUI для тестов"""
        cls.root = tk.Tk()
        cls.root.withdraw()  # Скрываем окно
        cls.app = SocialMediaAnalyticsGUI(cls.root)

    @classmethod
    def teardown_class(cls):
        """Закрываем GUI после тестов"""
        cls.root.destroy()

    def test_gui_initialization(self):
        """Тест инициализации GUI"""
        assert self.app is not None, "GUI не инициализирован"
        assert hasattr(self.app, 'notebook'), "Notebook не создан"

    def test_file_selection(self):
        """Тест выбора файла (симуляция)"""
        # Мокаем диалог выбора файла
        with patch('tkinter.filedialog.askopenfilename') as mock_dialog:
            mock_dialog.return_value = 'test/test_small.csv'
            
            # Вызываем метод выбора файла
            self.app.select_file()
            
            assert self.app.file_path == 'test/test_small.csv', "Файл не выбран"
            assert self.app.analyze_button['state'] == 'normal', "Кнопка анализа не активирована"

    def test_analysis_execution(self):
        """Тест выполнения анализа (частичный, без реального запуска)"""
        # Устанавливаем тестовый файл
        self.app.file_path = 'test/test_small.csv'
        self.app.analyze_button['state'] = 'normal'
        
        # Мокаем метод run_analysis
        with patch.object(self.app, 'run_analysis') as mock_run_analysis:
            # Запускаем анализ
            self.app.start_analysis()
            
            # Ждём завершения потока (максимум 5 секунд)
            start_time = time.time()
            while not mock_run_analysis.called and (time.time() - start_time) < 5:
                self.root.update()  # Обновляем GUI
                time.sleep(0.1)
            
            # Проверяем, что метод был вызван
            assert mock_run_analysis.called, "Анализ не был запущен"