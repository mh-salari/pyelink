"""Sphinx extension to generate a default settings table from pyelink.settings.Settings."""

from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx


class SettingsTableDirective(Directive):
    """Generate a table of all Settings fields with their default values."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> list[nodes.Node]:
        """Build the settings table from the Settings model."""
        from pyelink.settings import Settings

        result_nodes = []

        # Group fields by their section comments in the source
        sections = {
            "File Settings": ["filename", "filepath", "enable_long_filenames", "max_filename_length"],
            "Sampling Settings": ["sample_rate"],
            "Calibration Settings": [
                "n_cal_targets",
                "enable_automatic_calibration",
                "pacing_interval",
                "calibration_corner_scaling",
                "validation_corner_scaling",
                "calibration_area_proportion",
                "validation_area_proportion",
            ],
            "Target Appearance": [
                "target_type",
                "target_image_path",
                "cal_background_color",
                "calibration_instruction_text",
                "calibration_text_color",
                "calibration_text_font_size",
                "calibration_text_font_name",
                "calibration_instruction_page_callback",
                "fixation_center_diameter",
                "fixation_outer_diameter",
                "fixation_cross_width",
                "fixation_center_color",
                "fixation_outer_color",
                "fixation_cross_color",
                "circle_outer_radius",
                "circle_inner_radius",
                "circle_outer_color",
                "circle_inner_color",
            ],
            "Screen Physical Settings": [
                "screen_res",
                "screen_width",
                "screen_height",
                "camera_to_screen_distance",
                "screen_distance",
                "screen_distance_top_bottom",
                "camera_lens_focal_length",
            ],
            "Display Backend": ["backend", "fullscreen", "display_index"],
            "Tracking Settings": [
                "pupil_tracking_mode",
                "pupil_size_mode",
                "heuristic_filter",
                "set_heuristic_filter",
                "enable_dual_corneal_tracking",
            ],
            "Data Recording": [
                "file_event_filter",
                "link_event_filter",
                "link_sample_data",
                "file_sample_data",
                "record_samples_to_file",
                "record_events_to_file",
                "record_sample_over_link",
                "record_event_over_link",
            ],
            "Hardware Settings": [
                "enable_search_limits",
                "track_search_limits",
                "autothreshold_click",
                "autothreshold_repeat",
                "enable_camera_position_detect",
                "illumination_power",
                "host_ip",
            ],
            "Physical Setup": ["el_configuration", "eye_tracked"],
        }

        for section_title, field_names in sections.items():
            # Section heading
            section = nodes.section(ids=[nodes.make_id(section_title)])
            title = nodes.title(text=section_title)
            section += title

            # Build table
            table = nodes.table()
            tgroup = nodes.tgroup(cols=3)
            table += tgroup

            tgroup += nodes.colspec(colwidth=30)
            tgroup += nodes.colspec(colwidth=25)
            tgroup += nodes.colspec(colwidth=45)

            # Header
            thead = nodes.thead()
            tgroup += thead
            header_row = nodes.row()
            thead += header_row
            for header_text in ("Setting", "Default", "Description"):
                entry = nodes.entry()
                entry += nodes.paragraph(text=header_text)
                header_row += entry

            # Body
            tbody = nodes.tbody()
            tgroup += tbody

            for field_name in field_names:
                if field_name not in Settings.model_fields:
                    continue

                field_info = Settings.model_fields[field_name]
                default = field_info.default

                # Format default value
                if default is None:
                    default_str = "None"
                elif isinstance(default, str) and len(default) > 40:
                    default_str = f'"{default[:37]}..."'
                elif isinstance(default, str):
                    default_str = f'"{default}"'
                else:
                    default_str = repr(default)

                # Get first line of description
                desc = field_info.description or ""
                first_line = desc.strip().split("\n")[0].strip()

                row = nodes.row()
                tbody += row

                # Setting name (as code)
                name_entry = nodes.entry()
                name_entry += nodes.literal(text=field_name)
                row += name_entry

                # Default value (as code)
                default_entry = nodes.entry()
                default_entry += nodes.literal(text=default_str)
                row += default_entry

                # Description
                desc_entry = nodes.entry()
                desc_entry += nodes.paragraph(text=first_line)
                row += desc_entry

            section += table
            result_nodes.append(section)

        return result_nodes


def setup(app: Sphinx) -> dict:
    """Register the directive."""
    app.add_directive("settings-table", SettingsTableDirective)
    return {"version": "1.0", "parallel_read_safe": True}
