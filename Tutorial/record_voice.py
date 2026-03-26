#!/usr/bin/env python3
"""
Simple voice recorder for manim animations.
Records audio and saves it as MP3 or WAV file.

Usage:
    python record_voice.py --duration 20 --output voiceover.mp3
"""

import argparse
import wave
import pyaudio
import subprocess
from pathlib import Path


def record_audio_wav(duration=20, output_file="voiceover.wav"):
    """Record audio using PyAudio and save as WAV."""
    
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    
    print(f"Recording {duration} seconds of audio...")
    print("Make sure your microphone is ready! Starting in 3 seconds...")
    import time
    time.sleep(3)
    
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("🎤 Recording... Speak now!")
    frames = []
    
    try:
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    except KeyboardInterrupt:
        print("\n⏹ Recording stopped early.")
    
    print("✓ Recording finished!")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save as WAV
    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    
    print(f"✓ Saved to: {output_file}")
    return output_file


def convert_wav_to_mp3(wav_file, mp3_file=None):
    """Convert WAV to MP3 using ffmpeg."""
    
    if mp3_file is None:
        mp3_file = Path(wav_file).stem + ".mp3"
    
    cmd = ["ffmpeg", "-i", wav_file, "-q:a", "9", "-n", mp3_file]
    
    print(f"Converting to MP3...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Saved to: {mp3_file}")
        return mp3_file
    except subprocess.CalledProcessError:
        print(f"✗ Error converting to MP3. Install ffmpeg: https://ffmpeg.org")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record voiceover for manim animations")
    parser.add_argument("--duration", type=int, default=20, help="Recording duration in seconds")
    parser.add_argument("--output", default="voiceover.wav", help="Output file (wav or mp3)")
    parser.add_argument("--mp3", action="store_true", help="Convert to MP3 after recording")
    
    args = parser.parse_args()
    
    # Record audio
    wav_file = record_audio_wav(args.duration, args.output if args.output.endswith(".wav") else "temp.wav")
    
    # Convert to MP3 if requested
    if args.mp3 or args.output.endswith(".mp3"):
        mp3_file = args.output if args.output.endswith(".mp3") else args.output.replace(".wav", ".mp3")
        convert_wav_to_mp3(wav_file, mp3_file)
