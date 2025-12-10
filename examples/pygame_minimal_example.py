"""Minimal example using Pygame backend.

This example demonstrates the basic usage of pyelink with Pygame.
"""

import time

import pygame

import pyelink as el

# Detect available monitors
pygame.init()
num_displays = pygame.display.get_num_displays()
print(f"\nDetected {num_displays} monitor(s)")
display_info = pygame.display.Info()
for i in range(num_displays):
    # Pygame does not provide per-display resolution easily, so just print the primary
    if i == 0:
        print(f"  Display {i}: {display_info.current_w}x{display_info.current_h}")
    else:
        print(f"  Display {i}: (resolution info not available)")
selected_display = 0
print("Using primary monitor")

# Configure tracker - load from config file and customize
settings = el.Settings.load_from_file("examples/default_config.json")
settings.FILENAME = "test"
settings.SCREEN_RES = [display_info.current_w, display_info.current_h]
settings.CALIBRATION_AREA_PROPORTION = [0.75, 0.75]
settings.VALIDATION_AREA_PROPORTION = [0.75, 0.75]

print("\nConnecting to EyeLink...")
tracker = el.EyeLink(settings, record_raw_data=False)

# Now create Pygame window (after successful connection)
screen = pygame.display.set_mode(
    (display_info.current_w, display_info.current_h), pygame.FULLSCREEN, display=selected_display
)
pygame.display.set_caption("EyeLink Pygame Example")

# Create calibration display
print("Creating calibration display...")
calibration = el.create_calibration(settings, tracker, screen)

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
font = pygame.font.Font(None, 200)
for i in range(5, 0, -1):
    print(f"Recording... {i}")
    screen.fill((128, 128, 128))  # Clear screen with gray background
    text = font.render(str(i), True, (255, 255, 255))  # White text
    text_rect = text.get_rect(center=(640, 512))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(1)

tracker.stop_recording()
print("Recording complete!")

# Clean up
print("Closing...")
tracker.end_experiment("./")  # Stops recording, saves EDF file, disconnects
pygame.quit()
print("Done!")
