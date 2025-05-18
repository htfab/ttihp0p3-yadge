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

gds_height = top_cell.bounding_box()[1][1]
stripe_height = gds_height
panel_gap = 2.0  # µm
theta = 53  # degrees


def calculate_pitch(m: int, wavelength_nm: float, theta_deg: float) -> float:
    """
    Calculates the slit pitch 'd' using the diffraction grating equation:
        d * sin(theta) = m * lambda

    Parameters:
    - m: Order of the diffraction (integer)
    - wavelength: Wavelength of light in nanometers (float)
    - theta_deg: Diffraction angle in degrees (float)

    Returns:
    - d: Slit spacing in um (float)
    """
    wavelength_m = wavelength_nm * 1e-9
    return (m * wavelength_m / math.sin(math.radians(theta_deg))) * 1e6


def align_to_grid(value: float):
    """
    Aligns the given point x/y value to a 5 nm grid
    """
    return round(value * 200) / 200


# Panel parameters: (name, wavelength_nm, diffraction order, stripe_w, gap, panel_width)
panels = [
    ("G", 526, 7, 2.00, 50),  # Green
    ("R", 667, 6, 2.00, 50),  # Red
    ("Y", 580, 6, 2.00, 50),  # Yellow
    ("B", 457, 7, 2.00, 50),  # Blue
]

x = 0.0
for name, wavelength_nm, m, stripe_w, panel_width in panels:
    pitch = align_to_grid(calculate_pitch(m, wavelength_nm, theta))
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
    print(f"Panel: {name}, λ={wavelength_nm}, m={m}, pitch={pitch}")
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
