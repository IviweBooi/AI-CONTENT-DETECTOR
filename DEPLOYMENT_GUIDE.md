# Deployment Guide for AI Content Detector

## Problem
Your frontend is deployed on Netlify with a domain name, but the backend is only running locally on your laptop. Other devices can access the frontend but get "processing error" because they can't reach the localhost backend.

## Solutions

### Option 1: Quick Fix - Use Your Laptop as Backend Server (Temporary)

1. **Find your laptop's IP address:**
   - Windows: Open Command Prompt and run `ipconfig`
   - Look for "IPv4 Address" (usually starts with 192.168.x.x or 10.x.x.x)

2. **Update Netlify environment variable:**
   - Go to your Netlify dashboard
   - Navigate to Site settings > Environment variables
   - Add/update: `VITE_API_BASE_URL` = `http://YOUR_LAPTOP_IP:5000/api`
   - Example: `http://192.168.1.100:5000/api`

3. **Configure Windows Firewall:**
   - Open Windows Defender Firewall
   - Click "Allow an app or feature through Windows Defender Firewall"
   - Click "Change Settings" then "Allow another app"
   - Browse to your Python executable in the venv folder
   - Allow both Private and Public networks

4. **Ensure backend runs on all interfaces:**
   - Your `app.py` already has `host='0.0.0.0'` which is correct

5. **Redeploy frontend:**
   - Trigger a new build on Netlify to pick up the environment variable

### Option 2: Deploy Backend to Cloud (Recommended for Production)

#### Deploy to Railway/Render/Heroku:

1. **Create a `Procfile` in backend folder:**
   ```
   web: gunicorn app:app
   ```

2. **Update requirements.txt to include gunicorn:**
   ```
   gunicorn==20.1.0
   ```

3. **Deploy to your chosen platform**

4. **Update Netlify environment variable:**
   - Set `VITE_API_BASE_URL` to your deployed backend URL
   - Example: `https://your-app.railway.app/api`

### Option 3: Use ngrok for Testing (Quick temporary solution)

1. **Install ngrok:** Download from https://ngrok.com/

2. **Expose your local backend:**
   ```bash
   ngrok http 5000
   ```

3. **Update Netlify environment variable:**
   - Use the ngrok URL: `https://abc123.ngrok.io/api`

## Current Configuration

- Frontend: Deployed on Netlify with domain
- Backend: Running locally on laptop (localhost:5000)
- Issue: Other devices can't access localhost backend

## Files Modified

- `frontend/src/services/api.js`: Now uses environment variable for API URL
- `frontend/netlify.toml`: Added environment variable configuration
- `frontend/.env.example`: Example environment configuration

## Next Steps

1. Choose one of the solutions above
2. Update the `VITE_API_BASE_URL` in Netlify dashboard
3. Redeploy your frontend
4. Test from different devices

## Testing

After implementing any solution:
1. Access your Netlify domain from another device
2. Try uploading a file
3. Check if the "processing error" is resolved