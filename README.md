<p align="center">
	<a href="https://www.manim.community/">
		<img src="https://raw.githubusercontent.com/ManimCommunity/manim/main/logo/cropped.png" alt="Manim Community logo" width="220" />
	</a>
	<br />
	<br />
	<a href="https://pypi.org/project/manim/"><img src="https://img.shields.io/pypi/v/manim.svg?style=flat&logo=pypi" alt="Manim PyPI" /></a>
	<a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/package%20manager-uv-2ea44f" alt="uv" /></a>
	<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.13+-blue" alt="Python" /></a>
	<br />
	<br />
	<i>Mechanical engineering animations with Manim Community Edition</i>
</p>

---

# Manimations

Manimations is a curated collection of mechanical engineering visualizations built with Manim CE.

> [!WARNING]
> This project is configured for Manim Community Edition (Manim CE). Do not mix installation steps from 3b1b/manim, as dependency and command differences can break the environment.

> [!NOTE]
> Use `uv run` for consistent execution across machines and to avoid environment mismatch issues.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Command Reference](#command-reference)
- [Troubleshooting](#troubleshooting)

## Installation

### Requirements
- Python 3.13+
- uv
- FFmpeg in system PATH

### Setup
```bash
cd manimations
uv venv --python 3.13
uv sync
```

## Usage

Run any scene directly with uv:

```bash
uv run manim -pql path/to/file.py SceneName
```

PowerShell activation (optional):

```powershell
.venv\Scripts\Activate.ps1
manim -pql path/to/file.py SceneName
```

Example:

```bash
uv run manim -pql Tutorial/text.py TextMoving
```

## Video Example

Sample render from the Tutorial module:

<p align="center">
	<img src="https://raw.githubusercontent.com/sewaksunar/MechanicalManim/main/SliderCrankMechanism.gif" width="760" alt="SliderCrank mechanism preview" />
</p>

## Project Structure

- `Dynamics/`: mechanisms and velocity/acceleration visuals
- `Statics/`: stress transformation and free-body diagrams
- `Fluid/`: fluid flow and related animations
- `Thermodynamics/`: thermal process animations
- `Math/`: math concepts supporting engineering topics
- `fem/`: finite element examples
- `Tutorial/`: starter scenes and experiments

Rendered outputs are generated under each module's `media/` directory.

## Command Reference

```bash
# Health check
uv run manim checkhealth

# Version
uv run manim --version

# Add dependency
uv add package_name

# Sync dependencies after pulling changes
uv sync
```

Quality shortcuts:
- `-ql` low (fast iteration)
- `-qm` medium
- `-qh` high
- `-qk` 4K

## Troubleshooting

- PowerShell activation blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

- Missing dependencies or environment drift:

```bash
uv sync
```

- Slow rendering during development:
Use `-ql` for preview, then switch to `-qh`/`-qk` for final output.
