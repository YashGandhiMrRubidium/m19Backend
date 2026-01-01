from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Set
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# TMDB API Configuration
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Favorite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    movie_id: int
    movie_data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FavoriteCreate(BaseModel):
    user_id: str
    movie_id: int
    movie_data: dict

class Watchlist(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    movie_id: int
    movie_data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WatchlistCreate(BaseModel):
    user_id: str
    movie_id: int
    movie_data: dict

# TV Show Models
class TVShowFavorite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tv_id: int
    tv_data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TVShowFavoriteCreate(BaseModel):
    user_id: str
    tv_id: int
    tv_data: dict

class TVShowWatchlist(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tv_id: int
    tv_data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TVShowWatchlistCreate(BaseModel):
    user_id: str
    tv_id: int
    tv_data: dict

# Live Users Tracking
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_last_seen: Dict[str, datetime] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_last_seen[user_id] = datetime.now(timezone.utc)
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_last_seen:
            del self.user_last_seen[user_id]
            
    async def send_count(self):
        count = self.get_online_count()
        message = json.dumps({"type": "user_count", "count": count})
        disconnected = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except:
                disconnected.append(user_id)
        
        for user_id in disconnected:
            self.disconnect(user_id)
    
    def update_activity(self, user_id: str):
        self.user_last_seen[user_id] = datetime.now(timezone.utc)
        
    def get_online_count(self) -> int:
        now = datetime.now(timezone.utc)
        # Count users active in the last 1 minute
        online_users = sum(
            1 for last_seen in self.user_last_seen.values()
            if (now - last_seen).total_seconds() < 60
        )
        return online_users
    
    def cleanup_inactive_users(self):
        now = datetime.now(timezone.utc)
        inactive = [
            user_id for user_id, last_seen in self.user_last_seen.items()
            if (now - last_seen).total_seconds() >= 120  # Remove after 2 minutes
        ]
        for user_id in inactive:
            self.disconnect(user_id)

manager = ConnectionManager()

# TMDB API Routes
@api_router.get("/movies/trending")
async def get_trending_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/movies/popular")
async def get_popular_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/popular",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/movies/top-rated")
async def get_top_rated_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/top_rated",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/movies/now-playing")
async def get_now_playing_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/now_playing",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/movies/upcoming")
async def get_upcoming_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/upcoming",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/movies/search")
async def search_movies(query: str, page: int = 1):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={"api_key": TMDB_API_KEY, "query": query, "page": page}
        )
        return response.json()

@api_router.get("/movies/{movie_id}")
async def get_movie_details(movie_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY, "append_to_response": "credits,videos,similar"}
        )
        return response.json()

@api_router.get("/movies/genre/{genre_id}")
async def get_movies_by_genre(genre_id: int, page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params={"api_key": TMDB_API_KEY, "with_genres": genre_id, "page": page, "sort_by": "popularity.desc"}
        )
        return response.json()

@api_router.get("/genres")
async def get_genres():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/genre/movie/list",
            params={"api_key": TMDB_API_KEY}
        )
        return response.json()

# Favorites Routes
@api_router.post("/favorites", response_model=Favorite)
async def add_favorite(input: FavoriteCreate):
    # Check if already exists
    existing = await db.favorites.find_one({
        "user_id": input.user_id,
        "movie_id": input.movie_id
    }, {"_id": 0})
    
    if existing:
        return existing
    
    favorite_obj = Favorite(**input.model_dump())
    doc = favorite_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.favorites.insert_one(doc)
    return favorite_obj


@api_router.get("/ping")
async def ping():
    return {"message": "server is running"}

