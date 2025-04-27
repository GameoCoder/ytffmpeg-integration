# YouTube Video Downloader (with ffmpeg auto-setup)

A simple Python application to download YouTube videos easily using `yt-dlp` and `ffmpeg`, with **automatic setup** — no manual downloading needed!

✨ Features:
- Automatically downloads and sets up `ffmpeg` (Windows only)
- Bundled `7-Zip` binary to extract `.7z` files (no installation needed)
- Uses `yt-dlp` for downloading videos
- Easy-to-use standalone executable built with PyInstaller
- Smooth yes/no prompts
- Beginner-friendly project structure

---

## 🚀 How It Works

1. On first run, the app checks if `ffmpeg` is available.
2. If not, it:
   - Downloads `ffmpeg` archive from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
   - Extracts it automatically using bundled `7za.exe`
   - Fixes the folder structure
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
