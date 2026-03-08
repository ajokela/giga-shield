#!/usr/bin/env python3
"""
Build a pcb-rnd board for the Arduino Giga R1 Shield with SN74LVC8T245 driven level shifters.
Replaces the original TXB0108PW auto-sensing design.

Board: 155mm x 90mm (matching original KiCad design)
Components: 9x SN74LVC8T245PW (TSSOP-24), connectors, caps, resistors
"""

# Board dimensions (nanometers)
BOARD_W = 155000000  # 155mm
BOARD_H = 90000000   # 90mm

def mm(val):
    return int(val * 1000000)

# KiCad origin offset to shift to 0,0
KX = 106.0
KY = 30.5

def kpos(kx, ky):
    return (mm(kx - KX), mm(ky - KY))

# ============================================================
# Component positions (from KiCad export, converted to our origin)
# ============================================================
CONNECTORS = {
    'J1':  {'pos': kpos(149.11, 101.51), 'pkg': '1x08', 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J2':  {'pos': kpos(139.645, 53.34), 'pkg': '1x10', 'val': 'Conn_01x10', 'npins': 10, 'ncols': 1, 'rot': 90},
    'J3':  {'pos': kpos(171.85, 101.51), 'pkg': '1x08', 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J4':  {'pos': kpos(184.655, 53.37), 'pkg': '1x08', 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': -90},
    'J5':  {'pos': kpos(146.64, 114.67), 'pkg': '1x26', 'val': 'J_ANALOG', 'npins': 26, 'ncols': 1, 'rot': 90},
    'J6':  {'pos': kpos(194.63, 101.51), 'pkg': '1x08', 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J7':  {'pos': kpos(189.13, 53.42),  'pkg': '1x08', 'val': 'Conn_01x08', 'npins': 8, 'ncols': 1, 'rot': 90},
    'J8':  {'pos': kpos(145.02, 37.33),  'pkg': '1x26', 'val': 'J_DIGITAL', 'npins': 26, 'ncols': 1, 'rot': 90},
    'J9':  {'pos': kpos(214.89, 53.18),  'pkg': '2x18', 'val': 'JSIDE', 'npins': 36, 'ncols': 2, 'rot': 0},
    'J10': {'pos': kpos(250.73, 56.00),  'pkg': '2x18', 'val': 'JSIDE_5V', 'npins': 36, 'ncols': 2, 'rot': 0},
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
    'U6': kpos(232.6, 62.2),
    'U7': kpos(233.2, 99.1),
    'U8': kpos(232.5, 74.0),
    'U9': kpos(232.7, 85.7),
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
        'a': ['D37', 'D39', 'D41', 'D43', 'D45', 'D47', 'D49', 'D51'],
        'b': ['PJ6', 'PI14', 'PK7', 'PI10', 'PI13', 'PB2', 'PE4', 'PE5'],
        'dir_net': 'DIR_U7',
    },
    'U8': {
        'a': ['D21', 'D23', 'D25', 'D27', 'D29', 'D31', 'D33', 'D35'],
        'b': ['PH4', 'PG13', 'PJ0', 'PJ1', 'PJ2', 'PJ3', 'PJ4', 'PJ5'],
        'dir_net': 'DIR_U8',
    },
    'U9': {
        'a': ['D38', 'D40', 'D42', 'D44', 'D46', 'D48', 'D50', 'D52'],
        'b': ['PJ7', 'PE6', 'PI15', 'PG10', 'PH15', 'PK0', 'PI11', 'PK2'],
        'dir_net': 'DIR_U9',
    },
}

# ============================================================
# PCB element generators (matching pcb-rnd format)
# ============================================================

def tssop24_element(ref, val, x, y):
    """TSSOP-24: 0.65mm pitch, 6.4mm pad-to-pad span, 24 pins."""
    pitch = mm(0.65)
    pad_thick = mm(0.40)    # pad width (thickness in Pad[] terms)
    pad_len = mm(1.20)      # pad length (x1 to x2 extent)
    span = mm(6.40)         # center-to-center across body
    clear = mm(0.20)
    mask = mm(0.50)
    body_w = mm(4.40)
    body_h = mm(7.80)

    pin_names = [
        '1DIR', 'A1', 'A2', 'A3', 'A4', 'GND',
        'A5', 'A6', 'A7', 'A8', '1OE', 'GND',
        'B8', 'B7', 'B6', 'B5', 'VCCB', 'B4',
        'B3', 'B2', 'B1', 'VCCA', 'VCCA', 'VCCB'
    ]

    lines = []
    lines.append(f'Element["" "TSSOP24" "{ref}" "{val}" {x}nm {y}nm 0nm 0nm 0 100 ""]')
    lines.append('(')

    half_span = span // 2
    half_pad = pad_len // 2
    y_start = -pitch * 11 // 2  # center the 12 pins vertically

    # Left pads: pins 1-12
    for i in range(12):
        px1 = -half_span - half_pad
        px2 = -half_span + half_pad
        py = y_start + i * pitch
        flags = 'square' if i == 0 else ''
        lines.append(f'\tPad[{px1}nm {py}nm {px2}nm {py}nm {pad_thick}nm {clear}nm {mask}nm "{pin_names[i]}" "{i+1}" "{flags}"]')

    # Right pads: pins 13-24, bottom to top
    for i in range(12):
        px1 = half_span - half_pad
        px2 = half_span + half_pad
        py = -y_start - i * pitch  # start from bottom
        lines.append(f'\tPad[{px1}nm {py}nm {px2}nm {py}nm {pad_thick}nm {clear}nm {mask}nm "{pin_names[12+i]}" "{12+i+1}" ""]')

    # Body outline
    bx = body_w // 2
    by = body_h // 2
    lw = mm(0.15)
    lines.append(f'\tElementLine [-{bx}nm -{by}nm -{bx}nm {by}nm {lw}nm]')
    lines.append(f'\tElementLine [-{bx}nm {by}nm {bx}nm {by}nm {lw}nm]')
    lines.append(f'\tElementLine [{bx}nm {by}nm {bx}nm -{by}nm {lw}nm]')
    lines.append(f'\tElementLine [-{bx}nm -{by}nm {bx}nm -{by}nm {lw}nm]')

    lines.append('')
    lines.append('\t)')
    lines.append('')
    return '\n'.join(lines)


def pin_header_element(ref, val, x, y, npins, ncols=1, rot=0):
    """Through-hole pin header matching pcb-rnd format.
    rot: rotation in degrees (KiCad convention).
      90  = pins extend in +x direction
      -90 = pins extend in -x direction
      0   = pins extend in +y direction (default)
    """
    pitch = mm(2.54)
    pad_d = mm(1.70)
    drill = mm(1.00)
    clear = mm(0.30)
    mask_d = pad_d + mm(0.10)

    rows = npins // ncols

    def rotate(px, py):
        if rot == 90:
            return (py, -px)
        elif rot == -90:
            return (-py, px)
        elif rot == 180:
            return (-px, -py)
        return (px, py)

    lines = []
    lines.append(f'Element["" "HEADER{npins}_{ncols}" "{ref}" "{val}" {x}nm {y}nm 0nm 0nm 0 100 ""]')
    lines.append('(')

    pin_num = 1
    for col in range(ncols):
        for row in range(rows):
            lpx = col * pitch
            lpy = row * pitch
            rpx, rpy = rotate(lpx, lpy)
            flags = 'square' if pin_num == 1 else ''
            lines.append(f'\tPin[{rpx}nm {rpy}nm {pad_d}nm {clear}nm {mask_d}nm {drill}nm "{pin_num}" "{pin_num}" "{flags}"]')
            pin_num += 1

    # Outline - compute in local coords then rotate corners
    ox1 = -pitch // 2
    oy1 = -pitch // 2
    ox2 = (ncols - 1) * pitch + pitch // 2
    oy2 = (rows - 1) * pitch + pitch // 2
    corners = [(ox1, oy1), (ox2, oy1), (ox2, oy2), (ox1, oy2)]
    rc = [rotate(cx, cy) for cx, cy in corners]
    min_x = min(c[0] for c in rc)
    max_x = max(c[0] for c in rc)
    min_y = min(c[1] for c in rc)
    max_y = max(c[1] for c in rc)

    lw = mm(0.25)
    lines.append(f'\tElementLine [{min_x}nm {min_y}nm {min_x}nm {max_y}nm {lw}nm]')
    lines.append(f'\tElementLine [{min_x}nm {max_y}nm {max_x}nm {max_y}nm {lw}nm]')
    lines.append(f'\tElementLine [{max_x}nm {max_y}nm {max_x}nm {min_y}nm {lw}nm]')
    lines.append(f'\tElementLine [{max_x}nm {min_y}nm {min_x}nm {min_y}nm {lw}nm]')

    lines.append('')
    lines.append('\t)')
    lines.append('')
    return '\n'.join(lines)


def smd_0603_element(ref, val, x, y):
    """0603 SMD capacitor/resistor matching pcb-rnd Pad format."""
    # From working kz80.pcb 0805 format, scaled for 0603
    pad_thick = mm(0.90)   # pad width
    clear = mm(0.50)
    mask = mm(0.60)
    # Pad as a short line segment
    px = mm(0.75)  # center-to-center / 2

    lines = []
    lines.append(f'Element["" "0603" "{ref}" "{val}" {x}nm {y}nm 0nm 0nm 0 100 ""]')
    lines.append('(')
    lines.append(f'\tPad[-{px}nm 0nm -{px}nm 0nm {pad_thick}nm {clear}nm {mask}nm "1" "1" "square"]')
    lines.append(f'\tPad[{px}nm 0nm {px}nm 0nm {pad_thick}nm {clear}nm {mask}nm "2" "2" "square"]')
    bx = mm(0.80)
    by = mm(0.40)
    lw = mm(0.12)
    lines.append(f'\tElementLine [-{bx}nm -{by}nm -{bx}nm {by}nm {lw}nm]')
    lines.append(f'\tElementLine [{bx}nm -{by}nm {bx}nm {by}nm {lw}nm]')
    lines.append('')
    lines.append('\t)')
    lines.append('')
    return '\n'.join(lines)


def mounting_hole_element(ref, x, y):
    pad_d = mm(5.0)
    drill = mm(3.2)
    clear = mm(0.5)
    mask_d = pad_d + mm(0.1)
    lines = []
    lines.append(f'Element["" "MountingHole" "{ref}" "" {x}nm {y}nm 0nm 0nm 0 100 ""]')
    lines.append('(')
    lines.append(f'\tPin[0nm 0nm {pad_d}nm {clear}nm {mask_d}nm {drill}nm "" "1" ""]')
    lines.append('')
    lines.append('\t)')
    lines.append('')
    return '\n'.join(lines)


# ============================================================
# Build PCB
# ============================================================

def build_pcb():
    elements = []
    nets = {}  # net_name -> [(ref, pin_num), ...]

    def add_net(name, ref, pin):
        if name not in nets:
            nets[name] = []
        nets[name].append((ref, str(pin)))

    # Mounting holes
    for ref, (x, y) in MOUNTING_HOLES.items():
        elements.append(mounting_hole_element(ref, x, y))

    # Connectors
    for ref, info in CONNECTORS.items():
        x, y = info['pos']
        elements.append(pin_header_element(ref, info['val'], x, y, info['npins'], info['ncols'], info.get('rot', 0)))

    # Connector net assignments
    # J5 (J_ANALOG) 5V side
    j5 = ['NC', 'IOREF_3V3', 'NRST', '+3V3', '+5V', 'GND', 'GND', 'VIN',
          'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
          'A8', 'A9', 'A10', 'A11', 'DAC0', 'DAC1', 'CAN_RX', 'CAN_TX', 'NC', 'NC']
    for i, n in enumerate(j5):
        if n != 'NC':
            add_net(n, 'J5', i+1)

    # J8 (J_DIGITAL) 5V side
    j8 = ['PB6', 'PH12', 'AREF', 'GND',
          'PH6', 'PJ11', 'PJ10', 'PK1', 'PB9',
          'PB8', 'PB4', 'PD13_5V', 'PA7', 'PJ8', 'PA2', 'PA3', 'PA9',
          'PB7', 'PG14', 'PC7', 'PH13', 'PI9', 'PD5', 'PD6', 'PB11', 'PH4']
    for i, n in enumerate(j8):
        add_net(n, 'J8', i+1)

    # J1 (Giga 3.3V header - analog)
    j1 = ['PC4', 'PC5', 'PB0', 'PB1', 'PC3', 'PC2', 'PC0', 'PA0']
    for i, n in enumerate(j1):
        add_net(n, 'J1', i+1)

    # J2 (Giga 3.3V header)
    j2 = ['VIN', '+3V3', '+3V3', 'IOREF_3V3', 'NRST',
          'PC2_C', 'PC3_C', 'PA1_C', 'PA0_C', 'PB13']
    for i, n in enumerate(j2):
        add_net(n, 'J2', i+1)

    # J3 (Giga 3.3V header - digital D1-D8)
    j3 = ['D8', 'D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1']
    for i, n in enumerate(j3):
        add_net(n, 'J3', i+1)

    # J4 (Giga 3.3V header - SCL/SDA/D9-D13)
    j4 = ['SCL1', 'SDA1', 'AREF_3V3', 'D13', 'D12', 'D11', 'D10', 'D9']
    for i, n in enumerate(j4):
        add_net(n, 'J4', i+1)

    # J6 (Giga 3.3V header - D0/D14-D20)
    j6 = ['D0', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20']
    for i, n in enumerate(j6):
        add_net(n, 'J6', i+1)

    # J7 (Giga 3.3V header - D21 + analog ext)
    j7 = ['D21', 'PA4', 'PA5', 'PB5', '+3V3', 'GND', '+5V', 'GND']
    for i, n in enumerate(j7):
        add_net(n, 'J7', i+1)

    # J9 (JSIDE 3.3V 2x18)
    j9 = ['+5V', '+5V',
          'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29',
          'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37',
          'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45',
          'D46', 'D47', 'D48', 'D49', 'D50', 'D51', 'D52', 'D53',
          'GND', 'GND']
    for i, n in enumerate(j9):
        add_net(n, 'J9', i+1)

    # J10 (JSIDE_5V 2x18)
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
    for uref in ['U1','U2','U3','U4','U5','U6','U7','U8','U9']:
        ux, uy = SHIFTERS[uref]
        sn = SHIFTER_NETS[uref]

        elements.append(tssop24_element(uref, 'SN74LVC8T245PW', ux, uy))

        # Pin 1: DIR
        add_net(sn['dir_net'], uref, 1)
        # Pins 2-5: A1-A4
        for i in range(4):
            add_net(sn['a'][i], uref, i+2)
        # Pin 6: GND
        add_net('GND', uref, 6)
        # Pins 7-10: A5-A8
        for i in range(4):
            add_net(sn['a'][4+i], uref, i+7)
        # Pin 11: OE# (tie to GND = always enabled)
        add_net('GND', uref, 11)
        # Pin 12: GND
        add_net('GND', uref, 12)
        # Pin 13: B8, 14: B7, 15: B6, 16: B5
        add_net(sn['b'][7], uref, 13)  # B8
        add_net(sn['b'][6], uref, 14)  # B7
        add_net(sn['b'][5], uref, 15)  # B6
        add_net(sn['b'][4], uref, 16)  # B5
        # Pin 17: VCCB
        add_net('+5V', uref, 17)
        # Pin 18: B4, 19: B3, 20: B2, 21: B1
        add_net(sn['b'][3], uref, 18)  # B4
        add_net(sn['b'][2], uref, 19)  # B3
        add_net(sn['b'][1], uref, 20)  # B2
        add_net(sn['b'][0], uref, 21)  # B1
        # Pin 22,23: VCCA
        add_net('+3V3', uref, 22)
        add_net('+3V3', uref, 23)
        # Pin 24: VCCB
        add_net('+5V', uref, 24)

        # VCCA decoupling cap
        cref_a = f'C{cap_num}'
        elements.append(smd_0603_element(cref_a, '0.1uF', ux + mm(3), uy - mm(6)))
        add_net('+3V3', cref_a, 1)
        add_net('GND', cref_a, 2)
        cap_num += 1

        # VCCB decoupling cap
        cref_b = f'C{cap_num}'
        elements.append(smd_0603_element(cref_b, '0.1uF', ux - mm(3), uy - mm(6)))
        add_net('+5V', cref_b, 1)
        add_net('GND', cref_b, 2)
        cap_num += 1

    # Extra power decoupling
    for i in range(9):
        cref = f'C{cap_num}'
        cx = mm(15 + i * 14)
        cy = mm(80)
        elements.append(smd_0603_element(cref, '0.1uF', cx, cy))
        add_net('+3V3' if i % 2 == 0 else '+5V', cref, 1)
        add_net('GND', cref, 2)
        cap_num += 1

    # DIR control header (J11) - rotated 90° to run horizontally
    j11_x, j11_y = mm(40), mm(75)
    elements.append(pin_header_element('J11', 'DIR_CTRL', j11_x, j11_y, 10, 1, rot=90))
    dir_names = ['DIR_U1','DIR_U2','DIR_U3','DIR_U4','DIR_U5',
                 'DIR_U6','DIR_U7','DIR_U8','DIR_U9','GND']
    for i, n in enumerate(dir_names):
        add_net(n, 'J11', i+1)

    # DIR pull-down resistors (default A→B)
    # Custom offsets to avoid overlapping nearby headers and caps
    resistor_offsets = {
        3: (mm(8), mm(-5)),   # R3: further right to clear C5
        6: (mm(5), mm(-10)),  # R6: well above U6 to clear body and U8's C15
        8: (mm(8), mm(5)),    # R8: further right to clear U9's C17
    }
    for i in range(9):
        rref = f'R{i+1}'
        uref = f'U{i+1}'
        sx, sy = SHIFTERS[uref]
        dx, dy = resistor_offsets.get(i+1, (mm(5), mm(5)))
        elements.append(smd_0603_element(rref, '10K', sx + dx, sy + dy))
        add_net(SHIFTER_NETS[uref]['dir_net'], rref, 1)
        add_net('GND', rref, 2)

    # ============================================================
    # Assemble PCB file
    # ============================================================
    out = []
    out.append('# release: pcb-rnd 3.1.4')
    out.append('')
    out.append('# To read pcb files, the pcb version (or the git source date) must be >= the file version')
    out.append('FileVersion[20070407]')
    out.append('')
    out.append(f'PCB["GigaShield" {BOARD_W}nm {BOARD_H}nm]')
    out.append('')
    out.append('Grid[254000nm 0 0 0]')
    out.append('Cursor[0 0 1.000000]')
    out.append('PolyArea[200000000.000000]')
    out.append('Thermal[0.500000]')
    out.append('DRC[152400nm 254000nm 254000nm 152400nm 381000nm 254000nm]')
    out.append('Flags("nameonpcb,clearnew")')
    out.append('Groups("1,c:2,s:3")')
    out.append('Styles["Signal,254000nm,914400nm,508000nm,254000nm:Power,508000nm,1524000nm,889000nm,254000nm:Fat,1016000nm,1524000nm,889000nm,254000nm:Skinny,152400nm,610108nm,299974nm,152400nm"]')
    out.append('')

    # Symbol table (loaded from dual-z80 reference board)
    import os
    symbols_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'symbols.txt')
    if os.path.exists(symbols_path):
        with open(symbols_path) as sf:
            out.append(sf.read())
    else:
        out.append("Symbol[' ' 457200nm]")
        out.append('(')
        out.append(')')
    out.append('')

    # Elements
    for elem in elements:
        out.append(elem)

    # Layers
    out.append('Layer(1 "top")')
    out.append('(')
    out.append(')')
    out.append('')
    out.append('Layer(2 "bottom")')
    out.append('(')
    out.append(')')
    out.append('')
    out.append('Layer(3 "outline")')
    out.append('(')
    out.append(f'\tLine[254000nm 254000nm {BOARD_W - 254000}nm 254000nm 254000nm 508000nm "clearline"]')
    out.append(f'\tLine[{BOARD_W - 254000}nm 254000nm {BOARD_W - 254000}nm {BOARD_H - 254000}nm 254000nm 508000nm "clearline"]')
    out.append(f'\tLine[{BOARD_W - 254000}nm {BOARD_H - 254000}nm 254000nm {BOARD_H - 254000}nm 254000nm 508000nm "clearline"]')
    out.append(f'\tLine[254000nm {BOARD_H - 254000}nm 254000nm 254000nm 254000nm 508000nm "clearline"]')
    out.append(')')
    out.append('')
    out.append('Layer(4 "silk")')
    out.append('(')
    out.append(')')
    out.append('')
    out.append('Layer(5 "silk")')
    out.append('(')
    # J11 DIR control header pin labels (top silk)
    j11_labels = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'GND']
    j11_base_x = mm(40)
    j11_base_y = mm(75)
    pitch = mm(2.54)
    label_offset_y = mm(4.0)  # below the header pins
    for i, label in enumerate(j11_labels):
        lx = j11_base_x + i * pitch
        ly = j11_base_y + label_offset_y
        # direction 1 = 90° CCW rotation (text reads bottom-to-top)
        out.append(f'\tText[{lx}nm {ly}nm 1 120 "{label}" "clearline"]')
    # Header title above J11
    out.append(f'\tText[{j11_base_x}nm {j11_base_y - mm(4)}nm 0 150 "J11 DIR" "clearline"]')
    out.append(')')
    out.append('')

    # Netlist
    out.append('NetList()')
    out.append('(')
    for net_name in sorted(nets.keys()):
        conns = nets[net_name]
        if len(conns) < 2:
            continue
        out.append(f'\tNet("{net_name}" "(unknown)")')
        out.append('\t(')
        for ref, pin in conns:
            out.append(f'\t\tConnect("{ref}-{pin}")')
        out.append('\t)')
    out.append(')')
    out.append('')

    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    outfile = sys.argv[1] if len(sys.argv) > 1 else 'giga_shield.pcb'
    with open(outfile, 'w') as f:
        f.write(build_pcb())
    print(f"Generated {outfile}")
    print(f"Board: {BOARD_W/1e6:.0f}mm x {BOARD_H/1e6:.0f}mm")
    print(f"9x SN74LVC8T245PW (TSSOP-24) level shifters")
    print(f"DIR control via J11 (1x10 header)")
