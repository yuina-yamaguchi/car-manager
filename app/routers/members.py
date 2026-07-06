from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/members", tags=["家族メンバー"])


@router.get("/", response_model=List[schemas.MemberResponse])
def list_members(db: Session = Depends(get_db)):
    """家族メンバーの一覧を取得"""
    return db.query(models.Member).all()


@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """指定したメンバーの情報を取得"""
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")
    return member


@router.post("/", response_model=schemas.MemberResponse, status_code=201)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """家族メンバーを登録"""
    db_member = models.Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.put("/{member_id}", response_model=schemas.MemberResponse)
def update_member(member_id: int, member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """メンバーを更新"""
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")
    
    for key, value in member.model_dump().items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """メンバーを削除"""
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")
    db.delete(member)
    db.commit()
