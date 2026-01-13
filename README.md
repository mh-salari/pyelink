# PyeLink

Python wrapper for SR Research EyeLink eye trackers.

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

You'll also need to install pylink separately from SR Research:
```bash
pip install --index-url=https://pypi.sr-support.com sr-research-pylink
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

## Quick Start

```python
import pyelink as el

# Configure tracker with backend
settings = el.Settings(
    backend='pygame',  # or 'psychopy', 'pyglet'
    fullscreen=True,
    screen_width=1920,
    screen_height=1080,
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

## Development

For development with different backends:

```bash
# PsychoPy backend
uv pip uninstall pyelink && uv pip install -e ".[psychopy]" && uv pip install --index-url=https://pypi.sr-support.com sr-research-pylink

# Pygame backend
uv pip uninstall pyelink && uv pip install -e ".[pygame]" && uv pip install --index-url=https://pypi.sr-support.com sr-research-pylink

# Pyglet backend
uv pip uninstall pyelink && uv pip install -e ".[pyglet]" && uv pip install --index-url=https://pypi.sr-support.com sr-research-pylink
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
