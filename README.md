# Omni Converter version 3 (current build)

**Omni Converter** is on path to become a powerful, command-line media conversion tool with advanced steganography and watermarking capabilities.
Developed by the **BGGremlin Group**, it leverages FFmpeg, Pillow, OpenCV, and Stegano to provide a versatile solution for converting audio, video, and image files, embedding hidden messages, and applying watermarks.

## Features(*mostly functional*)

- **Media Conversion**:
  - Convert audio, video, and image files to a wide range of formats using FFmpeg.
  - Supports numerous codecs and quality presets for optimized output (e.g., MP3, AAC, FLAC, MP4, MKV, WebM, and more).
  - Single file and batch conversion modes.

- **Steganography**:
  - Embed encrypted messages in images using LSB (Least Significant Bit) steganography.
  - Extract hidden messages with password-based decryption.

- **Watermarking**:
  - Apply text watermarks to images using Pillow or OpenCV.
  - Apply text watermarks to videos using FFmpeg or OpenCV.
  - Batch watermarking for processing multiple files.

- **User-Friendly Interface**:
  - Color-coded CLI with progress bars (via `tqdm`).
  - Robust error handling and logging to `omni_converter.log`.
  - Dynamic dependency installation for Python packages.

## Requirements

- **Python 3.6+**
- **FFmpeg** (must be installed and accessible in your system PATH)
- Python packages (automatically installed if missing):
  - `colorama`
  - `stegano`
  - `pillow`
  - `opencv-python-headless`
  - `tqdm`

## Installation

1. **Install FFmpeg**:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) or install via a package manager like Chocolatey (`choco install ffmpeg`).
   - **macOS**: Install via Homebrew (`brew install ffmpeg`).
   - **Linux**: Install via your package manager (e.g., `sudo apt install ffmpeg` on Ubuntu).

2. **Clone or Download the Script**:
   ```bash
   git clone https://github.com/BGGremlin/Omni-Con.git
   cd omni-converter
   ```

3. **Run the Script**:
   ```bash
   python3 omni_con3.py
   ```
   The script will automatically install any missing Python dependencies.

## Usage

Run the script and follow the interactive CLI menu:

```bash
python3 omni_con3.py
```

### Main Menu Options

1. **Single File Convert**: Convert a single file to a specified format.
2. **Batch Convert**: Convert all files in a folder to a specified format.
3. **Steganography / Watermark**: Access Ascend to the steganography and watermarking sub-menu.
4. **List FFmpeg Formats**: Display supported FFmpeg formats.
5. **Exit**: Exit the program.

### Steganography / Watermark Sub-Menu

1. **Embed Encrypted Message in Image**: Hide a message in an image with password encryption.
2. **Extract Hidden Message from Image**: Reveal a hidden message using the correct password.
3. **Watermark Image**: Apply a text watermark to an image (Pillow or OpenCV).
4. **Watermark Video**: Apply a text watermark to a video (FFmpeg or OpenCV).
5. **Batch Watermark**: Watermark multiple images or videos in a folder.
6. **Back**: Return to the main menu.

### Supported Formats

- **Audio**: MP3 (low, standard, high), AAC (low, standard, high), WAV (16-bit, 24-bit), FLAC (standard, high), OGG (low, standard, high), Opus (low, standard, high), M4A, ALAC, WMA (low, standard), AC3, DTS.
- **Video**: MP4 (H.264, H.265, fast, high), MKV (H.264, H.265), WebM (low, standard, high), GIF (low, standard), AVI (MPEG-4, DivX), MOV (H.264, ProRes), FLV, M4V, OGV, 3GP, MPEG, VOB, M2TS, TS, ASF.
- **Images** (for steganography/watermarking): PNG, JPG, JPEG, BMP, WebP.

### Example Commands

- **Convert a single file**:
  ```
  Select option: 1
  Source file: video.mp4
  Target extension: webm
  Output directory (blank = same): 
  ```

- **Embed a message in an image**:
  ```
  Select option: 3
  Select 1-6: 1
  Source image: image.png
  Output image: stego_image.png
  Message to hide: Secret message
  Password: mypassword
  ```

- **Batch watermark videos**:
  ```
  Select option: 3
  Select 1-6: 5
  Folder with files: /path/to/videos
  Watermark text: Confidential
  Output directory (blank = same): /path/to/output
  Engine 1=Pillow (images) 2=OpenCV (images) 3=FFmpeg (videos) 4=OpenCV (videos): 3
  ```

## Logging

All actions and errors are logged to `omni_converter.log` in the script's directory for debugging and tracking purposes.

## Notes

- Ensure FFmpeg is installed and accessible in your system PATH.
- For steganography, use lossless formats like PNG or BMP for best results. WebP is supported with lossless settings.
- Watermarking with FFmpeg is lighter on CPU, while OpenCV offers more customization but is slower for videos.
- The script handles temporary files cleanly and includes progress bars for batch operations.

## Contributing

Contributions are welcome! Please submit pull requests or issues to the [GitHub repository]([https://github.com/BGGremlin/omni-converter](https://github.com/BGGremlin-Group/Omni-Con)).

## License

This project is licensed under the MIT License.

## Credits

Developed by the **BGGremlin Group** *Creation Unique Tools for Unique Individuals* 
For support, file an issue on the GitHub repository 
