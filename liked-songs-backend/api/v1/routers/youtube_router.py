from fastapi import APIRouter, Request
from api.v1.services import youtube_service

router = APIRouter()

@router.get("/login")
def youtube_login():
    return youtube_service.login()

@router.get("/callback")
def youtube_callback(request: Request, code: str):
    return youtube_service.callback(request, code)

@router.get("/liked-songs")
def get_youtube_liked_songs():
    return youtube_service.get_liked_songs()

@router.get("/create-playlist-from-spotify")
def spotify_to_youtube_playlist():
    return youtube_service.spotify_to_youtube_playlist()


# @router.get("/most-played-tracks")
# def get_youtube_track_ids_of_most_played_tracks():
#     return youtube_service.get_youtube_track_ids_of_most_played_tracks()
