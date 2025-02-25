import os
import redis

# from dotenv import load_dotenv
# print("Loading environment variables")
# load_dotenv()
# print("Environment variables loaded")

# Redis setup for token storage and caching
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
print("Connecting to Redis")
print("REDIS_HOST: ", REDIS_HOST)
print("REDIS_PORT: ", REDIS_PORT)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

CLEAR_REDIS_CACHE = os.environ["CLEAR_REDIS_CACHE"]
REDIS_FLUSH_DB = os.environ["REDIS_FLUSH_DB"]
PRINT_ENV_VARS = os.environ["PRINT_ENV_VARS"]

# Frontend URL
FRONTEND_URL = os.environ["FRONTEND_URL"]
GET_SPOTIFY_MOST_PLAYED_SONGS_API = os.environ["GET_SPOTIFY_MOST_PLAYED_SONGS_API"]

# Spotify API Credentials
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_AUTH_URL = os.environ["SPOTIFY_AUTH_URL"]
SPOTIFY_TOKEN_URL = os.environ["SPOTIFY_TOKEN_URL"]
SPOTIFY_API_URL = os.environ["SPOTIFY_API_URL"]
SPOTIFY_SCOPES = os.environ["SPOTIFY_SCOPES"]
SPOTIFY_TOP_TRACKS_URL = os.environ["SPOTIFY_TOP_TRACKS_URL"]
SPOTIFY_SCOPES_USER_TOP_READ = os.environ["SPOTIFY_SCOPES_USER_TOP_READ"]

# YouTube API Credentials
YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_AUTH_URL = os.environ["YOUTUBE_AUTH_URL"]
YOUTUBE_TOKEN_URL = os.environ["YOUTUBE_TOKEN_URL"]
YOUTUBE_LIKED_VIDEOS_URL = os.environ["YOUTUBE_LIKED_VIDEOS_URL"]
YOUTUBE_SCOPES = os.environ["YOUTUBE_SCOPES"]

SPOTIFY_REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URI"]
YOUTUBE_REDIRECT_URI = os.environ["YOUTUBE_REDIRECT_URI"]

YOUTUBE_PLAYLISTS_URL = os.environ["YOUTUBE_PLAYLISTS_URL"]
YOUTUBE_SEARCH_URL = os.environ["YOUTUBE_SEARCH_URL"]
YOUTUBE_PLAYLIST_ITEMS_URL = os.environ["YOUTUBE_PLAYLIST_ITEMS_URL"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]

SONGLINK_API_URL = os.environ["SONGLINK_API_URL"]
SPOTIFY_TRACK_URL_SONGLINK = os.environ["SPOTIFY_TRACK_URL_SONGLINK"]
