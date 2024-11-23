import openpyxl
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from io import BytesIO
from fastapi import APIRouter, UploadFile, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models import CargoItem, CargoStatus
from app.crud import get_all_cargo_items
from app.database import get_db


unloading_router = APIRouter()


@unloading_router.get("/cargo-items/", response_model=list)
async def get_cargo_items(db: AsyncSession = Depends(get_db)):
    try:
        cargo_items = await get_all_cargo_items(db)  # Получаем все записи из базы данных
        return cargo_items  # Возвращаем список всех записей в формате JSON
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})
    


@unloading_router.post("/update_cargo_status")
async def update_cargo_status(file: UploadFile, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для загрузки файла и обновления статуса грузов на SHIPPED по vehicle_number.
    """
    try:
        # Чтение содержимого файла
        contents = await file.read()
        workbook = openpyxl.load_workbook(BytesIO(contents))
        sheet = workbook.active

        # Пропускаем строку с заголовками
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[1]:  # Если vehicle_number пуст, пропускаем строку
                continue

            vehicle_number = row[1]

            # Ищем груз в БД по vehicle_number
            query = select(CargoItem).where(CargoItem.vehicle_number == vehicle_number)
            result = await db.execute(query)
            cargo_items = result.scalars().all()

            if cargo_items:
                for cargo_item in cargo_items:
                    cargo_item.status = CargoStatus.SHIPPED

                await db.commit()  # Сохраняем изменения для всех записей сразу
                print(f"Updated cargo status for vehicle_number: {vehicle_number} to SHIPPED")
            else:
                # Если грузы не найдены
                print(f"No cargo found with vehicle_number: {vehicle_number}")


        return {"message": "Statuses updated successfully"}

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail="Error processing file")
    

@unloading_router.get("/cargo-items/fileter/")
async def get_cargo_items(
    vehicle_number: Optional[str] = Query(None, description="Номер транспортного средства"),
    status: Optional[str] = Query(None, description="Статус груза"),
    product_name: Optional[str] = Query(None, description="Продукт"),
    db: AsyncSession = Depends(get_db),
):
    """
    Эндпоинт для получения списка грузов с фильтрацией по vehicle_number и статусу.

    Args:
        vehicle_number (Optional[str]): Номер транспортного средства для фильтрации.
        status (Optional[str]): Статус груза для фильтрации.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        List[CargoItemSchema]: Отфильтрованный список грузов.
    """
    try:
        query = select(CargoItem)

        # Применяем фильтры, если переданы параметры
        if vehicle_number:
            query = query.where(CargoItem.vehicle_number == vehicle_number)
        if status:
            query = query.where(CargoItem.status == status)
        if product_name:
            query = query.where(CargoItem.product_name.ilike(f"%{product_name}%"))
            
        result = await db.execute(query)
        cargo_items = result.scalars().all()

        if not cargo_items:
            raise HTTPException(status_code=404, detail="No cargo items found with the specified filters.")

        return cargo_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cargo items: {str(e)}")