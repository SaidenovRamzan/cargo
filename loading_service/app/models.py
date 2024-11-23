from sqlalchemy import Column, Integer, String, Float, Date, Enum
from app.database import Base
import enum

# Статусы для груза
class CargoStatus(str, enum.Enum):
    PENDING = "pending"
    ARRIVED = "arrived"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

# Модель для записи в таблицу
class CargoItem(Base):
    __tablename__ = "cargo_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, index=True) #номер
    shipment_date = Column(Date)    #дата отгрузки
    tracking_number = Column(String, unique=True, index=True)   #номер отслеживания
    quantity = Column(Integer)
    weight = Column(Float)
    volume = Column(Float)  #Объем
    product_name = Column(String)
    destination = Column(String)    #Место назначения
    status = Column(Enum(CargoStatus), default=CargoStatus.PENDING)
    file_name = Column(String)
