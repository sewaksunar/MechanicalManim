#!/usr/bin/env python3
"""
Helper script to add voiceover to manim animations using ffmpeg.

Usage:
1. Generate animation: manim --quality=l text.py CustomAnimation
2. Record voiceover audio file (e.g., voiceover.mp3)
3. Run this script: python add_voiceover.py voiceover.mp3
"""

import os
import subprocess
import sys
from pathlib import Path

def add_voiceover_to_video(audio_file, output_dir="media/videos/text/480p15"):
    """Add voiceover audio to the animation video."""
    
    video_file = Path(output_dir) / "CustomAnimation.mp4"
    output_with_audio = Path(output_dir) / "CustomAnimation_with_voiceover.mp4"
    
    if not video_file.exists():
        print(f"Error: Video file not found at {video_file}")
        print("Please run: manim --quality=l text.py CustomAnimation")
        return False
    
    if not Path(audio_file).exists():
        print(f"Error: Audio file not found at {audio_file}")
        return False
    
    # Use ffmpeg to add audio to video
    cmd = [
        "ffmpeg",
        "-i", str(video_file),
        "-i", str(audio_file),
        "-c:v", "copy",           # Copy video codec (no re-encoding)
        "-c:a", "aac",            # Convert audio to AAC
        "-shortest",              # Use shortest input length
        "-y",                     # Overwrite output file
        str(output_with_audio)
    ]
    
    print(f"Adding voiceover to video...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Success! Video with voiceover saved to: {output_with_audio}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running ffmpeg: {e}")
        print("Make sure ffmpeg is installed: https://ffmpeg.org/download.html")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    audio_file = sys.argv[1]
    add_voiceover_to_video(audio_file)
