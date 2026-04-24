#!/usr/bin/env python3
"""Add GND connections to the routed giga-shield PCB.

Strategy: place a via near each SMD GND pad, drop to the bottom layer,
and connect all GND points with traces on the bottom layer.

GND pads:
  - IC pins 6, 11, 12 (SMD, top layer) x 10 ICs = 30 pads
  - Cap pin 2 (SMD, top layer) x 29 caps = 29 pads
  - Resistor pin 2 (SMD, top layer) x 10 resistors = 10 pads
  - Connector through-hole pins: J5-6, J5-7, J11-11 = 3 pads (already on bottom)
"""

import re, math

# ============================================================
# Board geometry (must match build_giga_shield.py exactly)
# ============================================================
def mm(val):
    return int(val * 1000000)

KX = 106.0
KY = 30.5
def kpos(kx, ky):
    return (mm(kx - KX), mm(ky - KY))

# TSSOP-24 geometry
TSSOP_PITCH = mm(0.65)
TSSOP_SPAN = mm(6.40)   # pad center-to-center across body
TSSOP_PAD_LEN = mm(1.20)

# 0603 geometry
SMD0603_PX = mm(0.75)  # center-to-center / 2

# Via geometry
VIA_DRILL = mm(0.508)
VIA_COPPER = mm(0.127)
VIA_OUTER = mm(0.558)
VIA_CLEAR = mm(0.254)

# Trace geometry
TRACE_WIDTH = mm(0.508)  # 20 mil power traces
TRACE_CLEAR = mm(0.200)

# ============================================================
# Component positions (copy from build_giga_shield.py)
# ============================================================
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

CONNECTORS = {
    'J5': kpos(146.64, 114.67),
    'J11_pos': (mm(40), mm(75)),
}

# ============================================================
# Calculate GND pad absolute positions
# ============================================================
def tssop_pad_pos(ic_x, ic_y, pin_num):
    """Get absolute pad center position for a TSSOP-24 pin."""
    y_start = -TSSOP_PITCH * 11 // 2  # center 12 pins vertically

    if 1 <= pin_num <= 12:
        # Left side, top to bottom
        px = -TSSOP_SPAN // 2
        py = y_start + (pin_num - 1) * TSSOP_PITCH
    else:
        # Right side, bottom to top (pin 13 at bottom)
        px = TSSOP_SPAN // 2
        py = -y_start - (pin_num - 13) * TSSOP_PITCH

    return (ic_x + px, ic_y + py)


def smd0603_pad_pos(comp_x, comp_y, pin_num):
    """Get absolute pad center position for 0603 component."""
    if pin_num == 1:
        return (comp_x - SMD0603_PX, comp_y)
    else:
        return (comp_x + SMD0603_PX, comp_y)


def j5_pin_pos(pin_num):
    """J5 is a 1x26 header at kpos(146.64, 114.67) rotated 90°."""
    jx, jy = kpos(146.64, 114.67)
    pitch = mm(2.54)
    # Rotated 90°: pins go along x-axis
    offset = (pin_num - 1) * pitch
    # For 90° rotation in pcb-rnd: x -> -y, y -> x (from original vertical)
    # Original (vertical): pin at (0, offset from center)
    half = pitch * 25 // 2
    orig_y = -half + (pin_num - 1) * pitch
    # After 90° rotation
    return (jx - orig_y, jy)


def j11_pin_pos(pin_num):
    """J11 is a 1x11 header at (40mm, 75mm) rotated 90°."""
    jx, jy = mm(40), mm(75)
    pitch = mm(2.54)
    half = pitch * 10 // 2
    orig_y = -half + (pin_num - 1) * pitch
    # After 90° rotation
    return (jx - orig_y, jy)


# Collect all GND pad positions
gnd_pads = []  # list of (x, y, layer, label)

# IC GND pins: 6, 11, 12
for uref, (ux, uy) in SHIFTERS.items():
    for pin in [6, 11, 12]:
        px, py = tssop_pad_pos(ux, uy, pin)
        gnd_pads.append((px, py, 'top', f'{uref}-{pin}'))

# Cap GND pins (pin 2)
cap_num = 1
for uref in ['U1','U2','U3','U4','U5','U6','U7','U8','U9','U10']:
    ux, uy = SHIFTERS[uref]
    # VCCA cap
    cx, cy = ux + mm(3), uy - mm(6)
    gnd_pads.append((cx + SMD0603_PX, cy, 'top', f'C{cap_num}-2'))
    cap_num += 1
    # VCCB cap
    cx, cy = ux - mm(3), uy - mm(6)
    gnd_pads.append((cx + SMD0603_PX, cy, 'top', f'C{cap_num}-2'))
    cap_num += 1

# Extra power decoupling caps (C21-C29)
for i in range(9):
    cx = mm(15 + i * 14)
    cy = mm(80)
    gnd_pads.append((cx + SMD0603_PX, cy, 'top', f'C{cap_num}-2'))
    cap_num += 1

# Resistor GND pins (pin 2)
resistor_offsets = {
    3: (mm(8), mm(-5)),
    6: (mm(5), mm(-10)),
    8: (mm(8), mm(5)),
}
for i in range(10):
    uref = f'U{i+1}'
    sx, sy = SHIFTERS[uref]
    dx, dy = resistor_offsets.get(i+1, (mm(5), mm(5)))
    rx, ry = sx + dx, sy + dy
    gnd_pads.append((rx + SMD0603_PX, ry, 'top', f'R{i+1}-2'))

