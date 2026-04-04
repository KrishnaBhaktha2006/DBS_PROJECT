# Nexus Slate Marketplace

A FastAPI + MySQL marketplace project with a simple frontend for browsing listings, creating listings, and placing offers.

## Project Structure

```text
app/
  config.py
  main.py
  db/
  models/
  routes/
  services/
  utils/
frontend/
  index.html
  app.js
  styles.css
schema.sql
insertion.sql
run.py
requirements.txt
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update the database credentials.
4. Make sure MySQL is running.
5. Start the project:

```bash
python run.py
```

The launcher will:

- apply `schema.sql`
- apply `insertion.sql`
- start the API at `http://localhost:8000`
- serve the frontend at `http://localhost:8000`

## Environment Variables

Example `.env` values:

```env
APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENV=development

JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

DB_DRIVER=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=appuser
DB_PASSWORD=password123
DB_NAME=marketplace_db
```

## Main API Routes

- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`
- `GET /categories/tree`
- `POST /categories/`
- `GET /listings/`
- `GET /listings/{listing_id}`
- `POST /listings/`
- `PUT /listings/{listing_id}`
- `DELETE /listings/{listing_id}`
- `POST /offers/`
- `GET /offers/listing/{listing_id}`
- `POST /offers/{offer_id}/accept`
- `POST /offers/{offer_id}/reject`
- `POST /alerts/`
- `GET /alerts/me`
- `DELETE /alerts/{alert_id}`
- `GET /notifications/me`
- `PATCH /notifications/{notif_id}/seen`
- `GET /transactions/me`
- `GET /health`

## Notes

- Buy listings can have `cond = NULL`; sell listings require a condition.
- `insertion.sql` is now idempotent, so running the launcher multiple times will not duplicate the sample data.
- The frontend uses `http://127.0.0.1:8000` by default, but you can change the API base URL from the UI.
