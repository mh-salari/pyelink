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

**macOS:**
- PyAudio requires PortAudio. Install it first:
```bash
brew install portaudio
```

**Note:** You'll also need to install pylink separately from SR Research:
```bash
pip install --index-url=https://pypi.sr-support.com sr-research-pylink
```



## Quick Start

```python
import pyelink as el

# Configure tracker with backend
settings = el.Settings()
settings.BACKEND = 'pygame'  # or 'psychopy', 'pyglet'
settings.FULLSCREEN = True
settings.SCREEN_RES = [1920, 1080]

# Tracker creates and owns the window
tracker = el.EyeLink(settings)

# Calibrate (no parameters needed!)
tracker.calibrate()

# Option A: Direct window access for custom drawing
tracker.window.fill((128, 128, 128))
# ... backend-specific drawing ...
tracker.flip()

# Option B: Helper methods for common patterns
tracker.show_message("Press SPACE to begin")
tracker.wait_for_key('space')

# Run your experiment
tracker.start_recording()
# ... show stimuli, collect data ...
tracker.stop_recording()

# Clean up (closes window automatically)
tracker.end_experiment('./')
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



