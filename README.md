# YouTube Video Downloader (with ffmpeg auto-setup)

A simple Python application to download YouTube videos easily using `yt-dlp` and `ffmpeg`, with **automatic setup** — no manual downloading needed!

✨ Features:
- Automatically downloads and sets up `ffmpeg` on Windows and Linux
- Bundled `7-Zip` binary to extract `.7z` files (no installation needed)
- Uses `yt-dlp` for downloading videos
- Easy-to-use standalone executable built with PyInstaller
- Smooth yes/no prompts
- Beginner-friendly project structure

---

## 🚀 How It Works

1. On first run, the app checks if `ffmpeg` is available.
2. If not, it:
   - On Windows: downloads from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and extracts with bundled `7za.exe`
   - On Linux: downloads static builds from [johnvansickle.com](https://johnvansickle.com/ffmpeg/)
   - Fixes the folder structure automatically
3. You simply paste the YouTube link and download!

---

## 📦 Building from Source

Requirements:
- Python 3.8+
- [PyInstaller](https://pyinstaller.org/en/stable/)
- [wget](https://pypi.org/project/wget/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

Install dependencies:

```bash
pip install pyinstaller wget yt-dlp
pyinstaller --onefile --add-data "7zip;7zip" __init__.py
```

> For Linux builds, the bundled `7zip` files are not required for runtime setup.
