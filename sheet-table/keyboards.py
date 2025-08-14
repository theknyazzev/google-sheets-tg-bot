from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    @staticmethod
    def create_main_menu():
        """Создать главное меню с кнопками"""
        keyboard = [
           [KeyboardButton(text="🔍 Поиск по значению")],
            [KeyboardButton(text="📊 Получить строку по номеру")],
            [KeyboardButton(text="📄 Все строки")],
            [KeyboardButton(text="📋 Показать столбцы")],
            [KeyboardButton(text="✏️ Редактировать строку")],
            [KeyboardButton(text="➕ Создать новую строку")],
            [KeyboardButton(text="🧮 Работа с формулами")],
            [KeyboardButton(text="📝 Помощь"), KeyboardButton(text="ℹ️ О боте")]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="Выберите действие..."
        )

    @staticmethod
    def create_row_selection_keyboard(found_rows):
        """Создать клавиатуру для выбора строки из найденных"""
        keyboard = []
        
        for i, row_info in enumerate(found_rows[:10]):  # Максимум 10 строк
            row_number = row_info['row_number']
            # Берем первые несколько значений для preview
            preview_data = ' - '.join([str(val)[:20] for val in row_info['data'][:3] if val])
            button_text = f"{i+1}. [{row_number}] {preview_data[:40]}..."
            
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_row:{row_number}"
            )])
        
        # Кнопки навигации
        keyboard.append([
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_search"
            ),
            InlineKeyboardButton(
                text="🏠 Главное меню",
                callback_data="back_to_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_row_actions_keyboard(row_number):
        """Создать клавиатуру для действий со строкой"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"edit_row:{row_number}"
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data=f"refresh_row:{row_number}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_action"
                ),
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_to_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_edit_field_keyboard(row_number, columns):
        """Создать клавиатуру для выбора поля для редактирования"""
        keyboard = []
        
        for i, column_name in enumerate(columns[:10]):  # Максимум 10 столбцов
            if column_name:  # Только непустые названия столбцов
                keyboard.append([InlineKeyboardButton(
                    text=f"✏️ {column_name}",
                    callback_data=f"edit_field:{row_number}:{i+1}"
                )])
        
        keyboard.append([
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"back_to_row:{row_number}"
            ),
            InlineKeyboardButton(
                text="🏠 Главное меню",
                callback_data="back_to_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_confirm_keyboard(action_data):
        """Создать клавиатуру подтверждения"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"confirm:{action_data}"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="cancel_action"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_main_menu():
        """Создать главное меню с кнопками"""
        keyboard = [
            [KeyboardButton(text="🔍 Поиск по значению")],
            [KeyboardButton(text="📊 Получить строку по номеру")],
            [KeyboardButton(text="📄 Все строки")],
            [KeyboardButton(text="📋 Показать столбцы")],
            [KeyboardButton(text="✏️ Редактировать строку")],
            [KeyboardButton(text="➕ Создать новую строку")],
            [KeyboardButton(text="🧮 Работа с формулами")],
            [KeyboardButton(text="📝 Помощь"), KeyboardButton(text="ℹ️ О боте")]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="Выберите действие..."
        )

    @staticmethod
    def create_search_menu():
        """Создать инлайн меню для поиска"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="🔍 Поиск по значению",
                    callback_data="action:search"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Строка по номеру",
                    callback_data="action:get_row"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Показать столбцы",
                    callback_data="action:show_columns"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать строку",
                    callback_data="action:edit_row"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Все строки",
                    callback_data="action:all_rows"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_back_to_menu_keyboard():
        """Создать кнопку возврата в меню"""
        keyboard = [
            [InlineKeyboardButton(
                text="🏠 Главное меню",
                callback_data="back_to_menu"
            )]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_pagination_keyboard(current_page, total_pages, rows_on_page, prefix="page"):
        """Создать клавиатуру пагинации с навигацией по строкам"""
        keyboard = []
        
        # Кнопки для каждой строки на текущей странице
        for i, row_info in enumerate(rows_on_page):
            row_number = row_info['row_number']
            preview_data = ' - '.join([str(val)[:15] for val in row_info['data'][:2] if val])
            button_text = f"[{row_number}] {preview_data[:30]}..."
            
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_row:{row_number}"
            )])
        
        # Навигационные кнопки
        nav_buttons = []
        
        # Кнопка "Назад"
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️",
                callback_data=f"{prefix}:prev:{current_page}"
            ))
        
        # Показываем текущую страницу
        nav_buttons.append(InlineKeyboardButton(
            text=f"📄 {current_page}/{total_pages}",
            callback_data="page:info"
        ))
        
        # Кнопка "Вперед"
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️",
                callback_data=f"{prefix}:next:{current_page}"
            ))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Быстрая навигация (если много страниц)
        if total_pages > 3:
            quick_nav = []
            
            if current_page > 2:
                quick_nav.append(InlineKeyboardButton(
                    text="⏪ Начало",
                    callback_data=f"{prefix}:goto:1"
                ))
            
            if current_page < total_pages - 1:
                quick_nav.append(InlineKeyboardButton(
                    text="Конец ⏩",
                    callback_data=f"{prefix}:goto:{total_pages}"
                ))
            
            if quick_nav:
                keyboard.append(quick_nav)
        
        # Кнопка возврата в меню
        keyboard.append([InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="back_to_menu"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_new_row_keyboard(columns):
        """Создать клавиатуру для заполнения новой строки"""
        keyboard = []
        
        # Кнопки для заполнения каждого поля
        for i, column_name in enumerate(columns[:10]):  # Максимум 10 столбцов
            if column_name:
                keyboard.append([InlineKeyboardButton(
                    text=f"➕ {column_name}",
                    callback_data=f"fill_field:new:{i+1}"
                )])
        
        # Кнопки действий
        keyboard.append([
            InlineKeyboardButton(
                text="✅ Сохранить строку",
                callback_data="save_new_row"
            ),
            InlineKeyboardButton(
                text="🗑️ Очистить все",
                callback_data="clear_new_row"
            )
        ])
        
        keyboard.append([
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="cancel_new_row"
            ),
            InlineKeyboardButton(
                text="🏠 Главное меню",
                callback_data="back_to_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_formulas_menu():
        """Создать меню для работы с формулами"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="➕ Добавить формулу в ячейку",
                    callback_data="formula:add"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👁️ Посмотреть формулу ячейки",
                    callback_data="formula:view"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 Справочник формул",
                    callback_data="formula:help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧮 Примеры формул",
                    callback_data="formula:examples"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Проверить формулу",
                    callback_data="formula:validate"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_to_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_formula_examples_keyboard():
        """Создать клавиатуру с примерами формул"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="➕ Сумма (SUM)",
                    callback_data="example:sum"
                ),
                InlineKeyboardButton(
                    text="📊 Среднее (AVERAGE)",
                    callback_data="example:average"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📈 Подсчет (COUNT)",
                    callback_data="example:count"
                ),
                InlineKeyboardButton(
                    text="🔍 Поиск (VLOOKUP)",
                    callback_data="example:vlookup"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Дата (TODAY/NOW)",
                    callback_data="example:date"
                ),
                InlineKeyboardButton(
                    text="🔤 Текст (CONCATENATE)",
                    callback_data="example:text"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Условие (IF)",
                    callback_data="example:if"
                ),
                InlineKeyboardButton(
                    text="🔢 Округление (ROUND)",
                    callback_data="example:round"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к формулам",
                    callback_data="back_to_formulas"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
