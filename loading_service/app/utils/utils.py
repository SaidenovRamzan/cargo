import re


def validate_file_name(file_name):
    """
    Проверяет имя файла на допустимость.
    - Допустимые расширения: .xlsx, .xls
    - Имя файла не должно содержать запрещенные символы
    """
    allowed_extensions = {".xlsx", ".xls"}
    file_extension = file_name[file_name.rfind(".") :].lower()

    # Регулярное выражение для проверки имени файла
    invalid_characters = re.compile(r'[<>:"/\\|?*\']')
    if invalid_characters.search(file_name) or file_extension not in allowed_extensions:
        return False
    return True

