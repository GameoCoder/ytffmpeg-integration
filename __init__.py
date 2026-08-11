import platform
import sys
import subprocess, os, shutil
import tarfile
import stat
from urllib.parse import urlparse
import wget
import yt_dlp

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_extracted_folder_path(base_ffmpeg_dir):
    extracted_folders = [f for f in os.listdir(base_ffmpeg_dir) if os.path.isdir(os.path.join(base_ffmpeg_dir, f))]
    if not extracted_folders:
        raise Exception("No extracted folders found!")
    return os.path.join(base_ffmpeg_dir, extracted_folders[0])

def flatten_extracted_path(base_ffmpeg_dir, source_subdir=None):
    extracted_path = get_extracted_folder_path(base_ffmpeg_dir)
    source_path = extracted_path if source_subdir is None else os.path.join(extracted_path, source_subdir)
    if not os.path.exists(source_path):
        if source_subdir is None:
            raise Exception("Extracted ffmpeg directory does not exist!")
        raise Exception(f"No '{source_subdir}' folder inside extracted ffmpeg directory!")
    for filename in os.listdir(source_path):
        src = os.path.join(source_path, filename)
        dst = os.path.join(base_ffmpeg_dir, filename)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
    shutil.rmtree(extracted_path)
    print(f"Fixed FFmpeg structure! {extracted_path} removed.")

def fix_ffmpeg_extracted_path(base_ffmpeg_dir):
    # Step 1: Find the extracted folder
    extracted_path = get_extracted_folder_path(base_ffmpeg_dir)
    bin_path = os.path.join(extracted_path, "bin")
    if not os.path.exists(bin_path):
        raise Exception("No 'bin' folder inside extracted ffmpeg directory!")
    flatten_extracted_path(base_ffmpeg_dir, "bin")

def fix_linux_ffmpeg_extracted_path(base_ffmpeg_dir):
    flatten_extracted_path(base_ffmpeg_dir)
    for file_name in ("ffmpeg", "ffprobe"):
        file_path = os.path.join(base_ffmpeg_dir, file_name)
        if os.path.exists(file_path):
            os.chmod(
                file_path,
                os.stat(file_path).st_mode | stat.S_IXUSR
            )
        else:
            raise FileNotFoundError(f"Expected Linux FFmpeg binary is missing: {file_path}")

def extract_7z(archive_path, extract_to):
    seven_zip_path = resource_path(os.path.join("7zip", "7za.exe"))
    if not os.path.exists(seven_zip_path):
        raise FileNotFoundError("7z.exe not found!")
    # Create the destination folder if it doesn't exist
    os.makedirs(extract_to, exist_ok=True)
    # Run 7z.exe command to extract
    subprocess.run([
        seven_zip_path,
        'x', archive_path,
        f'-o{extract_to}',
        '-y'
    ], check=True)

def extract_tar_xz(archive_path, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    with tarfile.open(archive_path, "r:xz") as tar:
        extract_root = os.path.abspath(extract_to)
        safe_members = []
        for member in tar.getmembers():
            if os.path.isabs(member.name):
                raise RuntimeError(f"Absolute archive path is not allowed: {member.name}")
            normalized_member = os.path.normpath(member.name)
            member_path = os.path.abspath(os.path.join(extract_root, normalized_member))
            try:
                is_within_extract_root = os.path.commonpath([extract_root, member_path]) == extract_root
            except ValueError:
                is_within_extract_root = False
            if not is_within_extract_root:
                raise RuntimeError(f"Unsafe archive path detected: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"Symbolic links are not allowed in archive: {member.name}")
            safe_members.append(member)
        for member in safe_members:
            tar.extract(member, path=extract_to)

def get_ffmpeg_required_files():
    if platform.system() == "Windows":
        return ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]
    return ["ffmpeg", "ffprobe"]

def ensure_ffmpeg_ready():
    required_files = [os.path.join("ffmpeg", file_name) for file_name in get_ffmpeg_required_files()]
    all_exist = all(os.path.exists(file) for file in required_files)
    if all_exist:
        print("FFmpeg is ready to use!          ✅")
        return
    print("FFmpeg not found or incomplete. Setting up FFmpeg...")
    system_name = platform.system()
    if system_name == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
        file_name = "ffmpeg-git-essentials.7z"
        try:
            print(f"Downloading {url}")
            wget.download(url, file_name)
            print(f"\nDownloaded {url} to {file_name}")
        except Exception as e:
            print(f"Error occurred {e}")
            return
        extract_7z(file_name, "ffmpeg/")
        fix_ffmpeg_extracted_path("./ffmpeg/")
        os.remove(file_name)
    elif system_name == "Linux":
        architecture = platform.machine().lower()
        if architecture in ("x86_64", "amd64"):
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        elif architecture in ("aarch64", "arm64"):
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
        else:
            raise RuntimeError(
                f"Unsupported Linux architecture: {architecture}. "
                "Supported values include x86_64/amd64 and aarch64/arm64. "
                "Please install FFmpeg manually using your system package manager."
            )
        file_name = os.path.basename(urlparse(url).path)
        if not file_name:
            raise RuntimeError(f"Could not determine FFmpeg archive filename from URL: {url}")
        try:
            print(f"Downloading {url}")
            wget.download(url, file_name)
            print(f"\nDownloaded {url} to {file_name}")
        except Exception as e:
            print(f"Error occurred {e}")
            return
        extract_tar_xz(file_name, "ffmpeg/")
        fix_linux_ffmpeg_extracted_path("./ffmpeg/")
        os.remove(file_name)
    else:
        raise RuntimeError(
            f"Unsupported platform for bundled FFmpeg setup: {system_name}. "
            "Supported platforms: Windows and Linux. "
            "Please install FFmpeg manually for your platform."
        )
    print("FFmpeg setup completed!          🎉")

def download_youtube_video(url):
    try:
        ydl_opts = {
            'ffmpeg_location': './ffmpeg',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            print(f"Title: {info_dict.get('title', 'Unknown Title')}")
            print(f"Download completed! File saved as {info_dict.get('title', 'Unknown Title')}.{info_dict.get('ext', 'mp4')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__=="__main__":
    print("Program is Alive                 ✅")
    ensure_ffmpeg_ready()
    print("Program Initialized Successfully ✅")
    print("Please Enter Video URL:")
    link = input("URL: ")
    print("Your link is: " + link)
    choice = input("\nIs this correct? Yes/No (Y/N) [Default: Yes]: ").strip().lower()
    if choice in ("y", ""):
        download_youtube_video(link)
    elif choice == "n":
        print("Okay, canceling...")
