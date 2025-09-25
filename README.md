# Loyalty Card MVP — Admin + Merchant + Customer

- FastAPI backend; static SPA at `/`; Swagger at `/docs`.
- Seed on first boot: creates Admin (ADMIN_PHONE) and a **Sample Café**.
- Roles:
  - `customer` (default after OTP)
  - `merchant` (after registering café with MERCHANT_SIGNUP_CODE)
  - `admin` (login using ADMIN_PHONE)

## Render (Blueprint) Deploy
1. Put this repo on GitHub with `render.yaml` at the **root**.
2. Render → New → Blueprint → select repo/branch → Apply.
3. Env vars:
   - PYTHONPATH=backend
   - SECRET_KEY (auto)
   - DEV_RETURN_OTP_IN_RESPONSE=true
   - ADMIN_PHONE=+8801700000000
   - MERCHANT_SIGNUP_CODE=LETMEIN
4. Manual Deploy → Clear build cache & deploy.
5. Open your URL.
