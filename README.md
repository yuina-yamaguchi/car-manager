# 🚗 車管理アプリ

家族で複数の車を共有するための予約管理PWAアプリです。  
スマホのホーム画面に追加してアプリとして使えます。

---

## 機能

- **車の管理** - 車名・ナンバー・色を登録
- **家族メンバー管理** - 誰が使うか選べるよう名前を登録
- **予約** - 車・人・日時を選んで予約（重複防止あり）
- **予約一覧** - 今後・過去の予約を確認、キャンセルも可能
- **リアルタイム状況** - ホーム画面で各車の使用中/空きを確認
- **PWA対応** - スマホのホーム画面に追加してアプリとして使用可能

---

## セットアップ

### 1. Pythonパッケージのインストール

```bash
cd car-manager
pip install -r requirements.txt
```

### 2. 初期データの投入（車3台・家族4人）

```bash
python seed.py
```

実行すると以下のデータが登録されます：

| 種類 | データ |
|------|--------|
| 車 | プリウス（白）、ヴォクシー（黒）、フィット（シルバー） |
| 家族 | お父さん、お母さん、弟、私 |

### 3. サーバー起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. ブラウザで開く

```
http://localhost:8000
```

---

## スマホからアクセスする

1. PCとスマホを**同じWi-Fi**に接続する
2. PCのIPアドレスを確認する  
   - Windows: `ipconfig` で「IPv4アドレス」を確認  
   - 例: `192.168.1.10`
3. スマホのブラウザで `http://192.168.1.10:8000` を開く

### ホーム画面に追加する（PWAとして使う）

**Android（Chrome）**
1. ブラウザ右上のメニュー（⋮）をタップ
2. 「ホーム画面に追加」をタップ

**iPhone（Safari）**
1. 下部の共有ボタン（□↑）をタップ
2. 「ホーム画面に追加」をタップ

---

## ファイル構成

```
car-manager/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPIアプリ本体
│   ├── database.py      # DB接続設定（SQLite）
│   ├── models.py        # テーブル定義
│   ├── schemas.py       # リクエスト/レスポンス型定義
│   └── routers/
│       ├── cars.py          # 車API
│       ├── members.py       # 家族メンバーAPI
│       └── reservations.py  # 予約API（重複防止あり）
├── static/
│   ├── index.html       # PWAフロントエンド
│   ├── manifest.json    # PWAマニフェスト
│   ├── service-worker.js # オフライン対応
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
├── seed.py              # 初期データ投入
├── generate_icons.py    # アイコン生成（開発用）
├── requirements.txt
└── README.md
```

---

## API仕様

サーバー起動後、以下のURLでAPI仕様を確認できます：

```
http://localhost:8000/docs
```

### 主なエンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | /api/cars/ | 車一覧 |
| POST | /api/cars/ | 車を登録 |
| GET | /api/members/ | 家族メンバー一覧 |
| POST | /api/members/ | メンバーを登録 |
| GET | /api/reservations/ | 予約一覧（開始日時順） |
| POST | /api/reservations/ | 予約を作成（重複チェックあり） |
| DELETE | /api/reservations/{id} | 予約をキャンセル |

---

## データのリセット

```bash
# DBファイルを削除して再作成
del car_manager.db
python seed.py
```


---

## 外部公開デプロイ（Turso + FastAPI Cloud）

データはTursoクラウドに永続保存されます。期限なしの無料枠があります。

### Step 1: Tursoのセットアップ

**Turso CLIをインストール**
```bash
# Windows（winget）
winget install turso
```

**ログイン＆DBを作成**
```bash
turso auth login
turso db create car-manager
```

**接続情報を取得**
```bash
turso db show --url car-manager   # TURSO_DATABASE_URL
turso db tokens create car-manager  # TURSO_AUTH_TOKEN
```

表示された値をメモしておく（後でFastAPI Cloudに登録します）。

---

### Step 2: FastAPI Cloudにデプロイ

**FastAPI Cloud CLIはfastapi[standard]に含まれています**（別途インストール不要）。

**ログイン**
```bash
fastapi login
```
ブラウザが開くのでGitHubアカウントでサインアップ・ログイン。

**デプロイ**
```bash
cd car-manager
fastapi deploy
```

**環境変数を設定**
```bash
fastapi env set TURSO_DATABASE_URL libsql://<your-db>.turso.io
fastapi env set TURSO_AUTH_TOKEN <your-token>
```

設定後、自動で再デプロイされます。

**初期データを投入**
```bash
fastapi run seed.py
```

---

### Step 3: アクセス

デプロイ完了後、以下のようなURLでアクセスできます：
```
https://car-manager.fastapicloud.dev
```

スマホのブラウザで開いて「ホーム画面に追加」すればアプリとして使えます。

---

### 注意事項
- Turso無料枠：500DB、9GBストレージ、期限なし
- FastAPI Cloud：パブリックベータ中（料金は公式サイトで確認）
- ローカル開発は引き続きSQLite（`car_manager.db`）が使われます