# Through-hole GND pins (already on both layers)
# J5 pins 6 and 7
for pin in [6, 7]:
    px, py = j5_pin_pos(pin)
    gnd_pads.append((px, py, 'thru', f'J5-{pin}'))

# J11 pin 11
px, py = j11_pin_pos(11)
gnd_pads.append((px, py, 'thru', f'J11-11'))


# ============================================================
# Generate GND connections
# ============================================================
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def minimum_spanning_tree(points):
    """Prim's algorithm for MST. Returns list of (i, j) edges."""
    n = len(points)
    if n <= 1:
        return []

    in_tree = [False] * n
    min_edge = [float('inf')] * n
    min_from = [-1] * n
    edges = []

    in_tree[0] = True
    for j in range(1, n):
        min_edge[j] = dist(points[0], points[j])
        min_from[j] = 0

    for _ in range(n - 1):
        # Find closest point not in tree
        best = -1
        for j in range(n):
            if not in_tree[j] and (best == -1 or min_edge[j] < min_edge[best]):
                best = j

        in_tree[best] = True
        edges.append((min_from[best], best))

        # Update distances
        for j in range(n):
            if not in_tree[j]:
                d = dist(points[best], points[j])
                if d < min_edge[j]:
                    min_edge[j] = d
                    min_from[j] = best

    return edges


# Build MST of all GND points on bottom layer
# For SMD pads, the via position is offset slightly from the pad
# to avoid conflicting with other pads

# For each SMD GND pad, find a via position
via_positions = []  # (via_x, via_y) for each gnd_pad
VIA_OFFSET = mm(0.5)  # offset via from pad center

for x, y, layer, label in gnd_pads:
    if layer == 'thru':
        # Through-hole pins are already on the bottom layer, no via needed
        via_positions.append((x, y))
    elif 'U' in label and '-' in label:
        parts = label.split('-')
        pin = int(parts[1]) if parts[1].isdigit() else 0
        if pin in [6, 11, 12]:
            # IC pins on left side of TSSOP-24
            # Place via further to the left (away from IC body)
            via_positions.append((x - VIA_OFFSET, y))
        else:
            # Cap/resistor pad
            via_positions.append((x, y + VIA_OFFSET))
    else:
        # Cap or resistor pads - place via below
        via_positions.append((x, y + VIA_OFFSET))

# Compute MST on via positions (bottom layer connections)
points = [(x, y) for x, y in via_positions]
mst_edges = minimum_spanning_tree(points)

# ============================================================
# Write to PCB file
# ============================================================
with open('giga_shield.pcb', 'r') as f:
    pcb = f.read()

# Build the additions
additions = []

# 1. Vias from top-layer SMD pads to bottom layer
for i, (x, y, layer, label) in enumerate(gnd_pads):
    if layer == 'top':
        vx, vy = via_positions[i]
        additions.append(f'Via[{vx}nm {vy}nm {VIA_OUTER}nm {VIA_CLEAR}nm {VIA_OUTER}nm {VIA_DRILL}nm "" ""]')

# 2. Short top-layer traces from SMD pad to via (where pad and via don't overlap)
top_traces = []
for i, (x, y, layer, label) in enumerate(gnd_pads):
    if layer == 'top':
        vx, vy = via_positions[i]
        if abs(x - vx) > mm(0.1) or abs(y - vy) > mm(0.1):
            top_traces.append(f'\tLine[{x}nm {y}nm {vx}nm {vy}nm {TRACE_WIDTH}nm {TRACE_CLEAR}nm "clearline"]')

# 3. Bottom-layer traces connecting MST edges
bottom_traces = []
for i, j in mst_edges:
    x1, y1 = via_positions[i]
    x2, y2 = via_positions[j]
    bottom_traces.append(f'\tLine[{x1}nm {y1}nm {x2}nm {y2}nm {TRACE_WIDTH}nm {TRACE_CLEAR}nm "clearline"]')

# Insert vias before first Layer definition
layer_match = re.search(r'^Layer\(1 ', pcb, re.MULTILINE)
if not layer_match:
    print("ERROR: Could not find Layer(1)")
    exit(1)

via_text = '\n'.join(additions) + '\n'
pcb = pcb[:layer_match.start()] + via_text + pcb[layer_match.start():]

# Insert top traces into Layer(1 "top")
top_layer = re.search(r'Layer\(1 "top"\)\n\(', pcb)
if top_layer:
    insert_pos = top_layer.end()
    if top_traces:
        pcb = pcb[:insert_pos] + '\n' + '\n'.join(top_traces) + '\n' + pcb[insert_pos:]

# Insert bottom traces into Layer(2 "bottom")
bot_layer = re.search(r'Layer\(2 "bottom"\)\n\(', pcb)
if bot_layer:
    insert_pos = bot_layer.end()
    if bottom_traces:
        pcb = pcb[:insert_pos] + '\n' + '\n'.join(bottom_traces) + '\n' + pcb[insert_pos:]

with open('giga_shield.pcb', 'w') as f:
    f.write(pcb)

print(f"Added GND connections:")
print(f"  {len([p for p in gnd_pads if p[2] == 'top'])} vias (SMD pad to bottom layer)")
print(f"  {len(top_traces)} top-layer stub traces (pad to via)")
print(f"  {len(bottom_traces)} bottom-layer MST traces")
print(f"  {len(gnd_pads)} total GND pads connected")
