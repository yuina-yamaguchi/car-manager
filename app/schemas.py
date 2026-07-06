from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional


# ── 車 ──────────────────────────────────────────

class CarBase(BaseModel):
    name: str
    plate: str
    color: str

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int

    model_config = {"from_attributes": True}


# ── 家族メンバー ──────────────────────────────────

class MemberBase(BaseModel):
    name: str

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int

    model_config = {"from_attributes": True}


# ── 予約 ──────────────────────────────────────────

class ReservationCreate(BaseModel):
    car_id: int
    member_id: int
    start_time: datetime
    end_time: datetime
    note: Optional[str] = ""

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("終了日時は開始日時より後にしてください")
        return self

class ReservationResponse(BaseModel):
    id: int
    car_id: int
    member_id: int
    start_time: datetime
    end_time: datetime
    note: str
    car: CarResponse
    member: MemberResponse

    model_config = {"from_attributes": True}
