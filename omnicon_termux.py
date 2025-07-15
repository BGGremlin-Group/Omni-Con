#!/data/data/com.termux/files/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omni-con.py – Universal media converter with steganography and watermarking
Adapted for Termux (non-root) by BGGremlin Group
Features: File conversion, image watermarking, steganography with encryption
"""

import sys, subprocess, shutil, os, re, tempfile, itertools, hashlib, base64, time
from pathlib import Path
from typing import List, Set, Dict
from datetime import datetime
import logging
from tqdm import tqdm
import colorama
from colorama import Fore, Style, init as colorama_init
from PIL import Image, ImageDraw, ImageFont
colorama_init(autoreset=True)

# Dynamic dependency installation with progress feedback
def _ensure(pkg: str, import_as: str | None = None):
    """Ensure a package is installed, installing it if necessary with progress feedback."""
    try:
        return __import__(import_as or pkg)
    except ModuleNotFoundError:
        say(f"Installing {pkg}...", C_PROC)
        logging.info(f"Starting installation of {pkg}")
        cmd = [sys.executable, "-m", "pip", "install", pkg]
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            with tqdm.tqdm(total=100, desc=f"Installing {pkg}", unit="%", leave=False) as pbar:
                start_time = time.time()
                while process.poll() is None:
                    pbar.update(5)
                    time.sleep(0.5)
                    if time.time() - start_time > 300:
                        process.terminate()
                        raise subprocess.TimeoutExpired(cmd, timeout=300)
                pbar.update(100 - pbar.n)
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            say(f"{pkg} installed successfully.", C_PROC)
            logging.info(f"{pkg} installed successfully")
            return __import__(import_as or pkg)
        except subprocess.TimeoutExpired:
            say(f"Installation of {pkg} timed out after 5 minutes.", C_ERR)
            logging.error(f"Installation of {pkg} timed out")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            say(f"Failed to install {pkg}: {e}. Try 'pip install {pkg}' manually.", C_ERR)
            logging.error(f"Failed to install {pkg}: {e}")
            sys.exit(1)

colorama = _ensure("colorama")
PIL = _ensure("pillow", "PIL")
tqdm = _ensure("tqdm")

# Logging setup
logging.basicConfig(
    filename="/sdcard/omni_converter.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Color constants
C_MAIN = Fore.CYAN + Style.BRIGHT
C_PROC = Fore.GREEN + Style.BRIGHT
C_ERR = Fore.RED + Style.BRIGHT
C_WARN = Fore.YELLOW + Style.BRIGHT
C_INFO = Fore.MAGENTA + Style.BRIGHT

#BGGG Banner
BANNER = rf"""{C_MAIN}
                            ░▒█▀▀▀█░█▀▄▀█░█▀▀▄░░▀░░░░░▒█▀▀▄░▄▀▀▄░█▀▀▄
                            ░▒█░░▒█░█░▀░█░█░▒█░░█▀░▀▀░▒█░░░░█░░█░█░▒█
                            ░▒█▄▄▄█░▀░░▒▀░▀░░▀░▀▀▀░░░░▒█▄▄▀░░▀▀░░▀░░▀ vT
                            ┏━━━━┓┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃━━━┓┃┏┓┃┏┓┃┃┃┃┃┃┃┃
                            ┃┏┓┏┓┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┏━━┛┃┃┃┃┛┗┓┃┃┃┃┃┃┃
                            ┗┛┃┃┗┛━━┓━┓┓┏┓┓┏┓┓┏┓┃┃┃┗━━┓━┛┃┓┓┏┛┓━━┓━┓┃
                            ┃┃┃┃┃┃┏┓┃┏┛┗┛┃┃┃┃╋╋┛┃┃┃┏━━┛┏┓┃┫┃┃┃┫┏┓┃┏┓┓
                            ┃┏┛┗┓┃┃━┫┃┃┃┃┃┗┛┃╋╋┓┃┃┃┗━━┓┗┛┃┃┃┗┓┃┗┛┃┃┃┃
                            ┃┗━━┛┃━━┛┛┃┻┻┛━━┛┛┗┛┃┃┃━━━┛━━┛┛┗━┛┛━━┛┛┗┛
                            ┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃
                           █▀▄ ██▀ █ █ ██▀ █   ▄▀▄ █▀▄ ██▀ █▀▄   ██▄ ▀▄▀
                           █▄▀ █▄▄ ▀▄▀ █▄▄ █▄▄ ▀▄▀ █▀  █▄▄ █▄▀   █▄█  █
