import cv2
import argparse
import os
import telegram
from telegram import Bot
import numpy as np
import time
import asyncio
import subprocess

# Asynchronous function to send video to Telegram
async def send_video_to_telegram(bot_token, chat_id, video_path):
    bot = Bot(token=bot_token)
    with open(video_path, 'rb') as video_file:
        await bot.send_video(chat_id=chat_id, video=video_file)
    print(f"Video {video_path} sent to Telegram.")

# Function to remove the oldest video if more than 10 files exist
def clean_old_files(destination_folder, max_files=10):
    files = sorted(os.listdir(destination_folder), key=lambda x: os.path.getmtime(os.path.join(destination_folder, x)))
    if len(files) > max_files:
        os.remove(os.path.join(destination_folder, files[0]))
        print(f"Old video file deleted: {files[0]}")

# Function to record RTSP to MP4 with motion detection and splitting
def record_rtsp_to_mp4_with_motion_detection(rtsp_url, output_folder, bot_token, chat_id, max_file_size=10 * 1024 * 1024, min_motion_threshold=1000):
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Error: Unable to open RTSP stream.")
        return

    # Get frame width and height
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Video parameters
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # Initialize variables
    current_file_index = 0
    video_out = None
    out_file = None
    prev_frame_gray = None
    motion_detected = False
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the current frame to grayscale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Compute the absolute difference between the current and previous frame
            if prev_frame_gray is not None:
                frame_diff = cv2.absdiff(prev_frame_gray, frame_gray)
                _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
                motion_area = cv2.countNonZero(thresh)
                
                # Check for motion
                if motion_area > min_motion_threshold:
                    motion_detected = True
                    if video_out is None:
                        video_out = cv2.VideoWriter(
                            os.path.join(output_folder, f'video_{current_file_index}.mp4'), fourcc, 25.0, (width, height)
                        )
                        out_file = f'video_{current_file_index}.mp4'
                        print(f"New video file created: {out_file}")
            
            # If motion is detected, write the frame
            if motion_detected and video_out is not None:
                video_out.write(frame)
                frame_count += 1

                # Check if file exceeds max size
                if os.path.getsize(os.path.join(output_folder, out_file)) >= max_file_size:
                    video_out.release()
                    print(f"File {out_file} reached max size of 10MB, creating a new file.")
                    # Increment the file index and create a new file
                    current_file_index += 1
                    video_out = None
                    motion_detected = False  # Reset motion detection until next motion

                    # Clean up old files if more than 10 files are stored
                    clean_old_files(output_folder)

                    # Send the current video file to Telegram after conversion
                    video_path = os.path.join(output_folder, out_file)
                    converted_video_path = os.path.join(output_folder, f"converted_{out_file}")

                    # Use FFmpeg to convert to a compatible format (H.264 video, AAC audio)
                    ffmpeg_command = [
                        "ffmpeg", "-i", video_path, 
                        "-vcodec", "libx264", "-acodec", "aac", 
                        "-strict", "experimental", 
                        "-b:v", "1M", "-b:a", "128k", 
                        converted_video_path
                    ]
                    subprocess.run(ffmpeg_command, check=True)
                    os.remove(video_path)  # Remove the original video

                    # Send the converted video to Telegram
                    asyncio.run(send_video_to_telegram(bot_token, chat_id, converted_video_path))

                    # Optionally, delete the converted video after sending to Telegram
                    os.remove(converted_video_path)
                    print(f"Converted video {out_file} deleted after sending to Telegram.")

            prev_frame_gray = frame_gray

    except KeyboardInterrupt:
        print("Recording interrupted. Cleaning up...")
    finally:
        # Release resources
        if video_out is not None:
            video_out.release()

        cap.release()
        print("Video recording finished.")

# Main function to parse arguments and run the process
def main():
    parser = argparse.ArgumentParser(description="RTSP to MP4 with Motion Detection, File Splitting and Telegram upload")
    parser.add_argument('--source', type=str, required=True, help="RTSP stream URL")
    parser.add_argument('--output_folder', type=str, required=True, help="Folder to save the output MP4 files")
    parser.add_argument('--bot_token', type=str, required=True, help="Telegram bot token")
    parser.add_argument('--chat_id', type=str, required=True, help="Telegram channel chat ID")
    args = parser.parse_args()

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Record video from RTSP to MP4 with motion detection and file splitting
    record_rtsp_to_mp4_with_motion_detection(args.source, args.output_folder, args.bot_token, args.chat_id)

if __name__ == "__main__":
    main()
