import openpyxl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from io import BytesIO

from app.models import CargoItem, CargoStatus
from app.schemas import CargoItem as CargoItemShema


# Обработчик загрузки файла
async def process_cargo_file(file, db: AsyncSession):
    file_name = file.filename
    contents = await file.read()
    workbook = openpyxl.load_workbook(BytesIO(contents))
    sheet = workbook.active

    # Пропускаем строку с заголовками
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if (not bool(row[0])):  # Если строка пуста, пропускаем
            continue

        try:
            cargo_data = {
                "vehicle_number": row[1] if row[1] else None,
                "shipment_date": datetime.strptime(row[2], "%Y-%m-%d") if row[2] else None,
                "tracking_number": row[3] if row[3] else None,
                "quantity": int(row[4]) if row[4] else 0,
                "weight": float(row[5]) if row[5] else 0.0,
                "volume": float(row[6]) if row[6] else 0.0,
                "product_name": row[7] if row[7] else None,
                "destination": row[8] if row[8] else None,
                "status": CargoStatus.PENDING,
                "file_name": file_name,
            }
            # Создаем новый объект CargoItem и добавляем его в сессию
            cargo_item = CargoItem(**cargo_data)
            db.add(cargo_item)
            print(f"Successfully {row[0]} {type(row[0])} {bool(row[0])} added cargo item: {cargo_data['tracking_number']}")  # Принт успешного добавления
            await db.commit()
        except Exception as e:
            # Логируем или игнорируем строки с ошибками
            print(f"Error processing row: {row[0]} {row[1]} {row[2]} {row[3]}, error:{e}")
            break
    

async def get_all_cargo_items(db: AsyncSession):
    result = await db.execute(select(CargoItem))
    cargo_items = result.scalars().all()

    # Преобразуем в словарь
    cargo_items_list = []
    for item in cargo_items:
        cargo_item_dict = {
            "id": item.id,
            "vehicle_number": item.vehicle_number,
            "shipment_date": item.shipment_date.isoformat() if item.shipment_date else None,
            "tracking_number": item.tracking_number,
            "quantity": item.quantity,
            "weight": item.weight,
            "volume": item.volume,
            "product_name": item.product_name,
            "destination": item.destination,
            "status": item.status,
            "file_name": item.file_name,
        }
        cargo_items_list.append(cargo_item_dict)
    
    return cargo_items_list