░▀▀█▀▀░█░░░░█▀▀░░░▒█▀▀▄░▒█▀▀█░░░▒█▀▀█░▒█▀▀▄░▒█▀▀▀░▒█▀▄▀█░▒█░░░░▀█▀░▒█▄░▒█░░░▒█▀▀█░▒█▀▀▄░▒█▀▀▀█░▒█░▒█░▒█▀▀█░░
░░▒█░░░█▀▀█░█▀▀░░░▒█▀▀▄░▒█░▄▄░░░▒█░▄▄░▒█▄▄▀░▒█▀▀▀░▒█▒█▒█░▒█░░░░▒█░░▒█▒█▒█░░░▒█░▄▄░▒█▄▄▀░▒█░░▒█░▒█░▒█░▒█▄▄█░░
░░▒█░░░▀░░▀░▀▀▀░░░▒█▄▄█░▒█▄▄▀░░░▒█▄▄▀░▒█░▒█░▒█▄▄▄░▒█░░▒█░▒█▄▄█░▄█▄░▒█░░▀█░░░▒█▄▄▀░▒█░▒█░▒█▄▄▄█░░▀▄▄▀░▒█░░░░░


{Style.RESET_ALL}"""


# Utils
def ts() -> str:
    """Return current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def say(msg: str, col=C_INFO):
    """Print and log message."""
    print(f"{col}[{ts()}] {msg}{Style.RESET_ALL}")
    logging.info(msg)