@api_router.delete("/favorites/{user_id}/{movie_id}")
async def remove_favorite(user_id: str, movie_id: int):
    result = await db.favorites.delete_one({
        "user_id": user_id,
        "movie_id": movie_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Favorite removed"}

@api_router.get("/favorites/{user_id}", response_model=List[Favorite])
async def get_favorites(user_id: str):
    favorites = await db.favorites.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for fav in favorites:
        if isinstance(fav['timestamp'], str):
            fav['timestamp'] = datetime.fromisoformat(fav['timestamp'])
    
    return favorites

@api_router.get("/favorites/{user_id}/check/{movie_id}")
async def check_favorite(user_id: str, movie_id: int):
    exists = await db.favorites.find_one({
        "user_id": user_id,
        "movie_id": movie_id
    })
    
    return {"is_favorite": exists is not None}

# Watchlist Routes
@api_router.post("/watchlist", response_model=Watchlist)
async def add_to_watchlist(input: WatchlistCreate):
    # Check if already exists
    existing = await db.watchlist.find_one({
        "user_id": input.user_id,
        "movie_id": input.movie_id
    }, {"_id": 0})
    
    if existing:
        return existing
    
    watchlist_obj = Watchlist(**input.model_dump())
    doc = watchlist_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.watchlist.insert_one(doc)
    return watchlist_obj

@api_router.delete("/watchlist/{user_id}/{movie_id}")
async def remove_from_watchlist(user_id: str, movie_id: int):
    result = await db.watchlist.delete_one({
        "user_id": user_id,
        "movie_id": movie_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return {"message": "Removed from watchlist"}

@api_router.get("/watchlist/{user_id}", response_model=List[Watchlist])
async def get_watchlist(user_id: str):
    watchlist = await db.watchlist.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for item in watchlist:
        if isinstance(item['timestamp'], str):
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    
    return watchlist

@api_router.get("/watchlist/{user_id}/check/{movie_id}")
async def check_watchlist(user_id: str, movie_id: int):
    exists = await db.watchlist.find_one({
        "user_id": user_id,
        "movie_id": movie_id
    })
    
    return {"in_watchlist": exists is not None}

# TV Show TMDB API Routes
@api_router.get("/tv/trending")
async def get_trending_tv(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/trending/tv/week",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/tv/popular")
async def get_popular_tv(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/popular",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/tv/top-rated")
async def get_top_rated_tv(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/top_rated",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/tv/on-the-air")
async def get_on_the_air_tv(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/on_the_air",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/tv/airing-today")
async def get_airing_today_tv(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/airing_today",
            params={"api_key": TMDB_API_KEY, "page": page}
        )
        return response.json()

@api_router.get("/tv/search")
async def search_tv(query: str, page: int = 1):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/tv",
            params={"api_key": TMDB_API_KEY, "query": query, "page": page}
        )
        return response.json()

@api_router.get("/tv/{tv_id}")
async def get_tv_details(tv_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/{tv_id}",
            params={"api_key": TMDB_API_KEY, "append_to_response": "credits,videos,similar"}
        )
        return response.json()

@api_router.get("/tv/{tv_id}/season/{season_number}")
async def get_season_details(tv_id: int, season_number: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/{tv_id}/season/{season_number}",
            params={"api_key": TMDB_API_KEY}
        )
        return response.json()

@api_router.get("/tv/{tv_id}/season/{season_number}/episode/{episode_number}")
async def get_episode_details(tv_id: int, season_number: int, episode_number: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/tv/{tv_id}/season/{season_number}/episode/{episode_number}",
            params={"api_key": TMDB_API_KEY}
        )
        return response.json()

@api_router.get("/tv/genre/{genre_id}")
async def get_tv_by_genre(genre_id: int, page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/discover/tv",
            params={"api_key": TMDB_API_KEY, "with_genres": genre_id, "page": page, "sort_by": "popularity.desc"}
        )
        return response.json()

# TV Show Favorites Routes
@api_router.post("/tv/favorites", response_model=TVShowFavorite)
async def add_tv_favorite(input: TVShowFavoriteCreate):
    existing = await db.tv_favorites.find_one({
        "user_id": input.user_id,
        "tv_id": input.tv_id
    }, {"_id": 0})
    
    if existing:
        return existing
    
    favorite_obj = TVShowFavorite(**input.model_dump())
    doc = favorite_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.tv_favorites.insert_one(doc)
    return favorite_obj

@api_router.delete("/tv/favorites/{user_id}/{tv_id}")
async def remove_tv_favorite(user_id: str, tv_id: int):
    result = await db.tv_favorites.delete_one({
        "user_id": user_id,
        "tv_id": tv_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Favorite removed"}

@api_router.get("/tv/favorites/{user_id}", response_model=List[TVShowFavorite])
async def get_tv_favorites(user_id: str):
    favorites = await db.tv_favorites.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for fav in favorites:
        if isinstance(fav['timestamp'], str):
            fav['timestamp'] = datetime.fromisoformat(fav['timestamp'])
    
    return favorites

@api_router.get("/tv/favorites/{user_id}/check/{tv_id}")
async def check_tv_favorite(user_id: str, tv_id: int):
    exists = await db.tv_favorites.find_one({
        "user_id": user_id,
        "tv_id": tv_id
    })
    
    return {"is_favorite": exists is not None}

# TV Show Watchlist Routes
@api_router.post("/tv/watchlist", response_model=TVShowWatchlist)
async def add_to_tv_watchlist(input: TVShowWatchlistCreate):
    existing = await db.tv_watchlist.find_one({
        "user_id": input.user_id,
        "tv_id": input.tv_id
    }, {"_id": 0})
    
    if existing:
        return existing
    
    watchlist_obj = TVShowWatchlist(**input.model_dump())
    doc = watchlist_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.tv_watchlist.insert_one(doc)
    return watchlist_obj

@api_router.delete("/tv/watchlist/{user_id}/{tv_id}")
async def remove_from_tv_watchlist(user_id: str, tv_id: int):
    result = await db.tv_watchlist.delete_one({
        "user_id": user_id,
        "tv_id": tv_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return {"message": "Removed from watchlist"}

@api_router.get("/tv/watchlist/{user_id}", response_model=List[TVShowWatchlist])
async def get_tv_watchlist(user_id: str):
    watchlist = await db.tv_watchlist.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for item in watchlist:
        if isinstance(item['timestamp'], str):
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    
    return watchlist

@api_router.get("/tv/watchlist/{user_id}/check/{tv_id}")
async def check_tv_watchlist(user_id: str, tv_id: int):
    exists = await db.tv_watchlist.find_one({
        "user_id": user_id,
        "tv_id": tv_id
    })
    
    return {"in_watchlist": exists is not None}

# Live Users Counter
@api_router.get("/users/online-count")
async def get_online_count():
    return {"count": manager.get_online_count()}

# Anime API Routes (FireAnime API)
FIREANIME_BASE_URL = "https://fireani.me/api"

# Cache for anime API responses (in-memory cache with TTL)
anime_cache: Dict[str, Dict] = {}
CACHE_TTL = 300  # 5 minutes cache

def get_cache_key(endpoint: str, params: dict = None) -> str:
    """Generate cache key from endpoint and parameters"""
    if params:
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint}?{param_str}"
    return endpoint

def get_from_cache(key: str) -> Optional[dict]:
    """Get data from cache if not expired"""
    if key in anime_cache:
        data, timestamp = anime_cache[key]
        if datetime.now(timezone.utc) - timestamp < timedelta(seconds=CACHE_TTL):
            return data
        else:
            del anime_cache[key]
    return None

def set_cache(key: str, data: dict):
    """Store data in cache with timestamp"""
    anime_cache[key] = (data, datetime.now(timezone.utc))

@api_router.get("/anime/sliders")
async def get_anime_sliders():
    """Get featured anime from sliders endpoint"""
    cache_key = get_cache_key("sliders")
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{FIREANIME_BASE_URL}/sliders")
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/search")
async def search_anime(q: str):
    """Search anime by title or keyword"""
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    cache_key = get_cache_key("search", {"q": q})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{FIREANIME_BASE_URL}/anime/search",
            params={"q": q}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/genres")
async def get_anime_genres():
    """Get all anime organized by genre"""
    cache_key = get_cache_key("genres")
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{FIREANIME_BASE_URL}/genres")
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/genre")
async def get_anime_by_genre(genere: str, page: int = 1):
    """Get anime filtered by specific genre"""
    cache_key = get_cache_key("genre", {"genere": genere, "page": page})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{FIREANIME_BASE_URL}/animes/genre",
            params={"genere": genere, "page": page}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/calendars")
async def get_anime_calendars():
    """Get upcoming anime episode release schedule"""
    cache_key = get_cache_key("calendars")
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{FIREANIME_BASE_URL}/calendars")
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/details")
async def get_anime_details(slug: str):
    """Get detailed information about a specific anime"""
    if not slug:
        raise HTTPException(status_code=400, detail="Query parameter 'slug' is required")
    
    cache_key = get_cache_key("details", {"slug": slug})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{FIREANIME_BASE_URL}/anime",
            params={"slug": slug}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anime/episode")
async def get_anime_episode(slug: str, season: int, episode: int):
    """Get anime episode with video links"""
    if not slug:
        raise HTTPException(status_code=400, detail="Query parameter 'slug' is required")
    if season is None:
        raise HTTPException(status_code=400, detail="Query parameter 'season' is required")
    if episode is None:
        raise HTTPException(status_code=400, detail="Query parameter 'episode' is required")
    
    cache_key = get_cache_key("episode", {"slug": slug, "season": season, "episode": episode})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{FIREANIME_BASE_URL}/anime/episode",
            params={"slug": slug, "season": season, "episode": episode}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

# Anilist API Routes (GraphQL)
ANILIST_API_URL = "https://graphql.anilist.co"

@api_router.get("/anilist/trending")
async def get_anilist_trending(page: int = 1, perPage: int = 20):
    """Get trending anime from Anilist"""
    cache_key = get_cache_key("anilist_trending", {"page": page, "perPage": perPage})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    query = """
    query ($page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(sort: TRENDING_DESC, type: ANIME) {
                id
                idMal
                title {
                    romaji
                    english
                    native
                }
                coverImage {
                    extraLarge
                    large
                    medium
                }
                bannerImage
                averageScore
                meanScore
                genres
                episodes
                status
                format
                season
                seasonYear
                description
            }
        }
    }
    """
    
    variables = {"page": page, "perPage": perPage}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_API_URL,
            json={"query": query, "variables": variables}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anilist/popular")
async def get_anilist_popular(page: int = 1, perPage: int = 20):
    """Get popular anime from Anilist"""
    cache_key = get_cache_key("anilist_popular", {"page": page, "perPage": perPage})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    query = """
    query ($page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(sort: POPULARITY_DESC, type: ANIME) {
                id
                idMal
                title {
                    romaji
                    english
                    native
                }
                coverImage {
                    extraLarge
                    large
                    medium
                }
                bannerImage
                averageScore
                meanScore
                genres
                episodes
                status
                format
                season
                seasonYear
                description
            }
        }
    }
    """
    
    variables = {"page": page, "perPage": perPage}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_API_URL,
            json={"query": query, "variables": variables}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anilist/search")
async def search_anilist_anime(q: str, page: int = 1, perPage: int = 20):
    """Search anime on Anilist"""
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    cache_key = get_cache_key("anilist_search", {"q": q, "page": page, "perPage": perPage})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    query = """
    query ($search: String, $page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(search: $search, type: ANIME) {
                id
                idMal
                title {
                    romaji
                    english
                    native
                }
                coverImage {
                    extraLarge
                    large
                    medium
                }
                bannerImage
                averageScore
                meanScore
                genres
                episodes
                status
                format
                season
                seasonYear
                description
            }
        }
    }
    """
    
    variables = {"search": q, "page": page, "perPage": perPage}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_API_URL,
            json={"query": query, "variables": variables}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anilist/details/{anime_id}")
async def get_anilist_details(anime_id: int):
    """Get detailed information about a specific anime from Anilist"""
    cache_key = get_cache_key("anilist_details", {"id": anime_id})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    query = """
    query ($id: Int) {
        Media(id: $id, type: ANIME) {
            id
            idMal
            title {
                romaji
                english
                native
            }
            coverImage {
                extraLarge
                large
                medium
            }
            bannerImage
            averageScore
            meanScore
            genres
            episodes
            duration
            status
            format
            season
            seasonYear
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            description
            studios {
                nodes {
                    name
                }
            }
            characters(sort: ROLE, perPage: 10) {
                edges {
                    role
                    node {
                        id
                        name {
                            full
                        }
                        image {
                            large
                        }
                    }
                }
            }
            recommendations(perPage: 10) {
                edges {
                    node {
                        mediaRecommendation {
                            id
                            title {
                                romaji
                                english
                            }
                            coverImage {
                                large
                            }
                        }
                    }
                }
            }
            streamingEpisodes {
                title
                thumbnail
                url
            }
        }
    }
    """
    
    variables = {"id": anime_id}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_API_URL,
            json={"query": query, "variables": variables}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

@api_router.get("/anilist/genre")
async def get_anilist_by_genre(genre: str, page: int = 1, perPage: int = 20):
    """Get anime by genre from Anilist"""
    cache_key = get_cache_key("anilist_genre", {"genre": genre, "page": page, "perPage": perPage})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    query = """
    query ($genre: String, $page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(genre: $genre, type: ANIME, sort: POPULARITY_DESC) {
                id
                idMal
                title {
                    romaji
                    english
                    native
                }
                coverImage {
                    extraLarge
                    large
                    medium
                }
                bannerImage
                averageScore
                meanScore
                genres
                episodes
                status
                format
                season
                seasonYear
                description
            }
        }
    }
    """
    
    variables = {"genre": genre, "page": page, "perPage": perPage}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            ANILIST_API_URL,
            json={"query": query, "variables": variables}
        )
        data = response.json()
        set_cache(cache_key, data)
        return data

# Include the router in the main app
app.include_router(api_router)

# WebSocket endpoint for live users
@app.websocket("/ws/users/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "heartbeat":
                manager.update_activity(user_id)
                await manager.send_count()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.send_count()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(user_id)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task to broadcast user count and cleanup
async def broadcast_user_count():
    while True:
        await asyncio.sleep(5)  # Broadcast every 5 seconds
        manager.cleanup_inactive_users()
        await manager.send_count()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_user_count())

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
