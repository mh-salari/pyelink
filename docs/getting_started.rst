Getting Started
===============

Installation
------------

**You must specify a backend when installing PyeLink.** A simple ``pip install pyelink``
will not work because PyeLink requires one of three mutually exclusive display backends.

Choose **one** backend:

.. code-block:: bash

   # For Pygame users
   pip install pyelink[pygame]

   # For PsychoPy users (Python < 3.12 only)
   pip install pyelink[psychopy]

   # For Pyglet users (pyglet 2.0+)
   pip install pyelink[pyglet]

Prerequisites
^^^^^^^^^^^^^

You also need to install the **EyeLink Developers Kit** (native C libraries) from
`SR Research <https://www.sr-research.com/support/thread-13.html>`_.

Then install pylink separately from SR Research:

.. code-block:: bash

   uv pip install --extra-index-url https://pypi.sr-support.com sr-research-pylink

Backend Compatibility
^^^^^^^^^^^^^^^^^^^^^

.. warning::

   You **cannot** install both ``psychopy`` and ``pyglet`` backends together.
   PsychoPy pins ``pyglet==1.4.11`` (from 2017), while the modern pyglet backend
   requires ``pyglet>=2.0.0``.

- **Pygame** (recommended): Works everywhere, no conflicts
- **PsychoPy**: Use if you need PsychoPy features (Python 3.9--3.11 only)
- **Pyglet**: Use for modern pyglet (2.0+), but not with PsychoPy

Quick Start
-----------

.. code-block:: python

   import pyelink as el

   # Configure tracker with backend and physical screen measurements
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

   # Calibrate
   tracker.calibrate()

   # Option A: Direct window access for custom drawing
   tracker.window.fill((128, 128, 128))  # pygame example
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

.. important::

   The physical screen measurements (``screen_width``, ``screen_height``,
   ``screen_distance_top_bottom``) are critical for accurate gaze data.
   Measure your actual display area (not including the bezel) with a ruler.

Advanced Configuration
----------------------

All tracker parameters are configurable through the
:class:`~pyelink.settings.Settings` class. For example, to configure
a reduced calibration area for close eye-to-screen setups:

.. code-block:: python

   settings = el.Settings(
       backend='pygame',
       n_cal_targets=9,                           # 3, 5, 9, or 13 points
       calibration_area_proportion=(0.44, 0.415),  # reduce area for close viewing
       calibration_corner_scaling=0.8,             # pull corner targets inward
       sample_rate=1000,                           # 250, 500, 1000, or 2000 Hz
       illumination_power=3,                       # reduce IR (1=100%, 2=75%, 3=50%)
       pupil_tracking_mode='CENTROID',             # or 'ELLIPSE'
       heuristic_filter=(1, 1),                    # (link, file) filter levels 0-2
   )

See :doc:`/default_settings` for all 50+ configurable parameters with their defaults.

Direct Tracker Control
^^^^^^^^^^^^^^^^^^^^^^

For commands not exposed through Settings, you can send any EyeLink command
directly. This uses the same syntax as the INI files on the EyeLink Host PC:

.. code-block:: python

   # Send any EyeLink command
   tracker.send_command("select_parser_configuration 0")
   tracker.send_command("screen_pixel_coords = 0 0 1919 1079")

   # Send timestamped messages recorded in the EDF file
   tracker.send_message("TRIALID 1")
   tracker.send_message("STIMULUS_ONSET image.png")

   # Access the underlying pylink.EyeLink object for full low-level control
   tracker.tracker.getNewestSample()

See :doc:`/direct_control` for details and :doc:`/eyelink_commands_reference` for
a full list of all available EyeLink commands.

Usage Patterns
--------------

PyeLink supports two usage patterns:

**Option A -- Direct backend access:**

.. code-block:: python

   tracker.window.fill((128, 128, 128))  # pygame.Surface
   tracker.window.blit(...)
   tracker.flip()

**Option B -- Backend-agnostic helpers:**

.. code-block:: python

   tracker.show_message("Ready?")
   tracker.wait_for_key('space')
   tracker.fill((128, 128, 128))
   tracker.run_trial(draw_func, trial_data, duration=5.0)
