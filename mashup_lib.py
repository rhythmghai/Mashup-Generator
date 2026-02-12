
import os
from dotenv import load_dotenv
load_dotenv()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import glob
import zipfile
from moviepy import AudioFileClip, concatenate_audioclips
import yt_dlp
import sys
import shutil

class MashupError(Exception):
    """Custom exception for Mashup errors"""
    pass

def search_and_download_videos(singer_name, n_videos, output_dir="temp_downloads"):
    """
    Searches and downloads N videos (audio only) of the singer.
    Returns a list of downloaded file paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'ignoreerrors': True,
        # Search query
        'default_search': 'ytsearch{}'.format(n_videos),
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    print(f"Downloading {n_videos} videos for {singer_name}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use ytsearchN:query to get N results
            ydl.download([f"ytsearch{n_videos}:{singer_name}"])
    except Exception as e:
        raise MashupError(f"Download failed: {e}")

    # Get list of downloaded files
    files = glob.glob(os.path.join(output_dir, "*.mp3"))
    if len(files) < n_videos:
        # It's possible some failed or strict search didn't yield enough.
        # We'll proceed with what we have if > 0, else raise error.
        if len(files) == 0:
            raise MashupError("No videos found or downloaded.")
        print(f"Warning: Only {len(files)} videos downloaded out of {n_videos} requested.")
    
    return sorted(files)

def process_and_merge_audios(input_files, trim_duration, output_filename):
    """
    Trims the first `trim_duration` seconds of each file and merges them.
    Saves to `output_filename`.
    """
    clips = []
    print(f"Processing and merging {len(input_files)} files...")
    try:
        for file in input_files:
            try:
                clip = AudioFileClip(file)
                # Trim
                if clip.duration > trim_duration:
                    sub_clip = clip.subclipped(0, trim_duration)
                    clips.append(sub_clip)
                else:
                    # If clip is shorter than trim_duration, take whole clip or skip?
                    # "Extract the first Y seconds". We'll take whatever is there if < Y.
                    clips.append(clip)
            except Exception as e:
                print(f"Error processing {file}: {e}. Skipping.")
        
        if not clips:
            raise MashupError("No valid audio clips to merge.")

        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_filename, verbose=False, logger=None)
        
        # Close clips to release resources
        for clip in clips:
            clip.close()
            # If subclipped, the original clip might assume to be closed too if handled correctly
            # But explicitly closing the wrapper is good practice.
            if hasattr(clip, 'close'): clip.close() 
        final_clip.close()
        
    except Exception as e:
        raise MashupError(f"Merge failed: {e}")

def create_zip(file_path):
    """
    Zips the given file. Returns the path to the zip file.
    """
    zip_filename = os.path.splitext(file_path)[0] + ".zip"
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
        return zip_filename
    except Exception as e:
        raise MashupError(f"Zipping passed: {e}")

def send_email(recipient_email, attachment_path):
    """
    Sends an email with the attachment. 
    NOTE: Requires SMTP configuration. Since we cannot hardcode credentials safely,
    and the prompt doesn't provide them, this function will mock the sending 
    or fail if credentials aren't set in env vars.
    For this task, I will assume we should try to send if ENV vars are present, 
    otherwise print a message that it would be sent. 
    However, the prompt says "Failure to email... MUST be handled". 
    I will try to use a standard Gmail setup if env vars exist.
    """
    sender_email = os.environ.get("MASHUP_EMAIL")
    sender_password = os.environ.get("MASHUP_PASSWORD")
    
    if not sender_email or not sender_password:
        raise MashupError("Email credentials not configured (MASHUP_EMAIL, MASHUP_PASSWORD). Cannot send email.")

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Your Mashup is Ready!"
        
        body = "Attached is your requested mashup."
        msg.attach(MIMEText(body, 'plain'))
        
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print(f"Email sent successfully to {recipient_email}")
        
    except Exception as e:
        raise MashupError(f"Failed to send email: {e}")

def cleanup_temp(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
