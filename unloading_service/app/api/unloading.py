from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import APIRouter, UploadFile, Depends, HTTPException, Query, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.models import CargoItem

from app.crud import get_all_cargo_items, get_cargo_by_tracking_number, update_cargo_status_to_shipped, update_cargo_status_to_WAITING_FOR_SHIPMENT
from app.database import get_db
from app.utils.file_processor import parse_excel_file, parse_excel_cargo_file
from app.utils import utils
from app.models import CargoStatus

unloading_router = APIRouter()


@unloading_router.get("/cargo-items/", response_model=list)
async def get_cargo_items(db: AsyncSession = Depends(get_db)):
    try:
        cargo_items = await get_all_cargo_items(db)  # Получаем все записи из базы данных
        return cargo_items  # Возвращаем список всех записей в формате JSON
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})
    


@unloading_router.post("/update_cargo_status")
async def update_cargo_status(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для загрузки файла и обновления статуса грузов с Ождание на Ожидания отправки.
    """
    try:
        # Чтение содержимого файла
        file_name = file.filename
        if not utils.validate_file_name(file_name):
            raise HTTPException(status_code=400, detail="Некорректное название файла или расширение.")
        
        contents = await file.read()
        cargo_data = parse_excel_file(contents)

        for item in cargo_data:
            tracking_number = item["tracking_number"]

            cargo_items = await get_cargo_by_tracking_number(tracking_number, db, status='Ожидается приезд')
            if cargo_items:
                # Обновляем статус грузов на SHIPPED
                await update_cargo_status_to_WAITING_FOR_SHIPMENT(file_name, cargo_items, db)
                print(f"Updated cargo status for tracking_number: {tracking_number} to SHIPPED")
            else:
                print(f"No cargo found with tracking_number: {tracking_number}")

        return {"message": "Statuses updated successfully"}

    except ValueError as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@unloading_router.get("/cargo-items/fileter/")
async def get_cargo_items(
    vehicle_number: Optional[str] = Query(None, description="Номер транспортного средства"),
    tracking_number: Optional[str] = Query(None, description="Номер"),
    status: Optional[str] = Query(None, description="Статус груза"),
    product_name: Optional[str] = Query(None, description="Продукт"),
    db: AsyncSession = Depends(get_db),
):
    """
    Эндпоинт для получения списка грузов с фильтрацией
    """
    try:
        query = select(CargoItem)
        filters = []

        if vehicle_number:
            filters.append(CargoItem.vehicle_number == vehicle_number)
        if status:
            filters.append(CargoItem.status == status)
        if tracking_number:
            filters.append(CargoItem.tracking_number.ilike(f"%{tracking_number}%"))
        if product_name:
            filters.append(CargoItem.product_name.ilike(f"%{product_name}%"))

        # Если есть фильтры, добавляем их в запрос
        if filters:
            query = query.where(*filters)

        # Выполняем запрос и ждем результат
        result = await db.execute(query)
        cargo_items = result.scalars().all()

        if not cargo_items:
            raise HTTPException(status_code=404, detail="No cargo items found with the specified filters.")

        return cargo_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cargo items: {str(e)}")
    

@unloading_router.post("/update_cargo_status_arrived")
async def update_cargo_status_arrived(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для загрузки файла и обновления статуса грузов Ожидание отправки на Прибыло.
    """
    try:
        # Чтение содержимого файла
        file_name = file.filename
        if not utils.validate_file_name(file_name):
            raise HTTPException(status_code=400, detail="Некорректное название файла или расширение.")
        
        contents = await file.read()
        cargo_data = parse_excel_cargo_file(contents)

        for item in cargo_data:
            tracking_number = item["tracking_number"]
            file_quantity = item["quantity"]

            cargo_items = await get_cargo_by_tracking_number(tracking_number, db)
            if cargo_items:
                for cargo_item in cargo_items:
                    if cargo_item.quantity != file_quantity:
                        # Если количество не совпадает, создаем новый объект
                        new_cargo_item = CargoItem(
                            vehicle_number=cargo_item.vehicle_number,
                            shipment_date=cargo_item.shipment_date,
                            tracking_number=cargo_item.tracking_number,
                            quantity=cargo_item.quantity - file_quantity,  # Обновляем количество
                            weight=cargo_item.weight,
                            volume=cargo_item.volume,
                            product_name=cargo_item.product_name,
                            destination=cargo_item.destination,
                            status=CargoStatus.ARRIVED,  # Новый статус
                            file_expected=cargo_item.file_expected,
                            file_received=file_name,  # Название файла для нового объекта
                            file_shipped=cargo_item.file_shipped,
                            file_planned=cargo_item.file_planned,
                            created_at=cargo_item.created_at,
                            updated_at=cargo_item.updated_at
                        )
                        db.add(new_cargo_item)  # Добавляем новый объект в базу данных
                    else:
                        # Если количество совпадает, просто обновляем статус и файл
                        cargo_item.status = CargoStatus.ARRIVED
                        cargo_item.file_received = file_name

            else:
                print(f"No cargo found with tracking_number: {tracking_number}")

        await db.commit()  # Сохраняем изменения в базе данных

        return {"message": "Statuses updated successfully"}

    except ValueError as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unloading_router.post("/update_cargo_status_shipped")
async def update_cargo_status_arrived(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для загрузки файла и обновления статуса грузов с ожидает отпраки Отправлено.
    """
    try:
        # Чтение содержимого файла
        file_name = file.filename
        if not utils.validate_file_name(file_name):
            raise HTTPException(status_code=400, detail="Некорректное название файла или расширение.")
        
        contents = await file.read()
        cargo_data = parse_excel_cargo_file(contents)

        for item in cargo_data:
            tracking_number = item["tracking_number"]
            file_quantity = item["quantity"]

            cargo_items = await get_cargo_by_tracking_number(tracking_number, db)
            if cargo_items:
                for cargo_item in cargo_items:
                    if cargo_item.quantity != file_quantity:
                        # Если количество не совпадает, создаем новый объект
                        new_cargo_item = CargoItem(
                            vehicle_number=cargo_item.vehicle_number,
                            shipment_date=cargo_item.shipment_date,
                            tracking_number=cargo_item.tracking_number,
                            quantity=cargo_item.quantity - file_quantity,  # Обновляем количество
                            weight=cargo_item.weight,
                            volume=cargo_item.volume,
                            product_name=cargo_item.product_name,
                            destination=cargo_item.destination,
                            status=CargoStatus.SHIPPED,  # Новый статус
                            file_expected=cargo_item.file_expected,
                            file_received=file_name,  # Название файла для нового объекта
                            file_shipped=cargo_item.file_shipped,
                            file_planned=cargo_item.file_planned,
                            created_at=cargo_item.created_at,
                            updated_at=cargo_item.updated_at
                        )
                        db.add(new_cargo_item)  # Добавляем новый объект в базу данных
                    else:
                        # Если количество совпадает, просто обновляем статус и файл
                        cargo_item.status = CargoStatus.SHIPPED
                        cargo_item.file_received = file_name

            else:
                print(f"No cargo found with tracking_number: {tracking_number}")

        await db.commit()  # Сохраняем изменения в базе данных

        return {"message": "Statuses updated successfully"}

    except ValueError as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")