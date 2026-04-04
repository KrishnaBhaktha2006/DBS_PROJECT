#!/bin/bash
# Quick Test Guide for Nexus Slate Marketplace
# ═══════════════════════════════════════════════════════════
# This guide shows how to test the API after starting the server
# Run: python run.py
# Then test with these commands

API_BASE="http://localhost:8000"
TOKEN=""

echo "════════════════════════════════════════════════════════════"
echo "  NEXUS SLATE - API TESTING GUIDE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Make sure the server is running: python run.py"
echo ""

# ──────────────────────────────────────────────────────────────
# 1. HEALTH CHECK
# ──────────────────────────────────────────────────────────────
echo "1️⃣  Health Check"
echo "────────────────────────────────────────────────────────────"
curl -s "$API_BASE/health" | python -m json.tool
echo ""

# ──────────────────────────────────────────────────────────────
# 2. LOAD CATEGORIES
# ──────────────────────────────────────────────────────────────
echo "2️⃣  Load Categories (public)"
echo "────────────────────────────────────────────────────────────"
curl -s "$API_BASE/categories/tree" | python -m json.tool
echo ""

# ──────────────────────────────────────────────────────────────
# 3. REGISTER A NEW USER
# ──────────────────────────────────────────────────────────────
echo "3️⃣  Register New User"
echo "────────────────────────────────────────────────────────────"
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "test@example.com",
    "password": "securepass123",
    "phone": "+1234567890"
  }')
echo "$REGISTER_RESPONSE" | python -m json.tool
echo ""

# ──────────────────────────────────────────────────────────────
# 4. LOGIN
# ──────────────────────────────────────────────────────────────
echo "4️⃣  Login & Get Token"
echo "────────────────────────────────────────────────────────────"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }')
echo "$LOGIN_RESPONSE" | python -m json.tool

# Extract token for later use
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo ""
echo "📝 Token: $TOKEN"
echo ""

# ──────────────────────────────────────────────────────────────
# 5. GET MY PROFILE
# ──────────────────────────────────────────────────────────────
echo "5️⃣  Get Your Profile (authenticated)"
echo "────────────────────────────────────────────────────────────"
curl -s -X GET "$API_BASE/users/me" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# ──────────────────────────────────────────────────────────────
# 6. BROWSE LISTINGS
# ──────────────────────────────────────────────────────────────
echo "6️⃣  Browse All Listings (public)"
echo "────────────────────────────────────────────────────────────"
curl -s "$API_BASE/listings" | python -m json.tool
echo ""

# ──────────────────────────────────────────────────────────────
# 7. CREATE A LISTING
# ──────────────────────────────────────────────────────────────
echo "7️⃣  Create a Listing (authenticated)"
echo "────────────────────────────────────────────────────────────"
curl -s -X POST "$API_BASE/listings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "c_id": 1,
    "title": "iPhone 15 Pro",
    "description": "Excellent condition, minor scratches only",
    "price": 999.99,
    "cond": "good",
    "type": "sell"
  }' | python -m json.tool
echo ""

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ TESTING COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📖 For full API docs, visit: http://localhost:8000/docs"
echo "🌐 Web UI: http://localhost:8000"
echo ""
