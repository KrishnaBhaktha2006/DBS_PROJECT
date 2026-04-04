@echo off
REM Quick Test Guide for Nexus Slate Marketplace (Windows)
REM ═══════════════════════════════════════════════════════════
REM This guide shows how to test the API after starting the server
REM Run: python run.py
REM Then run this file: test_api.bat

setlocal enabledelayedexpansion
set API_BASE=http://localhost:8000
set TOKEN=

cls
echo ════════════════════════════════════════════════════════════
echo   NEXUS SLATE - API TESTING GUIDE (Windows)
echo ════════════════════════════════════════════════════════════
echo.
echo Make sure the server is running: python run.py
echo.
pause

REM ──────────────────────────────────────────────────────────────
REM 1. HEALTH CHECK
REM ──────────────────────────────────────────────────────────────
echo 1^) Health Check
echo ────────────────────────────────────────────────────────────
curl -s "%API_BASE%/health"
echo.
echo.

REM ──────────────────────────────────────────────────────────────
REM 2. LOAD CATEGORIES
REM ──────────────────────────────────────────────────────────────
echo 2^) Load Categories (public)
echo ────────────────────────────────────────────────────────────
curl -s "%API_BASE%/categories/tree"
echo.
echo.

REM ──────────────────────────────────────────────────────────────
REM 3. REGISTER A NEW USER
REM ──────────────────────────────────────────────────────────────
echo 3^) Register New User
echo ────────────────────────────────────────────────────────────
curl -s -X POST "%API_BASE%/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser123\", \"email\": \"test@example.com\", \"password\": \"securepass123\", \"phone\": \"+1234567890\"}"
echo.
echo.

REM ──────────────────────────────────────────────────────────────
REM 4. LOGIN
REM ──────────────────────────────────────────────────────────────
echo 4^) Login ^& Get Token
echo ────────────────────────────────────────────────────────────
for /f "delims=" %%a in ('curl -s -X POST "%API_BASE%/auth/login" -H "Content-Type: application/json" -d "{\"email\": \"test@example.com\", \"password\": \"securepass123\"}"') do (
  set LOGIN_RESPONSE=%%a
)
echo !LOGIN_RESPONSE!
echo.

REM Extract token (simple approach - just display instructions)
echo 📝 Copy the access_token value from above and set it as:
echo    set TOKEN=your_token_here
echo.

REM ──────────────────────────────────────────────────────────────
REM 5. GET MY PROFILE (needs token)
REM ──────────────────────────────────────────────────────────────
echo 5^) Get Your Profile (authenticated - requires token)
echo ────────────────────────────────────────────────────────────
echo To test authenticated endpoints, set TOKEN=your_access_token and run:
echo   curl -s -X GET "%API_BASE%/users/me" -H "Authorization: Bearer !TOKEN!"
echo.
echo.

REM ──────────────────────────────────────────────────────────────
REM 6. BROWSE LISTINGS
REM ──────────────────────────────────────────────────────────────
echo 6^) Browse All Listings (public)
echo ────────────────────────────────────────────────────────────
curl -s "%API_BASE%/listings"
echo.
echo.

echo ════════════════════════════════════════════════════════════
echo   ✓ TESTING COMPLETE
echo ════════════════════════════════════════════════════════════
echo.
echo 📖 For full API docs, visit: http://localhost:8000/docs
echo 🌐 Web UI: http://localhost:8000
echo.
pause
