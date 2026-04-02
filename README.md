# 🛒 Online Marketplace – FastAPI Backend

A production-quality marketplace REST API built with **FastAPI**, **raw SQL** (MySQL / Oracle), **JWT authentication**, and **bcrypt** password hashing. No ORM is used anywhere — all database operations use explicit, parameterised SQL queries.

---

## 📁 Folder Structure

```
marketplace/
├── .env.example              ← copy to .env and fill in your values
├── requirements.txt
├── sql/
│   └── schema.sql            ← run this first to create all tables
└── app/
    ├── main.py               ← FastAPI app, router registration
    ├── config.py             ← pydantic-settings from .env
    ├── db/
    │   ├── __init__.py
    │   └── connection.py     ← MySQL / Oracle pool + cursor helpers
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py        ← Pydantic v2 request/response models
    ├── services/             ← ALL business logic + raw SQL lives here
    │   ├── __init__.py
    │   ├── auth_service.py
    │   ├── user_service.py
    │   ├── category_service.py
    │   ├── listing_service.py
    │   ├── offer_service.py
    │   ├── txn_service.py
    │   ├── alert_service.py
    │   └── notification_service.py
    ├── routes/               ← thin HTTP layer, calls services
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── users.py
    │   ├── categories.py
    │   ├── listings.py
    │   ├── offers.py
    │   ├── transactions.py
    │   ├── alerts.py
    │   └── notifications.py
    └── utils/
        ├── __init__.py
        ├── security.py       ← bcrypt + JWT helpers + FastAPI dependency
        └── responses.py      ← consistent JSON envelope
```

---

## ⚙️ Setup Instructions

### 1. Clone / place files

```bash
cd marketplace
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt

# For Oracle instead of MySQL:
# pip install cx_Oracle
# (and comment out mysql-connector-python in requirements.txt)
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your DB credentials and a strong JWT_SECRET_KEY
```

### 5. Create the database schema

```bash
# MySQL
mysql -u root -p < sql/schema.sql

# Oracle (run in SQL*Plus or SQLcl)
# @sql/schema.sql
# Note: Oracle needs minor syntax adjustments (see schema.sql comments)
```

### 6. Run the server

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or directly
python app/main.py
```

### 7. Open the interactive API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

---

## 🔌 API Reference

### Auth
| Method | Endpoint         | Auth | Description              |
|--------|-----------------|------|--------------------------|
| POST   | /auth/register  | —    | Register new user        |
| POST   | /auth/login     | —    | Login, receive JWT token |

### Users
| Method | Endpoint        | Auth | Description        |
|--------|----------------|------|--------------------|
| GET    | /users/me      | ✅   | Own profile        |
| GET    | /users/{u_id}  | —    | Any user's profile |

### Categories
| Method | Endpoint           | Auth | Description               |
|--------|-------------------|------|---------------------------|
| POST   | /categories/       | ✅   | Create category           |
| GET    | /categories/tree  | —    | Full recursive tree (CTE) |

### Listings
| Method | Endpoint               | Auth | Description               |
|--------|------------------------|------|---------------------------|
| POST   | /listings/             | ✅   | Create listing + alerts   |
| GET    | /listings/             | —    | List with filters         |
| GET    | /listings/{id}         | —    | Single listing            |
| PUT    | /listings/{id}         | ✅   | Update (owner only)       |
| DELETE | /listings/{id}         | ✅   | Soft-delete (owner only)  |

Query params for GET /listings:
- `type` — `buy` or `sell`
- `c_id` — category filter
- `price_min` / `price_max` — price range
- `status` — default `active`

### Offers
| Method | Endpoint                      | Auth | Description                        |
|--------|------------------------------|------|------------------------------------|
| POST   | /offers/                     | ✅   | Place offer (buyer)                |
| GET    | /offers/listing/{listing_id} | ✅   | View offers on listing (seller)    |
| POST   | /offers/{id}/accept          | ✅   | Accept → creates Txn, marks sold   |
| POST   | /offers/{id}/reject          | ✅   | Reject offer                       |

### Transactions
| Method | Endpoint          | Auth | Description                      |
|--------|------------------|------|----------------------------------|
| GET    | /transactions/me | ✅   | All txns as buyer or seller      |

### Alerts
| Method | Endpoint         | Auth | Description       |
|--------|-----------------|------|-------------------|
| POST   | /alerts/        | ✅   | Create alert      |
| GET    | /alerts/me      | ✅   | My alerts         |
| DELETE | /alerts/{id}    | ✅   | Delete alert      |

### Notifications
| Method | Endpoint                    | Auth | Description        |
|--------|-----------------------------|------|--------------------|
| GET    | /notifications/me           | ✅   | My notifications   |
| PATCH  | /notifications/{id}/seen    | ✅   | Mark as seen       |

---

## 🔐 Authentication

All protected routes require a **Bearer token** in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

Get a token by calling `POST /auth/login`.

---

## 🗄️ Key SQL Patterns

### Recursive Category Tree (WITH RECURSIVE CTE)
```sql
WITH RECURSIVE cat_tree AS (
    SELECT c_id, name, parent_id, 0 AS depth
    FROM   Category WHERE parent_id IS NULL
    UNION ALL
    SELECT c.c_id, c.name, c.parent_id, ct.depth + 1
    FROM   Category c JOIN cat_tree ct ON c.parent_id = ct.c_id
)
SELECT * FROM cat_tree ORDER BY depth, parent_id, c_id;
```

### Accept Offer (Explicit Transaction)
```sql
-- Step 1: Accept the chosen offer
UPDATE Offer SET status = 'accepted' WHERE offer_id = ?;

-- Step 2: Reject all competing offers on the same listing
UPDATE Offer SET status = 'rejected'
WHERE listing_id = ? AND offer_id != ? AND status = 'pending';

-- Step 3: Record the transaction
INSERT INTO Txn (offer_id, listing_id, buyer_id, amount, status)
VALUES (?, ?, ?, ?, 'completed');

-- Step 4: Mark listing as sold
UPDATE Listing SET status = 'sold' WHERE listing_id = ?;
```

### Alert Matching (on listing create)
```sql
SELECT alert_id, u_id FROM Alert
WHERE (c_id        IS NULL OR c_id        = ?)
  AND (price_limit IS NULL OR price_limit >= ?)
  AND (keyword     IS NULL OR ? LIKE CONCAT('%', keyword, '%'))
  AND u_id != ?;   -- exclude the listing owner
```

---

## 🔄 Adapting to Oracle

1. Set `DB_DRIVER=oracle` in `.env`
2. Uncomment Oracle credentials in `.env`
3. In `schema.sql`: swap `AUTO_INCREMENT` → `GENERATED ALWAYS AS IDENTITY`, `DATETIME` → `TIMESTAMP`, `TINYINT(1)` → `NUMBER(1)`
4. In `connection.py`: the `cursor_execute()` helper auto-converts `%s` → `:1, :2 …` for Oracle
5. For INSERT returning IDs in Oracle, use `RETURNING col INTO :out` with an `outvar`

---

## 🧪 Quick Test with curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}'

# Use the token
TOKEN="<paste token here>"

# Create a category
curl -X POST http://localhost:8000/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Electronics"}'

# Create a listing
curl -X POST http://localhost:8000/listings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"c_id":1,"title":"iPhone 14","price":800.00,"cond":"like_new","type":"sell"}'
```
