"""
初期データ投入スクリプト
車3台・家族4人のサンプルデータをDBに登録します。

使い方:
  cd car-manager
  python seed.py
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models

# テーブルを作成（まだない場合）
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 既にデータがある場合はスキップ
if db.query(models.Car).count() > 0:
    print("既にデータが存在します。スキップします。")
    print("リセットする場合は car_manager.db を削除してください。")
    db.close()
    sys.exit(0)

try:
    # ── 車3台 ────────────────────────────────────────
    cars = [
        models.Car(name="プリウス",   plate="品川 300 あ 1234", color="白"),
        models.Car(name="ヴォクシー", plate="品川 500 い 5678", color="黒"),
        models.Car(name="フィット",   plate="品川 100 う 9012", color="シルバー"),
    ]
    db.add_all(cars)
    db.flush()

    # ── 家族4人 ──────────────────────────────────────
    members = [
        models.Member(name="お父さん"),
        models.Member(name="お母さん"),
        models.Member(name="弟"),
        models.Member(name="私"),
    ]
    db.add_all(members)
    db.commit()

    print("初期データを投入しました！")
    print()
    print("【車】")
    for car in db.query(models.Car).all():
        print(f"  ID:{car.id}  {car.name}  {car.color}  {car.plate}")
    print()
    print("【家族メンバー】")
    for m in db.query(models.Member).all():
        print(f"  ID:{m.id}  {m.name}")

except Exception as e:
    db.rollback()
    print(f"エラーが発生しました: {e}")
    sys.exit(1)
finally:
    db.close()
