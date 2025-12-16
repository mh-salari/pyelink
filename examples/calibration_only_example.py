"""Minimal calibration-only example.

This example records data ONLY during calibration and validation.
No trial recording is performed.
"""

import pyelink as el

# Configure tracker - tracker creates and owns the window
settings = el.Settings(
    backend="pyglet",  # Change to "psychopy" or "pyglet" as needed
    fullscreen=False,
    display_index=0,  # Primary monitor
    filename="cal_val",
    filepath="./examples/data/",  # Directory where EDF file will be saved
    enable_long_filenames=True,  # Default - allows up to 64 character filenames
    # host_ip="dummy",  # Use dummy mode for testing without EyeLink
)

print("Connecting to EyeLink and creating window...")
# record_raw_data=True enables raw pupil/CR data capture
tracker = el.EyeLink(settings, record_raw_data=True)

# Calibrate with sample recording enabled
# This will record GAZE samples (gaze x,y and pupil area) during calibration/validation
print("Starting calibration with sample recording...")
print("Press 'C' for calibration, 'V' for validation, ESC to exit")
tracker.calibrate(record_samples=True)
print("Calibration complete!")

# Clean up and save EDF file (closes window automatically)
print("Saving EDF file...")
tracker.end_experiment()
