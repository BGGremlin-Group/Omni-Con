#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omni_converter.py – Universal media converter with steganography and watermarking
Developed by the BGGremlin Group
Features: File conversion, image/video watermarking, steganography with encryption
"""

import sys, subprocess, shutil, os, re, tempfile, itertools, hashlib, base64, time
from pathlib import Path
from typing import List, Tuple, Set, Dict
from datetime import datetime
import platform
import logging
from tqdm import tqdm  # Progress bars

# ───────── Dynamic deps (auto-install once) ────────────────────────────────
def _ensure(pkg: str, import_as: str | None = None):
    """Ensure a package is installed, installing it if necessary."""
    try:
        return __import__(import_as or pkg)
    except ModuleNotFoundError:
        say(f"Installing {pkg}...", C_PROC)
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return __import__(import_as or pkg)

colorama = _ensure("colorama")
stegano  = _ensure("stegano")                         # Steganography
PIL      = _ensure("pillow", "PIL")                   # Pillow image utils
cv2      = _ensure("opencv-python-headless", "cv2")   # OpenCV (headless)
tqdm     = _ensure("tqdm")                           # Progress bars

# ───────── Stegano import shim (new ≥0.11 vs legacy) ───────────────────────
try:                                  # Stegano ≥ 0.11 / 2.x
    from stegano import lsb           as _lsb
    from stegano.lsb import generators
except ModuleNotFoundError:           # Stegano ≤ 0.10
    from stegano import lsbset        as _lsb
    from stegano.lsbset import generators

from colorama import Fore, Style, init as colorama_init
from PIL import Image, ImageDraw, ImageFont
colorama_init(autoreset=True)

# ───────── Logging setup ───────────────────────────────────────────────────
logging.basicConfig(
    filename="omni_converter.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ───────── Colour constants & banner ───────────────────────────────────────
C_MAIN  = Fore.CYAN    + Style.BRIGHT
C_PROC  = Fore.GREEN   + Style.BRIGHT
C_ERR   = Fore.RED     + Style.BRIGHT
C_WARN  = Fore.YELLOW  + Style.BRIGHT
C_INFO  = Fore.MAGENTA + Style.BRIGHT

BANNER = rf"""{C_MAIN}
                            ░▒█▀▀▀█░█▀▄▀█░█▀▀▄░░▀░░░░░▒█▀▀▄░▄▀▀▄░█▀▀▄
                            ░▒█░░▒█░█░▀░█░█░▒█░░█▀░▀▀░▒█░░░░█░░█░█░▒█
                            ░▒█▄▄▄█░▀░░▒▀░▀░░▀░▀▀▀░░░░▒█▄▄▀░░▀▀░░▀░░▀ V3
                            █▀▄ ██▀ █ █ ██▀ █   ▄▀▄ █▀▄ ██▀ █▀▄   ██▄ ▀▄▀    
                            █▄▀ █▄▄ ▀▄▀ █▄▄ █▄▄ ▀▄▀ █▀  █▄▄ █▄▀   █▄█  █     
░▀▀█▀▀░█░░░░█▀▀░░░▒█▀▀▄░▒█▀▀█░░░▒█▀▀█░▒█▀▀▄░▒█▀▀▀░▒█▀▄▀█░▒█░░░░▀█▀░▒█▄░▒█░░░▒█▀▀█░▒█▀▀▄░▒█▀▀▀█░▒█░▒█░▒█▀▀█░░
░░▒█░░░█▀▀█░█▀▀░░░▒█▀▀▄░▒█░▄▄░░░▒█░▄▄░▒█▄▄▀░▒█▀▀▀░▒█▒█▒█░▒█░░░░▒█░░▒█▒█▒█░░░▒█░▄▄░▒█▄▄▀░▒█░░▒█░▒█░▒█░▒█▄▄█░░
░░▒█░░░▀░░▀░▀▀▀░░░▒█▄▄█░▒█▄▄▀░░░▒█▄▄▀░▒█░▒█░▒█▄▄▄░▒█░░▒█░▒█▄▄█░▄█▄░▒█░░▀█░░░▒█▄▄▀░▒█░▒█░▒█▄▄▄█░░▀▄▄▀░▒█░░░░░
{Style.RESET_ALL}"""

# ───────── Utils: logging, FFmpeg runner, XOR crypto ───────────────────────
def ts() -> str:
    """Return current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def say(msg: str, col=C_INFO):
    """Print message with color and log it."""
    print(f"{col}[{ts()}] {msg}{Style.RESET_ALL}")
    logging.info(msg)

