import requests
from urllib.parse import urlencode
from fastapi import Request
from api.configuration import SPOTIFY_AUTH_URL, SPOTIFY_TOKEN_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPES, SPOTIFY_API_URL, FRONTEND_URL, SPOTIFY_TOP_TRACKS_URL, SPOTIFY_SCOPES_USER_TOP_READ
from api.configuration import redis_client
from fastapi.responses import RedirectResponse

def login():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES + " " + SPOTIFY_SCOPES_USER_TOP_READ,
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}

def callback(request: Request, code: str):
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data).json()
    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    if access_token and refresh_token:
        redis_client.set("spotify_access_token", access_token, ex=3600)
        redis_client.set("spotify_refresh_token", refresh_token)
    print("Spotify Callback Response: ", response)
    return RedirectResponse(FRONTEND_URL)

def refresh_spotify_token():
    refresh_token = redis_client.get("spotify_refresh_token")
    if not refresh_token:
        return None
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data).json()
    access_token = response.get("access_token")
    if access_token:
        redis_client.set("spotify_access_token", access_token, ex=3600)
    print("Spotify Refresh Token Response: ", response)
    return access_token

def get_liked_songs():
    print("Getting liked songs")
    access_token = redis_client.get("spotify_access_token")
    if not access_token:
        access_token = refresh_spotify_token()
        if not access_token:
            return {"error": "User not logged in"}, False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTIFY_API_URL, headers=headers)
    if response.status_code == 200:
        redis_client.set("spotify_liked_songs", str(response.json()), ex=3600)
    return response.json(), True

def get_spotify_track_ids_of_most_played_tracks():
    print("Getting most played tracks")
    if "spotify_top_tracks" in redis_client.keys():
        return eval(redis_client.get("spotify_top_tracks")), True
    
    access_token = redis_client.get("spotify_access_token")
    if not access_token:
        access_token = refresh_spotify_token()
        if not access_token:
            return {"error": "User not logged in"}, False

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTIFY_TOP_TRACKS_URL, headers=headers, params={"limit": 50})
    # print("response:", response.json())
    if response.status_code == 200:
        track_ids = [track["id"] for track in response.json()["items"]]
        print("track_ids:", track_ids)
        redis_client.set("spotify_top_tracks", str(track_ids))
        # with open("spotify_top_tracks.txt", "w") as f:
        #     f.write(str(track_ids))
        # print("Spotify Top Tracks Response: ")
        return track_ids, True
    return response.json(), False


def youtube_to_spotify_playlist():
    print("Creating playlist from YouTube liked songs")
    return {"message": "Creating playlist from YouTube liked songs"}


# def get_youtube_track_ids_of_most_played_tracks():
#     print("Getting most played tracks")
#     if "youtube_top_tracks" in redis_client.keys():
#         return eval(redis_client.get("youtube_top_tracks")), True
    
#     access_token = redis_client.get("youtube_access_token")
#     if not access_token:
#         access_token = refresh_spotify_token()
#         if not access_token:
#             return {"error": "User not logged in"}, False

#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(YOUTUBE_TOP_TRACKS_URL, headers=headers, params={"limit": 50})
#     print("response:", response.json())
#     if response.status_code == 200:
#         track_ids = [track["id"] for track in response.json()["items"]]
#         print("track_ids:", track_ids)
#         redis_client.set("youtube_top_tracks", str(track_ids))
#         with open("youtube_top_tracks.txt", "w") as f:
#             f.write(str(track_ids))
#         print("YouTube Top Tracks Response: ")
#         return track_ids, True
#     return response.json(), False