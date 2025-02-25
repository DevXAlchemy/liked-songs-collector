from fastapi import APIRouter
from api.v1.routers import spotify_router, youtube_router

router = APIRouter()

router.include_router(spotify_router.router, prefix="/spotify")
router.include_router(youtube_router.router, prefix="/youtube")

