from fastapi import File, UploadFile, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.crud import process_cargo_file, get_all_cargo_items
from app.database import get_db


loading_router = APIRouter()


@loading_router.post("/upload-cargo-file/")
async def upload_cargo_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    await process_cargo_file(file, db)  # Передаем асинхронную сессию
    return JSONResponse(status_code=200, content={"message": "File processed successfully"})



@loading_router.get("/cargo-items/", response_model=list)
async def get_cargo_items(db: AsyncSession = Depends(get_db)):
    try:
        cargo_items = await get_all_cargo_items(db)  # Получаем все записи из базы данных
        return cargo_items  # Возвращаем список всех записей в формате JSON
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})