"""Minimal example using Pygame backend.

This example demonstrates the basic usage of pyelink with Pygame.
Shows both Option A (direct window access) and Option B (helper methods).
"""

import pygame

import pyelink as el

# Configure tracker - tracker creates and owns the window
settings = el.Settings(
    backend="pygame",
    fullscreen=False,
    display_index=0,  # Primary monitor
    filename="pygame",
    filepath="./examples/data/",  # Directory where EDF file will be saved
    enable_long_filenames=True,  # Default - allows up to 64 character filenames
    # host_ip="dummy",  # Use dummy mode for testing without EyeLink
)

print("Connecting to EyeLink and creating window...")
tracker = el.EyeLink(settings, record_raw_data=True)

# Calibrate (window created automatically by tracker)
print("Starting calibration...")
print("Press 'C' for calibration, 'V' for validation, ESC to exit")
tracker.calibrate(record_samples=True)
print("Calibration complete!")

# Option B: Show instruction message using helper method
tracker.show_message("Recording will begin in 3 seconds...", duration=3.0)

# Start recording
print("Starting data recording...")
tracker.start_recording()

# Option A: Direct window access for custom drawing
print("Using Option A: Direct pygame window access")
font = pygame.font.Font(None, 200)
for i in range(5, 0, -1):
    print(f"Recording... {i}")
    # Direct access to pygame.Surface
    tracker.window.fill((128, 128, 128))
    text = font.render(str(i), True, (255, 255, 255))
    text_rect = text.get_rect(center=(tracker.window.get_width() // 2, tracker.window.get_height() // 2))
    tracker.window.blit(text, text_rect)
    tracker.flip()
    tracker.wait(1)  # Use tracker.wait() instead of time.sleep() to keep event loop active

tracker.stop_recording()
print("Recording complete!")

# Option B: Show completion message using helper method
tracker.show_message("Experiment complete! Press SPACE to exit")
tracker.wait_for_key("space")

# Clean up (closes window automatically)
print("Closing...")
tracker.end_experiment()
print("Done!")
