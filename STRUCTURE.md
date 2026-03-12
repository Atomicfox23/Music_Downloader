# Quick Start - Folder Structure

Create this exact structure for your project:

```
musicmaster-downloader/          # Your project root
│
├── app.py                       # Main Flask app
├── requirements.txt             # Python packages
├── build.sh                     # Build script for Render
├── render.yaml                  # Render config (optional)
├── README.md                    # Documentation
├── .gitignore                   # Git ignore rules
│
├── templates/                   # HTML templates folder
│   └── index.html              # Main page
│
└── static/                      # Static files folder
    └── style.css               # Stylesheet
```

## Commands to Set Up:

```bash
# 1. Create project folder
mkdir musicmaster-downloader
cd musicmaster-downloader

# 2. Create subdirectories
mkdir templates
mkdir static

# 3. Place files:
#    - app.py in root
#    - index.html in templates/
#    - style.css in static/
#    - All other files in root

# 4. Make build script executable
chmod +x build.sh

# 5. Initialize git
git init
git add .
git commit -m "Initial commit"

# 6. Push to GitHub
# (Create repo on GitHub first, then:)
git remote add origin https://github.com/YOUR_USERNAME/musicmaster-downloader.git
git branch -M main
git push -u origin main
```

That's it! Now you can deploy to Render.
