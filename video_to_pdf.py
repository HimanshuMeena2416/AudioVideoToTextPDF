import sys
from PIL import ImageFile
sys.modules['ImageFile'] = ImageFile
import cv2
import os
import tempfile
import re
from fpdf import FPDF
from PIL import Image
import yt_dlp
from skimage.metrics import structural_similarity as ssim

def download_video(url, filename, max_retries=3):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
    }
    retries = 0
    while retries < max_retries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return filename
        except yt_dlp.utils.DownloadError as e:
            print(f"Error downloading video: {e}. Retrying... (Attempt {retries + 1}/{max_retries})")
            retries += 1
    raise Exception("Failed to download video after multiple attempts.")

def get_video_id(url):
    video_id_match = re.search(r"shorts\/(\w+)", url)
    if video_id_match:
        return video_id_match.group(1)

    video_id_match = re.search(r"youtu\.be\/([\w\-_]+)(\?.*)?", url)
    if video_id_match:
        return video_id_match.group(1)

    video_id_match = re.search(r"v=([\w\-_]+)", url)
    if video_id_match:
        return video_id_match.group(1)

    video_id_match = re.search(r"live\/(\w+)", url)
    if video_id_match:
        return video_id_match.group(1)

    return None

def get_playlist_videos(playlist_url):
    ydl_opts = {
        'ignoreerrors': True,
        'playlistend': 1000,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        return [entry['url'] for entry in playlist_info['entries']]

def extract_unique_frames(video_file, output_folder, n=3, ssim_threshold=0.8):
    cap = cv2.VideoCapture(video_file)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    last_frame = None
    saved_frame = None
    frame_number = 0
    last_saved_frame_number = -1
    timestamps = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % n == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if last_frame is not None:
                similarity = ssim(gray_frame, last_frame, data_range=gray_frame.max() - gray_frame.min())

                if similarity < ssim_threshold:
                    if saved_frame is not None and frame_number - last_saved_frame_number > fps:
                        frame_path = os.path.join(output_folder, f'frame{frame_number:04d}_{frame_number // fps}.png')
                        cv2.imwrite(frame_path, saved_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                        timestamps.append((frame_number, frame_number // fps))

                    saved_frame = frame
                    last_saved_frame_number = frame_number
                else:
                    saved_frame = frame

            else:
                frame_path = os.path.join(output_folder, f'frame{frame_number:04d}_{frame_number // fps}.png')
                cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                timestamps.append((frame_number, frame_number // fps))
                last_saved_frame_number = frame_number

            last_frame = gray_frame

        frame_number += 1

    cap.release()
    return timestamps

def convert_frames_to_pdf(input_folder, output_file, timestamps):
    frame_files = sorted(os.listdir(input_folder), key=lambda x: int(x.split('_')[0].split('frame')[-1]))
    pdf = FPDF("L")
    pdf.set_auto_page_break(0)

    for i, (frame_file, (frame_number, timestamp_seconds)) in enumerate(zip(frame_files, timestamps)):
        frame_path = os.path.join(input_folder, frame_file)
        image = Image.open(frame_path)
        pdf.add_page()

        pdf.image(frame_path, x=0, y=0, w=pdf.w, h=pdf.h, type="PNG")

        timestamp = f"{timestamp_seconds // 3600:02d}:{(timestamp_seconds % 3600) // 60:02d}:{timestamp_seconds % 60:02d}"

        x, y, width, height = 5, 5, 60, 15
        region = image.crop((x, y, x + width, y + height)).convert("L")
        mean_pixel_value = region.resize((1, 1)).getpixel((0, 0))
        if mean_pixel_value < 64:
            pdf.set_text_color(255, 255, 255)
        else:
            pdf.set_text_color(0, 0, 0)

        pdf.set_xy(x, y)
        pdf.set_font("Arial", size=16)  # Increased font size for better readability
        pdf.cell(0, 0, timestamp)

    pdf.output(output_file, "F")

def get_video_title(url):
    ydl_opts = {
        'skip_download': True,
        'ignoreerrors': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=False)
        title = video_info['title'].replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '-').replace(
            '?', '-').replace('<', '-').replace('>', '-').replace('|', '-').replace('"', '-').strip('.')
        return title

def main(url):
    output_directory = './output/pdf'
    os.makedirs(output_directory, exist_ok=True)

    video_id = get_video_id(url)
    if video_id:
        video_file = download_video(url, "video.mp4")
        if not video_file:
            return
        video_title = get_video_title(url)
        output_pdf_name = os.path.join(output_directory, f"{video_title}.pdf")

        with tempfile.TemporaryDirectory() as temp_folder:
            timestamps = extract_unique_frames(video_file, temp_folder)
            convert_frames_to_pdf(temp_folder, output_pdf_name, timestamps)

        os.remove(video_file)
    else:
        video_urls = get_playlist_videos(url)
        for video_url in video_urls:
            video_file = download_video(video_url, "video.mp4")
            if not video_file:
                continue
            video_title = get_video_title(video_url)
            output_pdf_name = os.path.join(output_directory, f"{video_title}.pdf")

            with tempfile.TemporaryDirectory() as temp_folder:
                timestamps = extract_unique_frames(video_file, temp_folder)
                convert_frames_to_pdf(temp_folder, output_pdf_name, timestamps)

            os.remove(video_file)

if __name__ == "__main__":
    main("https://www.youtube.com/watch?v=R3GfuzLMPkA")  # Replace with the URL of the video or playlist
