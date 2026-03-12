# MusicMaster - YouTube Music Downloader

A sleek Flask web app for downloading music from YouTube with real-time progress tracking.

## 🚀 Deploy to Render.com

### Method 1: Automatic Deploy (Recommended)

1. **Create a GitHub Repository**
   - Go to https://github.com/new
   - Create a new repository (e.g., "musicmaster-downloader")
   - Push all your files to this repo

2. **Sign up for Render**
   - Go to https://render.com
   - Sign up with your GitHub account (it's free!)

3. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect it's a Python app

4. **Configure the Service**
   - **Name**: `musicmaster` (or whatever you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Select "Free" tier

5. **Add Persistent Disk (Important!)**
   - Scroll down to "Disks"
   - Click "Add Disk"
   - **Name**: `downloads`
   - **Mount Path**: `/downloads`
   - **Size**: 10 GB (or more if needed)

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://your-app-name.onrender.com`

### Method 2: Using render.yaml (Even Easier!)

1. Push all files including `render.yaml` to GitHub
2. In Render dashboard, click "New +" → "Blueprint"
3. Select your repo
4. Render will auto-configure everything from `render.yaml`
5. Click "Apply" and wait for deployment

## 📁 Required Files

Make sure you have these files in your repository:

```
your-repo/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── build.sh               # Build script (installs ffmpeg)
├── render.yaml            # Render configuration (optional)
├── templates/
│   └── index.html         # Frontend template
└── static/
    └── style.css          # Styling
```

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure ffmpeg is installed
# Windows: Download from https://ffmpeg.org
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Run the app
python app.py

# Visit http://localhost:5000
```

## ⚙️ Environment Variables (Optional)

You can set these in Render dashboard under "Environment":

- `PORT` - Auto-set by Render (default: 10000)
- `PYTHON_VERSION` - Set to `3.11.0` or higher

## 📝 Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity** (takes ~30 seconds to wake up)
- **750 hours/month free** (enough for personal use)
- **Disk storage is persistent** (your downloads stay between deploys)

### Upgrading ffmpeg Build Command:
If you need specific ffmpeg features, modify `build.sh`:
```bash
#!/bin/bash
apt-get update && apt-get install -y ffmpeg
pip install -r requirements.txt
```

### Custom Domain (Paid Feature):
- Free tier gives you: `https://your-app.onrender.com`
- Custom domains require paid plan ($7/month)

## 🐛 Troubleshooting

**Problem**: App crashes on startup
- **Solution**: Check Render logs, ensure ffmpeg installed correctly

**Problem**: Downloads not persisting
- **Solution**: Make sure you added the persistent disk at `/downloads`

**Problem**: Slow performance
- **Solution**: Free tier has limited resources. Consider upgrading to Starter plan ($7/month)

**Problem**: "Service Unavailable" after inactivity
- **Solution**: Normal on free tier - wait 30 seconds for it to wake up

## 🔗 Alternatives to Render

- **Railway.app** - Similar to Render, $5/month credit free
- **Fly.io** - More technical, better free tier
- **PythonAnywhere** - Free tier available but limited
- **Heroku** - No longer has free tier

## 📧 Support

If you encounter issues, check Render's logs:
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for error messages

---

Made with 💚 and Python
