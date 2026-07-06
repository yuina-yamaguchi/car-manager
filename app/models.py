from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # 車名（例：プリウス）
    plate = Column(String, nullable=False)         # ナンバープレート
    color = Column(String, nullable=False)         # 色

    reservations = relationship("Reservation", back_populates="car")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # 家族の名前

    reservations = relationship("Reservation", back_populates="member")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)  # 開始日時
    end_time = Column(DateTime, nullable=False)    # 終了日時
    note = Column(String, default="")              # メモ

    car = relationship("Car", back_populates="reservations")
    member = relationship("Member", back_populates="reservations")
