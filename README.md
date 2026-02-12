# Mashup Generator

A Python application to create audio mashups from YouTube videos of a specific singer. Includes both a Command Line Interface (CLI) and a Web Service.

## Prerequisites
- Python 3.x
- FFmpeg (installed and accessible in system PATH)
- Dependencies: `yt-dlp`, `moviepy`, `flask`, `python-dotenv`

## Installation
1. Install dependencies:
   ```bash
   pip install yt-dlp moviepy flask python-dotenv
   ```

2. Configure Email (for Web Service):
   - Edit the `.env` file in the project root:
     ```
     MASHUP_EMAIL=your_email@gmail.com
     MASHUP_PASSWORD=your_app_password
     ```
   - Note: Use an App Password if using Gmail with 2FA.

## Usage

### Command Line Interface (CLI)
Run the script with the following arguments:
```bash
python3 102303707.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFileName>
```
- **Constraints**:
  - `NumberOfVideos` must be > 10
  - `AudioDuration` must be > 20
- **Example**:
  ```bash
  python3 102303707.py "Sharry Maan" 11 21 output.mp3
  ```

### Web Service
1. Start the Flask server:
   ```bash
   python3 app.py
   ```
2. Open your browser and navigate to:
   `http://127.0.0.1:8000`
3. Fill in the form and submit. The mashup will be processed and sent to the provided email.

## Project Structure
- `102303707.py`: CLI Entry point.
- `app.py`: Web Service Backend (Flask).
- `templates/`: HTML templates for the Web App.

## Deployment

### Render
1. Create a new **Web Service** on [Render](https://render.com/).
2. Connect your GitHub repository.
3. Render should automatically detect `python` environment.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn app:app`
6. **Environment Variables**: Add the following in the "Environment" tab:
   - `MASHUP_EMAIL`: Your email.
   - `MASHUP_PASSWORD`: Your email app password.

> **⚠️ IMPORTANT WARNING**: YouTube actively blocks automated requests from public cloud IPs (like Render, Vercel, AWS, Heroku). The application works perfectly in local environments, but you may encounter `HTTP 429: Too Many Requests` or captchas when deploying to these free cloud tiers. To run in production, you would typically need a residential proxy or use a different hosting approach.

### Vercel
1. Import your project on [Vercel](https://vercel.com/).
2. Framework Preset: **Other**.
3. The `vercel.json` file in the repository will handle the configuration.
4. Add Environment Variables in the Project Settings.
**Note**: Vercel has a strict 10-second timeout for serverless functions on the free plan. The Mashup process (downloading/processing) will likely exceed this and fail. **Render is recommended for this application.**
