# World Cup Prediction League

Backend skeleton for the World Cup Prediction League MVP.

## Local Backend Setup

Requirements:

- Python 3.12
- PostgreSQL

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Update `DATABASE_URL` in `.env` if your local PostgreSQL username, password, host, port, or database name differs.

Create the PostgreSQL database:

```bash
createdb world_cup_prediction
```

Run migrations:

```bash
alembic upgrade head
```

Seed sample World Cup matches and markets:

```bash
python -m scripts.seed_matches
```

Seed tournament winner markets:

```bash
python -m scripts.seed_tournaments
```

Seed production-like initial data in one command:

```bash
python -m scripts.seed_initial_data
```

This creates configured seed users, initial wallet ledger rows, sample matches, match winner markets, over/under 2.5 markets, exact score markets, and tournament winner markets.

Run tests:

```bash
pytest
```

Start the FastAPI app:

```bash
uvicorn app.main:app --reload
```

Start the React frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000`. To override it:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

## Deployment Readiness

Target deployment:

- Backend: Render Web Service
- Database: Render PostgreSQL
- Frontend: Vercel

Note: Render Web Services include a free instance type. Render's current Postgres pricing page does not list a free PostgreSQL tier; the included `render.yaml` uses `basic-256mb`. If the Render dashboard offers a trial or free database option in your account, you can choose it there.

Backend production environment variables:

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/world_cup_prediction
SECRET_KEY=replace-with-a-random-secret-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
ADMIN_EMAILS=ian@test.com
```

Render PostgreSQL provides `DATABASE_URL` when connected to the backend service. The app accepts Render's standard `postgresql://...` URL and converts it internally for the installed `psycopg` driver.

The backend refuses to boot with `ENVIRONMENT=production` if `SECRET_KEY` is still the local placeholder or shorter than 32 characters.

Frontend production environment variables:

```bash
VITE_API_BASE_URL=https://your-render-backend.onrender.com
VITE_ADMIN_EMAILS=ian@test.com
```

### Render Backend And PostgreSQL

Files used by Render:

- `render.yaml`: backend web service, PostgreSQL database, env var wiring, health check
- `requirements.txt`: backend dependencies

Render setup:

1. Push this repo to GitHub.
2. In Render, create a new Blueprint from the repo.
3. Render will read `render.yaml`.
4. Confirm the web service root is the repository root.
5. Confirm the web service start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Confirm the health check path:

```text
/health
```

7. Set Render environment variables marked `sync: false` in `render.yaml`:

```bash
SECRET_KEY=<generate-a-random-secret-at-least-32-characters>
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
SEED_USERS=ian:ian@test.com:<strong-admin-password>,demo:demo@test.com:<strong-demo-password>
```

8. Render injects `PORT`.
9. Render injects `DATABASE_URL` from the PostgreSQL database defined in `render.yaml`.
10. Deploy the backend.

Render backend URL format:

```text
https://your-render-backend.onrender.com
```

After Render deploys the backend, open the backend service Shell and run migrations:

```bash
alembic upgrade head
```

Seed production sample data:

```bash
python -m scripts.seed_initial_data
```

The seed command is idempotent. It creates configured users, initial wallet transactions, sample matches, match winner markets, over/under 2.5 markets, exact score markets, tournament, and tournament winner markets.

### Vercel Frontend

Files used by Vercel:

- `frontend/vercel.json`: Vite build command, output directory, SPA rewrite
- `frontend/package.json`: build script

Vercel setup:

1. Create a new Vercel project from this repo.
2. Set the Vercel project root directory to `frontend`.
3. Use framework preset `Vite`.
4. Set frontend environment variables:

```bash
VITE_API_BASE_URL=https://your-render-backend.onrender.com
VITE_ADMIN_EMAILS=ian@test.com
```

5. Deploy the frontend.
6. Copy the deployed Vercel URL.
7. Go back to Render and set:

```bash
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
```

