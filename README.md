# ExpenseFlow API — Python (FastAPI) + MongoDB

Backend for the ExpenseFlow daily expense tracker: a FastAPI service with
JWT authentication, per-user expense storage, and spending analytics, backed
by **MongoDB** via the [Beanie](https://beanie-odm.dev/) ODM.

- **Framework:** Python FastAPI
- **Database:** MongoDB (Beanie ODM, async Motor driver)
- **Auth:** JWT (stateless), BCrypt password hashing

> Frontend lives in a separate repository: **expense-tracker-frontend**.

---

## Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- A running **MongoDB** instance — either:
  - local ([MongoDB Community Server](https://www.mongodb.com/try/download/community)), or
  - a free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster

---

## Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and edit the secret
copy .env.example .env   # Windows
# cp .env.example .env    # macOS/Linux
# IMPORTANT: change JWT_KEY in .env to your own long random secret.

# Run — collections and indexes are created automatically on startup
uvicorn main:app --reload --port 5050
```

The API runs at **http://localhost:5050**.
Interactive OpenAPI docs are available at `/docs`.

### Database configuration

The backend connects to a local MongoDB instance
(`mongodb://localhost:27017`, database `expensetracker`) by default.
To use a different database, set the following in `.env`:

| Key | Description | Example |
|-----|-------------|---------|
| `DATABASE_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `DATABASE_NAME` | Database name | `expensetracker` |

Collections (`users`, `expenses`) and their indexes are created automatically
on application startup — no manual migration step is required.

---

## API endpoints

| Method | Route                      | Auth | Description                |
|--------|----------------------------|------|----------------------------|
| POST   | `/api/auth/register`       | No   | Create account, returns JWT|
| POST   | `/api/auth/login`          | No   | Log in, returns JWT        |
| GET    | `/api/expenses`            | Yes  | List your expenses         |
| POST   | `/api/expenses`            | Yes  | Create an expense          |
| PUT    | `/api/expenses/{id}`       | Yes  | Update an expense          |
| DELETE | `/api/expenses/{id}`       | Yes  | Delete an expense          |
| GET    | `/api/expenses/summary`    | Yes  | Analytics summary          |

---

## Notes

- CORS is configured to allow `http://localhost:5173` by default
  (change via `CORS_ALLOWED_ORIGINS` in `.env`; comma-separate multiple origins).
- Passwords are hashed with BCrypt; raw passwords are never stored.
- The JWT is validated on every protected route; expired/invalid tokens return `401`.
- For production: keep secrets in environment variables (never commit `.env`)
  and consider shorter token lifetimes with refresh tokens.

---

## Deployment (Render + MongoDB Atlas)

### Step 1 — Create a MongoDB Atlas database

1. Go to [MongoDB Atlas](https://cloud.mongodb.com) → **Create** a new project
2. **Build a Database** → choose the **Free (M0)** shared cluster
3. Create a **database user** (username + password) under **Database Access**
4. Under **Network Access**, add `0.0.0.0/0` (allow access from anywhere) so
   Render can connect
5. Click **Connect** → **Drivers** and copy the connection string
   (starts with `mongodb+srv://...`). Replace `<password>` with your database
   user's password.

### Step 2 — Deploy the backend on Render

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**
2. Connect this GitHub repository
3. Configure:
   - **Name:** `expensetracker-api`
   - **Root Directory:** *(leave blank — this repo's root)*
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** (auto-detected from `Procfile`)
   - **Plan:** Free
4. Add **Environment Variables:**
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | *(paste the MongoDB Atlas connection string from Step 1)* |
   | `DATABASE_NAME` | `expensetracker` |
   | `JWT_KEY` | *(a long random secret — generate one with `openssl rand -hex 32`)* |
   | `JWT_ISSUER` | `ExpenseTrackerApi` |
   | `JWT_AUDIENCE` | `ExpenseTrackerClient` |
   | `JWT_EXPIRY_MINUTES` | `1440` |
   | `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` *(your deployed frontend URL)* |
5. Click **Deploy**
6. Once live, note your backend URL (e.g. `https://expensetracker-api.onrender.com`)

> **Note:** Render free tier sleeps after 15 minutes of inactivity.
> The first request after sleep takes ~30–60 seconds to wake up.
