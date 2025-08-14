import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from google_sheets import GoogleSheetsService
from keyboards import Keyboards
from utils import format_row_data, format_search_results, format_columns_list, escape_markdown

# Определение состояний для FSM
class EditStates(StatesGroup):
    waiting_for_new_value = State()

class SearchStates(StatesGroup):
    waiting_for_search_value = State()
    waiting_for_row_number = State()
    waiting_for_edit_row_number = State()

class NewRowStates(StatesGroup):
    filling_field = State()

class FormulaStates(StatesGroup):
    waiting_for_cell_position = State()
    waiting_for_formula = State()
    waiting_for_validation = State()

class BotHandlers:
    def __init__(self, sheets_service: GoogleSheetsService):
        self.sheets_service = sheets_service
        self.router = Router()
        self.logger = logging.getLogger(__name__)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        # Команды
        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.find_command, Command("find"))
        self.router.message.register(self.row_command, Command("row"))
        self.router.message.register(self.cols_command, Command("cols"))
        self.router.message.register(self.edit_command, Command("edit"))
        
        # Обработчики кнопок главного меню
        self.router.message.register(self.handle_search_button, F.text == "🔍 Поиск по значению")
        self.router.message.register(self.handle_get_row_button, F.text == "📊 Получить строку по номеру")
        self.router.message.register(self.handle_all_rows_button, F.text == "📄 Все строки")
        self.router.message.register(self.handle_show_columns_button, F.text == "📋 Показать столбцы")
        self.router.message.register(self.handle_edit_button, F.text == "✏️ Редактировать строку")
        self.router.message.register(self.handle_create_new_row_button, F.text == "➕ Создать новую строку")
        self.router.message.register(self.handle_formulas_button, F.text == "🧮 Работа с формулами")
        self.router.message.register(self.handle_help_button, F.text == "📝 Помощь")
        self.router.message.register(self.handle_about_button, F.text == "ℹ️ О боте")
        
        # Callback обработчики
        self.router.callback_query.register(self.handle_row_selection, F.data.startswith("select_row:"))
        self.router.callback_query.register(self.handle_edit_row, F.data.startswith("edit_row:"))
        self.router.callback_query.register(self.handle_edit_field, F.data.startswith("edit_field:"))
        self.router.callback_query.register(self.handle_refresh_row, F.data.startswith("refresh_row:"))
        self.router.callback_query.register(self.handle_back_to_row, F.data.startswith("back_to_row:"))
        self.router.callback_query.register(self.handle_confirm_action, F.data.startswith("confirm:"))
        self.router.callback_query.register(self.handle_cancel, F.data.in_({"cancel_search", "cancel_action"}))
        self.router.callback_query.register(self.handle_back_to_menu, F.data == "back_to_menu")
        self.router.callback_query.register(self.handle_action_callback, F.data.startswith("action:"))
        self.router.callback_query.register(self.handle_pagination, F.data.startswith("page:"))
        self.router.callback_query.register(self.handle_fill_field, F.data.startswith("fill_field:"))
        self.router.callback_query.register(self.handle_save_new_row, F.data == "save_new_row")
        self.router.callback_query.register(self.handle_clear_new_row, F.data == "clear_new_row")
        self.router.callback_query.register(self.handle_cancel_new_row, F.data == "cancel_new_row")
        self.router.callback_query.register(self.handle_formula_callback, F.data.startswith("formula:"))
        self.router.callback_query.register(self.handle_example_callback, F.data.startswith("example:"))
        self.router.callback_query.register(self.handle_back_to_formulas, F.data == "back_to_formulas")
        
        # Обработчики состояний FSM
        self.router.message.register(self.handle_new_value_input, EditStates.waiting_for_new_value)
        self.router.message.register(self.handle_search_input, SearchStates.waiting_for_search_value)
        self.router.message.register(self.handle_row_number_input, SearchStates.waiting_for_row_number)
        self.router.message.register(self.handle_edit_row_number_input, SearchStates.waiting_for_edit_row_number)
        self.router.message.register(self.handle_new_row_field_input, NewRowStates.filling_field)
        self.router.message.register(self.handle_cell_position_input, FormulaStates.waiting_for_cell_position)
        self.router.message.register(self.handle_formula_input, FormulaStates.waiting_for_formula)
        self.router.message.register(self.handle_validation_input, FormulaStates.waiting_for_validation)
        
        # Временный отладочный обработчик для всех текстовых сообщений
        self.router.message.register(self.handle_unhandled_text)
    
    async def start_command(self, message: Message):
        """Обработчик команды /start"""
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        self.logger.info(f"Пользователь {user_id} ({username}) запустил бота")
        
        welcome_text = f"""
🤖 **Добро пожаловать в бота для работы с Google Таблицей!**

👋 Привет, {message.from_user.first_name}!

Используйте кнопки меню ниже для удобной работы с таблицей или команды:

**Доступные команды:**
/find `[значение]` - поиск строк по значению
/row `[номер]` - получить строку по номеру
/cols - показать названия столбцов
/edit `[номер]` - редактировать строку

**Пример использования:**
`/find test@email.com`
`/row 5`
`/edit 10`

✅ Доступ разрешен. Ваш ID: {user_id}
        """
        
        keyboard = Keyboards.create_main_menu()
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def find_command(self, message: Message):
        """Обработчик команды /find"""
        user_id = message.from_user.id
        command_args = message.text.split(maxsplit=1)
        
        if len(command_args) < 2:
            await message.answer("❌ Укажите значение для поиска.\nПример: `/find test@email.com`", parse_mode="Markdown")
            return
        
        search_value = command_args[1].strip()
        self.logger.info(f"Пользователь {user_id} выполняет поиск: '{search_value}'")
        
        # Показываем индикатор загрузки
        await message.answer("🔍 Выполняю поиск...")
        
        # Поиск в таблице
        found_rows = self.sheets_service.search_in_sheet(search_value)
        
        if not found_rows:
            await message.answer(f"🔍 По запросу '**{escape_markdown(search_value)}**' ничего не найдено.", parse_mode="Markdown")
            return
        
        # Форматируем результаты
        results_text = format_search_results(found_rows, search_value)
        keyboard = Keyboards.create_row_selection_keyboard(found_rows)
        
        await message.answer(results_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def row_command(self, message: Message):
        """Обработчик команды /row"""
        user_id = message.from_user.id
        command_args = message.text.split(maxsplit=1)
        
        if len(command_args) < 2:
            await message.answer("❌ Укажите номер строки.\nПример: `/row 5`", parse_mode="Markdown")
            return
        
        try:
            row_number = int(command_args[1].strip())
        except ValueError:
            await message.answer("❌ Номер строки должен быть числом.")
            return
        
        if row_number < 2:
            await message.answer("❌ Номер строки должен быть больше 1 (первая строка - заголовки).")
            return
        
        self.logger.info(f"Пользователь {user_id} запрашивает строку {row_number}")
        
        # Получаем строку
        row_data = self.sheets_service.get_row_by_number(row_number)
        
        if not row_data:
            await message.answer(f"❌ Строка {row_number} не найдена или пуста.")
            return
        
        # Форматируем данные
        columns = self.sheets_service.get_columns()
        formatted_text = format_row_data(row_data, columns)
        keyboard = Keyboards.create_row_actions_keyboard(row_number)
        
        await message.answer(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def cols_command(self, message: Message):
        """Обработчик команды /cols"""
        user_id = message.from_user.id
        self.logger.info(f"Пользователь {user_id} запрашивает список столбцов")
        
        columns = self.sheets_service.get_columns()
        formatted_text = format_columns_list(columns)
        
        await message.answer(formatted_text, parse_mode="Markdown")
    
    async def edit_command(self, message: Message):
        """Обработчик команды /edit"""
        user_id = message.from_user.id
        command_args = message.text.split(maxsplit=1)
        
        if len(command_args) < 2:
            await message.answer("❌ Укажите номер строки для редактирования.\nПример: `/edit 5`", parse_mode="Markdown")
            return
        
        try:
            row_number = int(command_args[1].strip())
        except ValueError:
            await message.answer("❌ Номер строки должен быть числом.")
            return
        
        if row_number < 2:
            await message.answer("❌ Номер строки должен быть больше 1 (первая строка - заголовки).")
            return
        
        self.logger.info(f"Пользователь {user_id} хочет редактировать строку {row_number}")
        
        # Проверяем существование строки
        row_data = self.sheets_service.get_row_by_number(row_number)
        
        if not row_data:
            await message.answer(f"❌ Строка {row_number} не найдена или пуста.")
            return
        
        # Показываем выбор полей для редактирования
        columns = self.sheets_service.get_columns()
        keyboard = Keyboards.create_edit_field_keyboard(row_number, columns)
        
        formatted_text = format_row_data(row_data, columns)
        await message.answer(f"{formatted_text}\n\n📝 **Выберите поле для редактирования:**", 
                           reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_row_selection(self, callback: CallbackQuery):
        """Обработчик выбора строки из результатов поиска"""
        user_id = callback.from_user.id
        row_number = int(callback.data.split(":")[1])
        
        self.logger.info(f"Пользователь {user_id} выбрал строку {row_number}")
        
        # Получаем данные строки
        row_data = self.sheets_service.get_row_by_number(row_number)
        
        if not row_data:
            await callback.answer("❌ Строка не найдена", show_alert=True)
            return
        
        # Форматируем данные
        columns = self.sheets_service.get_columns()
        formatted_text = format_row_data(row_data, columns)
        keyboard = Keyboards.create_row_actions_keyboard(row_number)
        
        await callback.message.edit_text(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
    
    async def handle_edit_row(self, callback: CallbackQuery):
        """Обработчик начала редактирования строки"""
        user_id = callback.from_user.id
        row_number = int(callback.data.split(":")[1])
        
        self.logger.info(f"Пользователь {user_id} начинает редактирование строки {row_number}")
        
        columns = self.sheets_service.get_columns()
        keyboard = Keyboards.create_edit_field_keyboard(row_number, columns)
        
        await callback.message.edit_text(
            f"📝 **Редактирование строки {row_number}**\n\nВыберите поле для изменения:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def handle_edit_field(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик выбора поля для редактирования"""
        user_id = callback.from_user.id
        data_parts = callback.data.split(":")
        row_number = int(data_parts[1])
        column_number = int(data_parts[2])
        
        columns = self.sheets_service.get_columns()
        column_name = columns[column_number - 1] if column_number <= len(columns) else f"Столбец {column_number}"
        
        self.logger.info(f"Пользователь {user_id} редактирует поле '{column_name}' в строке {row_number}")
        
        # Сохраняем данные в состояние
        await state.update_data({
            'row_number': row_number,
            'column_number': column_number,
            'column_name': column_name
        })
        
        await state.set_state(EditStates.waiting_for_new_value)
        
        await callback.message.edit_text(
            f"✏️ **Редактирование поля '{column_name}'**\n\n"
            f"Строка: {row_number}\n"
            f"Введите новое значение:",
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def handle_new_value_input(self, message: Message, state: FSMContext):
        """Обработчик ввода нового значения"""
        user_id = message.from_user.id
        new_value = message.text.strip()
        
        # Получаем данные из состояния
        data = await state.get_data()
        row_number = data['row_number']
        column_number = data['column_number']
        column_name = data['column_name']
        
        self.logger.info(f"Пользователь {user_id} обновляет '{column_name}' в строке {row_number} на '{new_value}'")
        
        # Обновляем ячейку
        success = self.sheets_service.update_cell(row_number, column_number, new_value)
        
        if success:
            await message.answer(
                f"✅ **Поле обновлено успешно!**\n\n"
                f"Строка: {row_number}\n"
                f"Поле: {column_name}\n"
                f"Новое значение: {new_value}",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Ошибка при обновлении поля. Попробуйте позже.")
        
        # Очищаем состояние
        await state.clear()
    
    async def handle_refresh_row(self, callback: CallbackQuery):
        """Обработчик обновления отображения строки"""
        user_id = callback.from_user.id
        row_number = int(callback.data.split(":")[1])
        
        self.logger.info(f"Пользователь {user_id} обновляет отображение строки {row_number}")
        
        # Получаем актуальные данные
        row_data = self.sheets_service.get_row_by_number(row_number)
        
        if not row_data:
            await callback.answer("❌ Строка не найдена", show_alert=True)
            return
        
        # Форматируем данные
        columns = self.sheets_service.get_columns()
        formatted_text = format_row_data(row_data, columns)
        keyboard = Keyboards.create_row_actions_keyboard(row_number)
        
        await callback.message.edit_text(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer("🔄 Данные обновлены")
    
    async def handle_back_to_row(self, callback: CallbackQuery):
        """Обработчик возврата к просмотру строки"""
        user_id = callback.from_user.id
        row_number = int(callback.data.split(":")[1])
        
        self.logger.info(f"Пользователь {user_id} возвращается к просмотру строки {row_number}")
        
        # Получаем данные строки
        row_data = self.sheets_service.get_row_by_number(row_number)
        
        if not row_data:
            await callback.answer("❌ Строка не найдена", show_alert=True)
            return
        
        # Форматируем данные
        columns = self.sheets_service.get_columns()
        formatted_text = format_row_data(row_data, columns)
        keyboard = Keyboards.create_row_actions_keyboard(row_number)
        
        await callback.message.edit_text(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
    
    async def handle_confirm_action(self, callback: CallbackQuery):
        """Обработчик подтверждения действий"""
        await callback.answer("✅ Действие подтверждено")
    
    async def handle_cancel(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик отмены действий"""
        user_id = callback.from_user.id
        self.logger.info(f"Пользователь {user_id} отменил действие")
        
        # Очищаем состояние если есть
        await state.clear()
        
        await callback.message.edit_text("❌ Действие отменено.")
        await callback.answer()

    # === НОВЫЕ ОБРАБОТЧИКИ КНОПОК МЕНЮ ===
    
    async def handle_search_button(self, message: Message, state: FSMContext):
        """Обработчик кнопки поиска"""
        await state.set_state(SearchStates.waiting_for_search_value)
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(
            "🔍 **Поиск по значению**\n\nВведите значение для поиска в таблице:", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    async def handle_get_row_button(self, message: Message, state: FSMContext):
        """Обработчик кнопки получения строки по номеру"""
        await state.set_state(SearchStates.waiting_for_row_number)
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(
            "📊 **Получить строку по номеру**\n\nВведите номер строки:", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    async def handle_show_columns_button(self, message: Message):
        """Обработчик кнопки показа столбцов"""
        user_id = message.from_user.id
        self.logger.info(f"Пользователь {user_id} запросил список столбцов")
        
        columns = self.sheets_service.get_columns()
        
        if not columns:
            await message.answer("❌ Не удалось получить список столбцов")
            return
        
        # Формируем HTML список столбцов
        text_parts = ["📊 <b>Столбцы таблицы:</b>\n"]
        
        for i, column_name in enumerate(columns, 1):
            if column_name:
                safe_column = str(column_name).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                text_parts.append(f"{i}. <b>{safe_column}</b>")
            else:
                text_parts.append(f"{i}. <i>(пустой столбец)</i>")
        
        columns_text = "\n".join(text_parts)
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(columns_text, reply_markup=keyboard, parse_mode="HTML")
    
    async def handle_edit_button(self, message: Message, state: FSMContext):
        """Обработчик кнопки редактирования"""
        await state.set_state(SearchStates.waiting_for_edit_row_number)
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(
            "✏️ **Редактировать строку**\n\nВведите номер строки для редактирования:", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    async def handle_help_button(self, message: Message):
        """Обработчик кнопки помощи"""
        help_text = """
📝 **Справка по использованию бота**

🔍 **Поиск по значению** - найти строки, содержащие определенное значение
📊 **Получить строку по номеру** - показать конкретную строку по ее номеру
📄 **Все строки** - просмотр всех строк с пагинацией и навигацией
📋 **Показать столбцы** - отобразить названия всех столбцов таблицы
✏️ **Редактировать строку** - изменить значения в определенной строке

**Команды:**
/start - показать главное меню
/find [значение] - поиск по значению
/row [номер] - получить строку
/cols - показать столбцы
/edit [номер] - редактировать строку

**Навигация по страницам:**
• ⬅️ ➡️ - переход между страницами
• ⏪ ⏩ - быстрый переход к началу/концу
• 📄 X/Y - текущая страница из общего количества

**Примеры:**
• Нажмите "🔍 Поиск по значению" и введите email
• Нажмите "📊 Получить строку по номеру" и введите 5
• Нажмите "📄 Все строки" для просмотра с пагинацией
• Используйте кнопки для удобной навигации
        """
        
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(help_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_about_button(self, message: Message):
        """Обработчик кнопки о боте"""
        about_text = """
ℹ️ **О боте**

Бот для удобной работы с Google Таблицами прямо из Telegram.

**Возможности:**
• Поиск данных в таблице
• Просмотр строк по номеру
• Просмотр всех строк с пагинацией
• Удобная навигация по страницам
• Редактирование данных
• Просмотр структуры таблицы

**Новые функции:**
• 📄 Слайдер для просмотра всех строк
• ⬅️ ➡️ Навигация между страницами
• ⏪ ⏩ Быстрый переход к началу/концу
• 📊 Отображение номера страницы

**Безопасность:**
• Доступ только для авторизованных пользователей
• Все действия логируются
• Защита от спама
        """
        
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await message.answer(about_text, reply_markup=keyboard, parse_mode="Markdown")
    
    # === ОБРАБОТЧИКИ СОСТОЯНИЙ FSM ===
    
    async def handle_search_input(self, message: Message, state: FSMContext):
        """Обработчик ввода значения для поиска"""
        search_value = message.text.strip()
        user_id = message.from_user.id
        
        self.logger.info(f"Пользователь {user_id} выполняет поиск через меню: '{search_value}'")
        
        await message.answer("🔍 Выполняю поиск...")
        
        # Поиск в таблице
        found_rows = self.sheets_service.search_in_sheet(search_value)
        
        if not found_rows:
            keyboard = Keyboards.create_back_to_menu_keyboard()
            await message.answer(
                f"🔍 По запросу '**{escape_markdown(search_value)}**' ничего не найдено.", 
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # Форматируем результаты
            results_text = format_search_results(found_rows, search_value)
            keyboard = Keyboards.create_row_selection_keyboard(found_rows)
            await message.answer(results_text, reply_markup=keyboard, parse_mode="Markdown")
        
        await state.clear()
    
    async def handle_row_number_input(self, message: Message, state: FSMContext):
        """Обработчик ввода номера строки"""
        try:
            row_number = int(message.text.strip())
            user_id = message.from_user.id
            
            self.logger.info(f"Пользователь {user_id} запросил строку {row_number} через меню")
            
            await message.answer("📊 Получаю данные строки...")
            
            # Получаем данные строки
            row_data = self.sheets_service.get_row_by_number(row_number)
            
            if not row_data:
                keyboard = Keyboards.create_back_to_menu_keyboard()
                await message.answer(
                    f"❌ Строка с номером **{row_number}** не найдена.", 
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                # Форматируем данные
                columns = self.sheets_service.get_columns()
                formatted_text = format_row_data(row_data, columns)
                keyboard = Keyboards.create_row_actions_keyboard(row_number)
                
                await message.answer(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
            
        except ValueError:
            await message.answer("❌ Введите корректный номер строки (число)")
            return
        
        await state.clear()
    
    async def handle_edit_row_number_input(self, message: Message, state: FSMContext):
        """Обработчик ввода номера строки для редактирования"""
        try:
            row_number = int(message.text.strip())
            user_id = message.from_user.id
            
            self.logger.info(f"Пользователь {user_id} хочет редактировать строку {row_number}")
            
            await message.answer("✏️ Получаю данные для редактирования...")
            
            # Получаем данные строки
            row_data = self.sheets_service.get_row_by_number(row_number)
            
            if not row_data:
                keyboard = Keyboards.create_back_to_menu_keyboard()
                await message.answer(
                    f"❌ Строка с номером **{row_number}** не найдена.", 
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                # Показываем данные и кнопки редактирования
                columns = self.sheets_service.get_columns()
                formatted_text = format_row_data(row_data, columns)
                keyboard = Keyboards.create_row_actions_keyboard(row_number)
                
                await message.answer(formatted_text, reply_markup=keyboard, parse_mode="Markdown")
            
        except ValueError:
            await message.answer("❌ Введите корректный номер строки (число)")
            return
        
        await state.clear()
    
    # === CALLBACK ОБРАБОТЧИКИ ===
    
    async def handle_back_to_menu(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик возврата в главное меню"""
        await state.clear()
        
        welcome_text = """
🏠 **Главное меню**

Выберите действие, используя кнопки ниже:
        """
        
        keyboard = Keyboards.create_main_menu()
        await callback.message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
    
    async def handle_action_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик инлайн действий"""
        action = callback.data.split(":")[1]
        
        if action == "search":
            await self.handle_search_button(callback.message, state)
        elif action == "get_row":
            await self.handle_get_row_button(callback.message, state)
        elif action == "show_columns":
            await self.handle_show_columns_button(callback.message)
        elif action == "edit_row":
            await self.handle_edit_button(callback.message, state)
        elif action == "all_rows":
            await self.handle_all_rows_button(callback.message)
        
        await callback.answer()

    # === ОБРАБОТЧИК ВСЕХ СТРОК ===
    
    async def handle_all_rows_button(self, message: Message):
        """Обработчик кнопки показа всех строк"""
        user_id = message.from_user.id
        self.logger.info(f"Пользователь {user_id} запросил все строки")
        
        try:
            await message.answer("📄 Загружаю все строки...")
            
            # Получаем первую страницу
            await self._send_rows_page(message, page=1)
        except Exception as e:
            self.logger.error(f"Ошибка в handle_all_rows_button: {e}")
            await message.answer("❌ Произошла ошибка при загрузке строк. Попробуйте позже.")
    
    async def _send_rows_page(self, message, page=1, edit_message=False):
        """Отправить страницу со строками"""
        try:
            rows_per_page = 5
            self.logger.info(f"Запрос страницы {page} с {rows_per_page} строками на страницу")
            
            page_rows, total_pages, total_rows = self.sheets_service.get_all_rows_paginated(page, rows_per_page)
            
            self.logger.info(f"Получено: {len(page_rows)} строк, страниц: {total_pages}, всего строк: {total_rows}")
            
            if not page_rows:
                keyboard = Keyboards.create_back_to_menu_keyboard()
                text = "📄 <b>Все строки</b>\n\n❌ Строки не найдены или таблица пуста."
                
                if edit_message:
                    await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
                else:
                    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
                return
            
            # Формируем текст с информацией о строках
            text_parts = [
                f"📄 <b>Все строки</b> (Страница {page}/{total_pages})",
                f"📊 Всего строк: {total_rows}",
                "",
                "<b>Строки на текущей странице:</b>"
            ]
            
            # Добавляем информацию о каждой строке
            columns = self.sheets_service.get_columns()
            for row_info in page_rows:
                row_number = row_info['row_number']
                row_data = row_info['data']
                
                # Создаем краткое описание строки
                preview_parts = []
                for i, value in enumerate(row_data[:3]):  # Первые 3 значения
                    if value and i < len(columns):
                        column_name = columns[i] if i < len(columns) else f"Col{i+1}"
                        safe_column = str(column_name).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        safe_value = str(value)[:20].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        preview_parts.append(f"{safe_column}: {safe_value}")
                
                preview = " | ".join(preview_parts) if preview_parts else "Пустая строка"
                text_parts.append(f"<b>[{row_number}]</b> {preview}")
            
            text_parts.append("")
            text_parts.append("👆 Нажмите на строку для просмотра или выберите действие:")
            
            result_text = "\n".join(text_parts)
            keyboard = Keyboards.create_pagination_keyboard(page, total_pages, page_rows, "page")
            
            if edit_message:
                await message.edit_text(result_text, reply_markup=keyboard, parse_mode="HTML")
            else:
                await message.answer(result_text, reply_markup=keyboard, parse_mode="HTML")
        
        except Exception as e:
            self.logger.error(f"Ошибка в _send_rows_page: {e}")
            error_text = "❌ Произошла ошибка при загрузке страницы. Попробуйте позже."
            if edit_message:
                await message.edit_text(error_text)
            else:
                await message.answer(error_text)
    
    async def handle_pagination(self, callback: CallbackQuery):
        """Обработчик навигации по страницам"""
        user_id = callback.from_user.id
        data_parts = callback.data.split(":")
        
        if len(data_parts) < 3:
            await callback.answer("❌ Ошибка навигации")
            return
        
        action = data_parts[1]  # prev, next, goto, info
        
        if action == "info":
            await callback.answer("ℹ️ Информация о странице", show_alert=True)
            return
        
        try:
            current_page = int(data_parts[2])
            new_page = current_page
            
            if action == "prev":
                new_page = max(1, current_page - 1)
            elif action == "next":
                new_page = current_page + 1
            elif action == "goto":
                new_page = current_page  # Уже передан правильный номер страницы
            
            self.logger.info(f"Пользователь {user_id} переходит на страницу {new_page}")
            
            # Отправляем новую страницу
            await self._send_rows_page(callback.message, new_page, edit_message=True)
            await callback.answer(f"📄 Страница {new_page}")
        
        except (ValueError, IndexError) as e:
            self.logger.error(f"Ошибка обработки пагинации: {e}")
            await callback.answer("❌ Ошибка навигации")
        
        # Убираем этот дублированный callback.answer()

    # === ВРЕМЕННЫЙ ОТЛАДОЧНЫЙ ОБРАБОТЧИК ===
    
    async def handle_unhandled_text(self, message: Message):
        """Временный обработчик для отладки необработанных сообщений"""
        user_id = message.from_user.id
        text = message.text
        self.logger.warning(f"НЕОБРАБОТАННОЕ СООБЩЕНИЕ от пользователя {user_id}: '{text}' (длина: {len(text)}, bytes: {text.encode('utf-8')})")
        
        # Проверяем точное совпадение с нашими кнопками (включая искаженные символы)
        if text in ["📄 Все строки"]:
            self.logger.info("Совпадение найдено! Вызываем handle_all_rows_button")
            await self.handle_all_rows_button(message)
        elif text in ["📋 Показать столбцы"]:
            self.logger.info("Совпадение найдено! Вызываем handle_show_columns_button")
            await self.handle_show_columns_button(message)
        elif text in ["🔍 Поиск по значению"]:
            self.logger.info("Совпадение найдено! Вызываем handle_search_button")
            await self.handle_search_button(message, state=None)
        elif text in ["📊 Получить строку по номеру"]:
            self.logger.info("Совпадение найдено! Вызываем handle_get_row_button")
            await self.handle_get_row_button(message, state=None)
        elif text in ["✏️ Редактировать строку"]:
            self.logger.info("Совпадение найдено! Вызываем handle_edit_button")
            await self.handle_edit_button(message, state=None)
        elif text in ["➕ Создать новую строку"]:
            self.logger.info("Совпадение найдено! Вызываем handle_create_new_row_button")
            await self.handle_create_new_row_button(message)
        elif text in ["🧮 Работа с формулами"]:
            self.logger.info("Совпадение найдено! Вызываем handle_formulas_button")
            await self.handle_formulas_button(message)
        elif text in ["📝 Помощь"]:
            self.logger.info("Совпадение найдено! Вызываем handle_help_button")
            await self.handle_help_button(message)
        elif text in ["ℹ️ О боте"]:
            self.logger.info("Совпадение найдено! Вызываем handle_about_button")
            await self.handle_about_button(message)
        else:
            await message.answer(f"🤔 Неизвестная команда: '{text}'\nИспользуйте кнопки меню.")

    # === ОБРАБОТЧИКИ СОЗДАНИЯ НОВОЙ СТРОКИ ===
    
    async def handle_create_new_row_button(self, message: Message):
        """Обработчик кнопки создания новой строки"""
        user_id = message.from_user.id
        self.logger.info(f"Пользователь {user_id} начинает создание новой строки")
        
        columns = self.sheets_service.get_columns()
        
        if not columns:
            await message.answer("❌ Не удалось получить структуру таблицы")
            return
        
        # Инициализируем пустую строку в состоянии
        new_row_data = [''] * len(columns)
        
        # Отправляем интерфейс для заполнения
        await self._show_new_row_interface(message, columns, new_row_data)
    
    async def _show_new_row_interface(self, message, columns, row_data, edit_message=False):
        """Показать интерфейс создания новой строки"""
        text_parts = ["➕ <b>Создание новой строки</b>\n"]
        
        # Показываем текущее состояние полей
        for i, (column_name, value) in enumerate(zip(columns, row_data)):
            if column_name:
                safe_column = str(column_name).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                if value:
                    safe_value = str(value).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    text_parts.append(f"<b>{i+1}. {safe_column}:</b> {safe_value}")
                else:
                    text_parts.append(f"<b>{i+1}. {safe_column}:</b> <i>(не заполнено)</i>")
        
        text_parts.append("\n👆 Нажмите на поле для заполнения:")
        
        text = "\n".join(text_parts)
        keyboard = Keyboards.create_new_row_keyboard(columns)
        
        if edit_message:
            await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    async def handle_fill_field(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик выбора поля для заполнения"""
        user_id = callback.from_user.id
        data_parts = callback.data.split(":")
        row_type = data_parts[1]  # "new"
        column_number = int(data_parts[2])
        
        if row_type != "new":
            await callback.answer("❌ Ошибка обработки")
            return
        
        columns = self.sheets_service.get_columns()
        column_name = columns[column_number - 1] if column_number <= len(columns) else f"Столбец {column_number}"
        
        self.logger.info(f"Пользователь {user_id} заполняет поле '{column_name}' для новой строки")
        
        # Получаем текущие данные строки или создаем новые
        current_data = await state.get_data()
        row_data = current_data.get('new_row_data', [''] * len(columns))
        
        # Сохраняем состояние
        await state.update_data({
            'new_row_data': row_data,
            'filling_column': column_number,
            'column_name': column_name
        })
        
        await state.set_state(NewRowStates.filling_field)
        
        current_value = row_data[column_number - 1] if column_number <= len(row_data) else ""
        current_text = f" (текущее: {current_value})" if current_value else ""
        
        await callback.message.edit_text(
            f"✏️ <b>Заполнение поля '{column_name}'</b>\n\n"
            f"Введите значение{current_text}:",
            parse_mode="HTML"
        )
        await callback.answer()
    
    async def handle_new_row_field_input(self, message: Message, state: FSMContext):
        """Обработчик ввода значения для поля новой строки"""
        user_id = message.from_user.id
        new_value = message.text.strip()
        
        # Получаем данные из состояния
        data = await state.get_data()
        row_data = data.get('new_row_data', [])
        column_number = data.get('filling_column', 1)
        column_name = data.get('column_name', 'Поле')
        
        self.logger.info(f"Пользователь {user_id} ввел значение '{new_value}' для поля '{column_name}'")
        
        # Обновляем данные строки
        if column_number <= len(row_data):
            row_data[column_number - 1] = new_value
        
        # Сохраняем обновленные данные
        await state.update_data({'new_row_data': row_data})
        await state.clear()
        
        # Показываем обновленный интерфейс
        columns = self.sheets_service.get_columns()
        await message.answer(f"✅ Поле '{column_name}' заполнено: {new_value}")
        await self._show_new_row_interface(message, columns, row_data)
    
    async def handle_save_new_row(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик сохранения новой строки"""
        user_id = callback.from_user.id
        
        # Получаем данные строки
        data = await state.get_data()
        row_data = data.get('new_row_data', [])
        
        if not any(row_data):
            await callback.answer("❌ Заполните хотя бы одно поле", show_alert=True)
            return
        
        self.logger.info(f"Пользователь {user_id} сохраняет новую строку")
        
        # Сохраняем в Google Sheets
        new_row_number = self.sheets_service.add_new_row(row_data)
        
        if new_row_number:
            await callback.message.edit_text(
                f"✅ <b>Новая строка успешно создана!</b>\n\n"
                f"Номер строки: <b>{new_row_number}</b>\n"
                f"Заполненных полей: <b>{sum(1 for x in row_data if x)}</b>",
                parse_mode="HTML"
            )
            await state.clear()
        else:
            await callback.message.edit_text("❌ Ошибка при сохранении строки. Попробуйте позже.")
        
        await callback.answer()
    
    async def handle_clear_new_row(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик очистки полей новой строки"""
        user_id = callback.from_user.id
        self.logger.info(f"Пользователь {user_id} очищает поля новой строки")
        
        columns = self.sheets_service.get_columns()
        empty_row_data = [''] * len(columns)
        
        # Очищаем данные в состоянии
        await state.update_data({'new_row_data': empty_row_data})
        
        await self._show_new_row_interface(callback.message, columns, empty_row_data, edit_message=True)
        await callback.answer("🗑️ Все поля очищены")
    
    async def handle_cancel_new_row(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик отмены создания новой строки"""
        user_id = callback.from_user.id
        self.logger.info(f"Пользователь {user_id} отменил создание новой строки")
        
        await state.clear()
        
        await callback.message.edit_text("❌ Создание новой строки отменено.")
        await callback.answer()

    # === ОБРАБОТЧИКИ РАБОТЫ С ФОРМУЛАМИ ===
    
    async def handle_formulas_button(self, message: Message):
        """Обработчик кнопки работы с формулами"""
        user_id = message.from_user.id
        self.logger.info(f"Пользователь {user_id} открыл меню формул")
        
        keyboard = Keyboards.create_formulas_menu()
        await message.answer(
            "🧮 <b>Работа с формулами Google Sheets</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_formula_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик callback для работы с формулами"""
        user_id = callback.from_user.id
        action = callback.data.split(":")[1]
        
        if action == "add":
            await self._handle_add_formula(callback, state)
        elif action == "view":
            await self._handle_view_formula(callback, state)
        elif action == "help":
            await self._handle_formula_help(callback)
        elif action == "examples":
            await self._handle_formula_examples(callback)
        elif action == "validate":
            await self._handle_validate_formula(callback, state)
        
        await callback.answer()
    
    async def _handle_add_formula(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик добавления формулы"""
        await state.set_state(FormulaStates.waiting_for_cell_position)
        
        await callback.message.edit_text(
            "➕ <b>Добавление формулы в ячейку</b>\n\n"
            "Укажите позицию ячейки в формате:\n"
            "• <code>A1</code> - столбец A, строка 1\n"
            "• <code>B5</code> - столбец B, строка 5\n"
            "• <code>2,3</code> - строка 2, столбец 3\n\n"
            "Введите позицию ячейки:",
            parse_mode="HTML"
        )
    
    async def _handle_view_formula(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик просмотра формулы"""
        await state.set_state(FormulaStates.waiting_for_cell_position)
        await state.update_data({'action': 'view'})
        
        await callback.message.edit_text(
            "👁️ <b>Просмотр формулы в ячейке</b>\n\n"
            "Укажите позицию ячейки для просмотра формулы:\n"
            "• <code>A1</code> - столбец A, строка 1\n"
            "• <code>B5</code> - столбец B, строка 5\n"
            "• <code>2,3</code> - строка 2, столбец 3\n\n"
            "Введите позицию ячейки:",
            parse_mode="HTML"
        )
    
    async def _handle_formula_help(self, callback: CallbackQuery):
        """Обработчик справки по формулам"""
        help_text = """
📚 <b>Справочник формул Google Sheets</b>

<b>🧮 Математические функции:</b>
• <code>=SUM(A1:A10)</code> - сумма диапазона
• <code>=AVERAGE(A1:A10)</code> - среднее значение
• <code>=COUNT(A1:A10)</code> - подсчет чисел
• <code>=MAX(A1:A10)</code> - максимальное значение
• <code>=MIN(A1:A10)</code> - минимальное значение
• <code>=ROUND(A1,2)</code> - округление до 2 знаков

<b>📝 Текстовые функции:</b>
• <code>=CONCATENATE(A1,B1)</code> - объединение текста
• <code>=LEN(A1)</code> - длина текста
• <code>=UPPER(A1)</code> - в верхний регистр
• <code>=LOWER(A1)</code> - в нижний регистр

<b>📅 Функции даты:</b>
• <code>=TODAY()</code> - сегодняшняя дата
• <code>=NOW()</code> - текущие дата и время
• <code>=DATEDIF(A1,B1,"D")</code> - разность в днях

<b>❓ Логические функции:</b>
• <code>=IF(A1>10,"Да","Нет")</code> - условие
• <code>=AND(A1>0,B1<100)</code> - логическое И
• <code>=OR(A1=1,B1=2)</code> - логическое ИЛИ

<b>🔍 Функции поиска:</b>
• <code>=VLOOKUP(A1,B:D,2,0)</code> - вертикальный поиск
• <code>=INDEX(B:B,MATCH(A1,C:C,0))</code> - индекс+поиск
        """
        
        keyboard = Keyboards.create_back_to_menu_keyboard()
        await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="HTML")
    
    async def _handle_formula_examples(self, callback: CallbackQuery):
        """Обработчик примеров формул"""
        keyboard = Keyboards.create_formula_examples_keyboard()
        await callback.message.edit_text(
            "🧮 <b>Примеры формул</b>\n\n"
            "Выберите категорию для просмотра примеров:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def _handle_validate_formula(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик проверки формулы"""
        await state.set_state(FormulaStates.waiting_for_validation)
        
        await callback.message.edit_text(
            "🔧 <b>Проверка формулы</b>\n\n"
            "Введите формулу для проверки:\n"
            "Например: <code>=SUM(A1:A10)</code>\n\n"
            "Введите формулу:",
            parse_mode="HTML"
        )
    
    async def handle_cell_position_input(self, message: Message, state: FSMContext):
        """Обработчик ввода позиции ячейки"""
        user_id = message.from_user.id
        position = message.text.strip().upper()
        
        # Парсим позицию ячейки
        row_number, column_number = self._parse_cell_position(position)
        
        if not row_number or not column_number:
            await message.answer(
                "❌ Неверный формат позиции ячейки.\n"
                "Используйте формат: A1, B5 или 2,3"
            )
            return
        
        # Проверяем действие
        data = await state.get_data()
        action = data.get('action', 'add')
        
        if action == 'view':
            # Просматриваем формулу
            formula = self.sheets_service.get_cell_formula(row_number, column_number)
            
            if formula:
                await message.answer(
                    f"👁️ <b>Формула в ячейке {position}</b>\n\n"
                    f"<code>{formula}</code>",
                    parse_mode="HTML"
                )
            else:
                await message.answer(f"❌ В ячейке {position} нет формулы или ячейка пуста")
            
            await state.clear()
        else:
            # Добавляем формулу
            await state.update_data({
                'row_number': row_number,
                'column_number': column_number,
                'position': position
            })
            await state.set_state(FormulaStates.waiting_for_formula)
            
            await message.answer(
                f"➕ <b>Добавление формулы в ячейку {position}</b>\n\n"
                f"Введите формулу (без знака = в начале):\n"
                f"Например: <code>SUM(A1:A10)</code>\n\n"
                f"Введите формулу:",
                parse_mode="HTML"
            )
    
    async def handle_formula_input(self, message: Message, state: FSMContext):
        """Обработчик ввода формулы"""
        user_id = message.from_user.id
        formula = message.text.strip()
        
        # Получаем данные из состояния
        data = await state.get_data()
        row_number = data['row_number']
        column_number = data['column_number']
        position = data['position']
        
        self.logger.info(f"Пользователь {user_id} добавляет формулу '{formula}' в ячейку {position}")
        
        # Валидируем формулу
        is_valid, message_text = self.sheets_service.validate_formula(formula)
        
        if not is_valid:
            await message.answer(f"❌ Ошибка в формуле: {message_text}")
            return
        
        # Добавляем формулу
        success = self.sheets_service.update_cell_with_formula(row_number, column_number, formula)
        
        if success:
            await message.answer(
                f"✅ <b>Формула успешно добавлена!</b>\n\n"
                f"Ячейка: <b>{position}</b>\n"
                f"Формула: <code>={formula}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при добавлении формулы. Попробуйте позже.")
        
        await state.clear()
    
    async def handle_validation_input(self, message: Message, state: FSMContext):
        """Обработчик проверки формулы"""
        formula = message.text.strip()
        
        is_valid, message_text = self.sheets_service.validate_formula(formula)
        
        if is_valid:
            await message.answer(f"✅ <b>Формула корректна!</b>\n\n<code>={formula}</code>", parse_mode="HTML")
        else:
            await message.answer(f"❌ <b>Ошибка в формуле:</b>\n{message_text}", parse_mode="HTML")
        
        await state.clear()
    
    async def handle_example_callback(self, callback: CallbackQuery):
        """Обработчик примеров формул"""
        example_type = callback.data.split(":")[1]
        
        examples = {
            "sum": "➕ <b>Сумма (SUM)</b>\n\n<code>=SUM(A1:A10)</code> - сумма диапазона A1:A10\n<code>=SUM(A1,B1,C1)</code> - сумма отдельных ячеек\n<code>=SUM(A:A)</code> - сумма всего столбца A",
            "average": "📊 <b>Среднее (AVERAGE)</b>\n\n<code>=AVERAGE(A1:A10)</code> - среднее значение диапазона\n<code>=AVERAGE(A1,B1,C1)</code> - среднее отдельных ячеек\n<code>=AVERAGEIF(A1:A10,\">10\")</code> - среднее с условием",
            "count": "📈 <b>Подсчет (COUNT)</b>\n\n<code>=COUNT(A1:A10)</code> - количество чисел\n<code>=COUNTA(A1:A10)</code> - количество непустых ячеек\n<code>=COUNTIF(A1:A10,\">10\")</code> - количество с условием",
            "vlookup": "🔍 <b>Поиск (VLOOKUP)</b>\n\n<code>=VLOOKUP(A1,B:D,2,0)</code> - точный поиск\n<code>=VLOOKUP(A1,B:D,3,1)</code> - приблизительный поиск\n<code>=IFERROR(VLOOKUP(A1,B:D,2,0),\"Не найдено\")</code> - с обработкой ошибок",
            "date": "📅 <b>Дата (TODAY/NOW)</b>\n\n<code>=TODAY()</code> - сегодняшняя дата\n<code>=NOW()</code> - текущая дата и время\n<code>=DATEDIF(A1,TODAY(),\"D\")</code> - дней до сегодня",
            "text": "🔤 <b>Текст (CONCATENATE)</b>\n\n<code>=CONCATENATE(A1,\" \",B1)</code> - объединение с пробелом\n<code>=A1&\" \"&B1</code> - то же самое, короче\n<code>=UPPER(A1)</code> - в верхний регистр",
            "if": "❓ <b>Условие (IF)</b>\n\n<code>=IF(A1>10,\"Больше\",\"Меньше\")</code> - простое условие\n<code>=IF(A1=\"\",\"Пусто\",A1)</code> - проверка на пустоту\n<code>=IF(AND(A1>0,B1<100),\"OK\",\"Ошибка\")</code> - с логикой",
            "round": "🔢 <b>Округление (ROUND)</b>\n\n<code>=ROUND(A1,2)</code> - до 2 знаков после запятой\n<code>=ROUNDUP(A1,0)</code> - округление вверх\n<code>=ROUNDDOWN(A1,0)</code> - округление вниз"
        }
        
        example_text = examples.get(example_type, "Пример не найден")
        
        keyboard = Keyboards.create_formula_examples_keyboard()
        await callback.message.edit_text(example_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    
    async def handle_back_to_formulas(self, callback: CallbackQuery):
        """Обработчик возврата к меню формул"""
        keyboard = Keyboards.create_formulas_menu()
        await callback.message.edit_text(
            "🧮 <b>Работа с формулами Google Sheets</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    
    def _parse_cell_position(self, position):
        """Парсинг позиции ячейки"""
        try:
            if ',' in position:
                # Формат "2,3" (строка, столбец)
                parts = position.split(',')
                if len(parts) == 2:
                    row_number = int(parts[0].strip())
                    column_number = int(parts[1].strip())
                    return row_number, column_number
            else:
                # Формат "A1" (столбец буквой, строка числом)
                import re
                match = re.match(r'^([A-Z]+)(\d+)$', position)
                if match:
                    column_letters = match.group(1)
                    row_number = int(match.group(2))
                    
                    # Преобразуем буквы столбца в число
                    column_number = 0
                    for char in column_letters:
                        column_number = column_number * 26 + (ord(char) - ord('A') + 1)
                    
                    return row_number, column_number
            
            return None, None
            
        except (ValueError, AttributeError):
            return None, None
