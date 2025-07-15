# Omni-Con: Media Converter with Steganography & Watermarking

**BGGremlin Group presents Omni-Con V3**  
A powerful, all-in-one media conversion tool for Termux on non-rooted Android devices. Convert audio, video, and images, hide secret messages with encryption, and watermark your media with ease. Built for simplicity, reliability, and a touch of stealth. 🚀

```

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
```

## Features

- **Media Conversion**: Transform audio, video, and images to a wide range of formats using FFmpeg. Supports `mp3`, `flac`, `mp4`, `mkv`, `gif`, and more with quality presets (e.g., `mp3_high`, `webm_low`).
- **Steganography**: Hide encrypted messages in images using a custom LSB (Least Significant Bit) implementation with `Pillow`. Securely embed and extract secrets with password protection.
- **Watermarking**: Add text watermarks to images (`Pillow`) or videos (`FFmpeg`) with customizable placement and transparency.
- **Batch Processing**: Convert or watermark multiple files in one go, perfect for bulk operations.
- **Progress Feedback**: Real-time progress bars and ETA with `tqdm` for conversions, steganography, and watermarking.
- **Termux-Optimized**: Runs seamlessly on non-rooted Android devices in Termux, with storage access via `/sdcard/`.
- **Logging**: Detailed logs saved to `/sdcard/omni_converter.log` for troubleshooting.
- **BGGG Style**: Sleek CLI interface with colorful output and the iconic BGGremlin Group banner.

## Supported Formats

### Audio
- `mp3`, `mp3_low`, `mp3_high`
- `aac`, `aac_low`, `aac_high`
- `wav`, `wav_24bit`
- `flac`, `flac_high`
- `ogg`, `ogg_low`, `ogg_high`
- `opus`, `opus_low`, `opus_high`
- `m4a`, `alac`, `wma`, `wma_low`, `ac3`, `dts`

### Video
- `mp4`, `mp4_fast`, `mp4_high`, `mp4_h265`
- `mkv`, `mkv_h265`
- `webm`, `webm_low`, `webm_high`
- `gif`, `gif_low`
- `avi`, `avi_divx`
- `mov`, `mov_prores`
- `flv`, `m4v`, `ogv`, `3gp`, `mpeg`, `vob`, `m2ts`, `ts`, `asf`

### Images (Steganography & Watermarking)
- `png`, `jpg`, `jpeg`, `bmp`, `webp`

## Prerequisites

- **Termux**: Installed on a non-rooted Android device.
- **Storage Access**: Run `termux-setup-storage` to access `/sdcard/`.
- **Dependencies**:
  - `python` (3.8+)
  - `ffmpeg`
  - Python packages: `colorama`, `pillow`, `tqdm`

## Installation

1. **Set up Termux**:
   ```bash
   pkg update && pkg upgrade
   pkg install python ffmpeg
   termux-setup-storage
   pip install colorama pillow tqdm
   ```

2. **Clone or Download Omni-Con**:
   ```bash
   mkdir ~/OMNI_CON
   cd ~/OMNI_CON
   # Download omni-con.py (e.g., via wget, curl, or manual copy)
   wget <[URL_TO_SCRIPT](https://github.com/BGGremlin-Group/Omni-Con.git)> -O omnicon_termux.py
   chmod +x omnicon_termux.py
   ```

3. **Run the Script**:
   ```bash
   ./omni-con.py
   ```

## Usage

Launch the script and choose from the main menu:

```
1) Single file convert
2) Batch convert
3) Steganography / Watermark
4) Exit
```

### Single File Conversion
- Select **1** to convert a single file (e.g., `/sdcard/test.mp4` to `flac`).
- Specify the source file, target extension, and output directory (default: same as source).

### Batch Conversion
- Select **2** to convert all files in a folder to a chosen format (e.g., `mp3`, `mkv`).
- Progress bars show conversion status for each file.

### Steganography / Watermarking
Select **3** to access the sub-menu:
```
1) Embed encrypted message in image
2) Extract hidden message from image
3) Watermark image (Pillow)
4) Watermark video (FFmpeg)
5) Batch watermark (images or videos)
6) Back
```

- **Embed Message**: Hide a secret message in a PNG/JPG image with a password. Progress bar tracks bit embedding.
- **Extract Message**: Reveal a hidden message using the correct password.
- **Watermark Image/Video**: Add text watermarks to images or videos, with progress feedback.
- **Batch Watermark**: Apply watermarks to multiple files in a folder.

### Example Commands
- **Convert a video**:
  ```bash
  # Select 1, enter /sdcard/test.mp4, mp3, /sdcard/
  ```
- **Hide a message**:
  ```bash
  # Select 3 → 1, enter /sdcard/test.png, /sdcard/stego.png, "Secret message", "mypassword"
  ```
- **Watermark an image**:
  ```bash
  # Select 3 → 3, enter /sdcard/test.png, /sdcard/watermarked.png, "BGGG 2025"
  ```

## Logging
- All actions (success, errors, progress) are logged to `/sdcard/omni_converter.log`.
- Check the log for debugging or to review operations.

## Notes
- **FFmpeg Codecs**: Some formats (e.g., `prores`, `dts`) may not be supported by Termux’s FFmpeg. Run `ffmpeg -formats` or `ffmpeg -codecs` to check.
- **Steganography**: Uses a custom LSB implementation with `Pillow` for reliability in Termux, replacing `stegano` to avoid `opencv-python` issues.
- **Progress Bars**: Conversion and video watermarking use simulated progress due to FFmpeg limitations in Termux. Steganography and image watermarking provide accurate progress.
- **Storage**: Ensure `/sdcard/` is accessible via `termux-setup-storage`.

## Troubleshooting
- **Error: "Storage not accessible"**: Run `termux-setup-storage`.
- **FFmpeg not found**: Install with `pkg install ffmpeg`.
- **Dependency issues**: Manually install `colorama`, `pillow`, or `tqdm` with `pip`.
- **Conversion fails**: Verify the target format is supported (`ffmpeg -formats`) and check `/sdcard/omni_converter.log`.

## Contributing
Got ideas? Want to add audio steganography or new presets? Submit a pull request or contact the BGGremlin Group! 🦹‍♂️

## License
Developed by **BGGremlin Group**. *Creating Unique Tools for Unique Individuals* 
Licensed under MIT. Use it, tweak it, share it—just give us a shoutout!
