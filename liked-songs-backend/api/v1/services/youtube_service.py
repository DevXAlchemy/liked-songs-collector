import requests
from urllib.parse import urlencode
from fastapi import Request
from api.configuration import YOUTUBE_AUTH_URL, YOUTUBE_TOKEN_URL, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES, YOUTUBE_LIKED_VIDEOS_URL, FRONTEND_URL, YOUTUBE_PLAYLISTS_URL, YOUTUBE_SEARCH_URL, YOUTUBE_PLAYLIST_ITEMS_URL, YOUTUBE_API_KEY, SONGLINK_API_URL, SPOTIFY_TRACK_URL_SONGLINK, GET_SPOTIFY_MOST_PLAYED_SONGS_API
from api.configuration import redis_client
from fastapi.responses import RedirectResponse
import ast


def get_youtube_access_token():
    access_token = redis_client.get("youtube_access_token")
    if not access_token:
        access_token = refresh_youtube_token()
    return access_token

def login():
    params = {
    "client_id": YOUTUBE_CLIENT_ID,
    "redirect_uri": YOUTUBE_REDIRECT_URI,
    "response_type": "code",
    "scope": YOUTUBE_SCOPES,
    "access_type": "offline",
    "include_granted_scopes": "true",
    "prompt":"consent"
    }
    auth_url = f"{YOUTUBE_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}

def callback(request: Request, code: str):
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET
    }
    response = requests.post(YOUTUBE_TOKEN_URL, data=token_data).json()
    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    if access_token and refresh_token:
        print("Setting YouTube access token and refresh token in Redis")
        redis_client.set("youtube_access_token", access_token, ex=3600)
        redis_client.set("youtube_refresh_token", refresh_token)
    print("YouTube Callback Response: ", response)
    return RedirectResponse(FRONTEND_URL)

def refresh_youtube_token():
    refresh_token = redis_client.get("youtube_refresh_token")
    if not refresh_token:
        return None
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
    }
    response = requests.post(YOUTUBE_TOKEN_URL, data=token_data).json()
    access_token = response.get("access_token")
    if access_token:
        redis_client.set("youtube_access_token", access_token, ex=3600)
    print("YouTube Refresh Token Response: ", response)
    return access_token

def get_liked_songs_and_videos():
    access_token = get_youtube_access_token()
    if not access_token:
        return {"error": "User needs to re-login to YouTube"}, False
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "part": "snippet,contentDetails",
        "myRating": "like",
        "maxResults": 50,
    }
    response = requests.get(YOUTUBE_LIKED_VIDEOS_URL, headers=headers, params=params)
    if response.status_code == 200:
        redis_client.set("youtube_liked_songs", str(response.json()), ex=3600)
    return response.json(), True

