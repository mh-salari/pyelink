# PyELink

Multi-backend Python wrapper for SR Research EyeLink eye trackers.

## Installation

Choose ONE backend when installing:

```bash
# For Pygame users (recommended - works on all platforms)
pip install pyelink

# For PsychoPy users (Python < 3.12 only)
pip install pyelink[psychopy]

# For Pyglet users (pyglet 2.0+)
pip install pyelink[pyglet]
```

### ⚠️ Backend Compatibility Warning

**You CANNOT install both `psychopy` and `pyglet` backends together.**

**Why?** PsychoPy pins `pyglet==1.4.11` (from 2017) as a dependency, while the modern pyglet backend requires `pyglet>=2.0.0`. These versions are incompatible.

**Solution:** Choose ONE backend:
- **Pygame** (recommended): Works everywhere, no conflicts
- **PsychoPy**: Use if you need PsychoPy features, but cannot use pyglet 2.0+
- **Pyglet**: Use if you want modern pyglet (2.0+) but don't need PsychoPy

### Platform-Specific Notes

**Apple Silicon (M1/M2/M3/M4):**
- PsychoPy requires psychtoolbox, which is **not supported on Apple Silicon native Python**
- Audio playback issues with PsychoPy and Pyglet backends on Apple Silicon
- **Recommendation: Use Pygame backend on Apple Silicon**

**Note:** You'll also need to install pylink separately from SR Research:
```bash
pip install --index-url=https://pypi.sr-support.com sr-research-pylink
```



## Quick Start

```python
import pyelink as el
from psychopy import visual

# Create your experiment window
win = visual.Window(size=[1920, 1080], fullscr=True)

# Configure tracker
settings = el.Settings()
settings.SCREEN_RES = [1920, 1080]
tracker = el.EyeLink(settings)

# Create calibration (auto-detects backend from window type)
calibration = el.create_calibration(settings, tracker, win)

# Calibrate
tracker.calibrate(calibration)

# Run your experiment with the same window
# ... show stimuli, collect data ...

# Clean up
tracker.end_experiment('./')
win.close()
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



