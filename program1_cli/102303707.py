import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

# ---------------- BASE DIRECTORY ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
AUDIOS_DIR = os.path.join(BASE_DIR, "audios")
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

try:
    # ---------- ARGUMENT CHECK ----------
    if len(sys.argv) != 5:
        raise ValueError(
            "Usage: python <program.py> <SingerName> <NumberOfVideos> <DurationInSeconds> <OutputFile>"
        )

    singer = sys.argv[1]
    num_videos = int(sys.argv[2])
    duration = int(sys.argv[3])
    output_file = sys.argv[4]

    if num_videos <= 10:
        raise ValueError("Number of videos must be greater than 10")

    if duration <= 20:
        raise ValueError("Duration must be greater than 20 seconds")

    # ---------- CREATE DIRECTORIES ----------
    for folder in [VIDEOS_DIR, AUDIOS_DIR, CLIPS_DIR, OUTPUT_DIR]:
        os.makedirs(folder, exist_ok=True)

    # ---------- DOWNLOAD VIDEOS ----------
    print("Downloading videos...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(VIDEOS_DIR, '%(title)s.%(ext)s'),
        'quiet': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{num_videos}:{singer} songs"])

    # ---------- CONVERT TO AUDIO ----------
    print("Converting videos to audio...")
    for file in os.listdir(VIDEOS_DIR):
        video_path = os.path.join(VIDEOS_DIR, file)
        audio = AudioSegment.from_file(video_path)
        audio.export(
            os.path.join(AUDIOS_DIR, f"{file}.mp3"),
            format="mp3"
        )

    # ---------- CUT FIRST Y SECONDS ----------
    print("Cutting first seconds...")
    clips = []

    for file in os.listdir(AUDIOS_DIR):
        audio_path = os.path.join(AUDIOS_DIR, file)
        audio = AudioSegment.from_mp3(audio_path)
        clip = audio[:duration * 1000]
        clip.export(
            os.path.join(CLIPS_DIR, file),
            format="mp3"
        )
        clips.append(clip)

    # ---------- MERGE CLIPS ----------
    print("Merging clips...")
    final_audio = AudioSegment.empty()

    for clip in clips:
        final_audio += clip

    output_path = os.path.join(OUTPUT_DIR, output_file)
    final_audio.export(output_path, format="mp3")

    print("✅ Mashup created successfully!")
    print(f"📁 Output saved at: {output_path}")

except ValueError as ve:
    print("❌ Input Error:", ve)

except Exception as e:
    print("❌ Unexpected Error:", e)
