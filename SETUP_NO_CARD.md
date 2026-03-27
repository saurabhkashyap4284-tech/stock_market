# 🚀 "Zero Card" Deployment (Render + Neon + Upstash)

Follow these steps to deploy your project 100% free without adding any credit card.

## 1. Set Up Database (Neon.tech)
1. Go to [Neon.tech](https://neon.tech/) and sign up with GitHub (No card needed).
2. Create a new project named `fo-monitor-db`.
3. In the Dashboard, find the **Connection String**.
4. Select **Postgres 15** and **Direct Connection**.
5. Copy the URL (it looks like `postgresql://user:pass@host/dbname`).
6. **Save this!** You will need it for Render.

## 2. Set Up Redis (Upstash.com)
1. Go to [Upstash.com](https://upstash.com/) and sign up with GitHub (No card needed).
2. Create a new Redis Database named `fo-redis`.
3. Select **Global** for best performance.
4. Copy the **Redis URL** (it looks like `redis://default:pass@host:port`).
5. **Save this!** You will need it for Render.

## 3. Set Up Render
1. Go to [Render.com](https://render.com/) and sign up with GitHub.
2. Click **New** -> **Web Service**.
3. Connect your GitHub repository.
4. **Name**: `fo-monitor-api`
5. **Runtime**: `Python`
6. **Build Command**: 
   ```bash
   cd backend && pip install -r requirements.txt && python manage.py collectstatic --no-input
   ```
7. **Start Command**:
   ```bash
   cd backend && honcho start -f Procfile
   ```
8. **Environment Variables**:
   Click **Advanced** -> **Add Environment Variable**:
   - `DJANGO_SETTINGS_MODULE`: `config.settings.prod`
   - `DATABASE_URL`: *(Paste your Neon URL)*
   - `REDIS_URL`: *(Paste your Upstash URL)*
   - `SECRET_KEY`: *(Generate a random string or use 'dev-secret-key')*
   - `ALLOWED_HOSTS`: `.onrender.com`
9. Click **Create Web Service**.

## 4. Keep it Awake (Cron-job.org)
Since Render's free tier sleeps, we need a pinger:
1. Go to [Cron-job.org](https://cron-job.org/) and create an account.
2. Click **Create Cronjob**.
3. **Title**: `Keep Render Awake`
4. **URL**: `https://fo-monitor-api.onrender.com/api/` (Use your actual Render URL).
5. **Interval**: Every 5 minutes.
6. Click **Create**.

## 5. Frontend (Vercel)
1. Go to [Vercel.com](https://vercel.com/) and connect your GitHub repo.
2. Select the `frontend` folder.
3. Set Environment Variable:
   - `VITE_API_URL`: `https://fo-monitor-api.onrender.com`
4. Click **Deploy**.

**Profit!** 🚀
Your project is now running 24/7 for free with zero credit card info.
