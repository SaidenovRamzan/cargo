from sqlalchemy import Column, Integer, String, Float, Date, Enum, func
from app.database import Base
import enum

# Статусы для груза
class CargoStatus(str, enum.Enum):
    PENDING = "Ожидается приезд"
    WAITING_FOR_SHIPMENT = "Ожидается отправка"
    ARRIVED = "Приехал"
    SHIPPED = "Отправили"
    CANCELLED = "cancelled"

# Модель для записи в таблицу
class CargoItem(Base):
    __tablename__ = "cargo_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, index=True) #номер
    shipment_date = Column(Date)    #дата отгрузки
    tracking_number = Column(String, index=True)   #номер отслеживания
    quantity = Column(Integer)
    weight = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)  #Объем
    product_name = Column(String, nullable=True)
    destination = Column(String, nullable=True)    #Место назначения
    status = Column(Enum(CargoStatus), default=CargoStatus.PENDING)
    file_expected = Column(String, nullable=True) # Ожидаем 
    file_received = Column(String, nullable=True) # приехал 
    file_shipped = Column(String, nullable=True)  # отправлен
    file_planned = Column(String, nullable=True)  # должен быть отправлен
    created_at = Column(Date, default=func.current_date())  # Дата создания
    updated_at = Column(Date, default=func.current_date(), onupdate=func.current_date())




