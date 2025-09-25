# Loyalty Card MVP (Fixed)

- FastAPI backend + static SPA
- SQLite by default (no DB setup needed). Add Postgres later by setting `DATABASE_URL`.
- OTP dev mode shows OTP in response/logs.
- Roles: customer, merchant, admin.

## Render deploy (Blueprint)

1) Put this repo on GitHub with `render.yaml` at root.
2) Render → New → Blueprint → select repo/branch.
3) Env vars:
   - PYTHONPATH=backend
   - SECRET_KEY (auto by blueprint)
   - DEV_RETURN_OTP_IN_RESPONSE=true
   - ADMIN_PHONE=+8801XXXXXXXXX
   - MERCHANT_SIGNUP_CODE=LETMEIN
4) Open service URL. UI at `/`, Swagger at `/docs`.
