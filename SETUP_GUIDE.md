# 🎯 SETUP & CONNECTION GUIDE - Nexus Slate Marketplace

This document covers all the fixes that were made to connect your frontend and backend, plus complete setup instructions.

---

## ✅ What Was Fixed

### 1. **Database Configuration Mismatch** ✓
   - **Problem**: `.env` file had `DB_NAME=retail_db` but backend expected `marketplace_db`
   - **Fix**: Updated `.env` to use `marketplace_db`
   - **Fix**: Updated `schema.sql` to create `marketplace_db` instead of `retail_db`

### 2. **Missing Authentication on Listing Creation** ✓
   - **Problem**: Listings were created with hardcoded `mock_u_id = 1` for all users
   - **Fix**: Updated `/app/routes/listings.py` to require authentication
   - **Impact**: Now each listing is owned by the authenticated user who creates it

### 3. **Missing Startup Script** ✓
   - **Problem**: No easy way to initialize the database and start the server
   - **Fix**: Created `run.py` - a smart launcher that:
     - ✅ Automatically creates the database
     - ✅ Initializes tables from `schema.sql`
     - ✅ Starts the FastAPI server with hot reload
   - **Usage**: `python run.py`

### 4. **Documentation Missing** ✓
   - **Problem**: No clear instructions on how to set up and connect everything
   - **Fix**: Created comprehensive `README.md` with:
     - Quick start guide (3 steps)
     - API endpoint documentation
     - Frontend-backend connectivity explanation
     - Database schema reference

### 5. **Configuration Template Missing** ✓
   - **Problem**: No example `.env` file
   - **Fix**: Created `.env.example` with all required settings

### 6. **Testing Guide Missing** ✓
   - **Problem**: No way to verify API is working
   - **Fix**: Created `test_api.sh` (Unix/Linux/Mac) and `test_api.bat` (Windows)

---

## 🚀 QUICK START (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Database (Edit `.env`)
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=appuser
DB_PASSWORD=password123
DB_NAME=marketplace_db
```

Create the MySQL user:
```sql
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON marketplace_db.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Start Everything
```bash
python run.py
```

Open your browser:
- 🌐 Web UI: **http://localhost:8000**
- 📖 API Docs: **http://localhost:8000/docs**

---

## 🔌 Frontend & Backend Connection

### How It Works

The frontend (`index.html` + `app.js`) connects to the backend via:

1. **Default API Base URL**: `http://localhost:8000`
   - Stored in `app.js` as `DEFAULT_API_BASE`
   - Saved in browser `localStorage` for persistence

2. **Change API URL** (if backend is elsewhere):
   - Go to Categories sidebar → "API base URL" field
   - Enter new URL (e.g., `http://192.168.1.5:8000`)
   - Click "Save API base"
   - Refreshes all data from new endpoint

### Frontend Features

| Feature | Authentication | How It Works |
|---------|---|---|
| Browse listings | ❌ No | `GET /listings` - public endpoint |
| Browse categories | ❌ No | `GET /categories/tree` - public endpoint |
| Login/Register | ❌ No | `POST /auth/login`, `POST /auth/register` |
| Create listing | ✅ Yes | `POST /listings` - requires JWT token |
| Place offer | ✅ Yes | `POST /offers` - requires JWT token |
| Create alert | ✅ Yes | `POST /alerts` - requires JWT token |
| View notifications | ✅ Yes | `GET /notifications/me` - requires JWT token |

### JWT Authentication Flow

```
1. User enters email + password → Click "Login"
2. Frontend sends: POST /auth/login
3. Backend returns: { access_token: "...", token_type: "bearer" }
4. Frontend stores token in localStorage
5. All subsequent requests include: Authorization: Bearer <token>
6. Protected routes verify token via get_current_user() dependency
```

---

## 📊 API Endpoints Summary

### Public Endpoints (No Auth Needed)
```
GET  /health                    ← Health check
GET  /categories/tree           ← Full category hierarchy
GET  /listings                  ← Browse listings (with filters)
GET  /listings/{id}             ← Single listing details
GET  /users/{u_id}              ← View user's public profile
POST /auth/register             ← Create account
POST /auth/login                ← Get JWT token
```

### Protected Endpoints (JWT Required)
```
POST /listings                  ← Create listing (uses authenticated user's ID)
PUT  /listings/{id}             ← Edit listing (owner only)
DELETE /listings/{id}           ← Close listing (owner only)

POST /offers                    ← Place an offer
GET  /offers/listing/{id}       ← View offers on your listing
POST /offers/{id}/accept        ← Accept offer → creates transaction
POST /offers/{id}/reject        ← Reject offer

POST /alerts                    ← Create price/keyword alert
GET  /alerts/me                 ← Your alerts
DELETE /alerts/{id}             ← Delete alert

GET  /notifications/me          ← Your notifications
PATCH /notifications/{id}/seen  ← Mark notification as read

GET  /transactions/me           ← Your transactions
GET  /users/me                  ← Your profile
```

---

