def format_row_data(row_data, columns):
    """Форматировать данные строки для вывода"""
    if not row_data or not columns:
        return "❌ Нет данных для отображения"
    
    formatted_lines = []
    data = row_data['data']
    row_number = row_data['row_number']
    
    formatted_lines.append(f"📋 **Строка {row_number}:**\n")
    
    for i, (column_name, value) in enumerate(zip(columns, data)):
        if column_name:  # Только если есть название столбца
            display_value = escape_markdown(str(value)) if value else "—"
            safe_column = escape_markdown(str(column_name))
            formatted_lines.append(f"**{safe_column}:** {display_value}")
    
    return "\n".join(formatted_lines)


def format_search_results(found_rows, search_value):
    """Форматировать результаты поиска"""
    if not found_rows:
        return f"🔍 По запросу '**{search_value}**' ничего не найдено."
    
    result_lines = [f"🔍 Найдено {len(found_rows)} строк по запросу '**{search_value}**':\n"]
    
    for i, row_info in enumerate(found_rows[:10]):  # Показываем максимум 10 результатов
        row_number = row_info['row_number']
        # Берем первые 3 значения для превью
        preview_data = ' | '.join([str(val) for val in row_info['data'][:3] if val])
        if len(preview_data) > 60:
            preview_data = preview_data[:57] + "..."
        
        result_lines.append(f"{i+1}. **[{row_number}]** {preview_data}")
    
    if len(found_rows) > 10:
        result_lines.append(f"\n... и еще {len(found_rows) - 10} строк")
    
    result_lines.append("\n📌 Выберите строку для просмотра:")
    
    return "\n".join(result_lines)


def format_columns_list(columns):
    """Форматировать список столбцов"""
    if not columns:
        return "❌ Столбцы не найдены"
    
    result_lines = ["📊 **Столбцы таблицы:**\n"]
    
    for i, column_name in enumerate(columns, 1):
        if column_name:
            safe_column = escape_markdown(str(column_name))
            result_lines.append(f"{i}\\. **{safe_column}**")
        else:
            result_lines.append(f"{i}\\. *\\(пустой столбец\\)*")
    
    return "\n".join(result_lines)


def truncate_text(text, max_length=100):
    """Обрезать текст до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_markdown(text):
    """Экранировать специальные символы для Markdown"""
    if not text:
        return text
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text
