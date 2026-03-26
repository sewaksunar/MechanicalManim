#!/usr/bin/env python3
"""
Combine voiceover audio with manim animation video.

Usage:
    python merge_audio.py voiceover.mp3
    python merge_audio.py voiceover.wav --output final_video.mp4
"""

import argparse
import subprocess
from pathlib import Path


def merge_audio_video(audio_file, video_file=None, output_file=None):
    """Merge audio with video using ffmpeg."""
    
    # Default video location
    if video_file is None:
        video_file = Path("media/videos/text/480p15/CustomAnimation.mp4")
    
    # Default output name
    if output_file is None:
        output_file = Path("media/videos/text/480p15/CustomAnimation_with_voice.mp4")
    
    video_file = Path(video_file)
    audio_file = Path(audio_file)
    output_file = Path(output_file)
    
    # Check files exist
    if not video_file.exists():
        print(f"✗ Video not found: {video_file}")
        print("Run: manim --quality=l text.py CustomAnimation")
        return False
    
    if not audio_file.exists():
        print(f"✗ Audio not found: {audio_file}")
        return False
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", str(video_file),
        "-i", str(audio_file),
        "-c:v", "libx264",        # Video codec
        "-preset", "fast",         # Speed/quality tradeoff
        "-c:a", "aac",            # Audio codec
        "-b:a", "192k",           # Audio bitrate
        "-shortest",              # Use shortest input
        "-y",                     # Overwrite output
        str(output_file)
    ]
    
    print(f"Merging audio and video...")
    print(f"Video: {video_file}")
    print(f"Audio: {audio_file}")
    print(f"Output: {output_file}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Complete! Video with voiceover saved to:")
        print(f"  {output_file}")
        return True
    except FileNotFoundError:
        print("✗ ffmpeg not found. Install from: https://ffmpeg.org/download.html")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge voiceover with manim animation")
    parser.add_argument("audio", help="Audio file (mp3, wav, etc)")
    parser.add_argument("--video", default="media/videos/text/480p15/CustomAnimation.mp4", 
                        help="Video file path")
    parser.add_argument("--output", help="Output video file path")
    
    args = parser.parse_args()
    merge_audio_video(args.audio, args.video, args.output)
