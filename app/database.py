import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
    # 本番環境：Tursoクラウドにリモート接続
    # TURSO_DATABASE_URL の形式: libsql://<db-name>.turso.io
    engine = create_engine(
        f"sqlite+{TURSO_DATABASE_URL}?secure=true",
        connect_args={
            "auth_token": TURSO_AUTH_TOKEN,
        },
    )
else:
    # ローカル開発環境：SQLiteファイルを使用
    engine = create_engine(
        "sqlite:///./car_manager.db",
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
