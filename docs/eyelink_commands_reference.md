# EyeLink Commands Reference

## About This Document

This reference document is a comprehensive compilation of all EyeLink commands and configuration settings extracted from the INI files found on the EyeLink Host PC. These INI files contain the low-level commands used to configure and control EyeLink eye tracking hardware.

### Source

The commands documented here are sourced from configuration files located in the executable directory of the EyeLink Host PC (`exe\` dir). These INI files define the many of command set available for EyeLink tracker configuration and control.

### Implementation Status

PyeLink implements a subset of these commands through its Python API, with gradual expansion of coverage over time. Some commands are exposed directly through the [Settings](../src/pyelink/core.py) class, while others can be accessed via the underlying `pylink` library interface.

### Statistics

- **Configuration Files**: 21 INI files
- **Total Commands**: 290+ commands and settings
- **Categories**: Calibration, display configuration, data recording, analog output, parser settings, physical setup, and more

### How to Use This Reference

Each command entry includes:
- **Syntax**: The command format with parameter placeholders
- **Description**: What the command does and parameter meanings
- **Example**: Sample usage with typical values

For commands not yet wrapped in PyeLink's high-level API, you can use the tracker's underlying `pylink.EyeLink` connection directly via `tracker.tracker` to send raw commands.

---

### Configuration Files
1. [x] ANALOG.INI
2. [x] BUTTONS.INI
3. [x] CALIBR.INI
4. [x] CMV_CFG.INI
5. [x] COMMANDS.INI
6. [x] DATA.INI
7. [x] DEFAULTS.INI
8. [x] DSCFG.INI
9. [x] KEYS.INI
10. [x] MPRIMATE.INI
11. [x] PARSER.INI
12. [x] PHYSICAL.INI
13. [x] RAW.INI
14. [x] RBTABLEC.INI
15. [x] REMPARSE.INI
16. [x] RTABLEC.INI
17. [x] RTABLER.INI
18. [x] TOCFG.INI
19. [x] TSCFG.INI
20. [x] VIDOVL.INI
21. [x] elcl_config_db.txt

---

## Commands and Settings

#### `remote_camera_position`
**Syntax**: `remote_camera_position = <rh> <rv> <dx> <dy> <dz>`
**Description**: Sets the position and angles for remote camera mounting (Desktop Remote Recording configuration). <rh>: rotation of camera from screen (clockwise from top), i.e. how much the right edge of the camera is closer than left edge of camera. <rv>: tilt of camera from screen (top toward screen). <dx>: bottom-center of display in cam coords. <dy>: bottom-center of display in cam coords. <dz>: bottom-center of display in cam coords.
**Example**: `remote_camera_position = -10 17 80 60 -90`

#### `screen_phys_coords`
**Syntax**: `screen_phys_coords = <left>, <top>, <right>, <bottom>`
**Description**: Measure the distance of the visible part of the display screen edge relative to the center of the screen (measured in millimetres). <left>, <top>, <right>, <bottom>: position of display area corners relative to display center.
**Example**: `screen_phys_coords = -265, 150, 265, -150`

#### `screen_pixel_coords`
**Syntax**: `screen_pixel_coords = <left> <top> <right> <bottom>`
**Description**: Sets the gaze-position coordinate system, which is used for all calibration target locations and drawing commands. Usually set to correspond to the pixel mapping of the subject display. Issue the calibration_type command after changing this to recompute fixation target positions. You should also write a DISPLAY_COORDS message to the start of the EDF file to record the display resolution in EDF file. <left>: X coordinate of left of display area, <top>: Y coordinate of top of display area, <right>: X coordinate of right of display area, <bottom>: Y coordinate of bottom of display area.
**Example**: `screen_pixel_coords = 0, 0, 1023, 767`

#### `screen_distance`
**Syntax**: `screen_distance = <mm to center>` or `screen_distance = <mm to top> <mm to bottom>`
**Description**: Used for visual angle and velocity calculations. Providing <mm to top> <mm to bottom> parameters will give better estimates than <mm to center>. <mm to center>: distance from display center to subject in millimetres. <mm to top>: distance from display top to subject in millimetres. <mm to bottom>: distance from display bottom to subject in millimetres.
**Example**: `screen_distance = 930 960`

#### `analog_strobe_delay`
**Syntax**: `analog_strobe_delay = <delay in microseconds>`
**Description**: Sets delay after analog data change before strobe signal. Delay effectively rounds up to multiples of 500 μsec except for durations <50 μsec which are accurate. Suggested value is 400 μsec.
**Example**: `analog_strobe_delay = 400`

#### `analog_strobe_time`
**Syntax**: `analog_strobe_time = <strobe duration in microseconds>`
**Description**: Duration of strobe pulse to indicate new sample data is valid. Set to 0 to toggle for each sample. Suggested <1000 μsec for interrupt driven or hardware acquisition.
**Example**: `analog_strobe_time = 1000`

#### `analog_strobe_polarity`
**Syntax**: `analog_strobe_polarity = <polarity switch>`
**Description**: Sets strobe signal polarity. 1 for active-high, 0 for active-low.
**Example**: `analog_strobe_polarity = 1`

#### `analog_strobe_line`
**Syntax**: `analog_strobe_line = <digital line>`
**Description**: Digital line for strobe signal. Default is D7 (0x80).
**Example**: `analog_strobe_line = 0x80`

#### `analog_out_data_type`
**Syntax**: `analog_out_data_type = <Data type>`
**Description**: Select type of data for analog output. OFF turns off analog output, PUPIL is raw pupil x,y, HREF is headref-calibrated x,y, GAZE is screen gaze x,y. Overridden by setup menu and lastrun.ini.
**Example**: `analog_out_data_type = GAZE`

#### `analog_dac_range`
**Syntax**: `analog_dac_range = <min voltage>, <max voltage>`
**Description**: Total DAC voltage range (low, high) in volts. Range: -10V to +10V.
**Example**: `analog_dac_range = -5, +5`

#### `analog_no_pupil_value`
**Syntax**: `analog_no_pupil_value = <DAC data when pupil missing>`
**Description**: X, Y output value when pupil is missing, as fraction of DAC range (0.0 = min voltage, 1.0 = max voltage).
**Example**: `analog_no_pupil_value = 0.0`

#### `analog_x_range`
**Syntax**: `analog_x_range = <L, R or blank>, <data type>, <lower end>, <higher end>`
**Description**: Sets conversion of data to DAC voltage for X coordinate. Min and max are percentage of total data range that corresponds to DAC range. (0.0, 1.0) uses whole range, (0.1, 0.9) magnifies center 80%, (-0.2, 1.2) allows 20% over/under range.
**Example**:
```
analog_x_range = PUPIL, 0.1, 0.9
analog_x_range = HREF, 0.0, 1.0
analog_x_range = GAZE, -0.2, 1.2
```

#### `analog_y_range`
**Syntax**: `analog_y_range = <L, R or blank>, <data type>, <lower end>, <higher end>`
**Description**: Sets conversion of data to DAC voltage for Y coordinate. Same range specifications as analog_x_range.
**Example**:
```
analog_y_range = PUPIL, 0.1, 0.9
analog_y_range = HREF, 0.0, 1.0
analog_y_range = GAZE, -0.2, 1.2
```

#### `analog_force_4channel`
**Syntax**: `analog_force_4channel = <YES or NO>`
**Description**: Forces use of only 3 or 4 outputs when few analog channels can be used or pupil size is not needed.
**Example**: `analog_force_4channel = NO`

#### `analog_binocular_mapping`
**Syntax**: `analog_binocular_mapping = <ON or OFF>`
**Description**: TYPE: READABLE, WRITABLE, MENU, LASTRUN.INI. Sets whether monocular or binocular analog output configuration is used.
**Example**: `analog_binocular_mapping = NO`

#### `analog_p_maximum`
**Syntax**: `analog_p_maximum = <pupil size type>, <maximum expected value>`
**Description**: Sets range of data to be scaled to pupil size analog output (minimum is 0). Type can be: AREA (default 10000), DIAMETER (default 113), WIDTH (default 160), HEIGHT (default 80).
**Example**: `analog_p_maximum = AREA, 10000`

#### `button_debounce_time`
**Syntax**: `button_debounce_time = <delay>`
**Description**: Sets button debounce time. Button responds immediately to first change so delay does not add delay to RT. Any change following this is ignored for number of milliseconds defined.
**Example**: `button_debounce_time = 30`

#### `create_button`
**Syntax**: `create_button <number> <port> <bitmask> <invert?>`
**Description**: Defines a button to a bit in a hardware port. Values 1-8 are for subject i/o (logged as events), value 0 deletes, 9-31 are available for remote control or functions. Up to 32 buttons may be created. Parameters: button number (1 to 8), address of hardware port, 8-bit mask ANDed with port to test button line, inverted (1 if active-low, 0 if active-high).
**Example**: `create_button 1 9 0x20 1`

#### `create_key_button`
**Syntax**: `create_key_button <button number> <key ID>`
**Description**: Creates a "button" that can be simulated from a tracker key press. <button number> can be 1..32, but only 1..8 are reported. Others could be used to trigger button events. See "key_function" for a definition of <key_id>.
**Example**: `create_key_button 15 shift+g`

#### `delete_all_key_buttons`
**Syntax**: `delete_all_key_buttons`
**Description**: TYPE: Command. Send this command to quickly delete all key buttons.

#### `delete_all_key_functions`
**Syntax**: `delete_all_key_functions`
**Description**: TYPE: Command. Send this command to quickly delete all key functions.

#### `hide_abort_trial`
**Syntax**: `hide_abort_trial = <YES or NO>`
**Description**: Sets whether the "Abort Trial" button in the Record screen should be hidden.
**Example**: `hide_abort_trial NO`

#### `key_function`
**Syntax**: `key_function <keyspec> <command>`
**Description**: Keys may be used to generate commands. Give a key description string followed by "reserve" if you wish lock out other use of the key. Follow this by a quoted command string, or none to release key. <keyspec>: key name and modifiers. <command>: command string to execute when key pressed.
**Example**: `key_function ctrl+alt+q "exit_program"`

#### `lock_record_exit`
**Syntax**: `lock_record_exit = <switch>`
**Description**: Prevents "ESC" key from exiting record mode. "CTRL-ALT-A" remains active.
**Example**: `lock_record_exit = NO`

#### `user_record_key_item`
**Syntax**: `user_record_key_item = <button_text> <description> <key_spec> [<optional command>]`
**Description**: Add any one key item to Output mode menu bar.
**Example**: `user_record_key_item = " CTRL-ALT-A ", "Abort Trial  ", ctrl+alt+a, "display_user_menu 1"`

#### `write_ioport`
**Syntax**: `write_ioport <ioport> <data>`
**Description**: Writes data to I/O port. Useful to configure I/O cards.
**Example**: `write_ioport 8 0xE0`

#### `button_function`
**Syntax**: `button_function <button_number> [<press_command>] [<release_command>]`
**Description**: Buttons may be assigned to generate commands. Give the button number (1-31) then the command string in quotes. The first command is executed when the button is pressed. The optional second command is executed when button is released. Giving NO strings deletes the button function.
**Example**: `button_function 5 "start_recording" "set_idle_mode"`

#### `input_data_ports`
**Syntax**: `input_data_ports = <Port Address>`
**Description**: Up to 16 i/o lines can be reported. These consist of 2 ports, (high and low byte). Port: 2 or 3 are digital input card ports (2 = port A, 3 = port B). Other values are address of hardware I/O port. If only 1 entry, 8-bit port (high byte).
**Example**: `input_data_ports = 9`

#### `input_data_masks`
**Syntax**: `input_data_masks = <Mask Hex Value>`
**Description**: Port bits can be masked so changes don't trigger events.
**Example**: `input_data_masks = 0xFF`

#### `last_button_pressed`
**Syntax**: `last_button_pressed = <optional value assignment>`
**Description**: TYPE: Read/Write system variable. Contains the number of the last button pressed. This was intended for uses where a program would not be able to monitor the eye tracker for long periods of time. It could set this to 0, then read it later to see if it has changed.
**Example**: `last_button_pressed = 0`

#### `clear_button_list`
**Syntax**: `clear_button_list`
**Description**: WRITE. Clears the button history list.
**Example**: `clear_button_list`

#### `last_button_list`
**Syntax**: `last_button_list`
**Description**: READ, WRITE. Reads the list of buttons pressed since the list was last cleared. The button list is cleared when this command is issued (but not when read). When read, returns a list of all buttons pressed. The list consists of "<button_number> <button_time>" pairs.
**Example**: `last_button_list`

#### `read_ioport`
**Syntax**: `read_ioport <ioport>`
**Description**: Performs a dummy read of I/O port.
**Example**: `read_ioport 0x379`

#### `button_status_display`
**Syntax**: `button_status_display = <switch>`
**Description**: Enables button feedback display on output and Record mode screens. DEFAULT: ON.
**Example**: `button_status_display = ON`

#### `calibration_type`
**Syntax**: `calibration_type = <type>`
**Description**: What type of equation to use as a fit. H3 = horizontal-only 3-point quadratic, HV3 or 3 = 3-point bilinear, HV5 or 5 = 5-point bi-quadratic, HV9 or 9 = 9-point bi-quadratic with corner correction, HV13 = 13-point bi-cubic calibration. HV9 should NOT be used for remote mode. HV13 works best with larger angular displays (> +/-20 degrees). HV13 should NOT be used when accurate data is needed from corners of calibrated area.
**Example**: `calibration_type = HV9`

#### `x_gaze_constraint`
**Syntax**: `x_gaze_constraint = <position>`
**Description**: For H3 calibration, it is useful to be able to set the vertical position of generated targets, and to constrain the vertical position of the gaze to a vertical position. Use position, OFF for none, or AUTO for last calibration/validation/drift corr. in 1 D modes.
**Example**: `x_gaze_constraint = AUTO`

#### `y_gaze_constraint`
**Syntax**: `y_gaze_constraint = <position>`
**Description**: For H3 calibration, it is useful to be able to set the vertical position of generated targets, and to constrain the vertical position of the gaze to a vertical position. Use position, OFF for none, or AUTO for last calibration/validation/drift corr. in 1 D modes.
**Example**: `y_gaze_constraint = AUTO`

#### `calibration_bicubic_weights`
**Syntax**: `calibration_bicubic_weights = <list of weights>`
**Description**: HV13 weight for points in bi-cubic ("HV13", 13 pt) cal. Point order:
```
    6    2    7
      10   11
    4    1    5
      12   13
    8    3    9
```
Weights: ratio between weights determines effect, values 1 to 10 suggested. 10 2 2 2 2 1 1 1 1 4 4 4 4 weight pattern minimizes central error, corner error is high.
**Example**: `calibration_bicubic_weights 10 2 2 2 2 1 1 1 1 4 4 4 4`

#### `calibration_bicubic_correction`
**Syntax**: `calibration_bicubic_correction = <ON or OFF>`
**Description**: HV13 calibration type can perform a secondary fit of the data to try and improve accuracy. Should be OFF for head free setup. Unknown at this time if this actually improves calibration for head fixed setup. Default is OFF.
**Example**: `calibration_bicubic_correction OFF`

#### `generate_default_targets`
**Syntax**: `generate_default_targets = <YES or NO>`
**Description**: When calibration_type is changed, new target configurations may be required. This enables generation of the default targets and sequence.
**Example**: `generate_default_targets = YES`

#### `horizontal_target_y`
**Syntax**: `horizontal_target_y = <position>`
**Description**: This sets the Y of automatically-generated targets for the H3 cal mode.
**Example**: `horizontal_target_y = 200`

#### `calibration_targets`
**Syntax**: `calibration_targets = <list of x,y coordinate pairs>`
**Description**: X,Y pairs of target point positions. These are in display coordinates for the 9-SAMPLE ALGORITHM. POINTS MUST BE ORDERED ON SCREEN:
```
5  1  6
3  0  4
7  2  8
```
Ordering for points in bi-cubic ("HV13", 13 pt) cal. Point order:
```
    6    2    7
      10   11
    4    1    5
      12   13
    8    3    9
```
**Example**: `calibration_targets = 320,240  320,40  320,440  40,240  600,240  40,40  600,40, 40,440  600,440`

#### `validation_targets`
**Syntax**: `validation_targets = <list of x,y coordinate pairs>`
**Description**: X,Y pairs of validation target positions. These are in display screen coordinates.
**Example**: `validation_targets = 320,240  320,40  320,440  40,240  600,240  40,40  600,40, 40,440  600,440`

#### `calibration_area_proportion`
**Syntax**: `calibration_area_proportion = <x, y display proportion>`
**Description**: For auto generated calibration point positions, these set the part of the width or height of the display to be bounded by targets. Each may have a single proportion or a horizontal followed by a vertical proportion. Default values for both cal and val is 0.88, 0.83. NOTE: setting for calibration also sets validation.
**Example**: `calibration_area_proportion 0.88 0.83`

#### `validation_area_proportion`
**Syntax**: `validation_area_proportion = <x, y display proportion>`
**Description**: For auto generated calibration point positions, these set the part of the width or height of the display to be bounded by targets. Each may have a single proportion or a horizontal followed by a vertical proportion. Default values for both cal and val is 0.88, 0.83. NOTE: setting for calibration also sets validation.
**Example**: `validation_area_proportion  0.88 0.83`

#### `calibration_corner_scaling`
**Syntax**: `calibration_corner_scaling = <scaling factor>`
**Description**: For auto generated validation point positions, a scaling factor for distance of corner targets from the display center. Default is 1.0, but can be 0.75 to 0.9 to pull in corners (to limit gaze excursion or to limit validation to the useful part of the display). NOTE: setting for calibration also sets validation.
**Example**: `calibration_corner_scaling 1.0`

#### `validation_corner_scaling`
**Syntax**: `validation_corner_scaling = <scaling factor>`
**Description**: For auto generated validation point positions, a scaling factor for distance of corner targets from the display center. Default is 1.0, but can be 0.75 to 0.9 to pull in corners (to limit gaze excursion or to limit validation to the useful part of the display). NOTE: setting for calibration also sets validation.
**Example**: `validation_corner_scaling 0.88`

#### `randomize_calibration_order`
**Syntax**: `randomize_calibration_order = <YES or NO>`
**Description**: Switches on/off randomized target sequencing. For HV5, HV9 and HV13, the first sequence entry is not randomized (i.e., always starts at the center of the screen).
**Example**: `randomize_calibration_order = YES`

#### `randomize_validation_order`
**Syntax**: `randomize_validation_order = <YES or NO>`
**Description**: Switches on/off randomized target sequencing during validation. For HV5, HV9 and HV13, the first sequence entry is not randomized (i.e., always starts at the center of the screen).
**Example**: `randomize_validation_order = YES`

#### `cal_repeat_first_target`
**Syntax**: `cal_repeat_first_target = <YES or NO>`
**Description**: Sets whether the first point of the calibration should be repeated.
**Example**: `cal_repeat_first_target = YES`

#### `val_repeat_first_target`
**Syntax**: `val_repeat_first_target = <YES or NO>`
**Description**: Sets whether the first point of the validation should be repeated.
**Example**: `val_repeat_first_target = YES`

#### `auto_calibration_messages`
**Syntax**: `auto_calibration_messages = <YES or NO>`
**Description**: Should the calibration messages be printed in the EDF file?
**Example**: `auto_calibration_messages = YES`

#### `calibration_samples`
**Syntax**: `calibration_samples = <count>`
**Description**: Calibration point presentation is controlled from a list of point orders, drawn from an array of X,Y point positions. This allows repeated points to be averaged.
**Example**: `calibration_samples = 10`

#### `calibration_average`
**Syntax**: `calibration_average = <switch>`
**Description**: For the same calibration target position, multiple sampling can be made. Set this command to YES to average the repeated points, and NO to replace repeated points.
**Example**: `calibration_average = NO`

#### `calibration_sequence`
**Syntax**: `calibration_sequence = <list of target numbers>`
**Description**: Sequence of points to present (count = calibration_samples).
**Example**: `calibration_sequence = 0,1,2,3,4,5,6,7,8,0`

#### `validation_samples`
**Syntax**: `validation_samples = <count>`
**Description**: Number of targets to present for validation.
**Example**: `validation_samples = 9`

#### `validation_sequence`
**Syntax**: `validation_sequence = <list of target numbers>`
**Description**: Sequence of points to present (count = calibration_samples).
**Example**: `validation_sequence = 0,1,2,3,4,5,6,7,8,0`

#### `validation_weights`
**Syntax**: `validation_weights = <list of weights>`
**Description**: Weights to assign points for weighted error, offset.
**Example**: `validation_weights = 4,2,2,2,2,1,1,1,1`

#### `validation_online_fixup`
**Syntax**: `validation_online_fixup = <value>`
**Description**: Controls if validation shows drift correction. If "AUTO", will only display correction in pupil-only mode. Values: YES, NO, AUTO.
**Example**: `validation_online_fixup  = AUTO`

#### `validation_correct_drift`
**Syntax**: `validation_correct_drift = <value>`
**Description**: Sets whether drift is corrected after validation. If "AUTO", will only drift correct in pupil-only mode. Values: YES, NO, AUTO.
**Example**: `validation_correct_drift = AUTO`

#### `validation_resample_worst`
**Syntax**: `validation_resample_worst = <number of points>`
**Description**: Number of points to resample after validation.
**Example**: `validation_resample_worst = 2`

#### `validation_worst_error`
**Syntax**: `validation_worst_error = <degrees>`
**Description**: Error required for resampling.
**Example**: `validation_worst_error = 1.0`

#### `calibration_collection_interval`
**Syntax**: `calibration_collection_interval = <time in msec>`
**Description**: Time over which to collect data to compute fixation for calibrate/validate/dc.
**Example**: `calibration_collection_interval = 100`

#### `manual_collection_minimum_fixation`
**Syntax**: `manual_collection_minimum_fixation = <time in msec>`
**Description**: Target fixation duration in msec.
**Example**: `manual_collection_minimum_fixation = 300`

#### `manual_collection_fixation_lookback`
**Syntax**: `manual_collection_fixation_lookback = <time in msec>`
**Description**: Time fixation may have ended previous to manual collection.
**Example**: `manual_collection_fixation_lookback = 200`

#### `enable_automatic_calibration`
**Syntax**: `enable_automatic_calibration = <switch>`
**Description**: Enables automatic sequencing of calibration targets. NO forces manual or remote collection.
**Example**: `enable_automatic_calibration = YES`

#### `autocal_minimum_saccade`
**Syntax**: `autocal_minimum_saccade = <degrees>`
**Description**: Minimum saccade amplitude in degrees of visual angle before automatic accepting a fixation during calibration.
**Example**: `autocal_minimum_saccade = 2.5`

#### `autocal_saccade_fraction`
**Syntax**: `autocal_saccade_fraction = <fraction> [<min angle>]`
**Description**: Optionally scales auto-cal minimum saccade angle to be a fraction of the distance between the old and new targets. Fraction = 0 to disable. Otherwise, scales proportion of angle between the targets the saccade must cover (0.5 recommended). Min angle = The smallest angle permitted for the threshold (optional). This should be high enough to prevent triggering from blinks and noise.
**Example**: `autocal_saccade_fraction = 0  3`

#### `autocal_minimum_fixation`
**Syntax**: `autocal_minimum_fixation = <time in msec>`
**Description**: Target fixation duration in msec also controls subjective speed.
**Example**: `autocal_minimum_fixation = 500`

#### `automatic_calibration_pacing`
**Syntax**: `automatic_calibration_pacing = <time delay in msec>`
**Description**: Minimum time between target sequencing in auto sequencing.
**Example**: `automatic_calibration_pacing = 1000`

#### `validation_maximum_deviation`
**Syntax**: `validation_maximum_deviation = <degrees>`
**Description**: Maximum fixation distance from target that is automatically accepted in validation.
**Example**: `validation_maximum_deviation = 7.0`

#### `drift_correction_rpt_error`
**Syntax**: `drift_correction_rpt_error = <degrees>`
**Description**: Maximum degrees of error for the drift correction should be repeated.
**Example**: `drift_correction_rpt_error = 2.0`

#### `drift_correction_rpt_beep`
**Syntax**: `drift_correction_rpt_beep = <YES or NO>`
**Description**: Tracker will flash and repeat drift correction if the error is greater than a rpt_error. This also makes the tracker beep.
**Example**: `drift_correction_rpt_beep = YES`

#### `default_eye_mapping`
**Syntax**: `default_eye_mapping = <coefficients>`
**Description**: If possible, a .CAL file saved earlier is used. If not, these values are used to create a default map eye to head-related unit (fl=15000). X = a+bx, Y = c+dy. Give a, b, c ,d.
**Example**: `default_eye_mapping = -15360, 80, -12800, 160`

#### `online_dcorr_collection_time`
**Syntax**: `online_dcorr_collection_time = <min time> <max time>`
**Description**: First number sets minimum time to aggregate, second number sets maximum time to aggregate. If minimum time is not available from current fixation, data aggregated from the end of the previous fixation is checked.
**Example**: `online_dcorr_collection_time = 100, 300`

#### `online_dcorr_max_lookback`
**Syntax**: `online_dcorr_max_lookback = <max look back>`
**Description**: Maximum time from end of previous fixation to the trigger to allow use of the previous fixation data. This should be greater than the minimum aggregation time plus the longest expected, but not so long that data is irrelevant.
**Example**: `online_dcorr_max_lookback = 250`

#### `online_dcorr_refposn`
**Syntax**: `online_dcorr_refposn = <x coord> <y coord>`
**Description**: Position for drift correction (gaze). If doing manual recording, ensure pixel_coords is set in physical.ini.
**Example**: `online_dcorr_refposn = 512, 384`

#### `online_dcorr_maxangle`
**Syntax**: `online_dcorr_maxangle = <angle in degrees>`
**Description**: This is the maximum visual angle between the target and the computed (previous to correction) gaze position. A small angle (2 to 5 degrees) is preferable for regular on-line drift correction. A much larger angle should be used when performing parallax and depth correction in scene camera mode. When head tracking is turned off, carefully set the simulation distance in PHYSICAL.INI for this (and all) angles to be accurate.
**Example**: `online_dcorr_maxangle = 5.0`

#### `online_dcorr_trigger`
**Syntax**: `online_dcorr_trigger <x ref coord> <y ref coord>`
**Description**: The "online_dcorr_trigger" command can be used over the link and will return error codes if it fails: 1 if math failed (recalibration required), 2 if not usable data is possible (too early in fixation and last fixation too old), 3 if drift correction angle was too large.
**Example**: `online_dcorr_trigger`

#### `drift_correction_samples`
**Syntax**: `drift_correction_samples = <count>`
**Description**: These are similar to the "validation_xxx" commands. The idea was that you could collect several fixations at different locations for a drift correction, the drift correct to a weighted average of the error. The drift correction point presentation is controlled from a list of point orders, drawn from an array of X, Y positions. This commands set the number of targets to present for drift correction. By default, only 1 sample is used.
**Example**: `drift_correction_samples = 1`

#### `drift_correction_weights`
**Syntax**: `drift_correction_weights = <list of weight>`
**Description**: Weights to assign points for weighted error for drift correction.
**Example**: `drift_correction_weights = 1`

#### `drift_correction_targets`
**Syntax**: `drift_correction_targets = <list of x,y coordinates>`
**Description**: This sets an array of sequenced X, Y pairs of drift correction target positions in display coordinates. This command is used internally by the API function eyelink_driftcorr_start().
**Example**: `drift_correction_targets = 512, 384`

#### `drift_correction_fraction`
**Syntax**: `drift_correction_fraction = <fraction>`
**Description**: Fraction of drift correction to be applied. The idea is that applying a small correction many times will converge to zero error with less effect of inaccurate fixations. The default is full fixup (1.0).
**Example**: `drift_correction_fraction = 1.0`

#### `drift_correct_mouse`
**Syntax**: `drift_correct_mouse = <ON or OFF>`
**Description**: Whether drift correction is performed in mouse simulation. Because mouse reverse-maps gaze to eye position, the drift correction fixup will increase with each drift correction, eventually causing problems. Turning off the drift correction fixup is one solution. If on, we currently reduce the correction by half--this shows an effect at least.
**Example**: `drift_correct_mouse = ON`

#### `driftcorrect_cr_disable`
**Syntax**: `driftcorrect_cr_disable = <switch>`
**Description**: Disables drift correction unless in pupil-only mode. Drift correction functions normally but has no effect. Default: OFF. Values: OFF or 0 = normal DC even in P-CR mode, ON or 1 = DC has no effect any inaccurate fixation ignored, AUTO or -1 = Flash and bleep if subject is not fixating target but no correction for fixation error.
**Example**: `driftcorrect_cr_disable = AUTO`

#### `remote_cal_enable`
**Syntax**: `remote_cal_enable = <remote calibration settings>`
**Description**: Turns on remote calibration and disables automatic sequencing of targets. 0 to disable remote calibration. 1 or YES waits for all targets and at end of calibration. -1 waits only at end of cal (for data).
**Example**: `remote_cal_enable = OFF`

#### `remote_cal_target`
**Syntax**: `remote_cal_target <targnum>`
**Description**: Commands display of target in remote calibration. The target number is 1 to max for calibration mode. 0 will hide current target and return to waiting. Targets can be presented several times.
**Example**: `remote_cal_target 1`

#### `remote_cal_complete`
**Syntax**: `remote_cal_complete`
**Description**: Commands to complete remote calibration. Fails if data has not been collected for all targets yet.
**Example**: `remote_cal_complete`

#### `calibration_status`
**Syntax**: `calibration_status`
**Description**: READ-ONLY calibration data. Used to get current cal status and target info. The format of the string return value as: "targx targy targvis targnum totnum status". targx, targy: target location (floating point), targvis: 0 if hidden 1 if drawn, targnum totnum: same as the "%d of %d" on cal screen, status: status same as on cal screen one of: STABLE, WAITING, PACING, MARKERS, MOVING, NO PUPIL, NO CR.
**Example**: `calibration_status`

#### `calibration_fixation_data`
**Syntax**: `calibration_fixation_data`
**Description**: Used to get info after fixation accepted. Will be blank before first accepted. Use string compare to test for changes. One line with lots of data. The format of the string return value as: "fixdata targid seqnum eye targx, targy, tstart, tend, pxl, pyl pxr, pyr, dxl, dyl, dxr, dyr, hxl, hyl, hxr, hyr".
**Example**: `calibration_fixation_data`

#### `remote_cal_data`
**Syntax**: `remote_cal_data <targ> <pxl> <pyl> <pxr> <pyr> <dxl> <dyl> <dxr> <dyr> <mx1> <my1> <mx2> <my2> <mx3> <my3> <mx4> <my4>`
**Description**: This command requires 16 args from averages in the samples to be used as cal data. These are: p (pupil: x,y, left,right), d (p-cr: x,y, left,right), m (markers, x,y, 1 through 4). Any fields that were MISSING in all samples can be set to 0.
**Example**: `remote_cal_data`

#### `remote_cal_href_data`
**Syntax**: `remote_cal_href_data <id> <pxl> <pyl> <pxr> <pyr> <dxl> <dyl> <dxr> <dyr> <hxl> <hyl> <hxr> <hyr>`
**Description**: For use with external head-tracker. Supply eye data, target HREF equivalent. This command requires 12 args from averages in the samples to be used as cal data. These are: id: target number in XY position list, p (pupil: x,y, left,right), d (p-cr: x,y, left,right), h (target href: x,y, left,right). Any fields that were MISSING in all samples can be set to 0.
**Example**: `remote_cal_href_data`

#### `reset_cal_data_points`
**Syntax**: `reset_cal_data_points`
**Description**: Clears all calibration data points before sending remotely generated calibration data. Otherwise, both tracker and remote data will be plotted (and possibly averaged).
**Example**: `reset_cal_data_points`

#### `disable_cal_auto_sequence`
**Syntax**: `disable_cal_auto_sequence = <switch>`
**Description**: Disables auto-sequencing, prevents being turned on manually.
**Example**: `disable_cal_auto_sequence = NO`

#### `disable_cal_trigger`
**Syntax**: `disable_cal_trigger = <switch>`
**Description**: Disable any cal target fixation triggering; this forces use of remote data.
**Example**: `disable_cal_trigger = NO`

#### `disable_cal_backspace`
**Syntax**: `disable_cal_backspace = <switch>`
**Description**: Pressing the "backspace" key can redo the previous calibration points. Use this command to disable backing up through targets with "backspace" key.
**Example**: `disable_cal_backspace = NO`

#### `disable_cal_auto_manual_switch`
**Syntax**: `disable_cal_auto_manual_switch = <switch>`
**Description**: Prevents manual trigger (for targets other than first) from turning off automatic trigger and sequencing.
**Example**: `disable_cal_auto_manual_switch = NO`

#### `normal_click_dcorr`
**Syntax**: `normal_click_dcorr = <ON or OFF>`
**Description**: Whether the drift correction by mouse click button is available in normal (non-video) mode (default is OFF).
**Example**: `normal_click_dcorr = OFF`

#### `online_dcorr_button`
**Syntax**: `online_dcorr_button = <ON or OFF>`
**Description**: Whether the immediate drift correction to predefined target button is available in normal mode (default is OFF). Note the normal blue will only appear in the following settings: online_dcorr_button = ON; video_click_dcorr = OFF; normal_click_dcorr = OFF; scenecam_click_dcorr = OFF.
**Example**: `online_dcorr_button = OFF`

#### `always_default_calibration`
**Syntax**: `always_default_calibration`
**Description**: Resets all calibration values to defaults before collecting new calibration. Last good calibration is saved before this, so should have no effect. DEFAULT: ON.
**Example**: `always_default_calibration = ON`

#### `active_eye`
**Description**: TYPE:  READ, WRITE, LASTRUN.INI Sets which eye is being tracked in monocular mode by default. Use "binocular_enabled" function to select binocular tracking. <camera ID> can be a name or number: 1 or LEFT 3 or RIGHT
**Example**: `active_eye = RIGHT`

#### `allow_pupil_without_cr`
**Description**: <switch>: TRUE or FALSE Allows pupil without a CR nearby to be detected in pupil search (after pupil loss or on startup). This command is overridden in P-CR mode.
**Example**: `allow_pupil_without_cr = FALSE`

#### `ambient_filter_constant`
**Description**: This sets the ambient-light detector filter constant. The smaller this number, the longer the response time. This was added because a few systems showed a small periodicity in pupil size under certain lighting conditions, which could be fixed with a very small filter constant (very slow response).
**Example**: `ambient_filter_constant = 0.2`

#### `autothreshold_click`
**Description**: <switch>: TRUE or FALSE Auto-threshold on mouse click on setup mode image
**Example**: `autothreshold_click = TRUE`

#### `autothreshold_repeat`
**Description**: <switch>: TRUE or FALSE Allows repeat of auto-threshold if pupil not centered on first
**Example**: `autothreshold_repeat = TRUE`

#### `aux_mouse_simulation`
**Description**: TYPE: READ, WRITE, MENU, LASTRUN.INI Whether mouse simulation is enabled.
**Example**: `aux_mouse_simulation = NO`

#### `binocular_enabled`
**Description**: TYPE:  READ, WRITE, LASTRUN.INI Sets whether eye tracking is binocular or monocular.  Use "active_eye" to select eye being tracked in monocular mode.

#### `black_filter_constant`
**Description**: This sets the CCD black-level compensation filter constant. See "ambient_filter_constant" for more information.
**Example**: `black_filter_constant= 0.01`

#### `camera_color_ramp`
**Description**: Sets up camera image color sets. <ramp>: 0=greyscale, 1=pupil threshold, 2=CR threshold NOTE: ramp values are given as fraction of blk->wht range for red, green, and blue components. <rm>, <gm>, <bm> = range for ramp as fraction of blk->wht range <ra>, <ga>, <ba> = base brightness of darkest color in ramp Color component = (fraction of ramp)*(range) + (base)
**Example**: `camera_color_ramp 2, 0.000, 0.00, 0.400, 0.620, 0.400, 0.620`

#### `cl_edf_identifier`
**Description**: Specifies the EDF file identifier that is used by applications like edf2asc to determine the EDF file type DO NOT CHANGE THIS VALUE, OR YOUR EDF FILES WILL NOT BE READABLE Default Value: "SR_RESEARCH_COMBFILE"
**Example**: `cl_edf_identifier = "SR_RESEARCH_1000FILE"`

#### `corneal_mode`
**Description**: READ, WRITE, LASTRUN.INI Selects eye tracking mode.  Sets sampling rate in combination with "use_high_speed". YES selects pupil-corneal mode, NO selects pupil-only mode.
**Example**: `corneal_mode = YES`

#### `corneal_select_limits`
**Description**: Sets the rectangle to limit selection (left, top, right, bottom). If any part of candidate P or CR touches this, it is disqualified (must be inside of or equal to defaults). defaults:         1, 1, 191, 158

#### `corneal_select_size`
**Description**: Sets the size criteria for pupil and corneal reflection selection. minwidth, maxwidth: (1-191) minheight, maxheight: (1-150), minarea, maxarea: (area <= height*width)
**Example**: `pupil_select_size    =   8, 120,   8, 120,  100, 15000`

#### `current_camera`
**Description**: TYPE:  READ, WRITE, LASTRUN.INI Sets which camera is currently selected for threshold adjustment, displayed as the large image in Camera Setup mode, or is sent over the link. <camera ID> can be a name or number: 1 or LEFT 2 or HEAD 3 or RIGHT
**Example**: `current_camera = RIGHT`

#### `disable_corneal_reflection`
**Description**: These are used for primate systems, to remove buttons and permanently block CR and head tracking.  If enabled, the layout of the set options screen and camera setup screen are modified.
**Example**: `disable_head_camera = NO`

#### `disable_gaze_cursors`
**Description**: Disables drawing of gaze cursors, intended for recording without calibration.  This will print out a warning message on the tracker display ("Gaze cursor disabled by ini file or command").  As an alternative for video overlay, set the overlay cursor to be dark: Colors that work:1,3,4,25,26,30,31,32,140,141 Change colors in these commands from VIDOVL.INI: video_monoc_cursor_color = 141     // monoc and cyclopean video_custom_cursor_color = 141    // last color menu entry video_binoc_cursor_colors = 214, 234, 180 //binoc:L,R,overlap
**Example**: `disable_gaze_cursors = NO`

#### `disable_head_camera`
**Description**: These are used for primate systems, to remove buttons and permanently block CR and head tracking.  If enabled, the layout of the set options screen and camera setup screen are modified.
**Example**: `disable_head_camera = NO`

#### `draw_link_crosshairs`
**Description**: New camera options have been added, including allowing image data to be sent in any mode.  A new image type (4) has been added with enhanced compression for this purpose. In addition, cross-hair data has been packed into the PALDATA structure.  NOTE: the color of the pupil-limit box has been changed from green to blue as the new compression only handles 128 colors. This command sets whether cross-hairs will appear on the image sent over the link. These may be turned off if the cross-hairs are to be drawn on the display PC. (This is automatically done by selecting image mode 5). However, these must usually be turned on for older API program compatibility.
**Example**: `draw_link_crosshairs = ON`

#### `elcl_hold_if_no_corneal`
**Description**: <switch>: ON or OFF If true, eye window is frozen until both pupil and CR are present. Default Value: OFF
**Example**: `elcl_hold_if_no_corneal = OFF`

#### `elcl_pupil_symmetry_gain`
**Description**: <xm> <ym>: floating point gain values Parameter is used to compensate for pupil size change effects on pupil position when camera is at a large angle to the eye. Pupil area is multiplied by these and added to pupil position. Defaults are (0, 0)
**Example**: `elcl_pupil_symmetry_gain 0.0 0.0`

#### `elcl_search_if_no_corneal`
**Description**: <switch>: ON or OFF If corneal missing for long period, assumes false target and searches for pupil/CR candidate. Default Value: OFF
**Example**: `elcl_search_if_no_corneal = ON`

#### `elcl_use_pcr_matching`
**Description**: <switch>: ON or OFF Selects enhanced pupil-CR matching during pupil identification. If used, pupil and CR are selected as best matching pair. This can be used even if CR is not being used for tracking. Default Value: ON
**Example**: `elcl_use_pcr_matching = ON`

#### `enable_camera_position_detect`
**Description**: <switch>: TRUE or FALSE Allows camera position detect on click/auto-threshold in setup mode
**Example**: `enable_camera_position_detect = TRUE`

#### `enable_search_limits`
**Description**: <switch>: ON or OFF Enables use/display of global search limits
**Example**: `enable_search_limits = ON`

#### `eye_current_limit`
**Description**: Sets the maximum drive current to pupil illuminators. The default is 350 mA.
**Example**: `eye_current_limit = 350`

#### `eyelink_file_xfer_packets`
**Description**: Sets number of packets per file transfer block. This is 1 by default (reset at connection) for compatibility with older API code. Min 1, max 16. 0 - sets to 1, locks against further writes -1..-16: writes negative (1..16), unlocks
**Example**: `eyelink_file_xfer_packets 0`

#### `file_buffer_record_display`
**Description**: <enable>: ON or OFF Enables display of file buffer capacity during recording. Optionally sets color of background. Default: ON, 124
**Example**: `file_buffer_record_display = OFF`

#### `force_corneal_reflection`
**Description**: Hides "Pupil" mode button on Camera Setup screen Pupil Only mode should only be used in EyeLink 1000 when participants head is completely fixed. Default Value: OFF
**Example**: `force_corneal_reflection =TRUE`

#### `force_elcl_mode`
**Description**: <switch>: TRUE or FALSE Forces startup in ELCL mode Startup fails without hardware or -x option
**Example**: `force_elcl_mode = TRUE`

#### `force_network_present`
**Description**: <switch>: TRUE or FALSE Startup fails unless network hardware present
**Example**: `force_network_present = TRUE`

#### `hcam_center`
**Description**: Each head camera has been calibrated during manufacture, and its characteristics written on the camera back.  <hcam_center> are the OX and OY parameters and <hcam_scale> are the SX and SY parameters. These can be used in FINAL.INI to override the headband EEPROM calibration for the head camera.
**Example**: `hcam_center = -22400, -15700`

#### `hcam_scale`
**Description**: Each head camera has been calibrated during manufacture, and its characteristics written on the camera back.  <hcam_center> are the OX and OY parameters and <hcam_scale> are the SX and SY parameters. These can be used in FINAL.INI to override the headband EEPROM calibration for the head camera.
**Example**: `hcam_scale = -585, -245`

#### `heuristic_filter`
**Description**: TYPE: Read, Write, lastrun.ini, MENU Can be used to set level of filtering on the link and analog output, and on file data.  An additional delay of 1 sample is added to link or analog data for each filter level. If an argument of <ON> is used, link filter level is set to 1 to match EyeLink I delays.  The file filter level is not changed unless two arguments are supplied.  The default file filter level is 2. 0 or OFF disables link filter 1 or ON sets filter to 1 (moderate filtering, 1 sample delay) 2 applies an extra level of filtering (2 sample delay)
**Example**: `heuristic_filter 1 2`

#### `image_from_setup_menu`
**Description**: Allows Camera Setup menu to always have image sending turned on. This might have caused problems with EyeLink 1 apps, as "setup" and "image" modes would be confused by eyelink_current_mode(). Default is OFF.
**Example**: `image_from_setup_menu = OFF`

#### `imager_gain`
**Description**: Both the eye camera and head camera gains have a range between 0 snd 319.  The default values for them are 110,120.  Gain doubles for each 64 counts.
**Example**: `imager_gain = 110, 120`

#### `initial_thresholds`
**Description**: TYPE: WRITE, READ, LASTRUN.INI Image processing thresholds (values 0..255).
**Example**: `initial_thresholds = 66, 40, 66, 150, 150`

#### `left_eye_head_camera_offset`
**Description**: When in FINAL.INI, overrides head camera-to-eye parallax correction settings.  Set all to 0 to disable parallax fixup. While these settings are supposed to be based on difference in position in millimetres, in actuality these are determined empirically. <xo>: distance eye to left of head camera <yo>: distance eye below head camera <xz, yz>: fixup for eye distance behind head camera (head rotation change). Current settings (programmed into all headband EEPROMs) are: L:  40.0 70.0 0.0 70.0 R: -40.0 70.0 0.0 70.0
**Example**: `left_eye_head_camera_offset  = 40.0 70.0 0.0 70.0`

#### `lock_active_eye`
**Description**: TYPE:  READ, WRITE, LASTRUN.INI Controls whether the camera for the eye that is not being tracked monocularly (left or right, no effect in binocular) is locked out of camera selection. This prevents left and right arrow selection, or clicking on camera thumbnails, from selecting the uncalibrated eye.
**Example**: `lock_active_eye = YES`

#### `lock_eye_after_calibration`
**Description**: TYPE: READ, WRITE, MENU, LASTRUN.INI Controls whether the current eye (left or right, no effect in binocular) is locked in after calibration. Essentially this just sets "lock_active_eye" at the end of monocular calibration.
**Example**: `lock_eye_after_calibration = YES`

#### `logfile_contents`
**Description**: Each time the tracker is run, a log file (EYE.LOG) is created.  It can contain various kinds of data, including errors, calibration results, and debugging information.  These levels of logging are available: FILE    includes all commands in INI files, allowing a record of configuration to be kept LINK    includes all link commands, system variable writes and reads MACROS  includes contents of macros, key/button functions and internal commands executed MESSAGES includes all messages logged to the data file READ     includes all variable reads ALL      does all of the above
**Example**: `logfile_contents = ALL`

#### `mirror_elcl_image`
**Description**: <H switch><V switch>: ON or OFF Controls how display of ELCL images are flipped Raw pupil/CR data is never flipped. Default: ON, ON
**Example**: `mirror_elcl_image = ON, ON`

#### `mirror_eyecam_image`
**Description**: Controls orientation of eye/head camera image.  Flipping the image top-to-bottom or left-to-right may make setup more intuitive for some subjects.  This flips both image and data.  The default is to horizontally flip eye cameras only. <hflip> and <vflip> can be 0, 1, YES, NO.
**Example**: `mirror_eyecam_image = YES, YES`

#### `mirror_headcam_image`
**Description**: Controls orientation of eye/head camera image.  Flipping the image top-to-bottom or left-to-right may make setup more intuitive for some subjects.  This flips both image and data.  The default is to horizontally flip eye cameras only. <hflip> and <vflip> can be 0, 1, YES, NO.
**Example**: `mirror_headcam_image = NO, NO`

#### `pupil_crosstalk_fixup`
**Description**: A compensatory factor to remove effect of pupil size from pupil position (i.e., a small optical crosstalk between pupil size and Y position in the image). This is caused by not looking at the eye from straight on.   X and Y values scale pupil area are added to position actual scale: about 1/300 degree per unit.  Defaults are 0.000, -0.001. However, if you are using mirrors (e.g., in monkeys systems).  This should be set to 0.0, 0.0. <xfixup> <yfixup>: Adjustment of X, Y position of pupil for pupil size.
**Example**: `pupil_crosstalk_fixup = 0.000, -0.001`

#### `pupil_min_size`
**Description**: Sets the minimum size of pupil (default 8) and option second parameter, the minimum area (w*h*density) of pupil.
**Example**: `pupil_min_size 8`

#### `pupil_select_limits`
**Description**: Sets the rectangle to limit selection (left, top, right, bottom). If any part of candidate P or CR touches this, it is disqualified (must be inside of or equal to defaults). defaults:         1, 1, 191, 158
**Example**: `pupil_select_limits   1, 1, 191, 158`

#### `pupil_select_size`
**Description**: Sets the size criteria for pupil and corneal reflection selection. minwidth, maxwidth: (1-191) minheight, maxheight: (1-150), minarea, maxarea: (area <= height*width)
**Example**: `pupil_select_size    =   8, 120,   8, 120,  100, 15000`

#### `pupil_size_diameter`
**Description**: READ, WRITE, MENU. LASTRUN.INI Sets the type of data used for pupil size.  The type can be a number, or a word (only first letter checked). The <ID_CODE> below is the pupil type (prescaler) field of link data. TYPE        TYPE CODE              ID_CODE   DATA area        AREA, NO, OFF, 0         1      area diameter    DIAMETER, YES, ON, 1   128      128*sqrt(area) width       WIDTH, 2                90      180*width height      HEIGHT, 3              180      180*height
**Example**: `pupil_size_diameter = AREA`

#### `rec_plot_colors`
**Description**: Sets colors of traces in data plotting. Each of the 4 traces (LX, LY, RX, RY) can be changes separately.  The color of traces where overlaps occur may also be set. Finally, the background of the gain and offset edit boxes can be modified. Default Values: 255,210,227,192, 191, 15,4,15,4
**Example**: `rec_plot_colors = 255,95,210,192, 191, 15,4,15,4`

#### `rec_plot_mclick_step`
**Description**: sets step in gain/offsetr when clicking on arrow buttons <offset_step>: fraction of total range to adjust (0.00..1.00) <gain_ratio>:  multiplier/divisor for gain (1.00..2.00) default: 0.05    (20 steps top-to-bottom), 1.1892  (4 step for factor of 2 gain change)
**Example**: `rec_plot_mclick_step 0.05 1.1892`

#### `rec_plot_simple_offset`
**Description**: <switch>: ON or OFF Prevents offset from changing when gain is changed via the arrow buttons.  NOTE: this will cause the plot to shift when gain is adjusted. Default Value: OFF
**Example**: `rec_plot_simple_offset = OFF`

#### `recording_parse_type`
**Description**: Data type used to compute velocity for parsing of eye movements during recording. Both gaze and head-referenced data are available for other statistics.  Almost always left to GAZE. <type>: GAZE or HREF.
**Example**: `recording_parse_type = GAZE`

#### `right_eye_head_camera_offset`
**Description**: When in FINAL.INI, overrides head camera-to-eye parallax correction settings.  Set all to 0 to disable parallax fixup. While these settings are supposed to be based on difference in position in millimetres, in actuality these are determined empirically. <xo>: distance eye to left of head camera <yo>: distance eye below head camera <xz, yz>: fixup for eye distance behind head camera (head rotation change). Current settings (programmed into all headband EEPROMs) are: L:  40.0 70.0 0.0 70.0 R: -40.0 70.0 0.0 70.0
**Example**: `right_eye_head_camera_offset = -40.0 70.0 0.0 70.0`

#### `search_limits_rect`
**Description**: <left><top><right><bottom>: in pixels Specifies the location of the search limits on the sensor. Coords are in used sensor coords. right-left should equal width defined in search_limits_size bottom-top should equal height defined in search_limits_size Valid rage: x=32..1263, y=48..971 search_limits_rect = -1 means that the search limits rectangle is undefined lastrun.ini updates this command when ever the tracker is exited and enable_search_limits = True
**Example**: `search_limits_rect = -1`

#### `search_limits_shape`
**Description**: <type>: 1 or 0 Controls the shape of the search limits. 0  = rectangle, 1 = 'ellipse'
**Example**: `search_limits_shape = 1`

#### `search_limits_size`
**Description**: <width> <height>: in pixels Specifies the size of the search limits box
**Example**: `search_limits_size = 500 500`

#### `select_eye_after_validation`
**Description**: TYPE:  READ, WRITE Controls whether the best eye is automatically selected as the default after validation.  If NO, binocular mode is kept by default. This is automatically disabled in scene camera mode.
**Example**: `select_eye_after_validation = NO`

#### `select_parser_configuration`
**Syntax**: `select_parser_configuration = <set>`
**Description**: Selects the preset saccade detector configuration for standard parser setup (0) or more sensitive saccade detector (1). These are equivalent to the cognitive and psychophysical configurations. <set>: 0 for standard, 1 for high sensitivity.
**Example**: `select_parser_configuration 0`

#### `fast_velocity_filter`
**Syntax**: `fast_velocity_filter = <YES or NO>`
**Description**: Uses faster velocity filter. This shortens saccades, but has less noise immunity. The slow filter has 25% response at 2 samples, 0 at 3 samples. The fast filter has 50% response at 1 sample, 0 at 2 samples.
**Example**: `fast_velocity_filter = YES`

#### `saccade_velocity_threshold`
**Syntax**: `saccade_velocity_threshold = <vel>`
**Description**: Sets velocity threshold of saccade detection. <vel>: minimum velocity (°/sec) for saccade.
**Example**: `saccade_velocity_threshold = 30`

#### `saccade_acceleration_threshold`
**Syntax**: `saccade_acceleration_threshold = <accel>`
**Description**: Sets acceleration threshold of saccade detector. <accel>: minimum acceleration (°/sec/sec) for saccades.
**Example**: `saccade_acceleration_threshold = 8000`

#### `saccade_motion_threshold`
**Syntax**: `saccade_motion_threshold = <deg>`
**Description**: Sets a spatial threshold to shorten saccades. Usually 0.10 for cognitive research, 0 for pursuit and neurological work. <deg>: minimum motion (degrees) out of fixation before saccade onset allowed.
**Example**: `saccade_motion_threshold = 0.1`

#### `saccade_pursuit_fixup`
**Syntax**: `saccade_pursuit_fixup = <maxvel>`
**Description**: Sets the maximum pursuit velocity accommodation by the saccade detector. <maxvel>: maximum pursuit velocity fixup (°/sec).
**Example**: `saccade_pursuit_fixup = 60`

#### `saccade_extend_velocity`
**Syntax**: `saccade_extend_velocity = <degrees per second>`
**Description**: Extend length while above this velocity.
**Example**: `saccade_extend_velocity = 25`

#### `saccade_max_extend_start`
**Syntax**: `saccade_max_extend_start = <time in msec>`
**Description**: Max time to extend at the start of the saccade.
**Example**: `saccade_max_extend_start = 0`

#### `saccade_max_extend_after`
**Syntax**: `saccade_max_extend_after = <time in msec>`
**Description**: Max time to extend at the end of the saccade.
**Example**: `saccade_max_extend_after = 0`

#### `saccade_onset_verify_time`
**Syntax**: `saccade_onset_verify_time = <time in msec>`
**Description**: Milliseconds that saccade exceeds velocity threshold. These times are used to verify that saccade isn't borderline or noise.
**Example**: `saccade_onset_verify_time = 4`

#### `saccade_offset_verify_time`
**Syntax**: `saccade_offset_verify_time = <time in msec>`
**Description**: Fill-in for gaps in saccade. These times are used to verify that saccade isn't borderline or noise.
**Example**: `saccade_offset_verify_time = 20`

#### `blink_offset_verify_time`
**Syntax**: `blink_offset_verify_time = <time in msec>`
**Description**: Blink detection. Blink (missing pupil) gaps may need to be filled in.
**Example**: `blink_offset_verify_time = 12`

#### `parser_discard_startup`
**Syntax**: `parser_discard_startup = <YES or NO>`
**Description**: If enabled, does not output events until eye data changes. For example, if the eye is in a blink or fixation at the start of recording, no events will be output for that blink or fixation.
**Example**: `parser_discard_startup = NO`

#### `fixation_update_interval`
**Syntax**: `fixation_update_interval = <time>`
**Description**: During fixation, send updates every (m) msec, integrated over (n) msec (max=m, min = 4 msec). These can be used for gaze-controlled software or for pursuit tracking. Intervals of 50 or 100 msec are suggested. Interval of 0 disables. NOTE: 50 RECOMMENDED FOR ONLINE DRIFT CORRECT.
**Example**: `fixation_update_interval = 50`

#### `fixation_update_accumulate`
**Syntax**: `fixation_update_accumulate = <time>`
**Description**: During fixation, send updates every (m) msec, integrated over (n) msec (max=m, min = 4 msec). Normally set to 0 to disable fixation update events. Set to 50 or 100 msec to produce updates for gaze-controlled interface applications. Set to 4 to collect single sample rather than average position. <time>: milliseconds to collect data before fixation update for average gaze position.
**Example**: `fixation_update_accumulate = 50`

#### `set_image_channel`
**Description**: TYPE:  READ, WRITE, LASTRUN.INI Sets which camera is currently selected for threshold adjustment, displayed as the large image in Camera Setup mode, or is sent over the link. <camera ID> can be a name or number: 1 or LEFT 2 or HEAD 3 or RIGHT
**Example**: `current_camera = RIGHT`

#### `set_record_data_defaults`
**Description**: WRITE, MENU, LASTRUN.INI This sets the default behavior of "start_recording" when it has no data control arguments.  It is used for the Options menu manual data recording settings. NOTE: this is NOT affected by the data control arguments of "start_recording".  The "TRACK" program fools around with this setting, turning off all data so that when manually starting recording it can stop and restart recording with its own settings, graphics, etc.
**Example**: `set_record_data_defaults DATA=1,1,0,0`

#### `start_in_camera_setup`
**Description**: Allows tracker to start in Camera Setup mode rather than Offline mode Default: NO
**Example**: `start_in_camera_setup TRUE`

#### `sticky_mode_data_enable`
**Description**: Sets link and/or file data output in modes other than record. If the suffix is blank, data will be turned off. The data control will be overridden by a data control suffix in any mode-setting command. The data control specification is one of these formats: - "DATA <file samples> <file events> <link samples> <link events>" where the fields can be 0, 1, or ON, OFF, YES, or NO - one or more specifiers (FILE or LINK followed by SAMPLES and/or EVENTS) As always, commas, tabs, or '=' are equivalent to whitespace.
**Example**: `sticky_mode_data_enable DATA = 0 0 0 0`

#### `sticky_mode_parse_type`
**Description**: specifies parsing data type for all modes but record this will be overridden in cal (raw), val, and DC (gaze)
**Example**: `sticky_mode_parse_type GAZE`

#### `track_search_limits`
**Description**: <switch>: ON or OFF Enables tracking of pupil to global search limits
**Example**: `track_search_limits = OFF`

#### `use_camimg_palette_colors`
**Description**: Use tracker palette colors for display-PC camera image Default: NO
**Example**: `use_camimg_palette_colors = ON`

#### `use_high_speed`
**Description**: READ, WRITE, LASTRUN.INI Whether to use high-speed modes. Sets sampling rate in combination with "corneal_mode". This is YES for 500 Hz mode with pupil 250 Hz pupil-corneal mode.
**Example**: `use_high_speed = YES`

## Configuration Names Reference

Configuration abbreviations and their meanings:

**From CMV_CFG.INI:**
- MTABLER: Desktop ~ Stabilized Head ~ Monocular ~ 35mm lens
- BTABLER: Desktop ~ Stabilized Head ~ Binoc/Monoc ~ 35mm lens
- RTABLER: Desktop (Remote mode) ~ Target Sticker ~ Monocular ~ 16/25mm lens
- RBTABLER: Desktop (Remote mode) ~ Target Sticker ~ Binoc/Monoc ~ 16/25mm lens
- AMTABLER: Arm Mount ~ Stabilized Head ~ Monocular ~ 35mm lens
- ABTABLER: Arm Mount ~ Stabilized Head ~ Binoc/Monoc ~ 35mm lens
- ARTABLER: Arm Mount (Remote mode) ~ Target Sticker ~ Monocular ~ 16/25mm lens
- ABRTABLE: Arm Mount (Remote mode) ~ Target Sticker ~ Binoc/Monoc ~ 16/25mm lens
- BTOWER: Tower Mount (Binocular) ~ Stabilized Head ~ Binoc/Monoc ~ 25mm lens

**From TSCFG.INI:**
- TOWER: Tower Mount ~ Stabilized Head ~ Monocular ~ 25mm lens
- MPRIM: Primate Mount ~ Stabilized Head ~ Monocular ~ 25mm lens
- BPRIM: Primate Mount ~ Stabilized Head ~ Binoc/Monoc ~ 25mm lens

**From TOCFG.INI:**
- MLRR: Long Range Mount ~ Stabilized Head ~ Monocular ~ 35-75mm lenses ~ Camera Level
- BLRR: Long Range Mount ~ Stabilized Head ~ Binoc/Monoc ~ 35-75mm lenses ~ Camera Angled

#### `drift_correction`
**Syntax**: `drift_correction <offset x> <offset y> <gaze x> <gaze y> [list of options]`
**Description**: Performs a drift correction, using a display position and an offset. The offset is (target position - actual fixation). The drift correction happens immediately, and will cause a jump in eye-movement data. OPTIONS: L or 0 = do left eye, R or 1 = do right eye (if neither specified does one or both depending on eyes tracked), HREF = data and drift correction is in HREF coordinates, if HREF is not in the option list = simply add offset to gaze position.
**Example**: `drift_correction`

#### `accept_target_fixation`
**Syntax**: `accept_target_fixation`
**Description**: Acts to trigger manual accept of a target fixation. Used by many API programming examples and the API function eyelink_accept_trigger(). Most examples program button 5 to issue this command when pressed.
**Example**: `accept_target_fixation`

#### `collect_target_fixation`
**Syntax**: `collect_target_fixation <start time> <end time>`
**Description**: Acts to trigger manual accept of a target fixation. The time arguments are ignored for EyeLink 1000.
**Example**: `collect_target_fixation`

#### `apply_last_drift_correction`
**Syntax**: `apply_last_drift_correction <optional fraction>`
**Description**: When a drift correction is done using "start_drift_correction" issued through the link, the actual drift correction is not done. This command applies the computed correction. If a fraction is supplied, then only a portion of the error is corrected. Used by the API function eyelink_apply_driftcorr().
**Example**: `apply_last_drift_correction`

#### `restore_old_calibration`
**Syntax**: `restore_old_calibration`
**Description**: Supposed to reload the last calibration and drift correction. This happens automatically now, so these may have no effect.
**Example**: `restore_old_calibration`

#### `start_bitmap_transfer`
**Syntax**: `start_bitmap_transfer <type> <destx> <desty> <width> <height>`
**Description**: Starts transfer of record-background bitmap to tracker. It returns specifications for bitmap conversion. This command is only legal in Offline and Output menu modes. type: 0 if color, 1 if greyscale. destx, desty: position of top-left in gaze coords on tracker display. width, height: size of bitmap in gaze coords on tracker display. Returns: required bitmap specifications as a string: "<width> <height> <topdrop> <botdrop> <levels> <compsize>".
**Example**: `start_bitmap_transfer`

#### `stop_bitmap_transfer`
**Syntax**: `stop_bitmap_transfer`
**Description**: Aborts transfer of record-background bitmap to tracker, typically if an error occurs. Used by the API function gdi_bitmap_core().
**Example**: `stop_bitmap_transfer`

#### `start_playback`
**Syntax**: `start_playback`
**Description**: Starts last-trial playback which is limited to Offline mode. Used by the API function eyelink_playback_start().
**Example**: `start_playback`

#### `abort_playback`
**Syntax**: `abort_playback`
**Description**: Ends last-trial playback. Used by the API function eyelink_playback_stop().
**Example**: `abort_playback`

#### `mark_playback_start`
**Syntax**: `mark_playback_start`
**Description**: Marks the location in the data file from which playback will begin at the next call to eyelink_playback_start(). When this command is not used (or on older tracker versions), playback starts from the beginning of the previous recording block. This default behavior is suppressed after this command is used, until the tracker software is shut down.
**Example**: `mark_playback_start`

#### `print_position`
**Syntax**: `print_position <column><line>`
**Description**: Coordinates are text row and column, similar to C gotoxy() function. NOTE: row cannot be set higher than 25. Use 'draw_text' command to print anywhere on the tracker display. col: text column, 1 to 80. row: text line, 1 to 25.
**Example**: `print_position`

#### `clear_screen`
**Syntax**: `clear_screen <color: 0 to 15>`
**Description**: Clear tracker screen for drawing background graphics or messages.
**Example**: `clear_screen`

#### `draw_line`
**Syntax**: `draw_line <x1> <y1> <x2> <y2> <color>`
**Description**: Draws line, coordinates are gaze-position display coordinates. x1,y1: start point of line. x2,y2: end point of line. color: 0 to 15.
**Example**: `draw_line`

#### `draw_box`
**Syntax**: `draw_box <x1> <y1> <x2> <y2> <color>`
**Description**: Draws empty box, coordinates are gaze-position display coordinates. x1,y1: corner of box. x2,y2: opposite corner of box. color: 0 to 15.
**Example**: `draw_box`

#### `draw_filled_box`
**Syntax**: `draw_filled_box <x1> <y1> <x2> <y2> <color>`
**Description**: Draws a solid block of color, coordinates are gaze-position display coordinates. x1,y1: corner of box. x2,y2: opposite corner of box. color: 0 to 15.
**Example**: `draw_filled_box`

#### `draw_text`
**Syntax**: `draw_text <x1> <y1> <color> <text>`
**Description**: Draws text, coordinates are gaze-position display coordinates. x1,y1: center point of text. color: 0 to 15. text: text of line, in quotes.
**Example**: `draw_text`

#### `echo`
**Syntax**: `echo <text>`
**Description**: Prints text at current print position to tracker screen, gray on black only. text: text to print in quotes.
**Example**: `echo`

#### `draw_cross`
**Syntax**: `draw_cross <x> <y>`
**Description**: Draws a small '+' to mark a target point. x1,y1: center point of cross. color: 0 to 15.
**Example**: `draw_cross`

#### `begin_macro`
**Syntax**: `begin_macro <name>`
**Description**: Starts (opens) a macro definition. name can be any word that is not an existing command. All macro_line commands until the next end_macro will be added to this macro.
**Example**: `begin_macro`

#### `end_macro`
**Syntax**: `end_macro`
**Description**: Closes the current macro definition.
**Example**: `end_macro`

#### `macro_line`
**Syntax**: `macro_line <rest of line as command>`
**Description**: Adds all text following "macro_line as a line of the currently open macro. This includes comments, etc. Must be preceded by "begin_macro" and followed by "end_macro".
**Example**: `macro_line`

#### `do_macro`
**Syntax**: `do_macro <name>`
**Description**: Executes all lines of the macro <name>. These will be executed as a block, but may not be contiguous in time. Any data and image processing needs of the tracker take precedence over command execution, and thus changing data-control parameters while data is being recorded may result in undefined behavior.
**Example**: `do_macro`

#### `delete_macro`
**Syntax**: `delete_macro  <name>`
**Description**: Deletes the macro <name>.
**Example**: `delete_macro`

#### `flush_logfile`
**Syntax**: `flush_logfile`
**Description**: Forces all buffered log file data to be written. This could be used to ensure log file integrity, or to reduce the probability of disk writes happen for a short period.
**Example**: `flush_logfile`

#### `start_file_transfer`
**Syntax**: `start_file_transfer <optional file name>`
**Description**: Starts send of and EDF file. If a file name is supplied, it is converted to be in the specified directory or, if no directory is given, in the current EDF data path. If no file name is given, the current (or last) open EDF file is used. Used by the API function eyelink_request_file_read().
**Example**: `start_file_transfer`

#### `abort_file_transfer`
**Syntax**: `abort_file_transfer`
**Description**: Halts current EDF file transfer. Used by the API function eyelink_end_file_transfer().
**Example**: `abort_file_transfer`

#### `add_file_preamble_text`
**Syntax**: `add_file_preamble_text   <Descriptive text message>`
**Description**: Text messages describing a file's contents may be written into a data file's preamble, which is viewable with any text editor. This text must be written and the preamble closed before data may be written to the file.
**Example**: `add_file_preamble_text`

#### `open_data_file`
**Syntax**: `open_data_file <name of data file>`
**Description**: This command opens an eye tracker data file (.EDF extension), destroying any file with the same name without warning. If no path is given, the file will be written into the directory the eye tracker is running from. Returns error message or "<filename> successfully created".
**Example**: `open_data_file`

#### `close_data_file`
**Syntax**: `close_data_file`
**Description**: Closes any open EDF file. Attempts to clean up file structure if closing while data is being recorded.
**Example**: `close_data_file`

#### `data_file_name`
**Syntax**: `data_file_name`
**Description**: READ-ONLY. Returns the full name of the current or last EDF file opened.
**Example**: `data_file_name`

#### `call_setup_menu_mode`
**Syntax**: `call_setup_menu_mode`
**Description**: Designed for use from user menus--these execute the mode, then on exit return to the current mode (or menu).
**Example**: `call_setup_menu_mode`

#### `call_option_menu_mode`
**Syntax**: `call_option_menu_mode`
**Description**: Designed for use from user menus--these execute the mode, then on exit return to the current mode (or menu).
**Example**: `call_option_menu_mode`

#### `display_user_menu`
**Syntax**: `display_user_menu <menu number>`
**Description**: Starts a user menu, numbered from 1 to 3 (1 to 4 for EyeLink 1). User menu 1 will be called up on record abort (CTRL-ALT-A) by the API function record_abort_handler(). Up to 4 user menus can be created. These are accessed by `display_user_menu <number=1..4>`. The menu description is started with `create_user_menu <number=1..4> <title>` and each line is added with `add_user_menu_item <button_text> <description> <key_spec> <code> [<optional command>]`. When the menu is entered, it stays there till the tracker is switched to another mode, and monitors key presses. If identified, the code is sent to the remote PC, and any command is executed. THIS IS REQUIRED FOR DEVELOPER'S KIT SAMPLE CODE.
**Example**: `display_user_menu`

#### `option_menu_mode`
**Syntax**: `option_menu_mode`
**Description**: This calls up the "Set Options" menu screen. No data output is available.
**Example**: `option_menu_mode`

#### `output_menu_mode`
**Syntax**: `output_menu_mode <optional data control switches>`
**Description**: This calls up the Output menu screen. Data output is available in EyeLink 2.0 and later.
**Example**: `output_menu_mode DATA = 1 1 1 1`

#### `setup_menu_mode`
**Syntax**: `setup_menu_mode`
**Description**: This calls up the Setup menu in EyeLink 1, and the Camera Setup menu (with image sending off) in EyeLink II / CL. No data output is available.
**Example**: `setup_menu_mode`

#### `start_recording`
**Syntax**: `start_recording <optional data control switches>`
**Description**: The main data-output mode, optimized for best analog and link data quality. Used internally by many API functions. Data control can also be set using "record_data_defaults".
**Example**: `start_recording DATA = 1 1 1 1`

#### `start_calibration`
**Syntax**: `start_calibration <optional data control switches>`
**Description**: Starts calibration. Data output is available in EyeLink 2.0 and later.
**Example**: `start_calibration DATA = 1 1 1 1`

#### `start_validation`
**Syntax**: `start_validation <optional data control switches>`
**Description**: Starts validation. Data output is available in EyeLink 2.0 and later.
**Example**: `start_validation DATA = 1 1 1 1`

#### `start_drift_correction`
**Syntax**: `start_drift_correction <optional data control switches>`
**Description**: Starts drift correction. Used internally by the API function eyelink_driftcorr_start(). Data output is available in EyeLink 2.0 and later.
**Example**: `start_drift_correction DATA = 1 1 1 1`

#### `set_idle_mode`
**Syntax**: `set_idle_mode <optional data control switches>`
**Description**: Enters Offline mode. This is used by the API functions eyelink_abort() and set_offline_mode(). Data output is available in EyeLink 2.0 and later.
**Example**: `set_idle_mode DATA = 0 0 0 0`

#### `set_imaging_mode`
**Syntax**: `set_imaging_mode`
**Description**: Enters camera-image sending mode. On EyeLink II / CL, this is just turns on image sending in the Camera Setup screen, but it was a completely separate screen in EyeLink 1. No data output is available.
**Example**: `set_imaging_mode`

#### `refresh_buttons`
**Syntax**: `refresh_buttons`
**Description**: A command that forces redraw of mode elements. This is used after commands that change settings, to cause mode display to reflect these.
**Example**: `refresh_buttons`

#### `link_connect_command`
**Syntax**: `link_connect_command = <command string to execute>`
**Description**: Sets command to be executed whenever a computer connects. Use ' ' or " " if spaces in command.
**Example**: `link_connect_command = "echo 'LINK OPENED'"`

#### `link_shutdown_command`
**Syntax**: `link_shutdown_command =  <command string to execute>`
**Description**: Sets command to be executed whenever a computer disconnects. Use ' ' or " " if spaces in command.
**Example**: `link_shutdown_command =  "echo 'LINK CLOSED'"`

#### `exit_program`
**Syntax**: `exit_program`
**Description**: Exits the EyeLink CL executable, closing any open EDF file.
**Example**: `exit_program`

#### `screen_dump`
**Syntax**: `screen_dump <optional file name>`
**Description**: Saves the display to a PCX file. If no file name is given, creates a numbered file name. Adds the extension "PCX" to the file name if needed.
**Example**: `screen_dump`

#### `data_message`
**Syntax**: `data_message <message text>`
**Description**: This places a message in the EDF file. This was intended to allow message sending from digital inputs. NOTE: prior to EyeLink II v2.0, the message timestamp was when the command was executed, not when the command was issued.
**Example**: `data_message`

#### `record_status_message`
**Syntax**: `record_status_message <text message to be displayed in record mode>`
**Description**: Sets title displayed in Record mode. Use "" or ' ' quotes if contains spaces.
**Example**: `record_status_message 'Trial title message'`

#### `reset_record_lock`
**Syntax**: `reset_record_lock`
**Description**: Resets the record duration counter to 0.
**Example**: `reset_record_clock`

#### `set_href_point`
**Syntax**: `set_href_point <point index> <x coord> <y coord>`
**Description**: Sets individual reference gaze positions to be converted to HREF on a sample-by-sample basis. point index: 1 to 4. x coord, y coord: gaze coordinate of reference point.
**Example**: `set_href_point = 1 0 0`

#### `clear_href_points`
**Syntax**: `clear_href_points`
**Description**: Resets all gaze reference points to "MISSING". This can be used if points are to be removed (to reduce sample size).
**Example**: `clear_href_points`

#### `data_drive_name`
**Syntax**: `data_drive_name <dir>`
**Description**: Identifier for drive (or partition) for data files. This can be a volume name (usually "DATA") or a drive specifier such as "C:\".
**Example**: `data_drive_name = "."`

#### `data_drive_directory`
**Syntax**: `data_drive_directory <dir>`
**Description**: The path within the data drive for data files. This is only used if the drive specified. This will be created if it does not exist.
**Example**: `data_drive_directory = "../data"`

#### `data_file_path`
**Syntax**: `data_file_path <dir>`
**Description**: If the two previous options failed, this path will be used. If ".", uses current directory.
**Example**: `data_file_path = "."`

#### `required_disk_space`
**Syntax**: `required_disk_space <size> <min>`
**Description**: Disk space in megabytes to check at startup. Optional second parameter is minimum space to allow file open (default 2 MB).
**Example**: `required_disk_space = 2048`

#### `screen_write_prescale`
**Syntax**: `screen_write_prescale <scalar>`
**Description**: Screen pixels and resolution get prescaled (multiplied) by this value as they're sent to file and link as integers.
**Example**: `screen_write_prescale = 10`

#### `velocity_write_prescale`
**Syntax**: `velocity_write_prescale <scalar>`
**Description**: Velocity data in events gets prescaled (multiplied) by this value as they're sent to file and link as integers.
**Example**: `velocity_write_prescale = 10`

#### `file_event_filter`
**Syntax**: `file_event_filter <vargin>`
**Description**: Messages are always enabled for the file but must be selected for the link. Messages, buttons and input port changes are collected at any time, eye events only while recording. vargin = the data passed are in a list with these types: LEFT (events for one or both eyes), RIGHT, FIXATION (fixation start and end events), FIXUPDATE (fixation pursuit state updates), SACCADE (saccade start and end), BLINK (blink start and end), MESSAGE (messages user notes in file), BUTTON (button 1..8 press or release), INPUT (changes in input port lines).
**Example**: `file_event_filter = LEFT,RIGHT,FIXATION,BLINK,MESSAGE,BUTTON,SACCADE,INPUT`

#### `link_event_filter`
**Syntax**: `link_event_filter <vargin>`
**Description**: Same types as file_event_filter. Messages, buttons and input port changes are collected at any time, eye events only while recording.
**Example**: `link_event_filter = LEFT,RIGHT,FIXATION,BLINK,BUTTON,SACCADE`

#### `file_event_data`
**Syntax**: `file_event_data <vargin>`
**Description**: vargin = the data passed are in a list with these types: GAZE (screen xy gaze position, pupil position for calibration), GAZERES (units-per-degree screen resolution start/end of event), HREF (head-referenced gaze position), AREA (pupil area), VELOCITY (velocity of parsed position-type avg/peak), STATUS (warning and error flags aggregated across event), FIXAVG (include ONLY averages in fixation end events to reduce file size), NOSTART (start events have no data, just time stamp).
**Example**: `file_event_data = GAZE,GAZERES,HREF,AREA,VELOCITY`

#### `link_event_data`
**Syntax**: `link_event_data <vargin>`
**Description**: Same types as file_event_data.
**Example**: `link_event_data = GAZE,GAZERES,HREF,AREA,FIXAVG,NOSTART`

#### `file_sample_data`
**Syntax**: `file_sample_data <vargin>`
**Description**: This command sets the contents of the sample data in the EDF file recording. The data passed are in a list with these types:
- **LEFT/RIGHT**: data for one or both eyes (active_eye limits this for monocular)
- **GAZE**: screen xy (gaze) position (pupil position for calibration)
- **GAZERES**: units-per-degree screen resolution (start, end of event)
- **HREF**: head-referenced gaze position
- **PUPIL**: raw eye camera pupil coordinates
- **AREA**: pupil area
- **VELOCITY**: velocity of parsed position-type (avg, peak)
- **STATUS**: warning and error flags, aggregated across events
- **FIXAVG**: include ONLY averages in fixation end events, to reduce file size
- **NOSTART**: start events have no data, just time stamp
- **BUTTON**: button state and change flags
- **INPUT**: input port data lines
- **HTARGET**: head position data for EyeLink remote
**Example**: `file_sample_data = LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,INPUT,HTARGET`

#### `link_sample_data`
**Syntax**: `link_sample_data <vargin>`
**Description**: Same types as file_sample_data. Controls what is transferred over the link.
**Example**: `link_sample_data = LEFT,RIGHT,GAZE,HREF,GAZERES,AREA,STATUS,HTARGET`

#### `record_data_defaults`
**Syntax**: `record_data_defaults`
**Description**: READ-ONLY. Returns the current record data defaults. Return has 0 for off, 1 for on, and does not report link settings: "<file samples> <file events> 0 0".
**Example**: `record_data_defaults`

#### `file_sample_control`
**Syntax**: `file_sample_control = <output interval>,<movement threshold>, <minimum interval>`
**Description**: Controls the base interval at which samples are written, and writes extra samples if the gaze position has moved significantly since the last sample. First number is the time (msec) between base-rate sample writes (0 means don't put out base rate samples, only motion updates). Second number (float) is the gaze change in screen units since the last sample needed to trigger a motion update (0.0 means don't put out any motion updates). Third number sets the minimum time between motion updates: 2 or less means pass all.
**Example**: `file_sample_control = 1, 0.0, 0`

#### `link_sample_control`
**Syntax**: `link_sample_control = <output interval>,<movement threshold>, <minimum interval>`
**Description**: Same as file_sample_control but for link data.
**Example**: `link_sample_control = 1, 0.0, 0`

#### `link_update_interval`
**Syntax**: `link_update_interval = <time in msec>`
**Description**: Maximum interval (in milliseconds) to send something to connected computer. Any packet (data, image, etc) will do, but empty status packets will be sent if required. This is critical for syncing the tracker time estimate. 0 is off, else msec interval to send.
**Example**: `link_update_interval = 0`

#### `samples_between_timestamps`
**Syntax**: `samples_between_timestamps = <count>`
**Description**: By updating slowly-changing or predictable data items less frequently, file size can be substantially reduced. Can send 4-byte timestamps or 1-byte sample time delta. 0 forces full timestamp on each sample. Full timestamp is ALWAYS sent with link samples.
**Example**: `samples_between_timestamps = 10`

#### `samples_between_resolution`
**Syntax**: `samples_between_resolution = <count>`
**Description**: Controls how often resolution data is included: 0 means that it always included.
**Example**: `samples_between_resolution = 0`

#### `samples_between_status`
**Syntax**: `samples_between_status = <count>`
**Description**: Controls how often error-flags (status) data is included: 0 means always included.
**Example**: `samples_between_status = 0`

#### `samples_between_pupil_area`
**Syntax**: `samples_between_pupil_area = <count>`
**Description**: Controls how often pupil area data is included: 0 means always include. Pupil area is ALWAYS output before/after blink.
**Example**: `samples_between_pupil_area = 0`

#### `link_flush_age`
**Syntax**: `link_flush_age = <0, 1, or msec>`
**Description**: Controls packing of samples into link data packets in record mode. Default of 1 minimizes data latency, with each sample (and any associated events) packed into a single buffer and sent immediately. A setting of 0 only flushes when the buffer is full (5 to 30 samples, depending on contents). Other settings are the maximum age of a sample before flushing.
**Example**: `link_flush_age = 1`

#### `link_motion_flush`
**Syntax**: `link_motion_flush = <switch>`
**Description**: Can send data whenever a link sample motion update occurs, or whenever the position has moved so far relative to the last sample sent to the remote PC that a motion update should have occurred (this is needed if baseline sample rate is high). This is ideal for moving a gaze cursor on the remote PC.
**Example**: `link_motion_flush = NO`

#### `link_sample_recency`
**Syntax**: `link_sample_recency = <time in msec>`
**Description**: May want to add a sample to the buffer before sending it if the latest sample is too old. Specifies the maximum age (in msec) of latest sample.
**Example**: `link_sample_recency = 1`

#### `link_pacing_usec`
**Syntax**: `link_pacing_usec = <microseconds between link image packets>`
**Description**: Forces the Ethernet to wait between issuing packet send requests. The default is 0, for no pacing. If a client computer is being flooded (dropping samples and packets) this may be useful. However, it must be used with caution as it can greatly increase the number of samples delayed by 2 to 6 milliseconds during image streaming. Set to 50 to 100 less than the desired average packet interval, 900 for windows (image and data simultaneously).
**Example**: `link_pacing_usec = 0`

#### `link_echo_filter`
**Syntax**: `link_echo_filter = <list of tracker button and key events>`
**Description**: A set of key and button events on the tracker may be sent to the remote client to be logged or processed. The event types in the list will be echoed: all others will be ignored. Accepted types are: BUTTON (button press and release event), UP (key release events), DOWN (key press events), REPEAT (key repeat events).
**Example**: `link_echo_filter = DOWN, REPEAT, BUTTONS`

#### `do_mode_start_flush`
**Syntax**: `do_mode_start_flush = <switch>`
**Description**: Whether to flush samples that were collected between the end of one mode and the start of the next. If not flushed, these samples (usually no more than 2) will appear at the start of the next mode's data. These samples are likely earlier than the time the mode change command was issued.
**Example**: `do_mode_start_flush = ON`

#### `enable_file_buffer`
**Syntax**: `enable_file_buffer = <switch>`
**Description**: Whether to buffer file data to memory. If true, data is buffered to memory and written to disk in between recordings. If false, data is written directly to disk.
**Example**: `enable_file_buffer = ON`

#### `file_sample_raw_pcr`
**Syntax**: `file_sample_raw_pcr = <SWITCH>`
**Description**: Enables raw PCR mode for file output, which outputs only unmodified full-resolution pupil and CR data. This data is encoded using the RAW (px,py,pa), HREF (hx,hy), and gaze(gx,gy,rx,ry) fields of samples. This data is available at all speeds and for both monocular and binocular tracking modes. The following data types must be enabled for sample data: PUPIL, AREA, GAZE, GAZERES, HREF. Optionally, STATUS, BUTTONS and INPUT can be enabled. ENCODING: pa will be negative if this coding is in effect; rx encodes CR area (ca) for left eye; ry encodes CR area (ca) for right eye. Default: OFF.
**Example**: `file_sample_raw_pcr ON`

#### `link_sample_raw_pcr`
**Syntax**: `link_sample_raw_pcr = <SWITCH>`
**Description**: Enables raw PCR mode for link output, which outputs only unmodified full-resolution pupil and CR data. This data is encoded using the RAW (px,py,pa), HREF (hx,hy), and gaze(gx,gy,rx,ry) fields of samples. This data is available at all speeds and for both monocular and binocular tracking modes. The following data types must be enabled for sample data: PUPIL, AREA, GAZE, GAZERES, HREF. Optionally, STATUS, BUTTONS and INPUT can be enabled. ENCODING: pa will be negative if this coding is in effect; rx encodes CR area (ca) for left eye; ry encodes CR area (ca) for right eye. Default: OFF.
**Example**: `link_sample_raw_pcr ON`

#### `raw_pcr_processing`
**Syntax**: `raw_pcr_processing = <crfixup> <hfilter>`
**Description**: Sets processing for "raw_pcr" output mode. Typically this mode is used for raw pupil and CR data for external processing, and therefore no filtering or corrections are applied. <crfixup> is a switch that sets whether pupil-centroid processing has a correction for CR erosion in position and area. <hfilter> is a code for filtering of position and pupil area (CR area and pupil dimensions are not filtered). Filter codes: X = no filtering, H = single heuristic filter, A = 3-sample moving average. These can be combined into 2 steps, e.g. HH, HA, AA. Default: NO, X.
**Example**: `raw_pcr_processing NO, X`

#### `raw_pcr_dual_corneal`
**Syntax**: `raw_pcr_dual_corneal = <switch>`
**Description**: Enables detection of 2 corneal reflections in raw_pcr mode. These CR's are the 2 candidates closest to the pupil center. ENCODING: first CR encoded as usual; turn HMARKER data type on for samples; htype code = 0xC0 + (word count); for monocular, first 4 words are data; for binocular, first 4 words are L, remainder are R; X and Y are 24 bits, divide by 256 to get actual value. Words: [0] = 16 MSB of X, [1] = 16 MSB of Y, [2] = 2 bytes: (8 LSB of X) (8 LSB of Y), [3] = area (0 = no CR detected). Default: OFF.
**Example**: `raw_pcr_dual_corneal = OFF`

#### `show_exposure`
**Syntax**: `show_exposure <switch>`
**Description**: Allows tracker to display the exposure settings on the camera setup screen.
**Example**: `show_exposure 1`

#### `video_overlay_available`
**Syntax**: `video_overlay_available = <YES or NO>`
**Description**: Sets whether EyeLink is configured for video overlay. In particular, "NO" hides the Video Overlay buttons in the Set Options screen. If not set, this defaults to NO, so the vidovl.ini file can be excluded from the distribution.
**Example**: `video_overlay_available = NO`

#### `video_overlay_on`
**Syntax**: `video_overlay_on = <OFF or ON>`
**Description**: Sets the state of the video overlay mode. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file. OFF if video overlay mode is off; ON if video overlay mode is active.
**Example**: `video_overlay_on = OFF`

#### `video_background_color`
**Syntax**: `video_background_color = <palette index>`
**Description**: Sets the background color for overlay. This is always black (128). palette index (always black = 128).
**Example**: `video_background_color = 128`

#### `video_border_color`
**Syntax**: `video_border_color = <palette index>`
**Description**: Sets the dark gray used for the area of the gaze window outside the active overlay area, and for the gray box on the Video Setup screen. This color should be visibly different from black, but below the default keying level. A palette index of 136 (dark gray) is standard.
**Example**: `video_border_color = 136`

#### `video_monoc_cursor_color`
**Syntax**: `video_monoc_cursor_color = <palette index>`
**Description**: Sets the color of the monocular overlay gaze cursor. If this is not one of the preset options in the Video Setup screen, it will replace the first entry (light gray) in the color choices. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file.
**Example**: `video_monoc_cursor_color = 127`

#### `video_binoc_cursor_colors`
**Syntax**: `video_binoc_cursor_colors = <l>,<r>,<c>`
**Description**: Sets the colors of the binocular gaze cursors. The 3 colors are the left cursor, right cursors, and any overlap between them. <l>: palette index of left cursor (typically 214), <r>: palette index of right cursor (typically 234), <c>: palette index of overlap between left and right cursors (typically 180).
**Example**: `video_binoc_cursor_colors = 214, 234, 180`

#### `video_custom_cursor_color`
**Syntax**: `video_custom_cursor_color = <palette number>`
**Description**: Sets the last color in the cursor color menu on the Video Overlay Setup screen. If a custom cursor color is defined that is not in the menu, this command may be overridden and the custom cursor color placed in this slot instead.
**Example**: `video_custom_cursor_color = 141`

#### `video_cursor_type`
**Syntax**: `video_cursor_type = <shape number>`
**Description**: Sets gaze cursor shape. Choices are 0 (solid), 1 (hollow), 2 (hollow with a cross in). This is updated at the end of each session to lastrun.ini file, which overrides the vidovl.ini file. <shape number>: 0 (solid), 1 (hollow), 2 (hollow with a cross).
**Example**: `video_cursor_type = 0`

#### `video_cursor_limit`
**Syntax**: `video_cursor_limit = <pixels limit on motion>`
**Description**: Sets how far the gaze cursor is allowed to move outside the standard gaze area (set by 'screen_pixel_coords').
**Example**: `video_cursor_limit = 2`

#### `video_dim_mouse_fgcolor`
**Syntax**: `video_dim_mouse_fgcolor = <palette index>`
**Description**: Sets the color for the 'dimmed' mouse pointer allowed inside the active overlay area. Typically 140, or slightly brighter than the border gray.
**Example**: `video_dim_mouse_fgcolor = 140`

#### `video_dim_mouse_bgcolor`
**Syntax**: `video_dim_mouse_bgcolor = <palette index>`
**Description**: Sets the color for the 'dimmed' mouse pointer allowed inside the active overlay area. Typically 128, or black.
**Example**: `video_dim_mouse_bgcolor = 128`

#### `video_cal_hide_cursors`
**Syntax**: `video_cal_hide_cursors = <ON or OFF>`
**Description**: Whether the special video calibration generation option is enabled. This will hide cursors and feedback graphics, and uses a lighter background, allowing overlay to be used to calibrate subject. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file.
**Example**: `video_cal_hide_cursors = OFF`

#### `video_no_record_graphics`
**Syntax**: `video_no_record_graphics = <YES or NO>`
**Description**: WRITEABLE, MENU, LASTRUN.INI. This sets whether the record display is kept clean of graphics during recording. It is used to save and restore the state of the button on the Video Setup screen.
**Example**: `video_no_record_graphics = YES`

#### `video_cal_target_size`
**Syntax**: `video_cal_target_size = <size>`
**Description**: Sets size of calibration targets in video overlay mode. Legal values are 7, 9, 11, or 13 pixels (13 is the regular calibration target size). Smaller sizes are useful when the calibration display is used as a video overlay, to compensate for the magnification of the overlay. <size>: 7, 9, 11, or 13 pixels (9 default).
**Example**: `video_cal_target_size = 11`

#### `video_cal_backgr_color`
**Syntax**: `video_cal_backgr_color = <palette index>`
**Description**: Color of calibration background when the calibration overlay option is enabled (black in normal mode). Default is 156 (medium gray).
**Example**: `video_cal_backgr_color = 156`

#### `video_cal_target_color`
**Syntax**: `video_cal_target_color = <palette index>`
**Description**: Color of calibration targets when the calibration overlay option is enabled (black in normal mode). Default is 127 (bright white).
**Example**: `video_cal_target_color = 127`

#### `video_timecode_mode`
**Syntax**: `video_timecode_mode = <mode>`
**Description**: Sets the timecode mode. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file. <mode>: 0 is off, 1 is absolute, 2 is trial.
**Example**: `video_timecode_mode = 1`

#### `video_timecode_position`
**Syntax**: `video_timecode_position = <x pixel coordinate>, <y pixel coordinate>`
**Description**: Sets position of top-left of timecode display. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file.
**Example**: `video_timecode_position = 200, 100`

#### `video_timecode_bgcolor`
**Syntax**: `video_timecode_bgcolor = <palette index>`
**Description**: Color of timecode background. Default is 150 (gray just brighter than overlay key).
**Example**: `video_timecode_bgcolor = 150`

#### `video_timecode_fgcolor`
**Syntax**: `video_timecode_fgcolor = <palette index>`
**Description**: Color of timecode numbers. Default is 127 (bright white).
**Example**: `video_timecode_fgcolor = 127`

#### `video_window_default`
**Syntax**: `video_window_default = <l>,<t>,<r>,<b>`
**Description**: Sets the large dark gray box on the Video Setup display used for overlay setup. Also is the overlay window size set by pressing the F9 key. Typically 205, 23, 586, 351 for smaller '2x zoom' overlay area and 116, 35, 560, 360 for large overlay area.
**Example**: `video_window_default = 116, 35, 560, 360`

#### `video_window`
**Syntax**: `video_window = <l>,<t>,<r>,<b>`
**Description**: Sets the overlay window size and position. This is updated at the end of each session to the lastrun.ini file, which overrides the vidovl.ini file. <l>,<t>,<r>,<b>: box coordinates.
**Example**: `video_window = 222, 203, 574, 428`

#### `video_avi_timecode_enabled`
**Syntax**: `video_avi_timecode_enabled = <ON or OFF>`
**Description**: Controls display of machine-readable timecode line. Must be set before entry to record mode.
**Example**: `video_avi_timecode_enabled = NO`

#### `video_avi_timecode_offset`
**Syntax**: `video_avi_timecode_offset = <x offset> <y offset>`
**Description**: Sets offset of left end of timecode line relative to video window. Offset is in overlay pixels (each is 2 AVI lines by ~2 pixels). Default is 0, 0.
**Example**: `video_avi_timecode_offset = 0,0`

#### `video_click_dcorr`
**Syntax**: `video_click_dcorr = <ON or OFF>`
**Description**: Whether the drift correction by mouse button click is available in video overlay mode (default is ON).
**Example**: `video_click_dcorr = OFF`

####  `sample_rate`
**Syntax**: `sample_rate = <rate>`
**Description**: Sampling rate of the eye tracker (in Hz). Can only be changed in offline and camera setup modes. If changed in offline mode, may switch to camera setup mode. Common values: 250, 500, 1000, 2000 Hz. Default: 1000 Hz.
**Example**: `sample_rate = 1000`
---
