
import sys
import os
import argparse
from mashup_lib import search_and_download_videos, process_and_merge_audios, cleanup_temp, MashupError

def main():
    # Argument parsing
    if len(sys.argv) != 5:
        print("Usage: python 102303707.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer_name = sys.argv[1]
    
    try:
        n_videos = int(sys.argv[2])
        trim_duration = int(sys.argv[3])
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    output_filename = sys.argv[4]

    # Validation
    if n_videos <= 10:
        print("Error: NumberOfVideos (N) must be greater than 10.")
        sys.exit(1)
    
    if trim_duration <= 20:
        print("Error: AudioDuration (Y) must be greater than 20.")
        sys.exit(1)
        
    if not output_filename.endswith(".mp3"):
        output_filename += ".mp3"

    temp_dir = f"temp_{singer_name.replace(' ', '_')}"

    print(f"Starting Mashup for {singer_name}...")
    print(f"Videos: {n_videos}, Clip Duration: {trim_duration}s")
    
    try:
        # 1. Download
        downloaded_files = search_and_download_videos(singer_name, n_videos, temp_dir)
        
        # 2. Process & Merge
        process_and_merge_audios(downloaded_files, trim_duration, output_filename)
        
        print(f"Mashup created successfully: {output_filename}")

    except MashupError as e:
        print(f"Mashup Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)
    finally:
        # 3. Cleanup
        if os.path.exists(temp_dir):
            print("Cleaning up temporary files...")
            cleanup_temp(temp_dir)

if __name__ == "__main__":
    main()
