# Testing & Integration Guide - Codorch

## 🎯 Prerequisites

### 1. PostgreSQL Database
Ensure PostgreSQL is installed and running:
```bash
# Check PostgreSQL status (Windows)
Get-Service -Name postgresql*

# Or check if port 5432 is listening
netstat -an | findstr :5432
```

### 2. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE codorch_dev;
CREATE DATABASE codorch_test;

# Exit
\q
```

### 3. Update .env Configuration
Edit `config/.env.dev`:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/codorch_dev
OPENAI_BASE_URL=http://localhost:3000/v1
OPENAI_API_KEY=b09805ca3e309fcb98cf790e08b6ce422450c405e13f18f5476561b513034381
DEFAULT_MODEL=gemini-2.5-flash
ADVANCED_MODEL=gemini-2.5-pro
```

---

## 🚀 Step 1: Database Migrations

```bash
# Navigate to backend
cd backend

# Install dependencies (if not done)
poetry install

# Apply migrations
poetry run alembic upgrade head

# Verify migrations
poetry run alembic current
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
e6006195c986 (head)
```

---

## 🔧 Step 2: Start Backend

### Terminal 1 - Backend Server

```bash
cd backend

# Set environment
$env:ENV_FILE="config/.env.dev"

# Run with uvicorn
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should start on: **http://localhost:8000**

### Verify Backend

Open browser: **http://localhost:8000/docs**

You should see:
- ✅ Swagger UI (FastAPI docs)
- ✅ `/api/v1/auth/register` endpoint
- ✅ `/api/v1/goals/*` endpoints
- ✅ `/api/v1/opportunities/*` endpoints

---

## 🎨 Step 3: Start Frontend

### Terminal 2 - Frontend Dev Server

```bash
cd frontend

# Install dependencies (if not done)
npm install
# or
yarn install

# Run dev server
npm run dev
# or
yarn dev
# or
quasar dev
```

Frontend should start on: **http://localhost:9000**

---

## 🧪 Step 4: Integration Testing

### 4.1 Authentication Flow

1. **Register User**
   - Open: http://localhost:9000
   - Navigate to Register/Login
   - Register with:
     ```
     Email: test@codorch.com
     Password: Test123!@#
     Full Name: Test User
     ```
   - Should receive JWT token
   - Should redirect to dashboard

2. **Login**
   - Logout
   - Login with same credentials
   - Should work seamlessly

### 4.2 Create Project

1. Navigate to **Projects** page
2. Click **"New Project"**
3. Fill in:
   ```
   Name: E-Commerce Platform
   Description: Modern e-commerce solution
   Goal: Build scalable online store
   ```
4. Submit
5. Project should appear in list

### 4.3 Test Goals (Module 1)

Navigate to: `/project/{projectId}/goals`

**Test 1: Create Goal**
```
Title: Increase Revenue by 20%
Description: Achieve 20% revenue growth through new products
Category: business
Priority: high
Target Date: 2025-12-31
```

**Test 2: AI Analysis**
- Click **"Analyze"** button
- Wait for AI analysis (2-5 seconds)
- Should show:
  - ✅ SMART scores (5 dimensions)
  - ✅ Overall SMART score
  - ✅ Feedback and suggestions
  - ✅ Metrics recommendations

**Test 3: Goal Decomposition**
- Click **"Decompose"** button
- Should generate 3-5 subgoals
- Subgoals should appear as cards

**Test 4: CRUD Operations**
- Edit goal (update description)
- Update status (draft → active)
- Delete subgoal
- All should work smoothly

### 4.4 Test Opportunities (Module 2)

Navigate to: `/project/{projectId}/opportunities`

**Test 1: Manual Create**
```
Title: Mobile App Launch
Description: Launch iOS/Android app
Value Proposition: Reach mobile users
Category: product
```

**Test 2: AI Generation** ⭐
- Click **"Generate with AI"**
- Fill in:
  ```
  Context: E-commerce platform for sustainable products
  Number: 5
  Creativity Level: Balanced
  ```
- Click **"Generate"**
- Wait 10-20 seconds
- Should generate 5 opportunities with:
  - ✅ Title, description, category
  - ✅ Target market
  - ✅ Value proposition
  - ✅ Scoring (feasibility, impact, innovation, resources)
  - ✅ AI reasoning

**Test 3: Scoring Display**
- Each opportunity should show:
  - Overall score (0-10)
  - 4 dimension scores
  - Color-coded badges
  - Circular progress indicator

**Test 4: Compare Opportunities**
- Select 2-3 opportunities
- Click **"Compare"** (if implemented)
- Should show comparison matrix

---

## 🐛 Common Issues & Fixes

### Issue 1: Database Connection Error

**Error**: `could not connect to server`

**Fix**:
```bash
# Check PostgreSQL is running
Get-Service -Name postgresql*

# Start if stopped
Start-Service postgresql-x64-XX

# Verify connection
psql -U postgres -d codorch_dev
```

### Issue 2: RefMemTree Import Error

**Error**: `ModuleNotFoundError: No module named 'refmemtree'`

**Fix**:
```bash
cd backend
poetry install --no-root
# RefMemTree might fail, it's optional for basic testing
```

### Issue 3: CORS Error

**Error**: `Access to XMLHttpRequest blocked by CORS`

**Fix**: Check `backend/main.py` has CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 4: AI API Connection

**Error**: `Connection refused - localhost:3000`

**Fix**: 
- AI endpoint is configured but not running
- For testing, you can:
  1. Use mock AI responses
  2. Skip AI features temporarily
  3. Set up actual AI API endpoint

### Issue 5: Port Already in Use

**Error**: `Address already in use: 8000`

**Fix**:
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or use different port
uvicorn backend.main:app --port 8001
```

---

## ✅ Testing Checklist

### Backend API Tests
- [ ] `/health` endpoint responds
- [ ] `/api/v1/auth/register` creates user
- [ ] `/api/v1/auth/login` returns JWT
- [ ] `/api/v1/projects/` CRUD works
- [ ] `/api/v1/goals/*` endpoints work
- [ ] `/api/v1/opportunities/*` endpoints work
- [ ] Authentication required for protected routes

### Frontend UI Tests
- [ ] Login page loads
- [ ] Registration works
- [ ] Projects page displays
- [ ] Goals page loads
- [ ] Create goal dialog opens
- [ ] Goal cards display correctly
- [ ] Opportunities page loads
- [ ] AI generation dialog works
- [ ] Opportunity cards display scores
- [ ] Navigation between pages works
- [ ] Loading states show
- [ ] Error messages display

### Integration Tests
- [ ] Login → Create Project → Create Goal → AI Analysis
- [ ] Create Goal → Decompose → Subgoals appear
- [ ] Generate Opportunities → 5 opportunities created
- [ ] Edit goal → Updates immediately
- [ ] Delete opportunity → Removes from list

### AI Features Tests (if AI endpoint available)
- [ ] Goal SMART analysis works
- [ ] Goal decomposition generates subgoals
- [ ] Opportunity generation creates valid opportunities
- [ ] Scoring is reasonable (0-10 range)
- [ ] AI reasoning is present

---

## 📊 Expected Performance

| Operation | Expected Time | Status |
|-----------|---------------|--------|
| Page Load | < 1s | ✅ |
| API Call (simple) | < 100ms | ✅ |
| Create Goal | < 200ms | ✅ |
| AI Analysis | 2-5s | ⚠️ Depends on AI API |
| AI Generation | 10-20s | ⚠️ Depends on AI API |
| Goal Decomposition | 3-7s | ⚠️ Depends on AI API |

---

## 🎥 Demo Workflow

1. **Register** → test@codorch.com
2. **Create Project** → "E-Commerce Platform"
3. **Create Goal** → "Increase Revenue by 20%"
4. **AI Analysis** → Get SMART scores
5. **Decompose Goal** → Generate 3 subgoals
6. **Navigate to Opportunities**
7. **AI Generate** → 5 opportunities
8. **Review Scores** → Check feasibility/impact
9. **Update Status** → Mark opportunity as approved

---

## 📝 Test Results Template

```markdown
## Test Session: [Date/Time]

### Environment
- Backend: Running on port 8000
- Frontend: Running on port 9000
- Database: PostgreSQL 15.x
- AI API: [Available/Mock]

### Test Results

#### Authentication
- [ ] Register: PASS/FAIL
- [ ] Login: PASS/FAIL
- [ ] Token refresh: PASS/FAIL

#### Goals Module
- [ ] Create: PASS/FAIL
- [ ] Read: PASS/FAIL
- [ ] Update: PASS/FAIL
- [ ] Delete: PASS/FAIL
- [ ] AI Analysis: PASS/FAIL
- [ ] Decomposition: PASS/FAIL

#### Opportunities Module
- [ ] Create: PASS/FAIL
- [ ] Read: PASS/FAIL
- [ ] Update: PASS/FAIL
- [ ] Delete: PASS/FAIL
- [ ] AI Generation: PASS/FAIL
- [ ] Scoring: PASS/FAIL

### Issues Found
1. [Issue description]
2. [Issue description]

### Notes
[Any observations or comments]
```

---

**Happy Testing!** 🎉

If you encounter issues, check the logs:
- Backend: Terminal 1 output
- Frontend: Terminal 2 output + Browser Console (F12)
