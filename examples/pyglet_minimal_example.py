"""Minimal example using Pyglet backend.

This example demonstrates the basic usage of pyelink with Pyglet.
"""

import time

import pyglet

import pyelink as el

# Detect available monitors (pyglet 2.0+ API)
display = pyglet.display.get_display()
screens = display.get_screens()

print(f"\nDetected {len(screens)} monitor(s)")
for i, screen in enumerate(screens):
    print(f"  Screen {i}: {screen.width}x{screen.height}")
selected_screen = screens[0]
print("Using primary monitor")

# Configure tracker - load from config file and customize
settings = el.Settings.load_from_file("examples/default_config.json")
settings.FILENAME = "test"
settings.SCREEN_RES = [selected_screen.width, selected_screen.height]
settings.CALIBRATION_AREA_PROPORTION = [0.75, 0.75]
settings.VALIDATION_AREA_PROPORTION = [0.75, 0.75]

print("\nConnecting to EyeLink...")
tracker = el.EyeLink(settings, record_raw_data=False)

# Now create Pyglet window (after successful connection)
window = pyglet.window.Window(
    width=selected_screen.width,
    height=selected_screen.height,
    fullscreen=True,
    screen=selected_screen,
    caption="EyeLink Pyglet Example",
)

# Create calibration display
print("Creating calibration display...")
calibration = el.create_calibration(settings, tracker, window)

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
label = pyglet.text.Label(
    "",
    font_name="Arial",
    font_size=200,
    x=window.width // 2,
    y=window.height // 2,
    anchor_x="center",
    anchor_y="center",
    color=(255, 255, 255, 255),
)

for i in range(5, 0, -1):
    print(f"Recording... {i}")
    label.text = str(i)
    window.clear()
    label.draw()
    window.flip()
    time.sleep(1)

print("Recording complete!")

# Clean up
print("Closing...")
tracker.stop_recording()
tracker.end_experiment("./")  # Saves EDF file to current directory
window.close()
print("Done!")
