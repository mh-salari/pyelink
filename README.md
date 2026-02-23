# PyeLink

[![PyPI version](https://img.shields.io/pypi/v/pyelink)](https://pypi.org/project/pyelink/)
[![Downloads](https://static.pepy.tech/badge/pyelink)](https://pepy.tech/project/pyelink)
[![License](https://img.shields.io/pypi/l/pyelink)](https://github.com/mh-salari/pyelink/blob/main/LICENSE)
[![Documentation](https://readthedocs.org/projects/pyelink/badge/?version=latest)](https://pyelink.readthedocs.io/)
[![DOI](https://img.shields.io/badge/DOI-TODO-blue)](https://doi.org/TODO)

A modern Python wrapper for SR Research EyeLink eye trackers with multi-backend display support (pygame, PsychoPy, pyglet).

PyeLink provides programmatic control over the full EyeLink workflow: connection management, calibration and validation with configurable parameters (number of points, calibration area proportion, target appearance), recording with real-time data access, and direct access to any EyeLink command for advanced configurations not exposed through the high-level API.

For full documentation, see [pyelink.readthedocs.io](https://pyelink.readthedocs.io/).

## Features

- **Multi-backend display**: pygame (recommended), PsychoPy, or pyglet
- **Configurable calibration**: 3/5/9/13-point calibration, adjustable calibration area proportion, custom target appearance (ABC/circle/image)
- **Full programmatic control**: configure every tracker parameter from Python, including calibration area, sample rate, heuristic filtering, and screen geometry
- **Direct command access**: send any EyeLink command via `tracker.send_command()` for advanced configurations (same syntax as Host PC INI files)
- **Real-time data access**: gaze samples, fixation/saccade/blink events, with optional ring buffering
- **Validated settings**: Pydantic-based configuration with runtime type checking and helpful error messages
- **Graceful shutdown**: Ctrl+C at any point (including during calibration) automatically stops recording, saves data, and disconnects

## Installation

**You must specify a backend when installing pyelink.** A simple `pip install pyelink` will NOT work because pyelink requires one of three mutually exclusive display backends (pygame, psychopy, or pyglet).

Choose ONE backend:

```bash
# For Pygame users
pip install pyelink[pygame]

# For PsychoPy users (Python < 3.12 only)
pip install pyelink[psychopy]

# For Pyglet users (pyglet 2.0+)
pip install pyelink[pyglet]
```

You'll also need to install the **EyeLink Developers Kit** (native C libraries) from:
https://www.sr-research.com/support/thread-13.html

Then install pylink separately from SR Research:
```bash
uv pip install --extra-index-url https://pypi.sr-support.com sr-research-pylink
```

**Note:** This codebase has been tested on macOS ARM (Apple Silicon) only.

### ⚠️ Backend Compatibility Warning

**You CANNOT install both `psychopy` and `pyglet` backends together.**

**Why?** PsychoPy pins `pyglet==1.4.11` (from 2017) as a dependency, while the modern pyglet backend requires `pyglet>=2.0.0`. These versions are incompatible.

**Solution:** Choose ONE backend:
- **Pygame** (recommended): Works everywhere, no conflicts
- **PsychoPy**: Use if you need PsychoPy features, but cannot use pyglet 2.0+
- **Pyglet**: Use if you want modern pyglet (2.0+) but don't need PsychoPy

### Platform-Specific Notes

**macOS:**
- PyAudio requires PortAudio. Install it first:
```bash
brew install portaudio
```

**macOS ARM (Apple Silicon) — sr-research-pylink:**

SR Research does not publish ARM-native wheels for `sr-research-pylink`. The package must be installed separately using `uv pip install --extra-index-url` (as shown above) rather than through `uv sync` or `uv run`. This is because `uv sync` resolves dependencies across **all** Python versions specified by `requires-python`, and SR Research's PyPI server does not have wheels for every version. Using `uv pip install` resolves only for the **current** Python and works correctly.

## Quick Start

```python
import pyelink as el

# Configure tracker with backend
settings = el.Settings(
    backend='pygame',           # or 'psychopy', 'pyglet'
    fullscreen=True,
    screen_res=(1920, 1080),    # must match your display
    screen_width=530.0,         # physical display width in mm
    screen_height=300.0,        # physical display height in mm
    screen_distance_top_bottom=(600.0, 640.0),  # eye-to-screen edges in mm
    filename="mydata",
    filepath="./data/",
)

# Tracker creates and owns the window
tracker = el.EyeLink(settings)

# Calibrate (optionally record samples during calibration)
tracker.calibrate(record_samples=True)

# Option A: Direct window access for custom drawing
tracker.window.fill((128, 128, 128))  # pygame example
# ... backend-specific drawing ...
tracker.flip()

# Option B: Helper methods for common patterns
tracker.show_message("Press SPACE to begin")
tracker.wait_for_key('space')

# Run your experiment
tracker.start_recording()
# ... show stimuli, collect data ...
tracker.stop_recording()

# Clean up (closes window and saves EDF automatically)
tracker.end_experiment()
```

### Advanced Configuration

All tracker parameters are configurable through the Settings class:

```python
settings = el.Settings(
    backend='pygame',
    n_cal_targets=13,                         # 13-point calibration for large displays
    calibration_area_proportion=(0.44, 0.415), # reduce calibration area for close viewing
    calibration_corner_scaling=0.8,            # pull corner targets inward
    sample_rate=1000,                          # 250, 500, 1000, or 2000 Hz
    illumination_power=3,                      # reduce IR power (1=100%, 2=75%, 3=50%)
    # ... 50+ configurable parameters
)
```

For commands not exposed through Settings, use direct tracker control:

```python
tracker.send_command("select_parser_configuration 0")
tracker.send_command("file_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS")
```

## Development

For development with different backends:

```bash
# PsychoPy backend
uv pip uninstall pyelink && uv pip install -e ".[psychopy]" && uv pip install --extra-index-url https://pypi.sr-support.com sr-research-pylink

# Pygame backend
uv pip uninstall pyelink && uv pip install -e ".[pygame]" && uv pip install --extra-index-url https://pypi.sr-support.com sr-research-pylink

# Pyglet backend
uv pip uninstall pyelink && uv pip install -e ".[pyglet]" && uv pip install --extra-index-url https://pypi.sr-support.com sr-research-pylink
```

## Attribution

This package is based on code originally developed by:

- **Marcus Nyström** (Lund University Humanities Lab, Lund, Sweden)
  - Email: marcus.nystrom@humlab.lu.se

- **pylinkwrapper** by Nick DiQuattro
  - Repository: https://github.com/ndiquattro/pylinkwrapper
  - Core EyeLink functionality and wrapper architecture


## Acknowledgments

This project has received funding from the European Union's Horizon Europe research and innovation funding program under grant agreement No 101072410, Eyes4ICU project.

<p align="center">
<img src="https://github.com/mh-salari/zarafe/raw/main/resources/Funded_by_EU_Eyes4ICU.png" alt="Funded by EU Eyes4ICU" width="500">
</p>
