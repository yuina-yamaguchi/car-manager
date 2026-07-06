from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/cars", tags=["車"])


@router.get("/", response_model=List[schemas.CarResponse])
def list_cars(db: Session = Depends(get_db)):
    """車の一覧を取得"""
    return db.query(models.Car).all()


@router.get("/{car_id}", response_model=schemas.CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    """指定した車の情報を取得"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="車が見つかりません")
    return car


@router.post("/", response_model=schemas.CarResponse, status_code=201)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    """車を登録"""
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    """車を削除"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="車が見つかりません")
    db.delete(car)
    db.commit()
