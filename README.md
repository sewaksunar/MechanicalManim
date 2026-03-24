# Manimations - Mechanical Engineering Animations

A collection of animations created with **Manim Community** for visualizing mechanical engineering concepts, dynamics, statics, and more.

---

## 📋 Table of Contents
1. [Project Environment](#project-environment)
2. [Initial Setup](#initial-setup)
3. [Activation & Verification](#activation--verification)
4. [Working with Environments](#working-with-environments)
5. [GitHub Setup](#github-setup)
6. [Quick Start](#quick-start)
7. [Project Workflow](#project-workflow)
8. [File Structure](#file-structure)
9. [Troubleshooting](#troubleshooting)
10. [Sample Animation](#sample-animation)

---

## 🔧 Project Environment

### Current Configuration
| Setting | Value |
|---------|-------|
| **Package Manager** | `uv` (fast Python package manager) |
| **Python Version** | 3.13.5 |
| **Manim Version** | 0.20.1 |
| **Virtual Environment** | `.venv/` |
| **Location** | `c:\Users\sewak\Documents\MechanicalManim\manimations` |

---

## 🚀 Initial Setup

### Step 1: Project Initialization
Create a new project with uv and Python 3.13:
```bash
uv init --python 3.13 manimations
cd manimations
```

### Step 2: Install Manim
Add Manim as a dependency using uv:
```bash
uv add manim
```

### Step 3: Verify Installation
```bash
uv run manim checkhealth
```

---

## ✅ Activation & Verification

### Activate Virtual Environment (Windows PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

### Update Manim with UV
```bash
uv pip install --upgrade manim --python .venv\Scripts\python.exe
```

### Verify Manim Version
```bash
manim -version
# Output: Manim Community v0.20.1
```

---

## 🌍 Working with Environments

### Understanding Your Environment Setup

Your project uses:
- **Virtual Environment (venv)**: Isolates project dependencies from system Python
- **UV Package Manager**: Faster and more reliable than pip
- **Lock File (.lock)**: Ensures reproducible environments across machines

### ✅ Activating the Virtual Environment

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```
After activation, your prompt will show:
```
(manimations) PS C:\Users\sewak\Documents\MechanicalManim\manimations>
```

**Windows Command Prompt (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**To Deactivate:**
```powershell
deactivate
```

### 📦 Managing Packages with UV

#### View All Installed Packages
```bash
uv pip list
```

#### Install a New Package
```bash
uv add package_name
```
Example:
```bash
uv add numpy scipy sympy
```

#### Upgrade a Package
```bash
uv pip install --upgrade package_name
```
Example (upgrade manim):
```bash
uv pip install --upgrade manim
```

#### Remove a Package
```bash
uv remove package_name
```
Example:
```bash
uv remove unused_package
```

#### View Package Details
```bash
uv pip show package_name
```

### 🔄 Running Commands in the Environment

#### Option 1: Activate then Run
```powershell
.venv\Scripts\Activate.ps1
manim -pql my_file.py MyScene
```

#### Option 2: Direct Execution (without activation)
```powershell
.venv\Scripts\python.exe -m manim -pql my_file.py MyScene
```

#### Option 3: Using UV Run (Recommended)
```bash
uv run manim -pql my_file.py MyScene
```
**Advantages:**
- No need to manually activate
- Automatically uses correct Python version
- Consistent across different machines
- Syncs with `pyproject.toml` dependencies

### 🔐 Syncing Dependencies

When you pull updates to `pyproject.toml`, sync your environment:
```bash
uv sync
```

This will:
- Install any new dependencies
- Remove packages no longer in `pyproject.toml`
- Update to specified versions
- Update the `.lock` file

### 📋 Environment Information

Check your environment details:
```bash
# Show Python executable path
python -c "import sys; print(sys.executable)"

# Show all site-packages
python -c "import site; print(site.getsitepackages())"

# Check Python version
python --version

# Verify manim location
python -c "import manim; print(manim.__file__)"
```

### 💡 Best Practices

✅ **Do:**
- Always activate the environment or use `uv run` before running scripts
- Use `uv sync` after pulling changes to `pyproject.toml`
- Keep `pyproject.toml` and `.lock` file up to date
- Use `uv add` instead of `pip install` for new dependencies
- Run `uv run manim checkhealth` to verify installation

❌ **Don't:**
- Mix `pip` and `uv` commands in the same project
- Install packages system-wide when working on this project
- Delete `.lock` file manually
- Modify `.venv` directory directly

### 🚨 Troubleshooting Environment Issues

#### Issue: "command not found" after activation
```powershell
# Ensure PowerShell execution policy allows scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

#### Issue: Different Python version in environment
```bash
# Create new environment with specific Python
uv venv --python 3.13
uv sync
```

#### Issue: Packages not found after installation
```bash
# Deactivate and reactivate
deactivate
.venv\Scripts\Activate.ps1

# Or use uv directly
uv run python -m pip list
```

#### Issue: Lock file conflicts
```bash
# Remove and regenerate lock file
Remove-Item .lock
uv sync
```

---

## 🐙 GitHub Setup

### Initial Git Configuration

**Set your Git identity (one-time setup):**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Or for this project only:**
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Initialize Repository

**If you haven't created a Git repository yet:**
```bash
cd c:\Users\sewak\Documents\MechanicalManim\manimations
git init
```

### Add Files & Make Initial Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Manim environment setup with v0.20.1"
```

### Connect to Remote Repository

**If you have a GitHub repository ready:**
```bash
# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/yourusername/manimations.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

### Common Git Commands

#### Check Repository Status
```bash
git status
```

#### View Commit History
```bash
git log --oneline
```

#### Create a New Branch
```bash
git checkout -b feature/your-feature-name
```

#### Switch Between Branches
```bash
git checkout branch-name
```

#### Commit Changes
```bash
git add .
git commit -m "Descriptive commit message"
```

#### Push Changes
```bash
git push origin branch-name
```

#### Pull Latest Changes
```bash
git pull origin main
```

#### Merge a Branch
```bash
git checkout main
git merge feature/your-feature-name
```

### Best Practices

✅ **Do:**
- Write descriptive commit messages
- Commit frequently with logical changes
- Create feature branches for new work
- Keep `.lock` and `pyproject.toml` in sync
- Push changes regularly

❌ **Don't:**
- Commit `.venv/` (already in .gitignore)
- Commit generated media files (videos/images)
- Use vague messages like "fix" or "update"
- Force push to main branch
- Commit without testing

### .gitignore Verification

Your `.gitignore` is already configured to exclude:
- ✅ Virtual environment (`.venv/`)
- ✅ Cache files (`__pycache__/`)
- ✅ Media files (videos, images)
- ✅ Build artifacts

**Except:**
- ✅ Demo video: `Tutorial/media/videos/text/480p15/TextMoving.mp4` (tracked for README)

---

## ⚡ Quick Start

### Initialize a New Project
```bash
manim init project my-project --default
```

### Render an Animation
Navigate to your project folder and run:
```bash
manim -pql main.py SceneName
```

**Flags explained:**
- `-p` : Preview (plays the animation after rendering)
- `-q` : Quality (l=low, m=medium, h=high, k=4K)
- `-l` : Low quality (480p15 fps)

### Alternative: Using Manim Sideview Extension
You can also render animations directly from VS Code using the Manim Sideview extension for a visual editor experience.

---

## 📁 Project Workflow

### 1. Write Animation Code
Create a `.py` file with your Manim scene:
```python
from manim import *

class MyAnimation(Scene):
    def construct(self):
        text = Text("Hello World")
        self.play(FadeIn(text))
        self.wait()
```

### 2. Render the Animation
```bash
manim -pql your_file.py MyAnimation
```

### 3. Output Location
Rendered videos are saved in:
```
project_folder/media/videos/your_file/480p15/MyAnimation.mp4
```

### 4. Organize by Category
Keep animations organized in folders:
- `Tutorial/` - Basic examples
- `Dynamics/` - Mechanical dynamics
- `Statics/` - Static analysis
- `Fluid/` - Fluid dynamics
- `Thermodynamics/` - Thermal concepts
- `Math/` - Mathematical visualizations

---

## 🗂️ File Structure

```
manimations/
├── Tutorial/                          # Basic animation tutorials
│   ├── custom.py                      # Custom geometric shapes
│   ├── geometry.py                    # Geometric animations
│   ├── text.py                        # Text animations
│   └── media/videos/
├── Dynamics/                          # Mechanical dynamics
│   ├── main.py
│   ├── mechanism.py
│   ├── balance.py
│   └── media/
├── Statics/                           # Static analysis
│   ├── main.py
│   ├── fbd.py                         # Free body diagrams
│   ├── stress_transformation_2d.py
│   └── media/
├── Fluid/                             # Fluid dynamics
├── Thermodynamics/                    # Thermodynamic processes
├── Math/                              # Mathematical concepts
├── fem/                               # Finite element method
├── figure/                            # Visualization figures
├── .venv/                             # Python virtual environment
├── pyproject.toml                     # Project configuration
├── README.md                          # This file
└── .gitignore                         # Git ignore rules
```

---

## 🐛 Troubleshooting

### Issue: ImportError - DLL load failed (PyAV/FFmpeg)

**Cause:** Incompatible or missing FFmpeg dependencies on Windows.

**Solution:**
```bash
# Remove the problematic av package
pip uninstall av -y

# Reinstall from conda-forge with proper FFmpeg bindings
pip install av==16.0.1

# Upgrade related system libraries
uv pip install --upgrade ffmpeg openssl
```

**Why this works:**
- The problematic `av` v13.1.0 had incompatible FFmpeg dependencies
- Conda-forge's `av` v16.0.1 includes properly compiled DLL files for Windows
- All necessary dependencies (ffmpeg, openssl, etc.) are properly configured

### Issue: Module not found errors
Ensure you're in the correct directory and the virtual environment is activated:
```bash
.venv\Scripts\Activate.ps1
cd path/to/project
```

### Issue: Manim render takes too long
Use lower quality settings for faster testing:
```bash
manim -pl main.py Scene    # -l = low quality (480p15)
```
Use higher quality only for final renders:
```bash
manim -phk main.py Scene   # -h = high quality, -k = 4K
```

---

## 🎬 Sample Animation

### Tutorial - Text Animation

A simple animation demonstrating text rendering in Manim.

**To run:**
```bash
cd Tutorial
manim -pql text.py TextMoving
```

**Video Output:**
[![Play Video](https://img.shields.io/badge/Play-Video-blue?style=for-the-badge)](Tutorial/media/videos/text/480p15/TextMoving.mp4)

Or view directly: [TextMoving.mp4](Tutorial/media/videos/text/480p15/TextMoving.mp4)

---

## 📝 Notes

- Always activate the virtual environment before running manim commands
- Organize animations by topic in separate folders for better project management
- Use low quality (`-l`) for testing and high quality (`-h`) for final renders
- The `.gitignore` is configured to exclude most video files, except demo videos
