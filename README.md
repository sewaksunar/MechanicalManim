# Setup
```
uv init --python 3.13 manimations
cd manimations
uv add manim
```
# Verifying setup
```
uv run manim checkhealth
```

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

# Run the command line (navigating to that folder)
```
cd <>
```
```
manim -pql main.py <scene>
```
# Or can run the animation via manim sideview extension 
## This error can occus:
    The issue is now fixed. The manim command executed successfully without the DLL loading error.

    Summary of the fix:

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