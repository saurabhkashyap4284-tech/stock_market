# How to Check if Project is Running

## ⚡ Quick Check - 3 Ways

### Method 1: Using the Check Script (Easiest)
```batch
Double-click: CHECK_STATUS.bat
```
Shows:
- ✓ Backend status (Port 8000)
- ✓ Frontend status (Port 5173)
- ✓ Process IDs
- ✓ URLs to access

---

### Method 2: Using PowerShell Script
```powershell
.\CHECK_STATUS.ps1
```

---

### Method 3: Manual Check in Command Prompt

**Check Backend:**
```bash
netstat -ano | findstr :8000
```
- If something appears → Backend is running ✓
- If nothing appears → Backend is NOT running ✗

**Check Frontend:**
```bash
netstat -ano | findstr :5173
```
- If something appears → Frontend is running ✓
- If nothing appears → Frontend is NOT running ✗

---

## 🌐 Browser Check

### If both are running, open:

| Service | URL | What to expect |
|---------|-----|-----------------|
| **Frontend** | http://localhost:5173 | Login page or dashboard |
| **Backend** | http://localhost:8000 | Django welcome page |
| **API Docs** | http://localhost:8000/api/schema/ | API documentation |

---

## 🔍 What You'll See

### ✓ Backend is Running:
```
Proto  Local Address          State       PID
TCP    127.0.0.1:8000        LISTENING   5432
```

### ✓ Frontend is Running:
```
Proto  Local Address          State       PID
TCP    127.0.0.1:5173        LISTENING   7648
```

---

## ✅ Full Status Check

### Both Running (Perfect!) ✓
```
✓ Backend is RUNNING on http://localhost:8000
✓ Frontend is RUNNING on http://localhost:5173

BOTH SERVERS ARE RUNNING!
Access your project:
  Frontend:  http://localhost:5173
  Backend:   http://localhost:8000
```

### Backend Running, Frontend Not ⚠️
```
✓ Backend is RUNNING on http://localhost:8000
✗ Frontend is NOT RUNNING

Start Frontend with:
  cd frontend && npm run dev
```

### Frontend Running, Backend Not ⚠️
```
✗ Backend is NOT RUNNING
✓ Frontend is RUNNING on http://localhost:5173

Start Backend with:
  cd backend && python manage.py runserver
```

### Both Not Running ✗
```
✗ Backend is NOT RUNNING
✗ Frontend is NOT RUNNING

Start both with:
  RUN.bat
```

---

## 📋 Quick Reference

| Check | Command | Working? |
|-------|---------|----------|
| Backend | `netstat -ano \| findstr :8000` | See PID = ✓ |
| Frontend | `netstat -ano \| findstr :5173` | See PID = ✓ |
| Both | `CHECK_STATUS.bat` | See green ✓ = ✓ |

---

## 🚀 If Not Running

### Start Everything:
```bash
RUN.bat
```

### Start Separately:

**Terminal 1:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Then check status again:
```bash
CHECK_STATUS.bat
```

---

## 🎯 Troubleshooting

### Port Already in Use
If port 8000 is in use but you want to start on different port:
```bash
python manage.py runserver 8001
```

Then check on port 8001:
```bash
netstat -ano | findstr :8001
```

---

## 📊 Status Dashboard

Use this to quickly check:
```
CHECK_STATUS.bat  ← Shows everything
```

---

**Have fun! 🚀**

Last Updated: March 12, 2026
