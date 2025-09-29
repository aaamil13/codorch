# 🚀 Codorch Quick Start Guide

## Prerequisites Check ✅

- ✅ PostgreSQL Running (port 5432)
- ✅ Database `codorch_dev` created
- ✅ User `usr_codorch` with permissions
- ✅ Migrations applied
- ✅ Python 3.11+ with Poetry
- ✅ Node.js 16+ with npm

---

## Step 1: Start Backend 🔧

Open **PowerShell Terminal 1** and run:

```powershell
# Navigate to backend
cd D:\Dev\codorch\backend

# Set environment variables
$env:DATABASE_URL='postgresql://usr_codorch:lebaro13@localhost:5432/codorch_dev'
$env:SECRET_KEY='dev-secret-key-change-in-production-32-chars-min'
$env:OPENAI_BASE_URL='http://localhost:3000/v1'
$env:OPENAI_API_KEY='b09805ca3e309fcb98cf790e08b6ce422450c405e13f18f5476561b513034381'

# Start backend with Poetry
poetry run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Codorch Backend starting...
INFO:     Application startup complete.
```

**Test:** Open http://localhost:8000/docs (should see Swagger UI)

---

## Step 2: Start Frontend 🎨

Open **PowerShell Terminal 2** and run:

```powershell
# Navigate to frontend  
cd D:\Dev\codorch\frontend

# Start dev server
npm run dev
```

**Expected output:**
```
 App •  READY  • http://localhost:9000
```

**Test:** Open http://localhost:9000 (should see Codorch app)

---

## Troubleshooting 🔧

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:** Make sure you're in the `backend` directory and using `poetry run`

---

**Problem:** `ModuleNotFoundError: No module named 'jose'`

**Solution:** Install dependencies:
```powershell
cd backend
poetry install
```

---

**Problem:** Database connection error

**Solution:** Check DATABASE_URL and PostgreSQL:
```powershell
$env:PGPASSWORD='lebaro13'
psql -U usr_codorch -h localhost -d codorch_dev -c "\dt"
```

---

### Frontend Issues

**Problem:** `Unknown command "dev"`

**Solution:** Install dependencies:
```powershell
cd frontend
npm install --legacy-peer-deps
```

---

**Problem:** TypeScript errors

**Solution:** These are warnings and won't prevent the app from running. Ignore them for now or install missing @types packages.

---

## Quick Test Workflow 🧪

1. **Register User**
   - Open: http://localhost:9000
   - Click Register
   - Email: `test@codorch.com`
   - Password: `Test123!@#`

2. **Create Project**
   - Click "New Project"
   - Name: "Test Project"
   - Goal: "Test goal"

3. **Test Goals**
   - Navigate to project
   - Go to Goals tab
   - Create a goal
   - Click "Analyze" (AI feature)

4. **Test Opportunities**
   - Go to Opportunities tab
   - Click "Generate with AI"
   - Watch magic happen! ✨

---

## Stopping Services

**Backend:** Press `CTRL+C` in Terminal 1

**Frontend:** Press `CTRL+C` in Terminal 2

---

## Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL=postgresql://usr_codorch:lebaro13@localhost:5432/codorch_dev
SECRET_KEY=dev-secret-key-change-in-production-32-chars-min
OPENAI_BASE_URL=http://localhost:3000/v1
OPENAI_API_KEY=b09805ca3e309fcb98cf790e08b6ce422450c405e13f18f5476561b513034381
DEFAULT_MODEL=gemini-2.5-flash
ADVANCED_MODEL=gemini-2.5-pro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

**Happy Coding! 🎉**
