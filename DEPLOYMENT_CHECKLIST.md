# ✅ Railway Deployment Checklist

Use this checklist to ensure a smooth deployment process!

---

## 📋 Pre-Deployment (Before Railway)

### Code Preparation
- [ ] All changes committed to git
- [ ] `.env` file added to `.gitignore`
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` exists in backend directory
- [ ] `railway.toml` exists in backend directory
- [ ] Code tested locally and working

### Environment Variables
- [ ] List all required environment variables:
  - [ ] `MONGO_URL`
  - [ ] `DB_NAME`
  - [ ] `CORS_ORIGINS`
  - [ ] `TMDB_API_KEY`
- [ ] Have values ready for all variables

### GitHub Setup
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Repository is accessible (public or Railway has access)

---

## 🚀 Railway Setup

### Project Creation
- [ ] Signed up/logged in to [railway.app](https://railway.app)
- [ ] Created new project
- [ ] Connected GitHub repository
- [ ] Railway detected Python app

### Database Setup
- [ ] MongoDB plugin added to project
- [ ] MongoDB is running (check status)
- [ ] `MONGO_URL` environment variable auto-created

### Environment Variables Configuration
- [ ] Navigated to Variables tab
- [ ] Added all environment variables:
  ```
  DB_NAME=movie_database
  CORS_ORIGINS=*
  TMDB_API_KEY=your_actual_key_here
  ```
- [ ] Verified `MONGO_URL` exists (auto-added by Railway)
- [ ] `PORT` variable present (auto-added by Railway)

### Deployment
- [ ] Initial deployment triggered
- [ ] Build logs reviewed (no errors)
- [ ] Deployment successful
- [ ] Service is running

---

## 🌐 Domain & Access

### Get Your URLs
- [ ] Backend URL obtained from Railway
  - Example: `https://your-app.up.railway.app`
- [ ] URL saved for frontend configuration
- [ ] (Optional) Custom domain configured

---

## 🧪 Testing

### API Endpoints Testing
- [ ] Health check endpoint:
  ```bash
  curl https://your-app.up.railway.app/api/health
  ```
- [ ] Test movie endpoints:
  ```bash
  curl https://your-app.up.railway.app/api/movies/popular
  ```
- [ ] Test TV show endpoints:
  ```bash
  curl https://your-app.up.railway.app/api/tv/popular
  ```
- [ ] Test anime endpoints:
  ```bash
  curl https://your-app.up.railway.app/api/anilist/popular
  ```

### Database Testing
- [ ] Create a favorite (POST request)
- [ ] Retrieve favorites (GET request)
- [ ] Delete a favorite (DELETE request)
- [ ] Check MongoDB for saved data

### WebSocket Testing
- [ ] Connect to WebSocket endpoint
- [ ] Send heartbeat message
- [ ] Receive user count updates
- [ ] Multiple users can connect

---

## 🔗 Frontend Integration

### Update Frontend Configuration
- [ ] Updated `.env` file in frontend:
  ```bash
  REACT_APP_BACKEND_URL=https://your-app.up.railway.app
  ```
- [ ] Updated CORS_ORIGINS in Railway backend:
  ```bash
  CORS_ORIGINS=https://your-frontend.vercel.app
  ```
- [ ] Frontend redeployed with new backend URL

### Test Frontend-Backend Connection
- [ ] Frontend can fetch movies
- [ ] Frontend can add to favorites
- [ ] Frontend can view favorites
- [ ] WebSocket connection working
- [ ] No CORS errors in browser console

---

## 🔐 Security

### Environment Variables
- [ ] No sensitive data in git repository
- [ ] `.env` file not committed
- [ ] API keys not hardcoded in source code

### CORS Configuration
- [ ] CORS_ORIGINS updated with actual frontend URL
- [ ] Not using `*` in production
- [ ] HTTPS enforced on all URLs

---

## 📊 Monitoring & Logs

### Railway Dashboard
- [ ] Deployment metrics reviewed
- [ ] CPU usage normal
- [ ] Memory usage normal
- [ ] No error logs

### Application Logs
- [ ] Logs accessible in Railway
- [ ] No critical errors
- [ ] API calls logging correctly
- [ ] Database connections stable

---

## 🔄 Continuous Deployment

### GitHub Integration
- [ ] Automatic deployments enabled
- [ ] Test push triggers deployment
- [ ] Deployment completes successfully
- [ ] Changes reflected in live app

---

## 📱 Final Verification

### End-to-End Testing
- [ ] User can browse movies
- [ ] User can browse TV shows
- [ ] User can browse anime
- [ ] User can add to favorites
- [ ] User can add to watchlist
- [ ] User can remove items
- [ ] Search functionality works
- [ ] Real-time user count updates

### Performance
- [ ] API response times acceptable (< 2s)
- [ ] Images loading properly
- [ ] No timeout errors
- [ ] Database queries fast

### Error Handling
- [ ] Invalid requests handled gracefully
- [ ] 404 errors return proper response
- [ ] Database errors caught and logged
- [ ] External API failures handled

---

## 🎉 Post-Deployment

### Documentation
- [ ] Backend URL documented
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Deployment process documented

### Team Communication
- [ ] Team notified of deployment
- [ ] Backend URL shared
- [ ] Known issues documented
- [ ] Support plan in place

### Monitoring Setup
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring (optional)
- [ ] Performance monitoring (optional)

---

## 🆘 Troubleshooting Reference

If something goes wrong, check:

1. **Railway Logs**: Most issues show up here first
2. **Environment Variables**: Verify all are set correctly
3. **MongoDB Status**: Ensure database is running
4. **CORS Settings**: Common cause of frontend errors
5. **API Keys**: Verify TMDB API key is valid

### Quick Commands
```bash
# Test backend health
curl https://your-app.up.railway.app/api/health

# View Railway logs
# (Use Railway dashboard → Deployments → Latest → View Logs)

# Check environment variables
# (Railway dashboard → Variables tab)

# Restart service
# (Railway dashboard → Service → Restart)
```

---

## ✨ Success Criteria

Your deployment is successful when:
- ✅ Backend responds to API requests
- ✅ Database connections work
- ✅ Frontend can communicate with backend
- ✅ WebSocket connections established
- ✅ No errors in logs
- ✅ All features working as expected

---

## 📞 Need Help?

- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Railway Docs: [docs.railway.app](https://docs.railway.app)
- FastAPI Docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Congratulations! Your backend is deployed! 🎊**

---

## 📅 Maintenance Checklist (Weekly/Monthly)

### Weekly
- [ ] Review error logs
- [ ] Check database size
- [ ] Monitor API usage
- [ ] Verify uptime

### Monthly
- [ ] Review Railway usage/costs
- [ ] Update dependencies
- [ ] Review and optimize slow endpoints
- [ ] Backup database (if needed)

---

Save this checklist and refer to it for future deployments!
