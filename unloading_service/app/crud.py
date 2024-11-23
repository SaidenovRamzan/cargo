from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import CargoItem


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