"""Minimal example using PsychoPy backend.

This example demonstrates the basic usage of pyelink with PsychoPy.
"""

import time

import pyglet
from psychopy import visual

import pyelink as el

# Detect available monitors using pyglet
display = pyglet.canvas.get_display()
screens = display.get_screens()

print(f"\nDetected {len(screens)} monitor(s)")
for i, screen in enumerate(screens):
    print(f"  Screen {i}: {screen.width}x{screen.height}")
selected_screen = 0
print("Using primary monitor")

# Configure tracker - load from config file and customize
settings = el.Settings.load_from_file("examples/default_config.json")
settings.FILENAME = "test"
settings.SCREEN_RES = [screens[selected_screen].width, screens[selected_screen].height]
settings.CALIBRATION_AREA_PROPORTION = [0.75, 0.75]
settings.VALIDATION_AREA_PROPORTION = [0.75, 0.75]

print("\nConnecting to EyeLink...")
tracker = el.EyeLink(settings, record_raw_data=False)

# Now create PsychoPy window (after successful connection)
win = visual.Window(
    size=[screens[selected_screen].width, screens[selected_screen].height],
    fullscr=True,
    screen=selected_screen,
    units="pix",
    color=[0, 0, 0],
)

# Create calibration display
print("Creating calibration display...")
calibration = el.create_calibration(settings, tracker, win)

# Calibrate
print("Starting calibration...")
print("Press 'C' for calibration, 'V' for validation, Ctrl+Q or ESC to exit")
# Record eye data during calibration/validation (set to False to disable)
tracker.calibrate(calibration, record_samples=True)

print("Calibration complete!")
print("\nStarting data recording...")

# Start recording
tracker.start_recording()

# Countdown and record for 5 seconds
countdown_text = visual.TextStim(win, text="", pos=(0, 0), height=100, color=(1, 1, 1), font="Arial")
for i in range(5, 0, -1):
    print(f"Recording... {i}")
    countdown_text.text = str(i)
    countdown_text.draw()
    win.flip()
    time.sleep(1)

print("Recording complete!")

# Clean up
print("Closing...")
tracker.stop_recording()
tracker.end_experiment("./")  # Saves EDF file to current directory
win.close()
print("Done!")