8. Redeploy the Render backend after changing CORS.

### Production Commands

Clean database deployment order:

```bash
cp .env.production.example .env
# edit .env with real secrets and database URL
alembic upgrade head
python -m scripts.seed_initial_data
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Production frontend build:

```bash
cd frontend
cp .env.production.example .env.production
# edit .env.production with the deployed backend URL
npm install
npm run build
```

Optional seed users are controlled by `SEED_USERS`:

```bash
SEED_USERS=ian:ian@test.com:strong-admin-password,demo:demo@test.com:strong-demo-password
```

Run the smoke test against a production-like environment:

```bash
SMOKE_API_BASE_URL=https://your-render-backend.onrender.com \
SMOKE_ADMIN_EMAIL=ian@test.com \
SMOKE_ADMIN_PASSWORD=<strong-admin-password> \
python -m scripts.smoke_test
```

Smoke test coverage:

- health check
- register/login
- wallet balance starts at `10000`
- match list and market lookup
- place match winner bet
- place exact score bet
- place over/under 2.5 bet
- settle bets through the admin API
- verify API wallet balance matches the wallet transaction ledger

Manual ledger verification:

```sql
SELECT u.email, wt.amount, wt.transaction_type, wt.reference_id, wt.created_at
FROM wallet_transactions wt
JOIN users u ON u.id = wt.user_id
ORDER BY wt.id;
```

### Final Deployment Checklist

- Render PostgreSQL database is created.
- Render backend service is deployed from repository root.
- Render backend has `DATABASE_URL` from PostgreSQL.
- Render backend has `ENVIRONMENT=production`.
- Render backend has a strong `SECRET_KEY`.
- Render backend has `ADMIN_EMAILS=ian@test.com`.
- Render backend `BACKEND_CORS_ORIGINS` exactly matches the deployed Vercel URL.
- Render health check `/health` returns `{"status":"ok"}`.
- Production migration completed in Render Shell with `alembic upgrade head`.
- Production seed completed in Render Shell with `python -m scripts.seed_initial_data`.
- Vercel project root is `frontend`.
- Vercel has `VITE_API_BASE_URL` pointing to the Render backend URL.
- Vercel has `VITE_ADMIN_EMAILS=ian@test.com`.
- Browser can load the Vercel app.
- Login works with seeded admin user.
- `/matches` shows seeded matches and markets.
- A match winner bet can be placed.
- An exact score bet can be placed.
- An over/under 2.5 bet can be placed.
- Admin settlement works from the admin account.
- Wallet balance and `wallet_transactions` ledger match after settlement.

Health check:

```bash
curl http://127.0.0.1:8000/health
```

List matches:

```bash
curl http://127.0.0.1:8000/matches
```

Get one match:

```bash
curl http://127.0.0.1:8000/matches/1
```

Get open markets for a match:

```bash
curl http://127.0.0.1:8000/matches/1/markets
```

Market responses include match winner markets and over/under goals markets:

```json
{
  "id": 4,
  "market_type": "over_under",
  "selection": "OVER",
  "line": "2.50",
  "odds": "1.95",
  "status": "OPEN"
}
```

Exact score markets use `market_type = "exact_score"` and `selection = "HOME_SCORE-AWAY_SCORE"`:

```json
{
  "id": 6,
  "market_type": "exact_score",
  "selection": "2-1",
  "line": null,
  "odds": "9.00",
  "status": "OPEN"
}
```

Seeded exact-score selections include:

```text
0-0, 1-0, 1-1, 2-0, 2-1, 2-2,
3-0, 3-1, 3-2, 3-3,
4-0, 4-1, 4-2, 4-3, 4-4,
0-1, 0-2, 1-2
```

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"predictor","email":"predictor@example.com","password":"password123"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"predictor@example.com","password":"password123"}'
```

Store the returned access token:

```bash
export TOKEN="paste-access-token-here"
```

Get wallet balance:

