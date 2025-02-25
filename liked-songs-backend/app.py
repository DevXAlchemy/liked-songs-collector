from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.services import spotify_service, youtube_service, utils
from api.v1.routers import routers
from api.configuration import redis_client, CLEAR_REDIS_CACHE, REDIS_FLUSH_DB, PRINT_ENV_VARS
import os

app = FastAPI(title="Liked Songs API")

app.include_router(routers.router, prefix="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def print_all_env_vars():
    print("CLEAR_REDIS_CACHE: ", os.getenv("CLEAR_REDIS_CACHE"))
    print("REDIS_FLUSH_DB: ", os.getenv("REDIS_FLUSH_DB"))
    print("SPOTIFY_CLIENT_ID: ", os.getenv("SPOTIFY_CLIENT_ID"))
    print("SPOTIFY_CLIENT_SECRET: ", os.getenv("SPOTIFY_CLIENT_SECRET"))
    print("SPOTIFY_REDIRECT_URI: ", os.getenv("SPOTIFY_REDIRECT_URI"))
    print("YOUTUBE_CLIENT_ID: ", os.getenv("YOUTUBE_CLIENT_ID"))
    print("YOUTUBE_CLIENT_SECRET: ", os.getenv("YOUTUBE_CLIENT_SECRET"))
    print("YOUTUBE_REDIRECT_URI: ", os.getenv("YOUTUBE_REDIRECT_URI"))
    print("FRONTEND_URL: ", os.getenv("FRONTEND_URL"))
    print("GET_SPOTIFY_MOST_PLAYED_SONGS_API: ", os.getenv("GET_SPOTIFY_MOST_PLAYED_SONGS_API"))
    print("SPOTIFY_AUTH_URL: ", os.getenv("SPOTIFY_AUTH_URL"))
    print("SPOTIFY_TOKEN_URL: ", os.getenv("SPOTIFY_TOKEN_URL"))
    print("SPOTIFY_API_URL: ", os.getenv("SPOTIFY_API_URL"))
    print("SPOTIFY_SCOPES: ", os.getenv("SPOTIFY_SCOPES"))
    print("SPOTIFY_TOP_TRACKS_URL: ", os.getenv("SPOTIFY_TOP_TRACKS_URL"))
    print("SPOTIFY_SCOPES_USER_TOP_READ: ", os.getenv("SPOTIFY_SCOPES_USER_TOP_READ"))
    print("YOUTUBE_AUTH_URL: ", os.getenv("YOUTUBE_AUTH_URL"))
    print("YOUTUBE_TOKEN_URL: ", os.getenv("YOUTUBE_TOKEN_URL"))
    print("YOUTUBE_LIKED_VIDEOS_URL: ", os.getenv("YOUTUBE_LIKED_VIDEOS_URL"))
    print("YOUTUBE_SCOPES: ", os.getenv("YOUTUBE_SCOPES"))
    print("YOUTUBE_PLAYLISTS_URL: ", os.getenv("YOUTUBE_PLAYLISTS_URL"))
    print("YOUTUBE_SEARCH_URL: ", os.getenv("YOUTUBE_SEARCH_URL"))
    print("YOUTUBE_PLAYLIST_ITEMS_URL: ", os.getenv("YOUTUBE_PLAYLIST_ITEMS_URL"))
    print("YOUTUBE_API_KEY: ", os.getenv("YOUTUBE_API_KEY"))
    print("SONGLINK_API_URL: ", os.getenv("SONGLINK_API_URL"))
    print("SPOTIFY_TRACK_URL_SONGLINK: ", os.getenv("SPOTIFY_TRACK_URL_SONGLINK"))

    
def init():
    print("Initializing")
    global CLEAR_REDIS_CACHE
    global REDIS_FLUSH_DB

    if REDIS_FLUSH_DB == "True":
        print("Flushing Redis DB")
        utils.redis_flush_db()
        REDIS_FLUSH_DB = "False"
        print("Redis DB Flushed")
    elif CLEAR_REDIS_CACHE == "True":
        print("Clearing Redis Cache")
        utils.clear_redis_cache()
        CLEAR_REDIS_CACHE = "False"
        print("Redis Cache Cleared")
    print("Redis values: ", redis_client.keys())

    if PRINT_ENV_VARS:
        print_all_env_vars()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Liked Songs API"}


@app.get("/v1/merged-liked-songs")
def get_merged_liked_songs():
    is_spotify_logged_in = True
    is_youtube_logged_in = True

    spotify_songs = redis_client.get("spotify_liked_songs")
    youtube_songs = redis_client.get("youtube_liked_songs")

    if spotify_songs:
        spotify_songs = eval(spotify_songs)
    else:
        spotify_songs, is_spotify_logged_in = spotify_service.get_liked_songs()

    if youtube_songs:
        youtube_songs = eval(youtube_songs)
    else:
        youtube_songs, is_youtube_logged_in = youtube_service.get_liked_songs()

    merged_songs = []
    for item in spotify_songs.get("items", []):
        merged_songs.append({
            "platform": "Spotify",
            "title": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "added_at": item["added_at"]
        })
    
    for item in youtube_songs.get("items", []):
        merged_songs.append({
            "platform": "YouTube",
            "title": item["snippet"]["title"],
            "artist": item["snippet"]["channelTitle"],
            "added_at": item["snippet"]["publishedAt"]
        })
    
    merged_songs.sort(key=lambda x: x["added_at"], reverse=True)
    
    login_info = {"loggedIn": {"spotify": is_spotify_logged_in, "youtube": is_youtube_logged_in}}
    
    return {"status": "success", "data": merged_songs, "login_info": login_info}

init()