def get_liked_songs():
    access_token = get_youtube_access_token()
    if not access_token:
        return {"items": []}, False

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "part": "snippet,contentDetails",
        "myRating": "like",
        "maxResults": 50
    }
    
    response = requests.get(YOUTUBE_LIKED_VIDEOS_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        music_songs = []

        for item in data.get("items", []):
            title = item["snippet"]["title"].lower()
            category_id = item["snippet"].get("categoryId", None)  # Check for category
            channel_title = item["snippet"]["channelTitle"].lower()

            if not item['kind'] == 'youtube#video':
                print(f"kind: {item['kind']}, category_id: {category_id}")
            
            # Filtering based on common music indicators
            if "music" in title or "vevo" in channel_title or category_id == "10":  # 10 = Music Category
                music_songs.append(item)

        redis_client.set("youtube_liked_songs", str({"items": music_songs}), ex=3600)
        # print("Filtered YouTube Music Songs: ", music_songs)
        return {"items": music_songs}, True

    return {"items": []}, False


def create_youtube_playlist(title="Spotify Songs Playlist"):
    access_token = get_youtube_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "snippet": {
            "title": "Spotify Songs Playlist",
            "description": "Playlist created from Spotify liked songs"
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    params = {
        "part": "snippet,status"
    }

    response = requests.post(YOUTUBE_PLAYLISTS_URL, headers=headers, json=data, params=params)
    print("Playlist creation response: ", response.json())
    return response.json().get("id")


def get_items_from_playslit(playlist_id):
    existing_songs = redis_client.get("youtube_playlist_items")
    if existing_songs:
        return eval(existing_songs)
    
    access_token = get_youtube_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50
    }

    playlist_items = []
    next_page_token = None
    for _ in range(0, 10): # change if songs are more than 1000
        if next_page_token:
            params["pageToken"] = next_page_token
        response = requests.get(YOUTUBE_PLAYLIST_ITEMS_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            playlist_items.extend(data.get("items", []))
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        else:
            print("Failed to fetch playlist items", response.json())
            break
    
    print("Found playlist items: ", len(playlist_items))
    playlist_songs = []
    for songs_info in playlist_items:
        playlist_songs.append(songs_info["snippet"]["resourceId"]["videoId"])

    redis_client.set("youtube_playlist_items", str(playlist_songs))
    return playlist_songs


def add_songs_to_youtube_playlist(playlist_id, video_ids):
    access_token = get_youtube_access_token()
    if not access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {
        "part": "snippet"
    }

    success_list = redis_client.get("youtube_playlist_items")
    if success_list:
        success_list = eval(success_list)
    else:
        success_list = []
    
    for video_id in video_ids:
        payload = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

        response = requests.post(YOUTUBE_PLAYLIST_ITEMS_URL, headers=headers, params=params, json=payload)
        print("VideoId: ", video_id, "Response: ", response.status_code)
        if response.status_code == 200:
            success_list.append(video_id)
        else:
            print(f"Failed to add video ID: {video_id}" , "Response: ", response.json())
    redis_client.set("youtube_playlist_items", str(success_list))
    return True


def get_youtube_video_from_songlink(track_id):
    """
    Fetches the YouTube video ID for a given Spotify track using Songlink API.
    """
    try:
        params = {
            "url": SPOTIFY_TRACK_URL_SONGLINK + track_id,
            "userCountry": "US",
            "songIfSingle": "true"
        }

        response = requests.get(SONGLINK_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            youtube_url = data.get("linksByPlatform", {}).get("youtube", {}).get("url")
            if youtube_url:
                video_id = youtube_url.split("v=")[-1]  # Extract video ID from URL
                return video_id
        print(f"No YouTube match found for Spotify track: {track_id}")
    except Exception as e:
        print(f"Error fetching from Songlink: {e}")
    
    return None

def convert_spotify_playlist_to_youtube(spotify_track_ids):
    """
    Converts a list of Spotify track IDs to YouTube video IDs.
    """
    youtube_video_ids = []
    spotify_to_youtube_map = redis_client.get("spotify_to_youtube_map")
    if spotify_to_youtube_map:
        spotify_to_youtube_map = ast.literal_eval(spotify_to_youtube_map)
        print("Loaded Spotify to YouTube map from cache", spotify_to_youtube_map)
    else:
        spotify_to_youtube_map = {}

    spotify_id_not_found = redis_client.get("spotify_id_not_found")
    if spotify_id_not_found:
        spotify_id_not_found = eval(spotify_id_not_found)
    else:
        spotify_id_not_found = []

    api_hit_count = 0
    for track_id in spotify_track_ids:
        if track_id in spotify_id_not_found:
            print(f"Skipping Spotify track ID: {track_id}")
            continue

        if track_id in spotify_to_youtube_map:
            youtube_video_ids.append(spotify_to_youtube_map[track_id])
            continue

        video_id = get_youtube_video_from_songlink(track_id)
        api_hit_count += 1
        if video_id:
            spotify_to_youtube_map[track_id] = video_id
            youtube_video_ids.append(video_id)
        else:
            spotify_id_not_found.append(track_id)
        
        if api_hit_count >= 10:
            break
    
    redis_client.set("spotify_id_not_found", str(spotify_id_not_found))
    redis_client.set("spotify_to_youtube_map", str(spotify_to_youtube_map))
    # if os.path.exists("spotify_to_youtube_map.txt"):
    #     with open("spotify_to_youtube_map.txt", "a") as f:
    #         f.write(str(spotify_to_youtube_map))
    # else:
    #     with open("spotify_to_youtube_map.txt", "w") as f:
    #         f.write(str(spotify_to_youtube_map))
    return youtube_video_ids

def spotify_to_youtube_playlist():
    """
    Converts a Spotify playlist into a YouTube playlist.
    """
    print("Converting Spotify playlist to YouTube playlist")
    spotify_track_ids, login_info = requests.get(GET_SPOTIFY_MOST_PLAYED_SONGS_API).json()
    print("Fetched Spotify track IDs")

    playlist_id = redis_client.get("spotify_youtube_playlist")
    if playlist_id:
        existing_songs = get_items_from_playslit(playlist_id)
        if existing_songs:
            spotify_to_youtube_map = ast.literal_eval(redis_client.get("spotify_to_youtube_map"))
            for spotify_id, youtube_id in spotify_to_youtube_map.items():
                if youtube_id in existing_songs:
                    print(f"Removing existing song: {youtube_id}")
                    spotify_track_ids.remove(spotify_id)
    
    youtube_video_ids = convert_spotify_playlist_to_youtube(spotify_track_ids)
    print("Converted Spotify track IDs to YouTube video IDs")

    if youtube_video_ids:
        if "spotify_youtube_playlist" in redis_client.keys() and redis_client.get("spotify_youtube_playlist"):
            playlist_id = redis_client.get("spotify_youtube_playlist")
            print("Loaded YouTube playlist ID from cache")
        else:
            playlist_id = create_youtube_playlist()
            redis_client.set("spotify_youtube_playlist", str(playlist_id))
            print("Created YouTube playlist")

        print("playlist_id:", playlist_id)
        if playlist_id:
            youtube_video_ids = youtube_video_ids[:10]
            response = add_songs_to_youtube_playlist(playlist_id, youtube_video_ids)
            if response:
                print("Added songs to YouTube playlist")
                return f"Songs added to YouTube playlist successfully"
            return "Failed to add songs to YouTube playlist"
    
    return "No songs found to add to YouTube playlist"

