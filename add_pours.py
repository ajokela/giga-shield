#!/usr/bin/env python3
"""Add GND copper pour on bottom layer and stitching vias to the routed giga-shield PCB."""
import re

BOARD_W = 155000000  # 155mm in nm
BOARD_H = 90000000   # 90mm in nm
MARGIN = 500000      # 0.5mm margin from board edge

def mm(val):
    return int(val * 1000000)

# Read the routed PCB
with open('giga_shield.pcb', 'r') as f:
    pcb = f.read()

# Board polygon coordinates (with margin)
x1 = MARGIN
y1 = MARGIN
x2 = BOARD_W - MARGIN
y2 = BOARD_H - MARGIN

# GND polygon for bottom layer (full board)
gnd_polygon = f'''	Polygon("clearpoly")
	(
		[{x1}nm {y1}nm] [{x2}nm {y1}nm] [{x2}nm {y2}nm] [{x1}nm {y2}nm]
	)'''

# Shifter IC positions and their GND/power pin locations
# SN74LVC8T245PW TSSOP-24: pins 6, 11, 12 are GND; 22,23 are VCCA(+3V3); 17,24 are VCCB(+5V)
# Pitch 0.65mm, span 6.4mm center-to-center, 12 pins per side
# Pin 6 is left side, 6th from top; Pin 11 is left side, 11th; Pin 12 is left side, 12th
# Pins 17,22,23,24 are right side

KX = 106.0
KY = 30.5

def kpos(kx, ky):
    return (mm(kx - KX), mm(ky - KY))

SHIFTERS = {
    'U1': kpos(152.3, 45.8),
    'U2': kpos(184.8, 89.0),
    'U3': kpos(174.6, 46.7),
    'U4': kpos(200.4, 89.1),
    'U5': kpos(195.8, 45.7),
    'U6': kpos(232.6, 62.2),
    'U7': kpos(233.2, 99.1),
    'U8': kpos(232.5, 74.0),
    'U9': kpos(232.7, 85.7),
    'U10': kpos(233.0, 112.0),
}

# TSSOP-24 geometry
pitch = mm(0.65)
half_span = mm(6.40) // 2
y_start_offset = -pitch * 11 // 2  # center 12 pins vertically

def tssop24_pin_pos(ux, uy, pin_num):
    """Get absolute position of a TSSOP-24 pin."""
    if pin_num <= 12:
        # Left side, pins 1-12 top to bottom
        px = ux - half_span
        py = uy + y_start_offset + (pin_num - 1) * pitch
    else:
        # Right side, pins 13-24 bottom to top
        px = ux + half_span
        py = uy - y_start_offset - (pin_num - 13) * pitch
    return (px, py)

# Generate stitching vias near GND pads of each shifter IC
# GND pins: 6, 11, 12
# Via: 508000nm pad, 254000nm drill, 127000nm clearance, 558000nm mask
via_entries = []
via_offset = mm(1.5)  # offset from pad center to avoid pad overlap

for uref, (ux, uy) in SHIFTERS.items():
    for gnd_pin in [6, 11, 12]:
        px, py = tssop24_pin_pos(ux, uy, gnd_pin)
        # Place via slightly to the left of the left-side pads
        vx = px - via_offset
        vy = py
        via_entries.append(f'Via[{vx}nm {vy}nm 508000nm 127000nm 558000nm 254000nm "" ""]')

# Also add stitching vias near cap GND pads (pin 2 of each 0603 cap)
# Cap positions from build script: each IC gets 2 caps at (ux+3mm, uy-6mm) and (ux-3mm, uy-6mm)
cap_via_offset = mm(1.2)
for uref, (ux, uy) in SHIFTERS.items():
    # VCCA cap at (ux + 3mm, uy - 6mm) - pin 2 is at +0.75mm (right pad)
    cx1 = ux + mm(3) + mm(0.75)
    cy1 = uy - mm(6)
    via_entries.append(f'Via[{cx1}nm {cy1 + cap_via_offset}nm 508000nm 127000nm 558000nm 254000nm "" ""]')

    # VCCB cap at (ux - 3mm, uy - 6mm) - pin 2 is at +0.75mm (right pad)
    cx2 = ux - mm(3) + mm(0.75)
    cy2 = uy - mm(6)
    via_entries.append(f'Via[{cx2}nm {cy2 + cap_via_offset}nm 508000nm 127000nm 558000nm 254000nm "" ""]')

# Add a grid of stitching vias across the board for good GND coverage
grid_spacing = mm(15)
for gx in range(mm(10), BOARD_W - mm(5), grid_spacing):
    for gy in range(mm(10), BOARD_H - mm(5), grid_spacing):
        via_entries.append(f'Via[{gx}nm {gy}nm 508000nm 127000nm 558000nm 254000nm "" ""]')

print(f"Adding {len(via_entries)} stitching vias")

# Insert vias before Layer(1
lines = pcb.split('\n')
output = []
via_inserted = False

for i, line in enumerate(lines):
    if not via_inserted and line.startswith('Layer(1 '):
        # Insert vias before first Layer
        for ve in via_entries:
            output.append(ve)
        via_inserted = True

    # Insert GND polygon into Layer 2
    if line.startswith('Layer(2 "bottom")'):
        output.append(line)
        # Next line should be "("
        i_next = i + 1
        continue

    output.append(line)

# Now re-process to insert polygon into layer 2
final = []
in_layer2 = False
for line in output:
    final.append(line)
    if 'Layer(2 "bottom")' in line:
        in_layer2 = True
    elif in_layer2 and line.strip() == '(':
        final.append(gnd_polygon)
        in_layer2 = False

with open('giga_shield.pcb', 'w') as f:
    f.write('\n'.join(final))

print(f"Added GND copper pour on bottom layer")
print(f"Board area: {BOARD_W/1e6:.0f}mm x {BOARD_H/1e6:.0f}mm")
