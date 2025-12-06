# FastAPI Backend - Movie & TV Show Application

## 🎬 Overview

This is a FastAPI backend for a Movie and TV Show tracking application with the following features:
- **TMDB Integration**: Fetch movies and TV shows data
- **Anilist Integration**: Fetch anime data
- **User Management**: Favorites and Watchlists
- **Real-time Features**: WebSocket support for live user tracking
- **MongoDB Database**: Persistent data storage

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- MongoDB running locally or MongoDB Atlas account
- TMDB API Key

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file in the backend directory:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=movie_database
CORS_ORIGINS=*
TMDB_API_KEY=your_tmdb_api_key_here
```

3. **Run the server:**
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

4. **Access the API:**
- API Documentation: http://localhost:8001/docs
- Health Check: http://localhost:8001/api/health

---

## 📁 Project Structure

```
backend/
├── server.py           # Main FastAPI application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not committed)
├── Procfile           # Railway deployment config
├── railway.toml       # Railway-specific settings
└── README.md          # This file
```

---

## 🔌 API Endpoints

### Movies
- `GET /api/movies/popular` - Get popular movies
- `GET /api/movies/top_rated` - Get top rated movies
- `GET /api/movies/now_playing` - Get now playing movies
- `GET /api/movies/upcoming` - Get upcoming movies
- `GET /api/movies/{movie_id}` - Get movie details
- `GET /api/movies/{movie_id}/videos` - Get movie videos

### TV Shows
- `GET /api/tv/popular` - Get popular TV shows
- `GET /api/tv/top_rated` - Get top rated TV shows
- `GET /api/tv/on_the_air` - Get on the air TV shows
- `GET /api/tv/{tv_id}` - Get TV show details

### Anime (Anilist)
- `GET /api/anilist/popular` - Get popular anime
- `GET /api/anilist/trending` - Get trending anime
- `GET /api/anilist/top_rated` - Get top rated anime
- `GET /api/anilist/upcoming` - Get upcoming anime
- `GET /api/anilist/details/{anime_id}` - Get anime details

### User Features
- `POST /api/favorites` - Add to favorites
- `GET /api/favorites/{user_id}` - Get user favorites
- `DELETE /api/favorites/{favorite_id}` - Remove from favorites
- `POST /api/watchlist` - Add to watchlist
- `GET /api/watchlist/{user_id}` - Get user watchlist
- `DELETE /api/watchlist/{watchlist_id}` - Remove from watchlist

### TV Show User Features
- `POST /api/tv-favorites` - Add TV show to favorites
- `GET /api/tv-favorites/{user_id}` - Get TV show favorites
- `DELETE /api/tv-favorites/{favorite_id}` - Remove TV show from favorites
- `POST /api/tv-watchlist` - Add TV show to watchlist
- `GET /api/tv-watchlist/{user_id}` - Get TV show watchlist
- `DELETE /api/tv-watchlist/{watchlist_id}` - Remove TV show from watchlist

### Search
- `GET /api/search?query=term&type=movie` - Search movies/TV shows

### WebSocket
- `WS /ws/users/{user_id}` - WebSocket connection for live user tracking

---

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: MongoDB (Motor - async driver)
- **HTTP Client**: httpx (async)
- **External APIs**: TMDB, Anilist
- **WebSocket**: Native FastAPI WebSocket support
- **Validation**: Pydantic

---

## 🌐 Deployment to Railway

See [RAILWAY_DEPLOYMENT_GUIDE.md](/app/RAILWAY_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

**Quick Steps:**
1. Push code to GitHub
2. Create Railway project
3. Add MongoDB database
4. Configure environment variables
5. Deploy automatically

---

## 🔐 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `movie_database` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` or `https://yourfrontend.com` |
| `TMDB_API_KEY` | The Movie Database API key | `your_api_key` |
| `PORT` | Port to run on (Railway provides this) | `8001` |

---

## 📊 Database Collections

- **favorites**: User movie favorites
- **watchlist**: User movie watchlist
- **tv_favorites**: User TV show favorites
- **tv_watchlist**: User TV show watchlist

---

## 🧪 Testing

Test API endpoints using the interactive documentation:
```
http://localhost:8001/docs
```

Or use curl:
```bash
# Health check
curl http://localhost:8001/api/health

# Get popular movies
curl http://localhost:8001/api/movies/popular
```

---

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check `MONGO_URL` is correct
- Verify network access if using MongoDB Atlas

### CORS Errors
- Update `CORS_ORIGINS` with your frontend URL
- Use `*` for development (not recommended for production)

### Port Already in Use
- Change port: `uvicorn server:app --port 8002`
- Or kill the process using the port

---

## 📝 Notes

- All routes are prefixed with `/api` for consistency
- WebSocket connections are used for real-time user tracking
- Data is cached for 5 minutes to reduce API calls
- UUIDs are used for database IDs (not MongoDB ObjectIds)

---

## 🤝 Contributing

When adding new features:
1. Update the API documentation
2. Add appropriate error handling
3. Update this README
4. Test thoroughly before deploying

---

## 📄 License

This project is part of a full-stack application. See main repository for license details.
