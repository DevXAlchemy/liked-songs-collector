import redis
from api.configuration import redis_client


def clear_redis_cache():
    redis_client.delete("youtube_access_token")
    redis_client.delete("spotify_access_token")

    redis_client.delete("youtube_liked_songs")
    redis_client.delete("spotify_liked_songs")

    redis_client.delete("spotify_top_tracks")

    return {"message": "Redis cache cleared"}


def redis_flush_db():
    redis_client.flushdb()
    return {"message": "Redis cache flushed"}