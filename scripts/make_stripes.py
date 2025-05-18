# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Uri Shaked

import os

import gdstk

topmetal2_layer = 134
topmetal2_datatype = 0
topmetal2_nofill = 23
script_path = os.path.dirname(os.path.abspath(__file__))

# Load the original GDSII file
lib = gdstk.read_gds(os.path.join(script_path, "../gds/tt_um_template_1x1.gds"))
top_cell = lib.top_level()[0]

gds_height = top_cell.bounding_box()[1][1]
stripe_height = gds_height
panel_gap = 2.0  # µm


def add_stripe_panel(cell, stripe_w, pitch, panel_width):
    x = 0.0
    while x + stripe_w <= panel_width:
        cell.add(rect)
        x += pitch


# Panel parameters: (name, pitch, stripe_w, gap, panel_width)
panels = [
    ("G", 4.60, 2.00, 50),  # Green
    ("R", 5.00, 2.00, 50),  # Red
    ("Y", 4.35, 2.00, 50),  # Yellow
    ("B", 4.00, 2.00, 50),  # Blue
]

x = 0.0
for name, pitch, stripe_w, panel_width in panels:
    subcell = gdstk.Cell(f"panel_{name}")
    rect = gdstk.rectangle(
        (0, 0),
        (stripe_w, stripe_height),
        layer=topmetal2_layer,
        datatype=topmetal2_datatype,
    )
    subcell.add(rect)
    lib.add(subcell)
    columns = int(panel_width / pitch)
    top_cell.add(
        gdstk.Reference(
            subcell, (x, 0.0), columns=columns, rows=1, spacing=(pitch, 0.0)
        )
    )
    x += panel_width + panel_gap

# No fill for the whole cell
no_fill_rect = gdstk.rectangle(
    (0, 0),
    (top_cell.bounding_box()[1][0], top_cell.bounding_box()[1][1]),
    layer=topmetal2_layer,
    datatype=topmetal2_nofill,
)
top_cell.add(no_fill_rect)

top_cell.name = "tt_um_colorful_stripes"
lib.write_gds(os.path.join(script_path, "../gds/tt_um_colorful_stripes.gds"))
