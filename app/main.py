from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine
from . import models
from .routers import cars, members, reservations

# テーブル作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="車管理アプリ",
    description="家族で車を共有するための予約管理システム",
    version="1.0.0",
)

# APIルーター登録
app.include_router(cars.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(reservations.router, prefix="/api")

# 静的ファイル配信（PWAフロントエンド）
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root():
    """PWAのトップページを返す"""
    return FileResponse("static/index.html")
