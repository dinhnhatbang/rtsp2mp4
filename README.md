# RTSP to MP4 with Motion Detection, File Splitting, and Telegram Upload

This project captures video from an RTSP stream, detects motion, splits the video into smaller files, and uploads the video files to a Telegram channel. It also ensures that the video file is in a format compatible with Telegram by converting it using FFmpeg before sending it.

## Features
- **RTSP Stream Capture**: Capture video from an RTSP stream.
- **Motion Detection**: Detect motion in the video and record only when motion is detected.
- **File Splitting**: Split video files into chunks when they exceed a specified file size (default: 10MB).
- **Telegram Upload**: Automatically upload the video files to a specified Telegram channel.
- **FFmpeg Conversion**: Convert videos to a compatible format (H.264 video and AAC audio) before uploading to Telegram.
- **Old File Cleanup**: Delete the oldest video files when more than a specified number of files are present in the storage folder.

## Requirements
- **Python 3.x** (Tested with Python 3.7+)
- **FFmpeg**: Used for video conversion to a compatible format.
- **OpenCV**: Used for capturing the RTSP stream and processing frames.
- **Telegram Bot API**: Used for uploading videos to a Telegram channel.

### Installing Dependencies
1. Install Python dependencies:
   ```bash
   pip install opencv-python telegram numpy asyncio
   ```

2. Install FFmpeg (if not already installed):
   - **Ubuntu**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg official site](https://ffmpeg.org/download.html).

## Usage

### Command Line Arguments:
- `--source`: The RTSP stream URL (required).
- `--output_folder`: The folder to store the recorded MP4 video files (required).
- `--bot_token`: Your Telegram bot token (required).
- `--chat_id`: The Telegram chat or channel ID to upload videos to (required).

### Example Usage:
```bash
python rtsp_to_mp4_telegram.py --source rtsp://your_rtsp_stream_url --output_folder /path/to/output_folder --bot_token YOUR_BOT_TOKEN --chat_id YOUR_CHAT_ID
```

### Description of Functionality:
1. **Motion Detection**: The program continuously compares consecutive frames from the RTSP stream. If a significant motion is detected, the current frame is saved into a video file.
   
2. **File Splitting**: When the video file reaches the specified size (default: 10MB), it will close the current file and start a new one. The program automatically keeps the file size under control.

3. **Old File Cleanup**: If the output folder contains more than 10 video files, the oldest files will be deleted to maintain disk space.

4. **FFmpeg Conversion**: After a video file is created, the program uses FFmpeg to convert the file into a compatible format (`H.264` for video and `AAC` for audio). This conversion ensures that the file can be uploaded to Telegram without compatibility issues.

5. **Telegram Upload**: The converted video file is uploaded to the specified Telegram channel or chat using the Telegram Bot API. Optionally, the file is deleted after uploading to save space.

## Troubleshooting
- **"No supported streams" Error**: This error is usually caused by an incompatible video format. The program uses FFmpeg to convert the video into a supported format before uploading to Telegram.
- **FFmpeg Not Installed**: Ensure that FFmpeg is installed on your system. If it is not installed, you can download and install it from [FFmpeg](https://ffmpeg.org/download.html).

## License
This project is open-source and available under the MIT License.

---

If you have any questions or issues, feel free to open an issue in the GitHub repository!
