from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bets import router as bets_router
from app.api.routes.leaderboard import router as leaderboard_router
from app.api.routes.matches import router as matches_router
from app.api.routes.tournaments import router as tournaments_router
from app.api.routes.wallet import router as wallet_router
from app.core.config import settings

app = FastAPI(title="World Cup Prediction League API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(matches_router)
app.include_router(wallet_router)
app.include_router(bets_router)
app.include_router(admin_router)
app.include_router(leaderboard_router)
app.include_router(tournaments_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
