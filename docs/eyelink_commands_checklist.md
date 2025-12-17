# EyeLink Commands Implementation Status

List of commands from eyelink_commands_reference.md that have been used in pyelink.

1. [ ] abort_file_transfer
2. [ ] abort_playback
3. [ ] accept_target_fixation
4. [x] active_eye — **Used in:** pyelink/core.py, pyelink/settings.py
5. [ ] add_file_preamble_text
6. [x] allow_pupil_without_cr — **Used in:** pyelink/core.py
7. [ ] always_default_calibration
8. [ ] ambient_filter_constant
9. [ ] analog_binocular_mapping
10. [ ] analog_dac_range
11. [ ] analog_force_4channel
12. [ ] analog_no_pupil_value
13. [ ] analog_out_data_type
14. [ ] analog_p_maximum
15. [ ] analog_strobe_delay
16. [ ] analog_strobe_line
17. [ ] analog_strobe_polarity
18. [ ] analog_strobe_time
19. [ ] analog_x_range
20. [ ] analog_y_range
21. [ ] apply_last_drift_correction
22. [ ] auto_calibration_messages
23. [ ] autocal_minimum_fixation
24. [ ] autocal_minimum_saccade
25. [ ] autocal_saccade_fraction
26. [ ] automatic_calibration_pacing
27. [x] autothreshold_click — **Used in:** pyelink/settings.py, pyelink/calibration/base.py
28. [x] autothreshold_repeat — **Used in:** pyelink/settings.py, pyelink/calibration/base.py
29. [ ] aux_mouse_simulation
30. [ ] begin_macro
31. [x] binocular_enabled — **Used in:** pyelink/core.py, pyelink/settings.py
32. [ ] black_filter_constant
33. [ ] blink_offset_verify_time
34. [ ] button_debounce_time
35. [ ] button_function
36. [ ] button_status_display
37. [ ] cal_repeat_first_target
38. [x] calibration_area_proportion — **Used in:** pyelink/core.py, pyelink/settings.py
39. [ ] calibration_average
40. [ ] calibration_bicubic_correction
41. [ ] calibration_bicubic_weights
42. [ ] calibration_collection_interval
43. [x] calibration_corner_scaling — **Used in:** pyelink/core.py, pyelink/settings.py
44. [ ] calibration_fixation_data
45. [ ] calibration_samples
46. [ ] calibration_sequence
47. [ ] calibration_status
48. [ ] calibration_targets
49. [x] calibration_type — **Used in:** pyelink/core.py
50. [ ] call_option_menu_mode
51. [ ] call_setup_menu_mode
52. [ ] camera_color_ramp
53. [ ] cl_edf_identifier
54. [ ] clear_button_list
55. [ ] clear_href_points
56. [x] clear_screen — **Used in:** pyelink/core.py
57. [x] close_data_file — **Used in:** pyelink/core.py
58. [ ] collect_target_fixation
59. [x] corneal_mode — **Used in:** pyelink/core.py
60. [ ] corneal_select_limits
61. [ ] corneal_select_size
62. [ ] create_button
63. [ ] create_key_button
64. [ ] current_camera
65. [ ] data_drive_directory
66. [ ] data_drive_name
67. [ ] data_file_name
68. [ ] data_file_path
69. [ ] data_message
70. [ ] default_eye_mapping
71. [ ] delete_all_key_buttons
72. [ ] delete_all_key_functions
73. [ ] delete_macro
74. [ ] disable_cal_auto_manual_switch
75. [ ] disable_cal_auto_sequence
76. [ ] disable_cal_backspace
77. [ ] disable_cal_trigger
78. [ ] disable_corneal_reflection
79. [ ] disable_gaze_cursors
80. [ ] disable_head_camera
81. [ ] display_user_menu
82. [ ] do_macro
83. [ ] do_mode_start_flush
84. [ ] draw_box
85. [x] draw_cross — **Used in:** pyelink/calibration/psychopy_backend.py, pyelink/calibration/base.py
86. [ ] draw_filled_box
87. [x] draw_line — **Used in:** pyelink/calibration/pyglet_backend.py, pyelink/calibration/pygame_backend.py, pyelink/calibration/psychopy_backend.py, pyelink/calibration/base.py
88. [ ] draw_link_crosshairs
89. [x] draw_text — **Used in:** pyelink/core.py, pyelink/display/pyglet_display.py, pyelink/display/psychopy_display.py, pyelink/display/pygame_display.py, pyelink/display/base.py
90. [ ] drift_correct_mouse
91. [ ] drift_correction
92. [ ] drift_correction_fraction
93. [ ] drift_correction_rpt_beep
94. [ ] drift_correction_rpt_error
95. [ ] drift_correction_samples
96. [ ] drift_correction_targets
97. [ ] drift_correction_weights
98. [ ] driftcorrect_cr_disable
99. [ ] echo
100. [x] elcl_hold_if_no_corneal — **Used in:** pyelink/core.py
101. [ ] elcl_pupil_symmetry_gain
102. [x] elcl_search_if_no_corneal — **Used in:** pyelink/core.py
103. [x] elcl_use_pcr_matching — **Used in:** pyelink/core.py
104. [x] enable_automatic_calibration — **Used in:** pyelink/core.py, pyelink/settings.py
105. [x] enable_camera_position_detect — **Used in:** pyelink/settings.py, pyelink/calibration/base.py
106. [ ] enable_file_buffer
107. [x] enable_search_limits — **Used in:** pyelink/settings.py, pyelink/calibration/base.py
108. [ ] end_macro
109. [ ] exit_program
110. [ ] eye_current_limit
111. [ ] eyelink_file_xfer_packets
112. [ ] fast_velocity_filter
113. [ ] file_buffer_record_display
114. [ ] file_event_data
115. [x] file_event_filter — **Used in:** pyelink/core.py, pyelink/settings.py
116. [ ] file_sample_control
117. [x] file_sample_data — **Used in:** pyelink/core.py, pyelink/settings.py
118. [x] file_sample_raw_pcr — **Used in:** pyelink/core.py
119. [ ] fixation_update_accumulate
120. [ ] fixation_update_interval
121. [ ] flush_logfile
122. [x] force_corneal_reflection — **Used in:** pyelink/core.py
123. [ ] force_elcl_mode
124. [ ] force_network_present
125. [ ] generate_default_targets
126. [ ] hcam_center
127. [ ] hcam_scale
128. [x] heuristic_filter — **Used in:** pyelink/core.py, pyelink/settings.py
129. [ ] hide_abort_trial
130. [ ] horizontal_target_y
131. [ ] image_from_setup_menu
132. [ ] imager_gain
133. [ ] initial_thresholds
134. [ ] input_data_masks
135. [ ] input_data_ports
136. [ ] key_function
137. [ ] last_button_list
138. [ ] last_button_pressed
139. [ ] left_eye_head_camera_offset
140. [ ] link_connect_command
141. [ ] link_echo_filter
142. [ ] link_event_data
143. [x] link_event_filter — **Used in:** pyelink/core.py, pyelink/settings.py
144. [ ] link_flush_age
145. [ ] link_motion_flush
146. [ ] link_pacing_usec
147. [ ] link_sample_control
148. [x] link_sample_data — **Used in:** pyelink/core.py, pyelink/settings.py
149. [x] link_sample_raw_pcr — **Used in:** pyelink/core.py
150. [ ] link_sample_recency
151. [ ] link_shutdown_command
152. [ ] link_update_interval
153. [ ] lock_active_eye
154. [ ] lock_eye_after_calibration
155. [ ] lock_record_exit
156. [ ] logfile_contents
157. [ ] macro_line
158. [ ] manual_collection_fixation_lookback
159. [ ] manual_collection_minimum_fixation
160. [ ] mark_playback_start
161. [ ] mirror_elcl_image
162. [ ] mirror_eyecam_image
163. [ ] mirror_headcam_image
164. [ ] normal_click_dcorr
165. [ ] online_dcorr_button
166. [ ] online_dcorr_collection_time
167. [ ] online_dcorr_max_lookback
168. [ ] online_dcorr_maxangle
169. [ ] online_dcorr_refposn
170. [ ] online_dcorr_trigger
171. [x] open_data_file — **Used in:** pyelink/core.py
172. [ ] option_menu_mode
173. [ ] output_menu_mode
174. [ ] parser_discard_startup
175. [ ] print_position
176. [ ] pupil_crosstalk_fixup
177. [ ] pupil_min_size
178. [ ] pupil_select_limits
179. [ ] pupil_select_size
180. [x] pupil_size_diameter — **Used in:** pyelink/core.py
181. [ ] randomize_calibration_order
182. [ ] randomize_validation_order
183. [x] raw_pcr_dual_corneal — **Used in:** pyelink/core.py
184. [ ] raw_pcr_processing
185. [ ] read_ioport
186. [ ] rec_plot_colors
187. [ ] rec_plot_mclick_step
188. [ ] rec_plot_simple_offset
189. [ ] record_data_defaults
190. [x] record_status_message — **Used in:** pyelink/core.py
191. [ ] recording_parse_type
192. [ ] refresh_buttons
193. [ ] remote_cal_complete
194. [ ] remote_cal_data
195. [ ] remote_cal_enable
196. [ ] remote_cal_href_data
197. [ ] remote_cal_target
198. [x] remote_camera_position — **Used in:** pyelink/core.py
199. [ ] required_disk_space
200. [ ] reset_cal_data_points
201. [ ] reset_record_lock
202. [ ] restore_old_calibration
203. [ ] right_eye_head_camera_offset
204. [ ] saccade_acceleration_threshold
205. [ ] saccade_extend_velocity
206. [ ] saccade_max_extend_after
207. [ ] saccade_max_extend_start
208. [ ] saccade_motion_threshold
209. [ ] saccade_offset_verify_time
210. [ ] saccade_onset_verify_time
211. [ ] saccade_pursuit_fixup
212. [ ] saccade_velocity_threshold
213. [ ] samples_between_pupil_area
214. [ ] samples_between_resolution
215. [ ] samples_between_status
216. [ ] samples_between_timestamps
217. [x] screen_distance — **Used in:** pyelink/core.py, pyelink/settings.py, pyelink/calibration/targets.py
218. [ ] screen_dump
219. [x] screen_phys_coords — **Used in:** pyelink/core.py
220. [x] screen_pixel_coords — **Used in:** pyelink/core.py
221. [ ] screen_write_prescale
222. [ ] search_limits_rect
223. [ ] search_limits_shape
224. [ ] search_limits_size
225. [ ] select_eye_after_validation
226. [ ] select_parser_configuration
227. [ ] set_href_point
228. [x] set_idle_mode — **Used in:** pyelink/core.py
229. [ ] set_image_channel
230. [ ] set_imaging_mode
231. [ ] set_record_data_defaults
232. [x] setup_menu_mode — **Used in:** pyelink/core.py
233. [ ] show_exposure
234. [ ] start_bitmap_transfer
235. [ ] start_calibration
236. [ ] start_drift_correction
237. [ ] start_file_transfer
238. [ ] start_in_camera_setup
239. [ ] start_playback
240. [x] start_recording — **Used in:** pyelink/__init__.py, pyelink/core.py
241. [ ] start_validation
242. [x] sticky_mode_data_enable — **Used in:** pyelink/core.py
243. [ ] sticky_mode_parse_type
244. [ ] stop_bitmap_transfer
245. [x] track_search_limits — **Used in:** pyelink/settings.py, pyelink/calibration/base.py
246. [ ] use_camimg_palette_colors
247. [ ] use_high_speed
248. [ ] user_record_key_item
249. [ ] val_repeat_first_target
250. [x] validation_area_proportion — **Used in:** pyelink/core.py, pyelink/settings.py
251. [x] validation_corner_scaling — **Used in:** pyelink/core.py, pyelink/settings.py
252. [ ] validation_correct_drift
253. [ ] validation_maximum_deviation
254. [ ] validation_online_fixup
255. [ ] validation_resample_worst
256. [ ] validation_samples
257. [ ] validation_sequence
258. [ ] validation_targets
259. [ ] validation_weights
260. [ ] validation_worst_error
261. [ ] velocity_write_prescale
262. [ ] video_avi_timecode_enabled
263. [ ] video_avi_timecode_offset
264. [ ] video_background_color
265. [ ] video_binoc_cursor_colors
266. [ ] video_border_color
267. [ ] video_cal_backgr_color
268. [ ] video_cal_hide_cursors
269. [ ] video_cal_target_color
270. [ ] video_cal_target_size
271. [ ] video_click_dcorr
272. [ ] video_cursor_limit
273. [ ] video_cursor_type
274. [ ] video_custom_cursor_color
275. [ ] video_dim_mouse_bgcolor
276. [ ] video_dim_mouse_fgcolor
277. [ ] video_monoc_cursor_color
278. [ ] video_no_record_graphics
279. [ ] video_overlay_available
280. [ ] video_overlay_on
281. [ ] video_timecode_bgcolor
282. [ ] video_timecode_fgcolor
283. [ ] video_timecode_mode
284. [ ] video_timecode_position
285. [ ] video_window
286. [ ] video_window_default
287. [ ] write_ioport
288. [ ] x_gaze_constraint
289. [ ] y_gaze_constraint