def ensure_ffmpeg():
    """Ensure FFmpeg is installed."""
    if shutil.which("ffmpeg"):
        return
    say("FFmpeg not found in PATH – please install it first.", C_ERR)
    sys.exit(1)

def run(cmd: List[str], silent: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess command with error handling."""
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
        say("FFmpeg executable not found.", C_ERR)
        sys.exit(1)

def _xor(data: bytes, key: str) -> bytes:
    """XOR encrypt/decrypt data with a key."""
    key_b = hashlib.sha256(key.encode()).digest()
    return bytes(b ^ k for b, k in zip(data, itertools.cycle(key_b)))

# ───────── FFmpeg capability discovery & presets ───────────────────────────
def ffmpeg_formats() -> Tuple[Set[str], Set[str]]:
    """Discover FFmpeg supported formats."""
    try:
        out = run(["ffmpeg", "-formats"], silent=True).stdout.splitlines()
        d, m = set(), set()
        pat = re.compile(r'^\s*([D ])([E ])\s+([a-z0-9_,]+)\s')
        for ln in out:
            mo = pat.match(ln)
            if not mo:
                continue
            if mo.group(1).strip() == 'D':
                d.update(mo.group(3).split(','))
            if mo.group(2).strip() == 'E':
                m.update(mo.group(3).split(','))
        return d, m
    except Exception as e:
        say(f"Error discovering FFmpeg formats: {e}", C_ERR)
        return set(), set()

try:
    DEMUX, MUX = ffmpeg_formats()
except Exception:
    DEMUX = MUX = {
        "mp3", "wav", "flac", "aac", "ogg", "opus", "mp4", "mkv", "webm", "mov",
        "gif", "png", "jpg", "bmp", "webp", "avi", "wmv", "flv", "m4a", "alac",
        "m4v", "ogv", "3gp", "mpeg", "mpg", "vob", "m2ts", "ts", "asf", "wma"
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

IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

def build_cmd(src: Path, dst: Path) -> List[str]:
    """Build FFmpeg command for conversion."""
    ext = dst.suffix.lstrip('.').lower()
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if ext in AUDIO_PRESETS:
        cmd += AUDIO_PRESETS[ext]
    elif ext in VIDEO_PRESETS:
        cmd += VIDEO_PRESETS[ext]
    cmd.append(str(dst))
    return cmd

def convert(src: Path, outdir: Path, ext: str):
    """Convert a single file to the specified extension."""
    ext = ext.lstrip('.').lower()
    if ext not in MUX:
        raise ValueError(f"FFmpeg cannot write '.{ext}'")
    outdir.mkdir(parents=True, exist_ok=True)
    dst = outdir / f"{src.stem}.{ext}"
    say(f"Converting {src.name} → {dst.name}", C_PROC)
    run(build_cmd(src, dst))
    say(f"Saved: {dst}", C_MAIN)

# ───────── Steganography helpers ───────────────────────────────────────────
def hide_msg(img_in: Path, img_out: Path, msg: str, pwd: str):
    """Hide an encrypted message in an image using steganography."""
    if not img_in.suffix.lstrip('.').lower() in IMAGE_EXTS:
        raise ValueError("Source must be an image (png, jpg, jpeg, bmp, webp).")
    if not msg:
        raise ValueError("Message to hide cannot be empty.")
    if not pwd:
        raise ValueError("Password cannot be empty.")
    if img_out.suffix.lstrip('.').lower() not in IMAGE_EXTS:
        img_out = img_out.with_suffix('.png')
        say(f"Output extension changed to '.png' for compatibility.", C_WARN)
    say("Encrypting & embedding message...", C_PROC)
    cipher = base64.b64encode(_xor(msg.encode(), pwd)).decode()
    secret = _lsb.hide(str(img_in), cipher, generators.eratosthenes())

    suf = img_out.suffix.lower()
    if suf == ".webp":
        secret.save(str(img_out), lossless=True, quality=100)
    elif suf not in {".png", ".bmp"}:
        img_out = img_out.with_suffix(".png")
        secret.save(str(img_out))
    else:
        secret.save(str(img_out))
    say(f"Stego image saved: {img_out}", C_MAIN)

def reveal_msg(img: Path, pwd: str) -> str:
    """Reveal a hidden message from an image."""
    if not img.suffix.lstrip('.').lower() in IMAGE_EXTS:
        raise ValueError("Input must be an image (png, jpg, jpeg, bmp, webp).")
    if not pwd:
        raise ValueError("Password cannot be empty.")
    try:
        cipher = _lsb.reveal(str(img), generators.eratosthenes())
        if cipher is None:
            raise ValueError("No hidden data found in image!")
        return _xor(base64.b64decode(cipher), pwd).decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

# ───────── Pillow watermark (image) ────────────────────────────────────────
def wm_image_pillow(src: Path, dst: Path, text: str, alpha: int = 30):
    """Watermark an image using Pillow."""
    if not src.suffix.lstrip('.').lower() in IMAGE_EXTS:
        raise ValueError("Source must be an image (png, jpg, jpeg, bmp, webp).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip('.').lower() in IMAGE_EXTS:
        dst = dst.with_suffix('.png')
        say(f"Output extension changed to '.png' for compatibility.", C_WARN)
    im = Image.open(src).convert("RGBA")
    layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    try:
        font = ImageFont.truetype(_sys_font(), size=24)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    for y in range(0, im.size[1], h + 200):
        for x in range(-im.size[0], im.size[0] * 2, w + 200):
            draw.text((x + y // 2, y), text, font=font, fill=(255, 255, 255, alpha))
    
    Image.alpha_composite(im, layer).save(dst)
    say(f"Watermarked (Pillow) image saved: {dst}", C_MAIN)

# ───────── FFmpeg watermark (video, CPU-light) ─────────────────────────────
def _sys_font():
    """Return system font path based on OS."""
    if platform.system() == "Windows":
        return r"C:\Windows\Fonts\consola.ttf"
    elif platform.system() == "Darwin":
        return "/System/Library/Fonts/Supplemental/Arial.ttf"
    else:
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def wm_video_ffmpeg(src: Path, dst: Path, text: str):
    """Watermark a video using FFmpeg."""
    if not src.suffix.lstrip('.').lower() in {'mp4', 'mkv', 'webm', 'mov', 'avi', 'flv', 'm4v', 'mpeg', 'vob', 'm2ts', 'ts', 'asf'}:
        raise ValueError("Source must be a video (mp4, mkv, webm, mov, avi, flv, m4v, mpeg, vob, m2ts, ts, asf).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip('.').lower() in {'mp4', 'mkv', 'webm', 'mov', 'avi', 'flv', 'm4v', 'mpeg', 'vob', 'm2ts', 'ts', 'asf'}:
        dst = dst.with_suffix('.mp4')
        say(f"Output extension changed to '.mp4' for compatibility.", C_WARN)
    fontfile = _sys_font()
    if not os.path.exists(fontfile):
        raise FileNotFoundError(f"Font file not found: {fontfile}")
    txt_filter = (
        f"drawtext=fontfile='{fontfile}':"
        f"text='{text}':x=10:y=h-30:"
        "fontcolor=white@0.03:fontsize=24"
    )
    run(["ffmpeg", "-y", "-i", str(src), "-vf", txt_filter,
         "-c:v", "libx264", "-crf", '23', "-preset", "medium",
         "-c:a", "copy", str(dst)])
    say(f"Watermarked (FFmpeg) video saved: {dst}", C_MAIN)

# ───────── OpenCV watermark engines ────────────────────────────────────────
def _overlay(frame, text: str, alpha: float = 0.03):
    """Apply watermark text to a single frame."""
    overlay = frame.copy()
    h, w = frame.shape[:2]
    for y in range(0, h, 200):
        for x in range(-w, w * 2, 400):
            cv2.putText(
                overlay, text, (x + y // 2, y),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
            )
    return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

def wm_image_cv(src: Path, dst: Path, text: str, alpha: float = 0.03):
    """Watermark an image using OpenCV."""
    if not src.suffix.lstrip('.').lower() in IMAGE_EXTS:
        raise ValueError("Source must be an image (png, jpg, jpeg, bmp, webp).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip('.').lower() in IMAGE_EXTS:
        dst = dst.with_suffix('.png')
        say(f"Output extension changed to '.png' for compatibility.", C_WARN)
    frame = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
    if frame is None:
        raise ValueError("Cannot read image.")
    cv2.imwrite(str(dst), _overlay(frame, text, alpha))
    say(f"Watermarked (OpenCV) image saved: {dst}", C_MAIN)

def wm_video_cv(src: Path, dst: Path, text: str, alpha: float = 0.03):
    """Watermark a video using OpenCV."""
    if not src.suffix.lstrip('.').lower() in {'mp4', 'mkv', 'webm', 'mov', 'avi', 'flv', 'm4v', 'mpeg', 'vob', 'm2ts', 'ts', 'asf'}:
        raise ValueError("Source must be a video (mp4, mkv, webm, mov, avi, flv, m4v, mpeg, vob, m2ts, ts, asf).")
    if not text:
        raise ValueError("Watermark text cannot be empty.")
    if not dst.suffix.lstrip('.').lower() in {'mp4', 'mkv', 'webm', 'mov', 'avi', 'flv', 'm4v', 'mpeg', 'vob', 'm2ts', 'ts', 'asf'}:
        dst = dst.with_suffix('.mp4')
        say(f"Output extension changed to '.mp4' for compatibility.", C_WARN)
    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise ValueError("Cannot open video.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    four = cv2.VideoWriter_fourcc(*'mp4v')
    tmp = Path(tempfile.mkstemp(suffix=".mp4")[1])
    out = cv2.VideoWriter(str(tmp), four, fps, (w, h))
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    say("Overlaying frames with OpenCV...", C_PROC)
    with tqdm(total=frame_count, desc="Processing frames", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(_overlay(frame, text, alpha))
            pbar.update(1)
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    time.sleep(0.2)  # Allow OS to flush file buffers

    # Remux original audio
    aud = Path(tempfile.mkstemp(suffix=".aac")[1])
    run(["ffmpeg", "-y", "-i", str(src), "-vn", "-acodec", "copy", str(aud)])
    run(["ffmpeg", "-y", "-i", str(tmp), "-i", str(aud),
         "-c:v", "copy", "-c:a", "copy", str(dst)])
    tmp.unlink()
    aud.unlink()
    say(f"Watermarked (OpenCV) video saved: {dst}", C_MAIN)

# ───────── Batch watermarking ──────────────────────────────────────────────
def batch_watermark():
    """Batch watermark images or videos in a folder."""
    try:
        folder = _p("Folder with files:", is_dir=True)
        text = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
        if not text:
            raise ValueError("Watermark text cannot be empty.")
        outdir = _p("Output directory (blank = same):", must=False, is_dir=True)
        if not str(outdir):
            outdir = folder
        eng = input(f"{C_INFO}Engine 1=Pillow (images) 2=OpenCV (images) 3=FFmpeg (videos) 4=OpenCV (videos):{Style.RESET_ALL} ").strip()
        
        valid_exts = IMAGE_EXTS if eng in {"1", "2"} else {'mp4', 'mkv', 'webm', 'mov', 'avi', 'flv', 'm4v', 'mpeg', 'vob', 'm2ts', 'ts', 'asf'}
        files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lstrip('.').lower() in valid_exts]
        if not files:
            raise ValueError(f"No valid files found in folder with extensions: {', '.join(valid_exts)}")
        
        for f in tqdm(files, desc="Watermarking files", unit="file"):
            try:
                dst = outdir / f.name
                if eng == "1" and f.suffix.lstrip('.').lower() in IMAGE_EXTS:
                    wm_image_pillow(f, dst, text)
                elif eng == "2" and f.suffix.lstrip('.').lower() in IMAGE_EXTS:
                    wm_image_cv(f, dst, text)
                elif eng == "3" and f.suffix.lstrip('.').lower() in valid_exts:
                    wm_video_ffmpeg(f, dst, text)
                elif eng == "4" and f.suffix.lstrip('.').lower() in valid_exts:
                    wm_video_cv(f, dst, text)
                else:
                    say(f"Skipping {f.name}: Invalid engine or file type", C_WARN)
            except Exception as e:
                say(f"Error processing {f.name}: {e}", C_ERR)
    except Exception as e:
        say(f"Batch watermarking failed: {e}", C_ERR)

# ───────── CLI helpers ─────────────────────────────────────────────────────
def _p(prompt: str, must: bool = True, is_dir: bool = False) -> Path:
    """Prompt for a file or directory path with validation."""
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

# ───────── Conversion flows ────────────────────────────────────────────────
def single_convert():
    """Convert a single file."""
    try:
        src = _p("Source file:")
        ext = input(f"{C_INFO}Target extension (e.g., mp3, mp4, png):{Style.RESET_ALL} ").lstrip('.').lower()
        out = _p("Output directory (blank = same):", must=False)
        if not str(out):
            out = src.parent
        convert(src, out, ext)
    except Exception as e:
        say(str(e), C_ERR)

def batch_convert():
    """Convert all files in a folder to a specified extension."""
    try:
        folder = _p("Folder with files:", is_dir=True)
        ext = input(f"{C_INFO}Convert everything to extension (e.g., mp3, mp4, png):{Style.RESET_ALL} ").lstrip('.').lower()
        files = [f for f in folder.iterdir() if f.is_file()]
        if not files:
            raise ValueError("No files found in the specified folder.")
        for f in tqdm(files, desc="Converting files", unit="file"):
            try:
                convert(f, folder, ext)
            except Exception as e:
                say(f"{f.name}: {e}", C_ERR)
    except Exception as e:
        say(str(e), C_ERR)

# ───────── Stego / Watermark sub-menu ──────────────────────────────────────
def stego_menu():
    """Steganography and watermarking sub-menu."""
    sub = f"""{C_MAIN}
1) Embed encrypted message in image
2) Extract hidden message from image
3) Watermark image   (1 = Pillow  |  2 = OpenCV)
4) Watermark video   (1 = FFmpeg  |  2 = OpenCV)
5) Batch watermark   (images or videos)
6) Back
{Style.RESET_ALL}"""
    while True:
        print(sub)
        choice = input(f"{C_INFO}Select 1-6:{Style.RESET_ALL} ").strip()
        try:
            if choice == "1":  # Embed
                src = _p("Source image:")
                dest = _p("Output image:", must=False)
                msg = input(f"{C_INFO}Message to hide:{Style.RESET_ALL} ").strip()
                pwd = input(f"{C_INFO}Password:{Style.RESET_ALL} ").strip()
                hide_msg(src, dest, msg, pwd)

            elif choice == "2":  # Extract
                src = _p("Stego image:")
                pwd = input(f"{C_INFO}Password used at embed:{Style.RESET_ALL} ").strip()
                say("Revealed message →", C_MAIN)
                print(reveal_msg(src, pwd))

            elif choice == "3":  # Watermark image
                src = _p("Source image:")
                dest = _p("Output image:", must=False)
                txt = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
                eng = input(f"{C_INFO}Engine 1=Pillow  2=OpenCV:{Style.RESET_ALL} ").strip()
                if eng == "2":
                    wm_image_cv(src, dest, txt)
                else:
                    wm_image_pillow(src, dest, txt)

            elif choice == "4":  # Watermark video
                src = _p("Source video:")
                dest = _p("Output video:", must=False)
                txt = input(f"{C_INFO}Watermark text:{Style.RESET_ALL} ").strip()
                eng = input(f"{C_INFO}Engine 1=FFmpeg  2=OpenCV:{Style.RESET_ALL} ").strip()
                if eng == "2":
                    wm_video_cv(src, dest, txt)
                else:
                    wm_video_ffmpeg(src, dest, txt)

            elif choice == "5":  # Batch watermark
                batch_watermark()

            elif choice == "6":
                break
            else:
                say("Invalid choice.", C_WARN)
        except Exception as e:
            say(str(e), C_ERR)

# ───────── Main menu & entry point ─────────────────────────────────────────
def main():
    """Main program entry point."""
    print(BANNER)
    ensure_ffmpeg()

    menu = f"""{C_MAIN}
1) Single file convert
2) Batch convert
3) Steganography / Watermark
4) List FFmpeg formats
5) Exit
{Style.RESET_ALL}"""
    actions = {
        "1": single_convert,
        "2": batch_convert,
        "3": stego_menu,
        "4": lambda: (
            say("Encodable formats:", C_MAIN),
            print(", ".join(sorted(MUX))),
            say("Decodable formats:", C_MAIN),
            print(", ".join(sorted(DEMUX)))
        ),
    }

    while True:
        print(menu)
        choice = input(f"{C_INFO}Select option 1-5:{Style.RESET_ALL} ").strip()
        if choice == "5":
            say("BGGremlin Group signing off!", C_MAIN)
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