## 🧪 Testing the API

### Option 1: Browser UI
Open **http://localhost:8000** and use the web interface

### Option 2: Using Test Scripts
```bash
# On Windows:
test_api.bat

# On Linux/Mac:
bash test_api.sh
```

### Option 3: Swagger/OpenAPI Docs
Open **http://localhost:8000/docs** and click "Try it out"

### Option 4: Manual cURL
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'

# Copy the access_token and use it:
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📂 Project Structure After Fixes

```
DBS PROJECT/
├── .env                    ← ✨ FIXED: Now uses marketplace_db
├── .env.example            ← ✨ NEW: Template for .env
├── run.py                  ← ✨ NEW: Smart launcher
├── README.md               ← ✨ UPDATED: Full documentation
├── requirements.txt
├── schema.sql              ← ✨ FIXED: Creates marketplace_db
├── test_api.sh             ← ✨ NEW: Unix/Mac test script
├── test_api.bat            ← ✨ NEW: Windows test script
│
├── app/
│   ├── main.py             ← FastAPI app (already correct)
│   ├── config.py           ← Settings from .env
│   │
│   ├── routes/
│   │   ├── listings.py     ← ✨ FIXED: Now requires auth for POST
│   │   ├── offers.py       ← (already correct)
│   │   ├── alerts.py       ← (already correct)
│   │   └── ... (others)
│   │
│   ├── services/           ← Business logic (all correct)
│   ├── db/                 ← Database connection (all correct)
│   ├── models/             ← Schemas (all correct)
│   └── utils/              ← Security, responses (all correct)
│
└── frontend/
    ├── index.html          ← Web UI (no changes needed)
    ├── app.js              ← Already connects to backend correctly
    └── styles.css          ← Styling (no changes needed)
```

---

## 🐛 Troubleshooting

### Error: "Database connection failed"
**Cause**: MySQL user doesn't have permissions  
**Fix**:
```sql
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON marketplace_db.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "mkdir() failed: Parent directory does not exist"
**Cause**: Project path has spaces  
**Fix**: Ensure Python can read the project. Works in: `C:\Users\YourName\DBS PROJECT`

### Error: "Module 'mysql.connector' has no attribute '_mysql_connector'"
**Cause**: MySQL Connector needs compilation  
**Fix**: `pip install --upgrade mysql-connector-python`

### Frontend shows "API unavailable"
**Cause**: Backend not running or API URL is wrong  
**Fix**:
1. Check server is running: `python run.py`
2. Check API URL in sidebar → ensure it matches server host:port
3. Check browser console (F12) for CORS errors

### Can't login - "Token expired"
**Cause**: JWT_SECRET_KEY changed between requests  
**Fix**: Ensure `.env` doesn't change while server is running. Restart with `python run.py`

---

## 🔒 Security Notes

### For Development (Current Setup)
- ✅ CORS enabled for all origins (fine for local testing)
- ✅ JWT tokens expire after 24 hours
- ⚠️ JWT_SECRET_KEY is set to default (change this!)

### For Production
- ❌ Change `JWT_SECRET_KEY` to a random, strong value
- ❌ Disable CORS or restrict to your domain
- ❌ Use HTTPS
- ❌ Set `APP_ENV=production`
- ❌ Add rate limiting and input validation
- ❌ Use environment variables for all secrets

---

## 📞 Database Schema

All tables are created by `schema.sql`:

- **Users** - User accounts with bcrypt passwords
- **Category** - Hierarchical product categories
- **Listing** - Product listings (buy/sell)
- **Offer** - Offers on listings
- **Txn** (Transactions) - Completed sales
- **Alert** - Saved searches with price/keyword filters
- **Notification** - Alerts when matching listings appear

---

## ✨ Summary

Your marketplace is now **fully functional** with proper frontend-backend connectivity!

```
✅ Database properly configured (marketplace_db)
✅ Listing creation uses authenticated users (no more mock IDs)
✅ Easy startup with database initialization (python run.py)
✅ Full API documentation (README.md + Swagger)
✅ Test scripts for API verification
✅ Frontend properly connects to backend
✅ JWT authentication working end-to-end
```

**Next steps**:
1. Run `python run.py`
2. Open `http://localhost:8000` in your browser
3. Register an account and create your first listing!

---

## 📝 Files Changed

| File | Change | Type |
|------|--------|------|
| `.env` | Fixed DB name: `retail_db` → `marketplace_db` | `FIXED` |
| `schema.sql` | Fixed DB name: `retail_db` → `marketplace_db` | `FIXED` |
| `app/routes/listings.py` | Added auth requirement to POST /listings | `FIXED` |
| `run.py` | Created smart launcher | `NEW` |
| `.env.example` | Created config template | `NEW` |
| `README.md` | Updated with comprehensive guide | `UPDATED` |
| `test_api.sh` | Created test script for Unix/Linux/Mac | `NEW` |
| `test_api.bat` | Created test script for Windows | `NEW` |

---

**🎉 You're all set! Happy selling! 🛒**
