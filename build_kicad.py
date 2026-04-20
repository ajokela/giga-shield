#!/usr/bin/env python3
"""
Generate a modern KiCad 6+ .kicad_pcb file for the GigaShield.

Reuses component positions and netlist from build_giga_shield.py.
Outputs a proper .kicad_pcb with:
  - 2 copper layers (F.Cu, B.Cu)
  - GND copper zones on F.Cu and B.Cu
  - All components with KiCad 6 footprint format
  - Complete netlist including GND
  - Design rules set for PCBWay manufacturing
"""

import uuid
import os

# Import all the shared data from build_giga_shield
BOARD_W = 155000000  # 155mm in nm
BOARD_H = 90000000   # 90mm in nm

def mm(val):
    return int(val * 1000000)

def mm_f(nm_val):
    """Convert nm to mm float for KiCad output."""
    return nm_val / 1000000.0

KX = 106.0
KY = 30.5

def kpos(kx, ky):
    return (mm(kx - KX), mm(ky - KY))

def uid():
    return str(uuid.uuid4())

# ============================================================
# Component positions (same as build_giga_shield.py)
# ============================================================
CONNECTORS = {
    'J1':  {'pos': kpos(149.11, 101.51), 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J2':  {'pos': kpos(139.645, 53.34), 'val': 'Conn_01x10', 'npins': 10, 'ncols': 1, 'rot': 90},
    'J3':  {'pos': kpos(171.85, 101.51), 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J4':  {'pos': kpos(184.655, 53.37), 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': -90},
    'J5':  {'pos': kpos(146.64, 114.67), 'val': 'J_ANALOG', 'npins': 26, 'ncols': 1, 'rot': 90},
    'J6':  {'pos': kpos(194.63, 101.51), 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J7':  {'pos': kpos(189.13, 53.42),  'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J8':  {'pos': kpos(145.02, 37.33),  'val': 'J_DIGITAL', 'npins': 26, 'ncols': 1, 'rot': 90},
    'J9':  {'pos': kpos(214.89, 53.18),  'val': 'JSIDE', 'npins': 36, 'ncols': 2, 'rot': 0},
    'J10': {'pos': kpos(250.73, 56.00),  'val': 'JSIDE_5V', 'npins': 36, 'ncols': 2, 'rot': 0},
}

MOUNTING_HOLES = {
    'H1': kpos(113.0, 37.5),
    'H2': kpos(113.0, 113.5),
    'H3': kpos(254.0, 113.5),
    'H4': kpos(254.0, 37.5),
}

SHIFTERS = {
    'U1': kpos(152.3, 45.8),
    'U2': kpos(184.8, 89.0),
    'U3': kpos(174.6, 46.7),
    'U4': kpos(200.4, 89.1),
    'U5': kpos(195.8, 45.7),
    'U6': kpos(224.0, 56.0),
    'U8': kpos(240.0, 56.0),
    'U9': kpos(224.0, 74.0),
    'U7': kpos(240.0, 74.0),
    'U10': kpos(224.0, 92.0),
}

SHIFTER_NETS = {
    'U1': {
        'a': ['SCL1', 'SDA1', 'AREF_3V3', 'D13', 'D12', 'D11', 'D10', 'D9'],
        'b': ['PB6', 'PH12', 'AREF', 'PH6', 'PJ11', 'PJ10', 'PK1', 'PB9'],
        'dir_net': 'DIR_U1',
    },
    'U2': {
        'a': ['PC4', 'PC5', 'PB0', 'PB1', 'PC3', 'PC2', 'PC0', 'PA0'],
        'b': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'],
        'dir_net': 'DIR_U2',
    },
    'U3': {
        'a': ['D8', 'D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1'],
        'b': ['PB8', 'PB4', 'PD13_5V', 'PA7', 'PJ8', 'PA2', 'PA3', 'PA9'],
        'dir_net': 'DIR_U3',
    },
    'U4': {
        'a': ['PC2_C', 'PC3_C', 'PA1_C', 'PA0_C', 'PA4', 'PA5', 'PB5', 'PB13'],
        'b': ['A8', 'A9', 'A10', 'A11', 'DAC0', 'DAC1', 'CAN_RX', 'CAN_TX'],
        'dir_net': 'DIR_U4',
    },
    'U5': {
        'a': ['D0', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20'],
        'b': ['PB7', 'PG14', 'PC7', 'PH13', 'PI9', 'PD5', 'PD6', 'PB11'],
        'dir_net': 'DIR_U5',
    },
    'U6': {
        'a': ['D22', 'D24', 'D26', 'D28', 'D30', 'D32', 'D34', 'D36'],
        'b': ['PJ12', 'PG12', 'PJ14', 'PJ15', 'PK3', 'PK4', 'PK5', 'PK6'],
        'dir_net': 'DIR_U6',
    },
    'U7': {
        'a': ['D42', 'D43', 'D44', 'D45', 'D46', 'D47', 'D48', 'D49'],
        'b': ['PI15', 'PI10', 'PG10', 'PI13', 'PH15', 'PB2', 'PK0', 'PE4'],
        'dir_net': 'DIR_U7',
    },
    'U8': {
        'a': ['D21', 'D23', 'D25', 'D27', 'D29', 'D31', 'D33', 'D35'],
        'b': ['PH4', 'PG13', 'PJ0', 'PJ1', 'PJ2', 'PJ3', 'PJ4', 'PJ5'],
        'dir_net': 'DIR_U8',
    },
    'U9': {
        'a': ['D37', 'D39', 'D40', 'D41', 'D53', 'NC_U9A6', 'NC_U9A7', 'NC_U9A8'],
        'b': ['PJ6', 'PI14', 'PE6', 'PK7', 'PG7', 'NC_U9B6', 'NC_U9B7', 'NC_U9B8'],
        'dir_net': 'DIR_U9',
    },
    'U10': {
        'a': ['D38', 'D50', 'D51', 'D52', 'NC_U10A5', 'NC_U10A6', 'NC_U10A7', 'NC_U10A8'],
        'b': ['PJ7', 'PI11', 'PE5', 'PK2', 'NC_U10B5', 'NC_U10B6', 'NC_U10B7', 'NC_U10B8'],
        'dir_net': 'DIR_U10',
    },
}


# ============================================================
# Net collection (same logic as build_giga_shield.py)
# ============================================================
def collect_nets():
    """Build the complete netlist. Returns dict of net_name -> [(ref, pin), ...]"""
    nets = {}

    def add_net(name, ref, pin):
        if name.startswith('NC'):
            return
        if name not in nets:
            nets[name] = []
        nets[name].append((ref, str(pin)))

    # Connector nets (same as build_giga_shield.py)
    j5 = ['NC', 'IOREF_3V3', 'NRST', '+3V3', '+5V', 'GND', 'GND', 'VIN',
          'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
          'A8', 'A9', 'A10', 'A11', 'DAC0', 'DAC1', 'CAN_RX', 'CAN_TX', 'NC', 'NC']
    for i, n in enumerate(j5):
        if n != 'NC' and n != 'VIN':
            add_net(n, 'J5', i+1)

    j8 = ['PB6', 'PH12', 'AREF', 'GND',
          'PH6', 'PJ11', 'PJ10', 'PK1', 'PB9',
          'PB8', 'PB4', 'PD13_5V', 'PA7', 'PJ8', 'PA2', 'PA3', 'PA9',
          'PB7', 'PG14', 'PC7', 'PH13', 'PI9', 'PD5', 'PD6', 'PB11', 'PH4']
    for i, n in enumerate(j8):
        add_net(n, 'J8', i+1)

    j1 = ['PC4', 'PC5', 'PB0', 'PB1', 'PC3', 'PC2', 'PC0', 'PA0']
    for i, n in enumerate(j1):
        add_net(n, 'J1', i+1)

    j2 = ['VIN', '+3V3', '+3V3', 'IOREF_3V3', 'NRST',
          'PC2_C', 'PC3_C', 'PA1_C', 'PA0_C', 'PB13']
    for i, n in enumerate(j2):
        if n != 'VIN':
            add_net(n, 'J2', i+1)

    j3 = ['D8', 'D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1']
    for i, n in enumerate(j3):
        add_net(n, 'J3', i+1)

    j4 = ['SCL1', 'SDA1', 'AREF_3V3', 'D13', 'D12', 'D11', 'D10', 'D9']
    for i, n in enumerate(j4):
        add_net(n, 'J4', i+1)

    j6 = ['D0', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20']
    for i, n in enumerate(j6):
        add_net(n, 'J6', i+1)

    j7 = ['D21', 'PA4', 'PA5', 'PB5', '+3V3', 'GND', '+5V', 'GND']
    for i, n in enumerate(j7):
        if n != 'VIN':
            add_net(n, 'J7', i+1)

    j9 = ['+5V', '+5V',
          'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29',
          'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37',
          'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45',
          'D46', 'D47', 'D48', 'D49', 'D50', 'D51', 'D52', 'D53',
          'GND', 'GND']
    for i, n in enumerate(j9):
        add_net(n, 'J9', i+1)

    j10 = ['+5V', '+5V',
           'PJ12', 'PG13', 'PG12', 'PJ0', 'PJ14', 'PJ1', 'PJ15', 'PJ2',
           'PK3', 'PJ3', 'PK4', 'PJ4', 'PK5', 'PJ5', 'PK6', 'PJ6',
           'PJ7', 'PI14', 'PE6', 'PK7', 'PI15', 'PI10', 'PG10', 'PI13',
           'PH15', 'PB2', 'PK0', 'PE4', 'PI11', 'PE5', 'PK2', 'PG7',
           'GND', 'GND']
    for i, n in enumerate(j10):
        add_net(n, 'J10', i+1)

    # Level shifters
    cap_num = 1
    for uref in ['U1','U2','U3','U4','U5','U6','U7','U8','U9','U10']:
        sn = SHIFTER_NETS[uref]

        add_net(sn['dir_net'], uref, 1)
        for i in range(4):
            add_net(sn['a'][i], uref, i+2)
        add_net('GND', uref, 6)
        for i in range(4):
            add_net(sn['a'][4+i], uref, i+7)
        add_net('GND', uref, 11)
        add_net('GND', uref, 12)
        add_net(sn['b'][7], uref, 13)
        add_net(sn['b'][6], uref, 14)
        add_net(sn['b'][5], uref, 15)
        add_net(sn['b'][4], uref, 16)
        add_net('+5V', uref, 17)
        add_net(sn['b'][3], uref, 18)
        add_net(sn['b'][2], uref, 19)
        add_net(sn['b'][1], uref, 20)
        add_net(sn['b'][0], uref, 21)
        add_net('+3V3', uref, 22)
        add_net('+3V3', uref, 23)
        add_net('+5V', uref, 24)

        cref_a = f'C{cap_num}'
        add_net('+3V3', cref_a, 1)
        add_net('GND', cref_a, 2)
        cap_num += 1

        cref_b = f'C{cap_num}'
        add_net('+5V', cref_b, 1)
        add_net('GND', cref_b, 2)
        cap_num += 1

    # Extra power caps
    for i in range(9):
        cref = f'C{cap_num}'
        add_net('+3V3' if i % 2 == 0 else '+5V', cref, 1)
        add_net('GND', cref, 2)
        cap_num += 1

    # J11 DIR header
    dir_names = ['DIR_U1','DIR_U2','DIR_U3','DIR_U4','DIR_U5',
                 'DIR_U6','DIR_U7','DIR_U8','DIR_U9','DIR_U10','GND']
    for i, n in enumerate(dir_names):
        add_net(n, 'J11', i+1)

    # DIR resistors
    for i in range(10):
        rref = f'R{i+1}'
        uref = f'U{i+1}'
        add_net(SHIFTER_NETS[uref]['dir_net'], rref, 1)
        # R10 is pull-UP to +3V3 (U10 must default A→B for CLK/RESET/INT/NMI);
        # R1-R9 are pulldowns (default B→A, Z80→Giga)
        add_net('+3V3' if i + 1 == 10 else 'GND', rref, 2)

    # Filter out single-connection nets
    return {k: v for k, v in nets.items() if len(v) >= 2}


# ============================================================
# KiCad footprint generators
# ============================================================

def kicad_tssop24(ref, val, x_nm, y_nm, net_map, fp_uid):
    """TSSOP-24 footprint in KiCad 6 format."""
    x = mm_f(x_nm)
    y = mm_f(y_nm)
    pitch = 0.65
    pad_w = 1.20
    pad_h = 0.40
    span = 6.40

    lines = []
    lines.append(f'  (footprint "Package_SSOP:TSSOP-24_4.4x7.8mm_P0.65mm" (layer "F.Cu")')
    lines.append(f'    (tstamp {fp_uid})')
    lines.append(f'    (at {x:.3f} {y:.3f})')
    lines.append(f'    (property "Reference" "{ref}" (at 0 -5) (layer "F.SilkS")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')
    lines.append(f'    (property "Value" "{val}" (at 0 5) (layer "F.Fab")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')

    # Body outline
    bx = 2.2
    by = 3.9
    lines.append(f'    (fp_line (start {-bx} {-by}) (end {-bx} {by}) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')
    lines.append(f'    (fp_line (start {-bx} {by}) (end {bx} {by}) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')
    lines.append(f'    (fp_line (start {bx} {by}) (end {bx} {-by}) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')
    lines.append(f'    (fp_line (start {-bx} {-by}) (end {bx} {-by}) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')

    half_span = span / 2
    y_start = -pitch * 11 / 2

    # Left pads: pins 1-12
    for i in range(12):
        pin = i + 1
        py = y_start + i * pitch
        px = -half_span
        shape = "roundrect" if pin == 1 else "oval"
        net_str = net_map.get((ref, str(pin)), "")
        lines.append(f'    (pad "{pin}" smd {shape} (at {px:.3f} {py:.3f}) (size {pad_w:.3f} {pad_h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"){net_str})')

    # Right pads: pins 13-24 (bottom to top)
    for i in range(12):
        pin = 13 + i
        py = -y_start - i * pitch
        px = half_span
        net_str = net_map.get((ref, str(pin)), "")
        lines.append(f'    (pad "{pin}" smd oval (at {px:.3f} {py:.3f}) (size {pad_w:.3f} {pad_h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"){net_str})')

    lines.append(f'  )')
    return '\n'.join(lines)


def kicad_pin_header(ref, val, x_nm, y_nm, npins, ncols, rot, net_map, fp_uid):
    """Through-hole pin header in KiCad 6 format."""
    x = mm_f(x_nm)
    y = mm_f(y_nm)
    pitch = 2.54
    pad_size = 1.70
    drill = 1.00
    rows = npins // ncols

    lines = []
    fp_name = f"Connector_PinHeader_{ncols}x{rows:02d}_P2.54mm_Vertical"
    lines.append(f'  (footprint "{fp_name}" (layer "F.Cu")')
    lines.append(f'    (tstamp {fp_uid})')
    lines.append(f'    (at {x:.3f} {y:.3f} {rot})')
    lines.append(f'    (property "Reference" "{ref}" (at 0 -2.56) (layer "F.SilkS")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')
    lines.append(f'    (property "Value" "{val}" (at 0 -1.27) (layer "F.Fab")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')

    pin_num = 1
    for row in range(rows):
        for col in range(ncols):
            px = col * pitch
            py = row * pitch
            shape = "rect" if pin_num == 1 else "oval"
            net_str = net_map.get((ref, str(pin_num)), "")
            lines.append(f'    (pad "{pin_num}" thru_hole {shape} (at {px:.3f} {py:.3f}) (size {pad_size:.3f} {pad_size:.3f}) (drill {drill:.3f}) (layers "*.Cu" "*.Mask"){net_str})')
            pin_num += 1

    lines.append(f'  )')
    return '\n'.join(lines)


def kicad_smd_0603(ref, val, x_nm, y_nm, net_map, fp_uid):
    """0603 SMD cap/resistor in KiCad 6 format."""
    x = mm_f(x_nm)
    y = mm_f(y_nm)
    pad_w = 0.90
    pad_h = 0.90
    px = 0.75

    lines = []
    lines.append(f'  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")')
    lines.append(f'    (tstamp {fp_uid})')
    lines.append(f'    (at {x:.3f} {y:.3f})')
    lines.append(f'    (property "Reference" "{ref}" (at 0 -1.5) (layer "F.SilkS")')
    lines.append(f'      (effects (font (size 0.8 0.8) (thickness 0.12))))')
    lines.append(f'    (property "Value" "{val}" (at 0 1.5) (layer "F.Fab")')
    lines.append(f'      (effects (font (size 0.8 0.8) (thickness 0.12))))')

    net_str_1 = net_map.get((ref, "1"), "")
    net_str_2 = net_map.get((ref, "2"), "")
    lines.append(f'    (pad "1" smd roundrect (at {-px:.3f} 0) (size {pad_w:.3f} {pad_h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25){net_str_1})')
    lines.append(f'    (pad "2" smd roundrect (at {px:.3f} 0) (size {pad_w:.3f} {pad_h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25){net_str_2})')

    lines.append(f'  )')
    return '\n'.join(lines)


def kicad_mounting_hole(ref, x_nm, y_nm, fp_uid):
    """Mounting hole in KiCad 6 format."""
    x = mm_f(x_nm)
    y = mm_f(y_nm)
    lines = []
    lines.append(f'  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu")')
    lines.append(f'    (tstamp {fp_uid})')
    lines.append(f'    (at {x:.3f} {y:.3f})')
    lines.append(f'    (property "Reference" "{ref}" (at 0 -3.5) (layer "F.SilkS")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')
    lines.append(f'    (property "Value" "MountingHole" (at 0 3.5) (layer "F.Fab")')
    lines.append(f'      (effects (font (size 1 1) (thickness 0.15))))')
    lines.append(f'    (pad "1" thru_hole circle (at 0 0) (size 5.0 5.0) (drill 3.2) (layers "*.Cu" "*.Mask"))')
    lines.append(f'  )')
    return '\n'.join(lines)


# ============================================================
# Main generator
# ============================================================

def build_kicad_pcb(unplaced=False):
    def p(x, y):
        """Return position, zeroed if unplaced mode."""
        if unplaced:
            return (0, 0)
        return (x, y)

    nets = collect_nets()

    # Assign net IDs
    net_names = sorted(nets.keys())
    net_id = {}  # net_name -> id
    for i, name in enumerate(net_names):
        net_id[name] = i + 1

    # Build reverse map: (ref, pin) -> net string for pad output
    net_map = {}  # (ref, pin_str) -> ' (net N "name")'
    for name, conns in nets.items():
        nid = net_id[name]
        for ref, pin in conns:
            net_map[(ref, pin)] = f' (net {nid} "{name}")'

    bw = mm_f(BOARD_W)
    bh = mm_f(BOARD_H)

    out = []

    # Header
    out.append('(kicad_pcb (version 20221018) (generator "giga_shield_builder")')
    out.append('')
    out.append('  (general')
    out.append('    (thickness 1.6)')
    out.append('  )')
    out.append('')
    out.append('  (paper "A4")')
    out.append('')

    # Layers - 2 copper layers
    out.append('  (layers')
    out.append('    (0 "F.Cu" signal)')
    out.append('    (31 "B.Cu" signal)')
    out.append('    (32 "B.Adhes" user "B.Adhesive")')
    out.append('    (33 "F.Adhes" user "F.Adhesive")')
    out.append('    (34 "B.Paste" user)')
    out.append('    (35 "F.Paste" user)')
    out.append('    (36 "B.SilkS" user "B.Silkscreen")')
    out.append('    (37 "F.SilkS" user "F.Silkscreen")')
    out.append('    (38 "B.Mask" user "B.Solder Mask")')
    out.append('    (39 "F.Mask" user "F.Solder Mask")')
    out.append('    (40 "Dwgs.User" user "User.Drawings")')
    out.append('    (41 "Cmts.User" user "User.Comments")')
    out.append('    (42 "Eco1.User" user "User.Eco1")')
    out.append('    (43 "Eco2.User" user "User.Eco2")')
    out.append('    (44 "Edge.Cuts" user)')
    out.append('    (45 "Margin" user)')
    out.append('    (46 "B.CrtYd" user "B.Courtyard")')
    out.append('    (47 "F.CrtYd" user "F.Courtyard")')
    out.append('    (48 "B.Fab" user)')
    out.append('    (49 "F.Fab" user)')
    out.append('  )')
    out.append('')

    # Setup with design rules and stackup
    out.append('  (setup')
    out.append('    (stackup')
    out.append('      (layer "F.SilkS" (type "Top Silk Screen"))')
    out.append('      (layer "F.Paste" (type "Top Solder Paste"))')
    out.append('      (layer "F.Mask" (type "Top Solder Mask") (color "Black"))')
    out.append('      (layer "F.Cu" (type "copper"))')
    out.append('      (layer "B.Cu" (type "copper"))')
    out.append('      (layer "B.Mask" (type "Bottom Solder Mask") (color "Black"))')
    out.append('      (layer "B.Paste" (type "Bottom Solder Paste"))')
    out.append('      (layer "B.SilkS" (type "Bottom Silk Screen"))')
    out.append('    )')
    out.append('    (pad_to_mask_clearance 0.05)')
    out.append('    (pcbplotparams')
    out.append('      (layerselection 0x00010fc_ffffffff)')
    out.append('      (plot_on_all_layers_selection 0x0000000_00000000)')
    out.append('    )')
    out.append('  )')
    out.append('')

    # Net declarations
    out.append('  (net 0 "")')
    for name in net_names:
        out.append(f'  (net {net_id[name]} "{name}")')
    out.append('')

    # Net classes with design rules
    out.append('  (net_class "Default" "Default net class"')
    out.append('    (clearance 0.2)')
    out.append('    (trace_width 0.254)')
    out.append('    (via_dia 0.6)')
    out.append('    (via_drill 0.3)')
    out.append('    (uvia_dia 0.3)')
    out.append('    (uvia_drill 0.1)')
    out.append('  )')
    out.append('')

    out.append('  (net_class "Power" "Power net class"')
    out.append('    (clearance 0.2)')
    out.append('    (trace_width 0.508)')
    out.append('    (via_dia 0.8)')
    out.append('    (via_drill 0.4)')
    out.append('    (uvia_dia 0.3)')
    out.append('    (uvia_drill 0.1)')
    for name in net_names:
        if name in ('GND', '+3V3', '+5V'):
            out.append(f'    (add_net "{name}")')
    out.append('  )')
    out.append('')

    # Board outline on Edge.Cuts
    out.append(f'  (gr_line (start 0 0) (end {bw:.3f} 0) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')
    out.append(f'  (gr_line (start {bw:.3f} 0) (end {bw:.3f} {bh:.3f}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')
    out.append(f'  (gr_line (start {bw:.3f} {bh:.3f}) (end 0 {bh:.3f}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')
    out.append(f'  (gr_line (start 0 {bh:.3f}) (end 0 0) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')
    out.append('')

    # Silk screen text
    out.append(f'  (gr_text "tinycomputers.io" (at 55 86) (layer "F.SilkS") (tstamp {uid()})')
    out.append('    (effects (font (size 1.5 1.5) (thickness 0.2))))')
    out.append(f'  (gr_text "v0.4" (at 87 86) (layer "F.SilkS") (tstamp {uid()})')
    out.append('    (effects (font (size 1.5 1.5) (thickness 0.2))))')
    out.append('')

    # Mounting holes
    for ref, (x, y) in MOUNTING_HOLES.items():
        hx, hy = p(x, y)
        out.append(kicad_mounting_hole(ref, hx, hy, uid()))
    out.append('')

    # Connectors
    for ref in ['J1','J2','J3','J4','J5','J6','J7','J8','J9','J10']:
        info = CONNECTORS[ref]
        x, y = p(*info['pos'])
        out.append(kicad_pin_header(ref, info['val'], x, y, info['npins'], info['ncols'], info.get('rot', 0), net_map, uid()))
    out.append('')

    # J11 DIR header
    j11_x, j11_y = p(mm(40), mm(75))
    out.append(kicad_pin_header('J11', 'DIR_CTRL', j11_x, j11_y, 11, 1, 90, net_map, uid()))
    out.append('')

    # Level shifter ICs
    for uref in ['U1','U2','U3','U4','U5','U6','U7','U8','U9','U10']:
        ux, uy = p(*SHIFTERS[uref])
        out.append(kicad_tssop24(uref, 'SN74LVC8T245PW', ux, uy, net_map, uid()))
    out.append('')

    # Decoupling caps
    cap_num = 1
    for uref in ['U1','U2','U3','U4','U5','U6','U7','U8','U9','U10']:
        ux, uy = SHIFTERS[uref]
        # VCCA cap
        cx1, cy1 = p(ux + mm(3), uy - mm(6))
        out.append(kicad_smd_0603(f'C{cap_num}', '0.1uF', cx1, cy1, net_map, uid()))
        cap_num += 1
        # VCCB cap
        cx2, cy2 = p(ux - mm(3), uy - mm(6))
        out.append(kicad_smd_0603(f'C{cap_num}', '0.1uF', cx2, cy2, net_map, uid()))
        cap_num += 1

    # Extra power caps
    for i in range(9):
        cx = mm(15 + i * 14)
        cy = mm(80)
        if i == 8:  # C29: shift right to clear U10
            cx = mm(141)
        cx, cy = p(cx, cy)
        out.append(kicad_smd_0603(f'C{cap_num}', '0.1uF', cx, cy, net_map, uid()))
        cap_num += 1
    out.append('')

    # DIR resistors
    resistor_offsets = {
        3: (mm(8), mm(-5)),
        6: (mm(5), mm(-10)),
        8: (mm(8), mm(5)),
        10: (mm(5), mm(-8)),   # R10: above U10 to clear IC body
    }
    for i in range(10):
        rref = f'R{i+1}'
        uref = f'U{i+1}'
        sx, sy = SHIFTERS[uref]
        dx, dy = resistor_offsets.get(i+1, (mm(5), mm(5)))
        sx, sy = p(sx + dx, sy + dy)
        dx, dy = 0, 0
        out.append(kicad_smd_0603(rref, '10K', sx + dx, sy + dy, net_map, uid()))
    out.append('')

    # GND copper zones on both layers
    margin = 0.5
    gnd_nid = net_id.get('GND', 0)
    for layer in ['F.Cu', 'B.Cu']:
        out.append(f'  (zone (net {gnd_nid}) (net_name "GND") (layer "{layer}") (tstamp {uid()}) (hatch edge 0.5)')
        out.append(f'    (connect_pads (clearance 0.3))')
        out.append(f'    (min_thickness 0.25)')
        out.append(f'    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))')
        out.append(f'    (polygon')
        out.append(f'      (pts')
        out.append(f'        (xy {margin} {margin})')
        out.append(f'        (xy {bw - margin:.3f} {margin})')
        out.append(f'        (xy {bw - margin:.3f} {bh - margin:.3f})')
        out.append(f'        (xy {margin} {bh - margin:.3f})')
        out.append(f'      )')
        out.append(f'    )')
        out.append(f'  )')
        out.append('')

    out.append(')')
    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    unplaced = '--unplaced' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    outfile = args[0] if args else 'giga_shield_v04.kicad_pcb'
    content = build_kicad_pcb(unplaced=unplaced)
    with open(outfile, 'w') as f:
        f.write(content)
    print(f"Generated {outfile}")
    print(f"Board: {BOARD_W/1e6:.0f}mm x {BOARD_H/1e6:.0f}mm, 2 layers")
    print(f"GND copper zones on F.Cu and B.Cu")
    print(f"10x SN74LVC8T245PW, complete netlist with GND")
