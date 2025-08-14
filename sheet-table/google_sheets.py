import logging
import gspread
from google.oauth2.service_account import Credentials
from config import Config

class GoogleSheetsService:
    def __init__(self):
        self.client = None
        self.worksheet = None
        self.columns_cache = []
        self.logger = logging.getLogger(__name__)
        
    async def init_service(self):
        """Инициализация подключения к Google Sheets"""
        try:
            # Настройка авторизации
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                Config.CREDENTIALS_FILE, 
                scopes=scopes
            )
            
            self.client = gspread.authorize(credentials)
            
            # Открытие таблицы и листа
            spreadsheet = self.client.open_by_key(Config.GOOGLE_SHEET_ID)
            self.worksheet = spreadsheet.worksheet(Config.WORKSHEET_NAME)
            
            # Кэширование названий столбцов
            self.columns_cache = self.worksheet.row_values(1)
            
            self.logger.info(f"Подключение к Google Sheets установлено. Лист: {Config.WORKSHEET_NAME}")
            self.logger.info(f"Найдено столбцов: {len(self.columns_cache)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка подключения к Google Sheets: {e}")
            return False
    
    def get_columns(self):
        """Получить названия столбцов"""
        return self.columns_cache
    
    def search_in_sheet(self, search_value):
        """Поиск строк по значению"""
        try:
            all_values = self.worksheet.get_all_values()
            found_rows = []
            
            for i, row in enumerate(all_values[1:], start=2):  # Начинаем с 2-й строки (пропускаем заголовки)
                for cell_value in row:
                    if search_value.lower() in cell_value.lower():
                        found_rows.append({
                            'row_number': i,
                            'data': row
                        })
                        break
            
            self.logger.info(f"Поиск '{search_value}': найдено {len(found_rows)} строк")
            return found_rows
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска в таблице: {e}")
            return []
    
    def get_row_by_number(self, row_number):
        """Получить строку по номеру"""
        try:
            if row_number < 2:  # Первая строка - заголовки
                return None
                
            row_values = self.worksheet.row_values(row_number)
            
            if not row_values:
                return None
                
            self.logger.info(f"Получена строка {row_number}")
            return {
                'row_number': row_number,
                'data': row_values
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения строки {row_number}: {e}")
            return None
    
    def update_cell(self, row, col, value):
        """Обновить ячейку"""
        try:
            self.worksheet.update_cell(row, col, value)
            self.logger.info(f"Обновлена ячейка [{row}, {col}] = '{value}'")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления ячейки [{row}, {col}]: {e}")
            return False
    
    def update_row(self, row_number, values):
        """Обновить всю строку"""
        try:
            # Обновляем только непустые значения
            for i, value in enumerate(values, start=1):
                if value:  # Только если значение непустое
                    self.worksheet.update_cell(row_number, i, value)
            
            self.logger.info(f"Обновлена строка {row_number}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления строки {row_number}: {e}")
            return False

    def get_all_rows_paginated(self, page=1, per_page=5):
        """Получить все строки с пагинацией"""
        try:
            self.logger.info(f"Запрос пагинации: страница {page}, по {per_page} строк")
            
            # Получаем все строки (начиная со второй, пропуская заголовки)
            all_rows = self.worksheet.get_all_values()[1:]  # Пропускаем заголовки
            self.logger.info(f"Получено {len(all_rows)} строк из таблицы")
            
            if not all_rows:
                self.logger.warning("Таблица пуста")
                return [], 0, 0
            
            # Фильтруем пустые строки
            non_empty_rows = []
            for i, row in enumerate(all_rows, start=2):  # Начинаем с 2 (после заголовков)
                if any(cell.strip() for cell in row if cell):  # Если есть хотя бы одна непустая ячейка
                    non_empty_rows.append({
                        'row_number': i,
                        'data': row
                    })
            
            total_rows = len(non_empty_rows)
            self.logger.info(f"Найдено {total_rows} непустых строк")
            
            if total_rows == 0:
                return [], 0, 0
            
            total_pages = (total_rows + per_page - 1) // per_page  # Округляем вверх
            
            # Вычисляем индексы для текущей страницы
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            
            # Получаем строки для текущей страницы
            page_rows = non_empty_rows[start_index:end_index]
            
            self.logger.info(f"Получено строк для страницы {page}: {len(page_rows)} из {total_rows}, всего страниц: {total_pages}")
            
            return page_rows, total_pages, total_rows
            
        except Exception as e:
            self.logger.error(f"Ошибка получения всех строк: {e}")
            return [], 0, 0
    
    def add_new_row(self, row_data):
        """Добавить новую строку в конец таблицы"""
        try:
            # Проверяем, что количество данных соответствует количеству столбцов
            if len(row_data) > len(self.columns_cache):
                row_data = row_data[:len(self.columns_cache)]
            elif len(row_data) < len(self.columns_cache):
                # Дополняем пустыми значениями
                row_data.extend([''] * (len(self.columns_cache) - len(row_data)))
            
            # Добавляем строку
            self.worksheet.append_row(row_data)
            
            # Получаем номер добавленной строки
            all_values = self.worksheet.get_all_values()
            new_row_number = len(all_values)
            
            self.logger.info(f"Добавлена новая строка {new_row_number}")
            return new_row_number
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления строки: {e}")
            return None
    
    def insert_row_at_position(self, row_number, row_data):
        """Вставить строку на определенную позицию"""
        try:
            # Проверяем, что количество данных соответствует количеству столбцов
            if len(row_data) > len(self.columns_cache):
                row_data = row_data[:len(self.columns_cache)]
            elif len(row_data) < len(self.columns_cache):
                # Дополняем пустыми значениями
                row_data.extend([''] * (len(self.columns_cache) - len(row_data)))
            
            # Вставляем строку
            self.worksheet.insert_row(row_data, row_number)
            
            self.logger.info(f"Вставлена строка на позицию {row_number}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка вставки строки: {e}")
            return False
    
    def update_cell_with_formula(self, row_number, column_number, formula):
        """Обновить ячейку формулой"""
        try:
            # Формула должна начинаться с =
            if not formula.startswith('='):
                formula = '=' + formula
            
            # Обновляем ячейку формулой
            self.worksheet.update_cell(row_number, column_number, formula)
            
            self.logger.info(f"Ячейка [{row_number}, {column_number}] обновлена формулой: {formula}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления ячейки формулой: {e}")
            return False
    
    def get_cell_formula(self, row_number, column_number):
        """Получить формулу из ячейки"""
        try:
            # Получаем формулу через batch_get с параметром valueRenderOption
            range_name = f"{self.worksheet.title}!{chr(64 + column_number)}{row_number}"
            result = self.client.values_batch_get(
                self.worksheet.spreadsheet.id,
                ranges=[range_name],
                valueRenderOption='FORMULA'
            )
            
            if result.get('valueRanges') and result['valueRanges'][0].get('values'):
                formula = result['valueRanges'][0]['values'][0][0]
                return formula
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения формулы: {e}")
            return None
    
    def validate_formula(self, formula):
        """Проверить корректность формулы"""
        try:
            # Основные проверки формулы
            if not formula:
                return False, "Формула не может быть пустой"
            
            if not formula.startswith('='):
                formula = '=' + formula
            
            # Проверка на недопустимые символы
            forbidden_chars = ['<script>', '<iframe>', 'javascript:', 'vbscript:']
            formula_lower = formula.lower()
            for char in forbidden_chars:
                if char in formula_lower:
                    return False, f"Недопустимый элемент в формуле: {char}"
            
            # Проверка парности скобок
            open_brackets = formula.count('(')
            close_brackets = formula.count(')')
            if open_brackets != close_brackets:
                return False, "Неправильное количество скобок в формуле"
            
            return True, "Формула корректна"
            
        except Exception as e:
            return False, f"Ошибка валидации: {str(e)}"
