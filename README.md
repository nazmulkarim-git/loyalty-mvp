# AnniCard — Digital Stamp Card MVP

FastAPI + static HTML/JS.
- Cookie sessions (HttpOnly; isolated per device) — **no OTP**.
- **Customer**: sign up/sign in with phone + 4-digit PIN, view partners, stamps, edit profile (name/phone/email/dob/PIN), request redeem, logout.
- **Merchant**: separate portal; sign up/sign in (business details + PIN), add stamps to customers, approve redemptions, view-only merchant profile, logout.
- **Admin**: sign in with predefined phone + PIN (env), see & manage **all** merchants, users, and pending redemptions; can edit any user or merchant.

## Deploy on Render (Blueprint)
1. Push this folder to GitHub so the **repo root** has:
   - `render.yaml`
   - `backend/` (with `requirements.txt`, `.env.example`, `app/`)
   - `README.md`
2. Render → New → **Blueprint** → pick your repo → **Apply**.
3. Set env vars (Service → Environment):
   - `PYTHONPATH=backend`
   - `SECRET_KEY` (auto-generated is fine)
   - `SESSION_COOKIE_SECURE=true` (Render is HTTPS)
   - `ADMIN_PHONE=+8801700000000`
   - `ADMIN_PIN=1234`
   - `MERCHANT_SIGNUP_CODE=LETMEIN`
4. Manual Deploy → **Clear build cache & deploy**.

## Using the app
- Open your app URL.
- **Customer** tab → sign up or sign in → Partner Cafés + My Stamps + Profile.
- **Merchant** tab → sign up (with `MERCHANT_SIGNUP_CODE`) or sign in → Lookup customer → Add Stamp → Pending → Approve.
- **Admin** tab → sign in with `ADMIN_PHONE` + `ADMIN_PIN` → manage everything.
- API docs at `/docs`.

## Local dev (optional)
```bash
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload
```
UI is served at `/` (same origin as API).