```bash
curl http://127.0.0.1:8000/wallet \
  -H "Authorization: Bearer $TOKEN"
```

Place a bet:

```bash
curl -X POST http://127.0.0.1:8000/bets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"market_id":1,"stake":100}'
```

Place an over/under bet:

```bash
curl -X POST http://127.0.0.1:8000/bets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"market_id":4,"stake":100}'
```

Place an exact-score bet:

```bash
curl -X POST http://127.0.0.1:8000/bets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"market_id":6,"stake":100}'
```

Get my bets:

```bash
curl http://127.0.0.1:8000/bets/me \
  -H "Authorization: Bearer $TOKEN"
```

Update a match result and settle bets:

```bash
curl -X PATCH http://127.0.0.1:8000/admin/matches/1/result \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"home_score":2,"away_score":1}'
```

Unsettle a match for local testing:

```bash
curl -X POST http://127.0.0.1:8000/admin/matches/1/unsettle \
  -H "Authorization: Bearer $TOKEN"
```

Void all bets for a match and refund original stakes for local testing:

```bash
curl -X POST http://127.0.0.1:8000/admin/matches/1/void-bets \
  -H "Authorization: Bearer $TOKEN"
```

Get leaderboard:

```bash
curl http://127.0.0.1:8000/leaderboard
curl http://127.0.0.1:8000/leaderboard?limit=10
```

List tournaments:

```bash
curl http://127.0.0.1:8000/tournaments
```

Get tournament winner markets:

```bash
curl http://127.0.0.1:8000/tournaments/1/markets
```

Place a tournament winner bet:

```bash
curl -X POST http://127.0.0.1:8000/tournament-bets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tournament_market_id":1,"stake":100}'
```

Get my tournament bets:

```bash
curl http://127.0.0.1:8000/tournament-bets/me \
  -H "Authorization: Bearer $TOKEN"
```

Settle a tournament winner:

```bash
curl -X PATCH http://127.0.0.1:8000/admin/tournaments/1/winner \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"winner_team":"Brazil"}'
```

Unsettle a tournament for local testing:

```bash
curl -X PATCH http://127.0.0.1:8000/admin/tournaments/1/unsettle \
  -H "Authorization: Bearer $TOKEN"
```

Void all bets for a tournament and refund original stakes for local testing:

```bash
curl -X PATCH http://127.0.0.1:8000/admin/tournaments/1/void-bets \
  -H "Authorization: Bearer $TOKEN"
```

Verify wallet balance changed from `10000` to `9900` after placing a `100` coin bet:

```bash
curl http://127.0.0.1:8000/wallet \
  -H "Authorization: Bearer $TOKEN"
```

Sample SQL checks:

```sql
SELECT id, username, email FROM users;
SELECT user_id, SUM(amount) AS balance FROM wallet_transactions GROUP BY user_id;
SELECT
  ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(wt.amount), 0) DESC, u.id) AS rank,
  u.id AS user_id,
  u.username,
  COALESCE(SUM(wt.amount), 0) AS balance
FROM users u
JOIN wallet_transactions wt ON wt.user_id = u.id
GROUP BY u.id, u.username
ORDER BY balance DESC, u.id
LIMIT 50;
SELECT id, user_id, market_id, stake, odds, status FROM bets;
SELECT user_id, amount, transaction_type, reference_id FROM wallet_transactions ORDER BY id;
SELECT id, home_score, away_score, status FROM matches;
SELECT id, match_id, selection, status FROM markets ORDER BY id;
SELECT id, match_id, market_type, selection, line, odds, status FROM markets ORDER BY id;
SELECT id, name, year, status, winner_team FROM tournaments;
SELECT id, tournament_id, selection, odds, status FROM tournament_markets ORDER BY id;
SELECT id, user_id, tournament_market_id, selection, stake, odds, payout, status FROM tournament_bets;
SELECT user_id, amount, transaction_type, reference_id FROM wallet_transactions ORDER BY id;
```
