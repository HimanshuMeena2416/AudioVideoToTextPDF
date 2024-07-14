# Audio to Text and Video to PDF Converter

This Python project converts audio files to text using OpenAI and video files to PDFs by extracting frames.

## Requirements

- Python 3.12 (or higher)
- Required Python packages (install using `pip install -r requirements.txt`):
  - openai
  - Pillow (PIL)
  - opencv-python
  - fpdf
  - youtube-dl
  - scikit-image

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
Install dependencies:
bash
Copy code
pip install -r requirements.txt
Usage
Convert Audio to Text
Ensure your audio file is in one of the supported formats (mp3, mp4, mpeg, mpga, m4a, wav, webm).
Modify audio_to_text.py to specify your input audio file and output text file paths.
Run python audio_to_text.py.
Convert Video to PDF
Ensure you have URLs of videos or playlists from YouTube.
Modify video_to_pdf.py to specify your input video URL and output PDF directory.
Run python video_to_pdf.py.
Example
To convert a specific YouTube video to PDF:

bash
Copy code
python video_to_pdf.py https://www.youtube.com/watch?v=R3GfuzLMPkA
Notes
File uploads are limited to 25 MB for audio.
Video download retries up to 3 times in case of errors.
Frames are extracted based on structural similarity with a default threshold of 0.8.
