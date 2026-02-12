
from flask import Flask, render_template, request
import os
import shutil
from mashup_lib import search_and_download_videos, process_and_merge_audios, create_zip, send_email, cleanup_temp, MashupError

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        singer = request.form['singer']
        count = int(request.form['count'])
        duration = int(request.form['duration'])
        email = request.form['email']

        # Validation
        if count <= 10:
            return render_template('index.html', error="Number of videos must be greater than 10.")
        if duration <= 20:
            return render_template('index.html', error="Duration must be greater than 20 seconds.")

        # Processing
        # We'll use a unique output filename to avoid collisions
        output_filename = f"mashup_{singer.replace(' ', '_')}_{count}_{duration}.mp3"
        temp_dir = f"temp_web_{singer.replace(' ', '_')}"

        try:
            # 1. Download
            files = search_and_download_videos(singer, count, temp_dir)
            
            # 2. Process
            process_and_merge_audios(files, duration, output_filename)
            
            # 3. Zip
            zip_file = create_zip(output_filename)
            
            # 4. Email
            try:
                send_email(email, zip_file)
                message = f"Mashup created and sent to {email} successfully!"
                success = True
            except MashupError as ignored_email_error:
                # If email fails, we still created the mashup. 
                # "Failure to email... MUST be handled with clear error feedback"
                # We can show success in creation but error in email.
                message = f"Mashup created successfully, but email sending failed: {ignored_email_error}. File is saved as {zip_file}."
                success = False # Or True with warning? Let's say False for "Failure in email delivery" requirement.
            
            # Cleanup
            if os.path.exists(output_filename):
                os.remove(output_filename) # We zipped it, so remove mp3
            # We keep the zip? Or remove it after sending? 
            # Usually strict cleanup means remove it. But if email failed, we might want to keep it.
            # For this simple app, let's remove the zip if sent, keep if failed?
            # actually prompt says "Resource cleanup".
            if success and os.path.exists(zip_file):
                os.remove(zip_file)
                
            return render_template('result.html', success=success, message=message)

        finally:
            cleanup_temp(temp_dir)

    except MashupError as e:
        return render_template('result.html', success=False, message=str(e))
    except Exception as e:
        return render_template('result.html', success=False, message=f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=8000)
