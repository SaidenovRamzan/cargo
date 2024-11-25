import re
import pandas as pd
from sqlalchemy.orm import Session
from app import schemas, crud


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


def validate_excel(df: pd.DataFrame):
    """
    Проверка и валидация данных из Excel.
    """
    required_columns = ["第二次整车编号", "口岸发货日期", "运单号", "实发件数", "实发重量", "实发体积", "品名", "目的地"]

    # Проверяем наличие необходимых колонок
    for col in required_columns:
        if col not in df.columns:
            return None

    # Пропускаем пустые строки
    df = df.dropna()

    # Преобразуем в ожидаемый формат
    df = df.rename(
        columns={
            "第二次整车编号": "vehicle_number",
            "口岸发货日期": "shipment_date",
            "运单号": "tracking_number",
            "实发件数": "quantity",
            "实发重量": "weight",
            "实发体积": "volume",
            "品名": "product_name",
            "目的地": "destination",
        }
    )

    return df


def process_unloading_data(df: pd.DataFrame, db: Session):
    """
    Сохранение валидированных данных в базу данных.
    """
    for _, row in df.iterrows():
        item = schemas.UnloadedItemCreate(
            vehicle_number=row["vehicle_number"],
            shipment_date=row["shipment_date"],
            tracking_number=row["tracking_number"],
            quantity=row["quantity"],
            weight=row["weight"],
            volume=row["volume"],
            product_name=row["product_name"],
            destination=row["destination"],
        )
        crud.create_unloaded_item(db, item)

