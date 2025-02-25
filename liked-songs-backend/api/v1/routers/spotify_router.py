from fastapi import APIRouter, Request
from api.v1.services import spotify_service

router = APIRouter()

@router.get("/login")
def spotify_login():
    return spotify_service.login()

@router.get("/callback")
def spotify_callback(request: Request, code: str):
    return spotify_service.callback(request, code)

@router.get("/liked-songs")
def get_spotify_liked_songs():
    return spotify_service.get_liked_songs()

@router.get("/most-played-tracks")
def get_spotify_track_ids_of_most_played_tracks():
    return spotify_service.get_spotify_track_ids_of_most_played_tracks()


# @router.get('create-playlist-from-youtube')
# def youtube_to_spotify_playlist():
#     return spotify_service.youtube_to_spotify_playlist()
