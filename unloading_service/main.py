import uvicorn
from fastapi import FastAPI
from app.database import create_tables
from app.api import unloading_router


async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(unloading_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
