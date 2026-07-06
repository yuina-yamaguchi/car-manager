from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/reservations", tags=["予約"])


def check_conflict(db: Session, car_id: int, start_time, end_time, exclude_id: int = None):
    """同じ車の予約が重複していないかチェック"""
    query = db.query(models.Reservation).filter(
        models.Reservation.car_id == car_id,
        models.Reservation.start_time < end_time,
        models.Reservation.end_time > start_time,
    )
    if exclude_id:
        query = query.filter(models.Reservation.id != exclude_id)
    return query.first()


@router.get("/", response_model=List[schemas.ReservationResponse])
def list_reservations(db: Session = Depends(get_db)):
    """予約一覧を取得（開始日時順）"""
    return (
        db.query(models.Reservation)
        .order_by(models.Reservation.start_time)
        .all()
    )


@router.get("/{reservation_id}", response_model=schemas.ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """指定した予約を取得"""
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    return reservation


@router.post("/", response_model=schemas.ReservationResponse, status_code=201)
def create_reservation(
    reservation: schemas.ReservationCreate, db: Session = Depends(get_db)
):
    """予約を作成（重複チェックあり）"""
    # 車の存在確認
    car = db.query(models.Car).filter(models.Car.id == reservation.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="車が見つかりません")

    # メンバーの存在確認
    member = db.query(models.Member).filter(
        models.Member.id == reservation.member_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")

    # 重複チェック
    conflict = check_conflict(
        db, reservation.car_id, reservation.start_time, reservation.end_time
    )
    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"この時間帯は既に「{conflict.member.name}」さんが予約しています",
        )

    db_reservation = models.Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """予約をキャンセル"""
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    db.delete(reservation)
    db.commit()


@router.post("/recurring", status_code=201)
def create_recurring_reservations(
    car_id: int,
    member_id: int,
    start_time_str: str,  # 例: "05:30"
    end_time_str: str,    # 例: "20:30"
    start_date: str,      # 例: "2026-07-07"
    weeks: int = 4,       # デフォルト4週間分
    db: Session = Depends(get_db),
):
    """定期予約を一括作成（平日のみ、月〜金）"""
    
    # 車とメンバーの存在確認
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="車が見つかりません")
    
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")
    
    # 開始日をパース
    try:
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日付形式が不正です（YYYY-MM-DD）")
    
    # 時刻をパース
    try:
        start_hour, start_min = map(int, start_time_str.split(":"))
        end_hour, end_min = map(int, end_time_str.split(":"))
    except ValueError:
        raise HTTPException(status_code=400, detail="時刻形式が不正です（HH:MM）")
    
    created_count = 0
    end_date = current_date + timedelta(weeks=weeks)
    
    while current_date < end_date:
        # 平日のみ（月曜=0, 日曜=6）
        if current_date.weekday() < 5:  # 0-4 = 月〜金
            start_datetime = datetime.combine(current_date, datetime.min.time()).replace(
                hour=start_hour, minute=start_min
            )
            end_datetime = datetime.combine(current_date, datetime.min.time()).replace(
                hour=end_hour, minute=end_min
            )
            
            # 重複チェック
            conflict = check_conflict(db, car_id, start_datetime, end_datetime)
            if not conflict:
                reservation = models.Reservation(
                    car_id=car_id,
                    member_id=member_id,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    note="定期予約",
                )
                db.add(reservation)
                created_count += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    
    return {
        "message": f"{created_count}件の定期予約を作成しました",
        "created_count": created_count,
    }
