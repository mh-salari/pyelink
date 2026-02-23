Direct Tracker Control
======================

PyeLink wraps common EyeLink operations through its Python API, but you always
have full access to send **any** command directly to the tracker hardware.
This is essential for advanced configurations or commands not yet exposed through
the :class:`~pyelink.settings.Settings` class.

Sending Commands
----------------

.. automethod:: pyelink.core.EyeLink.send_command
   :no-index:

Sending Messages
----------------

.. automethod:: pyelink.core.EyeLink.send_message
   :no-index:

Direct pylink Access
--------------------

For full low-level control, the underlying ``pylink.EyeLink`` object is available
as the ``tracker`` attribute. This gives access to every method in SR Research's
``pylink`` library.

.. code-block:: python

   # Access the underlying pylink.EyeLink object
   el = tracker.tracker  # pylink.EyeLink instance

   # Use any pylink method directly
   el.sendCommand("calibration_type = HV9")
   el.getNewestSample()
   el.isRecording()
   el.getTrackerVersion()

   # Read tracker responses
   el.readRequest("sample_rate")
   result = el.readReply()

See Also
--------

- :doc:`/eyelink_commands_reference` -- Full list of all EyeLink commands
- :doc:`/default_settings` -- Default values for settings exposed through the Python API
