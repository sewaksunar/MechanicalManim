# Manimations - Mechanical Engineering Animations

A collection of animations created with **Manim Community** for visualizing mechanical engineering concepts, dynamics, statics, and more.

## Current Setup

**Project Environment:**
- **Package Manager:** `uv` (fast Python package manager)
- **Python Version:** 3.13.5
- **Manim Version:** 0.20.1
- **Virtual Environment Location:** `.venv/`

## Installation & Setup
```bash
uv init --python 3.13 manimations
cd manimations
uv add manim
```
# Verifying setup
```
uv run manim checkhealth
```

## Sample Animation

**Tutorial - Text Animation:**
A simple animation demonstrating text rendering in Manim.
```
cd Tutorial
manim -pql text.py TextMoving
```

**Video Preview:**
<video width="480" controls>
  <source src="Tutorial/media/videos/text/480p15/TextMoving.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

Generated video: `Tutorial/media/videos/text/480p15/TextMoving.mp4`

# Starting a new project
first start the virtual enviroment
```
.venv\Scripts\activate
```
then create new project
```
manim init project my-project --default   
```
then select a peference template to choose
```
manim main.py Test --format=png
```

# Run the command line (navigating to that folder)
```
cd <>
```
```
manim -pql main.py <scene>
```
# Or can run the animation via manim sideview extension 
## This error can occus:
    Removed the problematic av package (version 13.1.0) from your environment
    Reinstalled av (version 16.0.1) from conda-forge, which includes properly compiled FFmpeg dependencies for Windows
    Upgraded related system libraries (ffmpeg, openssl, python, etc.) to ensure compatibility
    The error you were experiencing (ImportError: DLL load failed while importing _core) was due to incompatible or missing FFmpeg dependencies. By using conda-forge's build of PyAV, all necessary DLL files and dependencies are properly configured for Windows.

# File structure
```
Dyncamics
|---SP1
|---SP2
|---KP2
|...
.
.
.
```
