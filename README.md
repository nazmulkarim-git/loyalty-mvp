# Loyalty Card MVP — fully working demo (seeded)

- FastAPI backend + static SPA
- DB seeding: creates an admin and a **Sample Café** on first boot so the list isn’t empty.
- OTP dev mode: response contains OTP when `DEV_RETURN_OTP_IN_RESPONSE=true`.
- Roles: customer (default), merchant (after registering café), admin (login with ADMIN_PHONE).

## Deploy (Render Blueprint)
1) Push to GitHub with `render.yaml` at root.
2) Render → New → Blueprint → select repo/branch.
3) Env vars:
   - PYTHONPATH=backend
   - SECRET_KEY (auto)
   - DEV_RETURN_OTP_IN_RESPONSE=true
   - ADMIN_PHONE=+8801700000000
   - MERCHANT_SIGNUP_CODE=LETMEIN
4) Open your URL.
   - UI: `/`
   - API docs: `/docs`
