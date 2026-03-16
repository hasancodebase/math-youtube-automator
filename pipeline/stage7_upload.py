"""
================================================
  MATHSOLVER — STAGE 7: YOUTUBE AUTO UPLOAD
  Automatically uploads videos to YouTube
  with full SEO metadata, thumbnail, playlist
================================================
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
CLIENT_SECRET   = "D:/math-channel/client_secret.json"
TOKEN_FILE      = "D:/math-channel/youtube_token.pickle"
OUTPUT_DIR      = Path("D:/math-channel/output")
FINAL_DIR       = OUTPUT_DIR / "final_videos"
THUMBNAIL_DIR   = OUTPUT_DIR / "thumbnails"
SCRIPTS_DIR     = OUTPUT_DIR / "scripts"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

CHANNEL_NAME    = "MathSolver"
CHANNEL_HANDLE  = "@MathSolver"


# ─────────────────────────────────────────────
#  AUTHENTICATE
# ─────────────────────────────────────────────
def authenticate():
    """
    Authenticates with YouTube API.
    First time: opens browser for Google login.
    After that: uses saved token automatically.
    """
    creds = None

    # Load saved token if exists
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  Refreshing token...")
            creds.refresh(Request())
        else:
            print("  Opening browser for Google login...")
            print("  Sign in with your MathSolver Gmail account!")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("  Token saved — won't need to login again!")

    return build("youtube", "v3", credentials=creds)


# ─────────────────────────────────────────────
#  GET OR CREATE PLAYLIST
# ─────────────────────────────────────────────
def get_or_create_playlist(youtube, level: str) -> str:
    """
    Gets existing playlist for a math level
    or creates a new one automatically.
    """
    playlist_names = {
        "primary":      "Primary Math — Building Foundations",
        "middle":       "Middle School Math — Stepping Up",
        "algebra":      "Algebra — From Easy to Expert",
        "trigonometry": "Trigonometry — Angles Made Easy",
        "calculus":     "Calculus — Step by Step",
    }

    playlist_name = playlist_names.get(level, "MathSolver — General")

    # Search existing playlists
    response = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    ).execute()

    for playlist in response.get("items", []):
        if playlist["snippet"]["title"] == playlist_name:
            print(f"  Found playlist: {playlist_name}")
            return playlist["id"]

    # Create new playlist
    print(f"  Creating playlist: {playlist_name}")
    playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name,
                "description": f"Step by step {level} math solutions — MathSolver",
            },
            "status": {"privacyStatus": "public"}
        }
    ).execute()

    print(f"  ✓ Playlist created: {playlist_name}")
    return playlist["id"]


# ─────────────────────────────────────────────
#  ADD TO PLAYLIST
# ─────────────────────────────────────────────
def add_to_playlist(youtube, video_id: str, playlist_id: str):
    """Adds uploaded video to its playlist."""
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()
    print("  ✓ Added to playlist!")


# ─────────────────────────────────────────────
#  UPLOAD VIDEO
# ─────────────────────────────────────────────
def upload_video(youtube, video_path: str, seo: dict,
                 thumbnail_path: str = None, level: str = "algebra") -> str:
    """
    Uploads video to YouTube with full SEO metadata.
    Returns the YouTube video ID.
    """
    print(f"\n  Uploading: {Path(video_path).name}")
    print(f"  Title: {seo['title']}")

    # Build video metadata
    body = {
        "snippet": {
            "title":       seo["title"][:100],
            "description": seo["description"][:5000],
            "tags":        seo.get("tags", [])[:500],
            "categoryId":  "27",  # Education category
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids":             False,
        }
    }

    # Upload video file
    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024*1024*5  # 5MB chunks
    )

    print("  Uploading video... (this takes 2-5 minutes)")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    # Upload with progress
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"  Upload progress: {progress}%", end="\r")

    video_id = response["id"]
    print(f"\n  ✓ Video uploaded! ID: {video_id}")
    print(f"  URL: https://youtube.com/watch?v={video_id}")

    # Upload thumbnail
    if False and thumbnail_path and Path(thumbnail_path).exists():
        print("  Uploading thumbnail...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("  ✓ Thumbnail uploaded!")

    # Add to playlist
    playlist_id = get_or_create_playlist(youtube, level)
    add_to_playlist(youtube, video_id, playlist_id)

    return video_id


# ─────────────────────────────────────────────
#  MASTER UPLOAD FUNCTION
# ─────────────────────────────────────────────
def upload_from_pipeline(safe_name: str) -> str:
    """
    Uploads a completed video from the pipeline.
    Reads SEO data from JSON, finds video and thumbnail,
    then uploads everything to YouTube automatically.
    """
    print(f"\n{'='*50}")
    print(f"  MATHSOLVER — YOUTUBE UPLOADER")
    print(f"{'='*50}")

    # Find JSON script file
    json_files = list(SCRIPTS_DIR.glob(f"{safe_name}*.json"))
    if not json_files:
        json_files = list(SCRIPTS_DIR.glob("*.json"))

    if not json_files:
        print("  ✗ No script JSON found!")
        print(f"  Looking in: {SCRIPTS_DIR}")
        return None

    json_file = json_files[-1]
    print(f"  Loading: {json_file.name}")

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    seo   = data.get("seo", {})
    level = data.get("level", "algebra")

    # Find video file
    video_files = list(FINAL_DIR.glob("*.mp4"))
    if not video_files:
        print(f"  ✗ No video found in {FINAL_DIR}")
        return None

    video_path = str(video_files[-1])
    print(f"  Video: {Path(video_path).name}")

    # Find thumbnail
    thumb_files = list(THUMBNAIL_DIR.glob("*.png"))
    thumb_path  = str(thumb_files[-1]) if thumb_files else None
    if thumb_path:
        print(f"  Thumbnail: {Path(thumb_path).name}")

    # Authenticate
    print("\n  Authenticating with YouTube...")
    youtube = authenticate()
    print("  ✓ Authenticated!")

    # Upload
    video_id = upload_video(
        youtube      = youtube,
        video_path   = video_path,
        seo          = seo,
        thumbnail_path = thumb_path,
        level        = level
    )

    if video_id:
        url = f"https://youtube.com/watch?v={video_id}"
        print(f"\n{'='*50}")
        print(f"  SUCCESS! Video is LIVE on YouTube!")
        print(f"  {url}")
        print(f"{'='*50}\n")

        # Save upload record
        record = {
            "video_id":   video_id,
            "url":        url,
            "title":      seo.get("title", ""),
            "uploaded_at": datetime.now().isoformat(),
            "level":      level,
        }

        records_file = OUTPUT_DIR / "upload_records.json"
        records = []
        if records_file.exists():
            with open(records_file) as f:
                records = json.load(f)
        records.append(record)
        with open(records_file, "w") as f:
            json.dump(records, f, indent=2)

        return url

    return None


# ─────────────────────────────────────────────
#  RUN DIRECTLY
# ─────────────────────────────────────────────
if __name__ == "__main__":

    print("=" * 50)
    print("  MATHSOLVER — YOUTUBE AUTO UPLOADER")
    print("=" * 50)

    result = upload_from_pipeline("Solve_2x_5_13")

    if result:
        print(f"\n🎉 VIDEO IS LIVE!")
        print(f"URL: {result}")
    else:
        print("\n✗ Upload failed — check errors above")
