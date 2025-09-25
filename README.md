# Loyalty Card MVP (FastAPI + Static Frontend)

This is a **single-repo MVP** for your digital stamp/loyalty platform.

- Backend: FastAPI + SQLite (default) or PostgreSQL
- Frontend: Single-page static app (vanilla JS) served by FastAPI
- Auth: Phone + OTP (DEV mode returns OTP in response)
- Roles: customer, merchant, admin
- Core flows: add stamp (merchant), view progress (customer), redeem → approve (merchant)

## 1) Local setup

### Prereqs
- Python 3.11+
- (Optional) PostgreSQL if you don't want SQLite

### Create virtualenv & install
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure environment
Copy `.env.example` to `.env` and edit if needed:
```
cp .env.example .env
```

Key options:
- `ADMIN_PHONE`: first login from this phone becomes admin
- `MERCHANT_SIGNUP_CODE`: required to register a merchant (except admin)
- `DEV_RETURN_OTP_IN_RESPONSE=true`: shows OTP in API response for easy testing
- `DATABASE_URL`: leave empty to use local SQLite file `loyalty.db`

### Run the server
```bash
uvicorn app.main:app --reload
```
Open the app at **http://127.0.0.1:8000/** (UI) and **/docs** (API docs).

## 2) Basic usage (Happy path)

1. **Customer** logs in:
   - Enter phone → Request OTP → Verify (use dev OTP shown).
   - You are logged in as `customer` and can see cafés (empty initially).

2. **Become merchant**:
   - Using the same logged-in session, fill *Register your Café* with the signup code from `.env` (or log in as `ADMIN_PHONE` to skip code).
   - After creation, your role is upgraded to `merchant`.
   - Use *Add Stamp*: enter a customer's phone and select your café.

3. **Customer redemption**:
   - After enough stamps (default N=9), the **Redeem** button is enabled.
   - Customer clicks Redeem → Merchant sees a pending request → Approve.
   - The customer's count resets to 0.

## 3) Deploy to Render (one service)

This repo is self-contained. Render will run the FastAPI app and serve the static site.

### render.yaml (root)
We include a minimal `render.yaml`:
- Web service: Python (uvicorn) command

### Steps
1. Push this repo to GitHub.
2. In Render: New → Web Service → Connect repo.
3. Select a region, set environment to **Python 3.11**.
4. Build Command: `pip install -r backend/requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
6. Environment:
   - `PYTHONPATH=backend`
   - (optional) `DATABASE_URL` for Postgres (Render PostgreSQL add-on), else SQLite will be used.
   - `SECRET_KEY`, `ADMIN_PHONE`, `MERCHANT_SIGNUP_CODE`, `DEV_RETURN_OTP_IN_RESPONSE=true`

> Note: On Render, ensure **PYTHONPATH=backend** or change start command to `uvicorn backend.app.main:app ...`.

## 4) Structure

```
/backend
  requirements.txt
  .env.example
  /app
    main.py               # FastAPI app + static site
    config.py             # settings via .env
    database.py           # SQLAlchemy setup
    models.py             # DB models
    schemas.py            # Pydantic schemas
    auth_utils.py         # JWT + role guard
    routers_*.py          # feature routers
    /static
      index.html          # simple SPA
```

## 5) Notes & next steps
- This is intentionally minimal for speed. You can replace the static frontend with React/Next later.
- For production:
  - Move to PostgreSQL, turn off `DEV_RETURN_OTP_IN_RESPONSE`, use real SMS for OTP.
  - Add proper sessions/refresh tokens; this MVP uses short-lived Bearer tokens only.
  - Add idempotency and rate limiting on `/stamps/add`.
  - Add more granular merchant staff users if needed.
