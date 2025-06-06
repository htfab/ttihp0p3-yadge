# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Uri Shaked

import os
import math

import gdstk

topmetal2_layer = 134
topmetal2_datatype = 0
topmetal2_nofill = 23
script_path = os.path.dirname(os.path.abspath(__file__))

# Load the original GDSII file
lib = gdstk.read_gds(os.path.join(script_path, "../gds/tt_um_template_1x1.gds"))
top_cell = lib.top_level()[0]

gds_width, gds_height = top_cell.bounding_box()[1]
panel_gap = 2.0  # µm
theta = 53  # degrees


def align_to_grid(value: float):
    """
    Aligns the given point x/y value to a 5 nm grid
    """
    return round(value * 200) / 200

colors = {
    'B': 470,  # blue
    'G': 510,  # green
    'Y': 570,  # yellow
    'R': 650,  # red
    'I': 760,  # invisible
}

alt_stripes_h = [(0, 7), (28, 47), (68, 87), (108, 127), (148, gds_height)]
alt_stripes_v = [(0, 9.06), (44.24, 56.2), (92.15, 106.5), (143.22, 158), (192, gds_width)]

patterns = [
    ('R', [((0, 129), (gds_width+2, 146), 'V')] + [((11.06, y1), (45, y2), 'V') for y1, y2 in alt_stripes_h]),
    ('Y', [((0, 89), (gds_width+2, 106), 'V')] + [((58.2, y1), (93, y2), 'V') for y1, y2 in alt_stripes_h]),
    ('G', [((0, 49), (gds_width+2, 66), 'V')] + [((108.5, y1), (144, y2), 'V') for y1, y2 in alt_stripes_h]),
    ('B', [((0, 9), (gds_width+2, 26), 'V')] + [((160, y1), (193, y2), 'V') for y1, y2 in alt_stripes_h]),
    ('I', [((x1, y1), (x2, y2), 'F') for y1, y2 in alt_stripes_h for x1, x2 in alt_stripes_v]),
]

min_pitch = 4.0
gap_width = 2.0
min_wavelength_nm = 470
for name, areas in patterns:
    wavelength_nm = colors[name]
    pitch = align_to_grid(wavelength_nm/min_wavelength_nm * min_pitch)
    stripe_width = pitch - gap_width
    for i, ((x1, y1), (x2, y2), d) in enumerate(areas):
        subcell = gdstk.Cell(f"pattern_{name}{i}")
        rect = gdstk.rectangle(
            (0, 0),
            (x2-x1 if d in 'HF' else stripe_width, y2-y1 if d in 'VF' else stripe_width),
            layer=topmetal2_layer,
            datatype=topmetal2_datatype,
        )
        subcell.add(rect)
        lib.add(subcell)
        columns = 1 if d in 'HF' else int((x2-x1) / pitch)
        rows = 1 if d in 'VF' else int((y2-y1) / pitch)
        top_cell.add(
            gdstk.Reference(
                subcell, (x1, y1), columns=columns, rows=rows, spacing=(pitch, pitch)
            )
        )
    print(f"Pattern: {name}, λ={wavelength_nm}, pitch={pitch}")

# Add partial top-right "red" cell manually
subcell = gdstk.Cell("pattern_Rx")
rect = gdstk.rectangle((0, 0), (3, 17), layer=topmetal2_layer, datatype=topmetal2_datatype)
subcell.add(rect)
lib.add(subcell)
top_cell.add(gdstk.Reference(subcell, (199.08, 129)))

# No fill for the whole cell
no_fill_rect = gdstk.rectangle(
    (0, 0),
    (top_cell.bounding_box()[1][0], top_cell.bounding_box()[1][1]),
    layer=topmetal2_layer,
    datatype=topmetal2_nofill,
)
top_cell.add(no_fill_rect)

top_cell.name = "tt_um_htfab_yadge"
lib.write_gds(os.path.join(script_path, "../gds/tt_um_htfab_yadge.gds"))
