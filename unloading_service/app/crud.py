from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import CargoItem, CargoStatus


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
        }
        cargo_items_list.append(cargo_item_dict)
    
    return cargo_items_list


async def get_cargo_by_tracking_number(tracking_number: str, db: AsyncSession, status=None):
    """
    Возвращает грузы с указанным tracking_number.
    """
    query = select(CargoItem).where(CargoItem.tracking_number == tracking_number)

    if status:
        query = query.where(CargoItem.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_cargo_status_to_shipped(file_name, file_quantity, cargo_items: list, db: AsyncSession):
    """
    Обновляет статус грузов на SHIPPED.
    """
    for cargo_item in cargo_items:
        if cargo_item.quantity != file_quantity:
            new_quantity = cargo_item.quantity-file_quantity
            
            new_cargo_item = CargoItem(
                vehicle_number=cargo_item.vehicle_number,
                shipment_date=cargo_item.shipment_date,
                tracking_number=cargo_item.tracking_number,
                quantity=new_quantity,  # Используем количество из файла
                weight=cargo_item.weight,
                volume=cargo_item.volume,
                product_name=cargo_item.product_name,
                destination=cargo_item.destination,
                status=CargoStatus.SHIPPED,  # Новый статус для нового объекта
                file_expected=cargo_item.file_expected,
                file_received=cargo_item.file_received,
                file_shipped=cargo_item.file_shipped,
                file_planned=file_name,  # Название файла
                created_at=cargo_item.created_at,
                updated_at=cargo_item.updated_at
            )
            db.add(new_cargo_item)  # Добавляем новый объект в базу данных
        else:
            cargo_item.status = CargoStatus.SHIPPED
            cargo_item.file_planned = file_name

    await db.commit()


async def update_cargo_status_to_WAITING_FOR_SHIPMENT(file_name, cargo_items: list, db: AsyncSession):
    """
    Обновляет статус грузов на SHIPPED.
    """
    for cargo_item in cargo_items:
        cargo_item.status = CargoStatus.WAITING_FOR_SHIPMENT
        cargo_item.file_planned = file_name
    await db.commit()