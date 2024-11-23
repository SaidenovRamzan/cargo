from datetime import datetime
from pydantic import BaseModel
from app.models import CargoStatus


class CargoItemBase(BaseModel):
    vehicle_number: str
    shipment_date: str
    tracking_number: str
    quantity: int
    weight: float
    volume: float
    product_name: str
    destination: str


class CargoItemCreate(CargoItemBase):
    pass


class CargoItem(CargoItemBase):
    id: int
    status: CargoStatus

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