def ensure_ffmpeg():
    """Ensure FFmpeg is installed."""
    if shutil.which("ffmpeg"):
        return
    say("Installing FFmpeg...", C_PROC)
    with tqdm.tqdm(total=100, desc="Installing FFmpeg", unit="%", leave=False) as pbar:
        process = subprocess.Popen(
            ["pkg", "install", "ffmpeg", "-y"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        start_time = time.time()
        while process.poll() is None:
            pbar.update(5)
            time.sleep(0.5)
            if time.time() - start_time > 300:
                process.terminate()
                raise subprocess.TimeoutExpired(["pkg", "install", "ffmpeg"], timeout=300)
        pbar.update(100 - pbar.n)
    if not shutil.which("ffmpeg"):
        say("FFmpeg installation failed. Please install manually with 'pkg install ffmpeg'.", C_ERR)
        sys.exit(1)
    say("FFmpeg installed successfully.", C_PROC)

def run(cmd: List[str], silent: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess command."""
    try:
        result = subprocess.run(
            cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if not silent:
            say(f"Command executed: {' '.join(cmd)}", C_PROC)
        return result
    except subprocess.CalledProcessError as e:
        say(f"Command failed: {e.stderr.strip() or 'Unknown error'}", C_ERR)
        raise
    except FileNotFoundError:
        say("FFmpeg not found. Run 'pkg install ffmpeg' and try again.", C_ERR)
        sys.exit(1)

def _xor(data: bytes, key: str) -> bytes:
    """XOR encrypt/decrypt data."""
    key_b = hashlib.sha256(key.encode()).digest()
    return bytes(b ^ k for b, k in zip(data, itertools.cycle(key_b)))

# Custom LSB steganography using PIL
def hide_msg(img_in: Path, img_out: Path, msg: str, pwd: str):
    """Hide encrypted message in image using LSB."""
    if not img_in.suffix.lstrip(".").lower() in IMAGE_EXTS:
        raise ValueError("Source must be an image (png, jpg, jpeg, bmp, webp).")
    if not msg:
        raise ValueError("Message cannot be empty.")
    if not pwd:
        raise ValueError("Password cannot be empty.")
    if img_out.suffix.lstrip(".").lower() not in IMAGE_EXTS:
        img_out = img_out.with_suffix(".png")
        say("Output changed to '.png' for compatibility.", C_WARN)
    
    # Encrypt message
    cipher = base64.b64encode(_xor(msg.encode(), pwd)).decode()
    bits = ''.join(format(ord(c), '08b') for c in cipher + '\0')  # Null terminator
    
    # Load image
    img = Image.open(img_in).convert("RGB")
    pixels = img.load()
    width, height = img.size
    max_bits = width * height * 3  # 3 bits per pixel (R, G, B)
    if len(bits) > max_bits:
        raise ValueError("Message too large for image capacity.")
    
    say("Embedding message...", C_PROC)
    with tqdm.tqdm(total=len(bits), desc="Embedding message", unit="bit") as pbar:
        bit_idx = 0
        for y in range(height):
            for x in range(width):
                if bit_idx >= len(bits):
                    break
                r, g, b = pixels[x, y]
                if bit_idx < len(bits):
                    r = (r & ~1) | int(bits[bit_idx])
                    bit_idx += 1
                    pbar.update(1)
                if bit_idx < len(bits):
                    g = (g & ~1) | int(bits[bit_idx])
                    bit_idx += 1
                    pbar.update(1)
                if bit_idx < len(bits):
                    b = (b & ~1) | int(bits[bit_idx])
                    bit_idx += 1
                    pbar.update(1)
                pixels[x, y] = (r, g, b)
    
    img.save(img_out, format="PNG")
    say(f"Stego image saved: {img_out}", C_MAIN)

def reveal_msg(img: Path, pwd: str) -> str:
    """Reveal hidden message from image using LSB."""
    if not img.suffix.lstrip(".").lower() in IMAGE_EXTS:
        raise ValueError("Input must be an image (png, jpg, jpeg, bmp, webp).")
    if not pwd:
        raise ValueError("Password cannot be empty.")
    
    img = Image.open(img).convert("RGB")
    pixels = img.load()
    width, height = img.size
    bits = []
    
    say("Extracting message...", C_PROC)
    with tqdm.tqdm(total=width * height * 3, desc="Extracting message", unit="bit") as pbar:
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                bits.extend([str(r & 1), str(g & 1), str(b & 1)])
                pbar.update(3)
                if len(bits) >= 8 and ''.join(bits[-8:]) == '00000000':  # Null terminator
                    bits = bits[:-8]
                    break
            else:
                continue
            break
    
    # Convert bits to string
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        chars.append(chr(int(''.join(byte), 2)))
    cipher = ''.join(chars)
    
    try:
        return _xor(base64.b64decode(cipher), pwd).decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

# FFmpeg formats
try:
    out = run(["ffmpeg", "-formats"], silent=True).stdout.splitlines()
    DEMUX, MUX = set(), set()
    pat = re.compile(r'^\s*([D ])([E ])\s+([a-z0-9_,]+)\s')
    for ln in out:
        mo = pat.match(ln)
        if not mo:
            continue
        if mo.group(1).strip() == 'D':
            DEMUX.update(mo.group(3).split(','))
        if mo.group(2).strip() == 'E':
            MUX.update(mo.group(3).split(','))
except:
    DEMUX = MUX = {
        "mp3", "wav", "flac", "aac", "ogg", "opus", "mp4", "mkv", "webm", "mov",
        "gif", "png", "jpg", "jpeg", "bmp", "webp", "avi", "wmv", "flv", "m4a",
        "alac", "m4v", "ogv", "3gp", "mpeg", "mpg", "vob", "m2ts", "ts", "asf", "wma"
    }

AUDIO_PRESETS: Dict[str, List[str]] = {
    'mp3': ['-vn', '-acodec', 'libmp3lame', '-b:a', '192k'],
    'mp3_low': ['-vn', '-acodec', 'libmp3lame', '-b:a', '128k'],
    'mp3_high': ['-vn', '-acodec', 'libmp3lame', '-b:a', '320k'],
    'aac': ['-vn', '-acodec', 'aac', '-b:a', '192k'],
    'aac_low': ['-vn', '-acodec', 'aac', '-b:a', '128k'],
    'aac_high': ['-vn', '-acodec', 'aac', '-b:a', '256k'],
    'wav': ['-vn', '-acodec', 'pcm_s16le'],
    'wav_24bit': ['-vn', '-acodec', 'pcm_s24le'],
    'flac': ['-vn', '-acodec', 'flac'],
    'flac_high': ['-vn', '-acodec', 'flac', '-compression_level', '8'],
    'ogg': ['-vn', '-acodec', 'libvorbis', '-q:a', '5'],
    'ogg_low': ['-vn', '-acodec', 'libvorbis', '-q:a', '3'],
    'ogg_high': ['-vn', '-acodec', 'libvorbis', '-q:a', '8'],
    'opus': ['-vn', '-acodec', 'libopus', '-b:a', '192k'],
    'opus_low': ['-vn', '-acodec', 'libopus', '-b:a', '96k'],
    'opus_high': ['-vn', '-acodec', 'libopus', '-b:a', '256k'],
    'm4a': ['-vn', '-acodec', 'aac', '-b:a', '192k'],
    'alac': ['-vn', '-acodec', 'alac'],
    'wma': ['-vn', '-acodec', 'wmav2', '-b:a', '192k'],
    'wma_low': ['-vn', '-acodec', 'wmav2', '-b:a', '128k'],
    'ac3': ['-vn', '-acodec', 'ac3', '-b:a', '192k'],
    'dts': ['-vn', '-acodec', 'dts', '-b:a', '768k'],
}

VIDEO_PRESETS: Dict[str, List[str]] = {
    'mp4': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'mp4_fast': ['-vcodec', 'libx264', '-crf', '28', '-preset', 'ultrafast', '-c:a', 'copy'],
    'mp4_high': ['-vcodec', 'libx264', '-crf', '18', '-preset', 'slow', '-c:a', 'copy'],
    'mp4_h265': ['-vcodec', 'libx265', '-crf', '25', '-preset', 'medium', '-c:a', 'copy'],
    'mkv': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'mkv_h265': ['-vcodec', 'libx265', '-crf', '25', '-preset', 'medium', '-c:a', 'copy'],
    'webm': ['-vcodec', 'libvpx-vp9', '-crf', '30', '-b:v', '0', '-c:a', 'copy'],
    'webm_low': ['-vcodec', 'libvpx-vp9', '-crf', '36', '-b:v', '0', '-c:a', 'copy'],
    'webm_high': ['-vcodec', 'libvpx-vp9', '-crf', '24', '-b:v', '0', '-c:a', 'copy'],
    'gif': ['-vf', 'fps=15,scale=480:-1:flags=lanczos', '-loop', '0'],
    'gif_low': ['-vf', 'fps=10,scale=320:-1:flags=lanczos', '-loop', '0'],
    'avi': ['-vcodec', 'mpeg4', '-q:v', '5', '-c:a', 'copy'],
    'avi_divx': ['-vcodec', 'libxvid', '-q:v', '5', '-c:a', 'copy'],
    'mov': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'mov_prores': ['-vcodec', 'prores', '-profile:v', '2', '-c:a', 'copy'],
    'flv': ['-vcodec', 'flv1', '-q:v', '5', '-c:a', 'copy'],
    'm4v': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'ogv': ['-vcodec', 'libtheora', '-q:v', '7', '-c:a', 'copy'],
    '3gp': ['-vcodec', 'h263', '-s', '176x144', '-c:a', 'copy'],
    'mpeg': ['-vcodec', 'mpeg2video', '-q:v', '5', '-c:a', 'copy'],
    'vob': ['-vcodec', 'mpeg2video', '-q:v', '5', '-c:a', 'copy'],
    'm2ts': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'ts': ['-vcodec', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy'],
    'asf': ['-vcodec', 'wmv2', '-q:v', '5', '-c:a', 'copy'],
}

IMAGE_EXTS = {"png", "jpg", "jpeg", "bmp", "webp"}

def build_cmd(src: Path, dst: Path) -> List[str]:
    """Build FFmpeg command."""
    ext = dst.suffix.lstrip(".").lower()
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if ext in AUDIO_PRESETS:
        cmd += AUDIO_PRESETS[ext]
    elif ext in VIDEO_PRESETS:
        cmd += VIDEO_PRESETS[ext]
    cmd.append(str(dst))
    return cmd

def convert(src: Path, outdir: Path, ext: str):
    """Convert a single file."""
    ext = ext.lstrip(".").lower()
    if ext not in MUX:
        raise ValueError(f"FFmpeg cannot write '.{ext}'")
    outdir.mkdir(parents=True, exist_ok=True)
    dst = outdir / f"{src.stem}.{ext}"
    say(f"Converting {src.name} → {dst.name}", C_PROC)
    with tqdm.tqdm(total=100, desc=f"Converting {src.name}", unit="%", leave=False) as pbar:
        process = subprocess.Popen(
            build_cmd(src, dst), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        start_time = time.time()
        while process.poll() is None:
            pbar.update(5)
            time.sleep(0.5)
            if time.time() - start_time > 600:
                process.terminate()
                raise subprocess.TimeoutExpired(build_cmd(src, dst), timeout=600)
        pbar.update(100 - pbar.n)
    say(f"Saved: {dst}", C_MAIN)

# Watermarking
def _sys_font():
    """Return Termux-compatible font."""
    font_path = "/system/fonts/DroidSans.ttf"
    if os.path.exists(font_path):
        return font_path
    say("Default font not found. Using Pillow default.", C_WARN)
    return None

def wm_image_pillow(src: Path, dst: Path, text: str, alpha: int = 30):
    """Watermark image using Pillow."""
    if not src.suffix.lstrip(".").lower() in IMAGE_EXTS:
        raise ValueError("Source must be an image (png, jpg, jpeg, bmp, webp).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip(".").lower() in IMAGE_EXTS:
        dst = dst.with_suffix(".png")
        say("Output changed to '.png'.", C_WARN)
    im = Image.open(src).convert("RGBA")
    layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(_sys_font()) if _sys_font() else ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    with tqdm.tqdm(total=100, desc=f"Watermarking {src.name}", unit="%", leave=False) as pbar:
        for y in range(0, im.size[1], h + 200):
            for x in range(-im.size[0], im.size[0] * 2, w + 200):
                draw.text((x + y // 2, y), text, font=font, fill=(255, 255, 255, alpha))
            pbar.update(100 // (im.size[1] // (h + 200) + 1))
        Image.alpha_composite(im, layer).save(dst)
        pbar.update(100 - pbar.n)
    say(f"Watermarked image saved: {dst}", C_MAIN)

def wm_video_ffmpeg(src: Path, dst: Path, text: str):
    """Watermark video using FFmpeg."""
    if not src.suffix.lstrip(".").lower() in {"mp4", "webm", "mov", "mkv", "avi", "flv", "m4v", "mpeg", "vob", "m2ts", "ts", "asf"}:
        raise ValueError("Source must be a video (mp4, webm, mov, mkv, avi, flv, m4v, mpeg, vob, m2ts, ts, asf).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip(".").lower() in {"mp4", "webm", "mov", "mkv", "avi", "flv", "m4v", "mpeg", "vob", "m2ts", "ts", "asf"}:
        dst = dst.with_suffix(".mp4")
        say("Output changed to '.mp4'.", C_WARN)
    fontfile = _sys_font() or "/system/fonts/DroidSans.ttf"
    txt_filter = (
        f"drawtext=fontfile='{fontfile}':"
        f"text='{text}':x=10:y=h-30:"
        "fontcolor=white@0.03:fontsize=24"
    )
    cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", txt_filter,
           "-c:v", "libx264", "-crf", "23", "-preset", "medium",
           "-c:a", "copy", str(dst)]
    with tqdm.tqdm(total=100, desc=f"Watermarking {src.name}", unit="%", leave=False) as pbar:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        start_time = time.time()
        while process.poll() is None:
            pbar.update(5)
            time.sleep(0.5)
            if time.time() - start_time > 600:
                process.terminate()
                raise subprocess.TimeoutExpired(cmd, timeout=600)
        pbar.update(100 - pbar.n)
    say(f"Watermarked video saved: {dst}", C_MAIN)

# Batch watermarking
def batch_watermark():
    """Batch watermark images or videos."""
    try:
        folder = _p("Folder with files:", is_dir=True)
        text = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
        if not text:
            raise ValueError("Watermark text cannot be empty.")
        outdir = _p("Output directory (blank = same):", must=False, is_dir=True)
        if not str(outdir):
            outdir = folder
        eng = input(f"{C_INFO}Engine 1=Pillow (images) 2=FFmpeg (videos):{Style.RESET_ALL} ").strip()
        
        valid_exts = IMAGE_EXTS if eng == "1" else {"mp4", "webm", "mov", "mkv", "avi", "flv", "m4v", "mpeg", "vob", "m2ts", "ts", "asf"}
        files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lstrip(".").lower() in valid_exts]
        if not files:
            raise ValueError(f"No valid files found with extensions: {', '.join(valid_exts)}")
        
        for f in tqdm.tqdm(files, desc="Watermarking files", unit="file"):
            try:
                dst = outdir / f.name
                if eng == "1" and f.suffix.lstrip(".").lower() in IMAGE_EXTS:
                    wm_image_pillow(f, dst, text)
                elif eng == "2" and f.suffix.lstrip(".").lower() in valid_exts:
                    wm_video_ffmpeg(f, dst, text)
                else:
                    say(f"Skipping {f.name}: Invalid engine or file type", C_WARN)
            except Exception as e:
                say(f"Error processing {f.name}: {e}", C_ERR)
    except Exception as e:
        say(f"Batch watermarking failed: {e}", C_ERR)

# CLI helpers
def _p(prompt: str, must: bool = True, is_dir: bool = False) -> Path:
    """Prompt for path with Termux storage check."""
    if not os.path.exists("/sdcard"):
        say("Storage not accessible. Run 'termux-setup-storage' first.", C_ERR)
        sys.exit(1)
    while True:
        p = Path(input(f"{C_INFO}{prompt}{Style.RESET_ALL} ").strip('" '))
        try:
            if must and not p.exists():
                raise FileNotFoundError(f"Path does not exist: {p}")
            if is_dir and not p.is_dir():
                raise NotADirectoryError(f"Not a directory: {p}")
            return p
        except Exception as e:
            say(str(e), C_ERR)

# Conversion flows
def single_convert():
    """Convert a single file."""
    try:
        src = _p("Source file:")
        ext = input(f"{C_INFO}Target extension (e.g., mp3, mp4, png):{Style.RESET_ALL} ").lstrip(".").lower()
        out = _p("Output directory (blank = same):", must=False)
        if not str(out):
            out = src.parent
        convert(src, out, ext)
    except Exception as e:
        say(str(e), C_ERR)

def batch_convert():
    """Batch convert files."""
    try:
        folder = _p("Folder with files:", is_dir=True)
        ext = input(f"{C_INFO}Convert to extension (e.g., mp3, mp4, png):{Style.RESET_ALL} ").lstrip(".").lower()
        files = [f for f in folder.iterdir() if f.is_file()]
        if not files:
            raise ValueError("No files found in folder.")
        for f in tqdm.tqdm(files, desc="Converting files", unit="file"):
            try:
                convert(f, folder, ext)
            except Exception as e:
                say(f"{f.name}: {e}", C_ERR)
    except Exception as e:
        say(f"Batch conversion failed: {e}", C_ERR)

# Stego/Watermark menu
def stego_menu():
    """Steganography and watermarking menu."""
    sub = f"""{C_MAIN}
1) Embed encrypted message in image
2) Extract hidden message from image
3) Watermark image (Pillow)
4) Watermark video (FFmpeg)
5) Batch watermark (images or videos)
6) Back
{Style.RESET_ALL}"""
    while True:
        print(sub)
        choice = input(f"{C_INFO}Select 1-6:{Style.RESET_ALL} ").strip()
        try:
            if choice == "1":
                src = _p("Source image:")
                dest = _p("Output image:", must=False)
                msg = input(f"{C_INFO}Message to hide:{Style.RESET_ALL} ").strip()
                pwd = input(f"{C_INFO}Password:{Style.RESET_ALL} ").strip()
                hide_msg(src, dest, msg, pwd)
            elif choice == "2":
                src = _p("Stego image:")
                pwd = input(f"{C_INFO}Password used at embed:{Style.RESET_ALL} ").strip()
                say("Revealed message →", C_MAIN)
                print(reveal_msg(src, pwd))
            elif choice == "3":
                src = _p("Source image:")
                dest = _p("Output image:", must=False)
                txt = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
                wm_image_pillow(src, dest, txt)
            elif choice == "4":
                src = _p("Source video:")
                dest = _p("Output video:", must=False)
                txt = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
                wm_video_ffmpeg(src, dest, txt)
            elif choice == "5":
                batch_watermark()
            elif choice == "6":
                break
            else:
                say("Invalid choice.", C_WARN)
        except Exception as e:
            say(str(e), C_ERR)

# Main menu
def main():
    """Main entry point."""
    print(BANNER)
    ensure_ffmpeg()

    menu = f"""{C_MAIN}
1) Single file convert
2) Batch convert
3) Steganography / Watermark
4) Exit
{Style.RESET_ALL}"""
    actions = {
        "1": single_convert,
        "2": batch_convert,
        "3": stego_menu,
    }

    while True:
        print(menu)
        choice = input(f"{C_INFO}Select option 1-4:{Style.RESET_ALL} ").strip()
        if choice == "4":
            say("Exiting...", C_MAIN)
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            say("Invalid choice.", C_WARN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + C_WARN + "Interrupted by user." + Style.RESET_ALL)
        logging.info("Program interrupted by user.")
        sys.exit(0)
    except Exception as e:
        say(f"Unexpected error: {e}", C_ERR)
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
