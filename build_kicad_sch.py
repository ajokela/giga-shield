#!/usr/bin/env python3
"""
Generate a KiCad 6+ .kicad_sch schematic for the GigaShield v0.4.

Uses net labels on every pin — no explicit wires needed.
KiCad matches labels by name to form nets.
"""

import uuid
import sys

def uid():
    return str(uuid.uuid4())

# SN74LVC8T245 pin definitions (matches datasheet)
SN74_PINS = [
    (1,  'DIR',  'input'),
    (2,  'A1',   'bidirectional'),
    (3,  'A2',   'bidirectional'),
    (4,  'A3',   'bidirectional'),
    (5,  'A4',   'bidirectional'),
    (6,  'GND',  'power_in'),
    (7,  'A5',   'bidirectional'),
    (8,  'A6',   'bidirectional'),
    (9,  'A7',   'bidirectional'),
    (10, 'A8',   'bidirectional'),
    (11, 'OE',   'input'),
    (12, 'GND',  'power_in'),
    (13, 'B8',   'bidirectional'),
    (14, 'B7',   'bidirectional'),
    (15, 'B6',   'bidirectional'),
    (16, 'B5',   'bidirectional'),
    (17, 'VCCB', 'power_in'),
    (18, 'B4',   'bidirectional'),
    (19, 'B3',   'bidirectional'),
    (20, 'B2',   'bidirectional'),
    (21, 'B1',   'bidirectional'),
    (22, 'VCCA', 'power_in'),
    (23, 'VCCA', 'power_in'),
    (24, 'VCCB', 'power_in'),
]

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

# Connector pin lists
CONNECTORS = {
    'J1':  {'pins': ['PC4', 'PC5', 'PB0', 'PB1', 'PC3', 'PC2', 'PC0', 'PA0'], 'val': '1x08 Analog 3.3V'},
    'J2':  {'pins': ['VIN', '+3V3', '+3V3', 'IOREF_3V3', 'NRST', 'PC2_C', 'PC3_C', 'PA1_C', 'PA0_C', 'PB13'], 'val': '1x10 Power 3.3V'},
    'J3':  {'pins': ['D8', 'D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1'], 'val': '1x08 Digital 3.3V'},
    'J4':  {'pins': ['SCL1', 'SDA1', 'AREF_3V3', 'D13', 'D12', 'D11', 'D10', 'D9'], 'val': '1x08 Digital 3.3V'},
    'J5':  {'pins': ['NC', 'IOREF_3V3', 'NRST', '+3V3', '+5V', 'GND', 'GND', 'VIN',
                     'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
                     'A8', 'A9', 'A10', 'A11', 'DAC0', 'DAC1', 'CAN_RX', 'CAN_TX', 'NC', 'NC'], 'val': '1x26 Analog 5V'},
    'J6':  {'pins': ['D0', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20'], 'val': '1x08 Digital 3.3V'},
    'J7':  {'pins': ['D21', 'PA4', 'PA5', 'PB5', '+3V3', 'GND', '+5V', 'GND'], 'val': '1x08 Misc 3.3V'},
    'J8':  {'pins': ['PB6', 'PH12', 'AREF', 'GND',
                     'PH6', 'PJ11', 'PJ10', 'PK1', 'PB9',
                     'PB8', 'PB4', 'PD13_5V', 'PA7', 'PJ8', 'PA2', 'PA3', 'PA9',
                     'PB7', 'PG14', 'PC7', 'PH13', 'PI9', 'PD5', 'PD6', 'PB11', 'PH4'], 'val': '1x26 Digital 5V'},
    'J9':  {'pins': ['+5V', '+5V',
                     'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29',
                     'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37',
                     'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45',
                     'D46', 'D47', 'D48', 'D49', 'D50', 'D51', 'D52', 'D53',
                     'GND', 'GND'], 'val': '2x18 Side 3.3V'},
    'J10': {'pins': ['+5V', '+5V',
                     'PJ12', 'PG13', 'PG12', 'PJ0', 'PJ14', 'PJ1', 'PJ15', 'PJ2',
                     'PK3', 'PJ3', 'PK4', 'PJ4', 'PK5', 'PJ5', 'PK6', 'PJ6',
                     'PJ7', 'PI14', 'PE6', 'PK7', 'PI15', 'PI10', 'PG10', 'PI13',
                     'PH15', 'PB2', 'PK0', 'PE4', 'PI11', 'PE5', 'PK2', 'PG7',
                     'GND', 'GND'], 'val': '2x18 Side 5V'},
    'J11': {'pins': ['DIR_U1', 'DIR_U2', 'DIR_U3', 'DIR_U4', 'DIR_U5',
                     'DIR_U6', 'DIR_U7', 'DIR_U8', 'DIR_U9', 'DIR_U10', 'GND'], 'val': '1x11 DIR Control'},
}

POWER_NETS = {'+3V3', '+5V', 'GND'}


def get_shifter_net(uref, pin_num):
    """Get the net name for a given shifter pin."""
    sn = SHIFTER_NETS[uref]
    pin_map = {
        1: sn['dir_net'],
        2: sn['a'][0], 3: sn['a'][1], 4: sn['a'][2], 5: sn['a'][3],
        6: 'GND',
        7: sn['a'][4], 8: sn['a'][5], 9: sn['a'][6], 10: sn['a'][7],
        11: 'GND', 12: 'GND',
        13: sn['b'][7], 14: sn['b'][6], 15: sn['b'][5], 16: sn['b'][4],
        17: '+5V',
        18: sn['b'][3], 19: sn['b'][2], 20: sn['b'][1], 21: sn['b'][0],
        22: '+3V3', 23: '+3V3', 24: '+5V',
    }
    return pin_map.get(pin_num, '')


def emit_lib_symbol_sn74(out):
    """Emit the SN74LVC8T245 library symbol definition."""
    out.append('    (symbol "SN74LVC8T245PW" (in_bom yes) (on_board yes)')
    out.append('      (property "Reference" "U" (at 0 16.51 0)')
    out.append('        (effects (font (size 1.27 1.27))))')
    out.append('      (property "Value" "SN74LVC8T245PW" (at 0 -16.51 0)')
    out.append('        (effects (font (size 1.27 1.27))))')
    out.append('      (property "Footprint" "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm" (at 0 0 0)')
    out.append('        (effects (font (size 1.27 1.27)) hide))')
    out.append('      (symbol "SN74LVC8T245PW_0_1"')
    out.append('        (rectangle (start -10.16 15.24) (end 10.16 -15.24)')
    out.append('          (stroke (width 0.254) (type default))')
    out.append('          (fill (type background))))')
    out.append('      (symbol "SN74LVC8T245PW_1_1"')
    # Left side pins (1-12)
    pins_left = [
        (1, 'DIR', -12.7, 13.97, 0, 'input'),
        (2, 'A1', -12.7, 11.43, 0, 'bidirectional'),
        (3, 'A2', -12.7, 8.89, 0, 'bidirectional'),
        (4, 'A3', -12.7, 6.35, 0, 'bidirectional'),
        (5, 'A4', -12.7, 3.81, 0, 'bidirectional'),
        (6, 'GND', -12.7, 1.27, 0, 'power_in'),
        (7, 'A5', -12.7, -1.27, 0, 'bidirectional'),
        (8, 'A6', -12.7, -3.81, 0, 'bidirectional'),
        (9, 'A7', -12.7, -6.35, 0, 'bidirectional'),
        (10, 'A8', -12.7, -8.89, 0, 'bidirectional'),
        (11, '~{OE}', -12.7, -11.43, 0, 'input'),
        (12, 'GND', -12.7, -13.97, 0, 'power_in'),
    ]
    pins_right = [
        (13, 'B8', 12.7, -8.89, 180, 'bidirectional'),
        (14, 'B7', 12.7, -6.35, 180, 'bidirectional'),
        (15, 'B6', 12.7, -3.81, 180, 'bidirectional'),
        (16, 'B5', 12.7, -1.27, 180, 'bidirectional'),
        (17, 'VCCB', 12.7, 1.27, 180, 'power_in'),
        (18, 'B4', 12.7, 3.81, 180, 'bidirectional'),
        (19, 'B3', 12.7, 6.35, 180, 'bidirectional'),
        (20, 'B2', 12.7, 8.89, 180, 'bidirectional'),
        (21, 'B1', 12.7, 11.43, 180, 'bidirectional'),
        (22, 'VCCA', 12.7, 13.97, 180, 'power_in'),
        (23, 'VCCA', 12.7, -11.43, 180, 'power_in'),
        (24, 'VCCB', 12.7, -13.97, 180, 'power_in'),
    ]
    for num, name, px, py, angle, ptype in pins_left + pins_right:
        out.append(f'        (pin {ptype} line (at {px} {py} {angle}) (length 2.54)')
        out.append(f'          (name "{name}" (effects (font (size 1.27 1.27))))')
        out.append(f'          (number "{num}" (effects (font (size 1.27 1.27)))))' )
    out.append('      )')
    out.append('    )')


def emit_lib_symbol_conn(out, npins, ncols):
    """Emit a generic connector library symbol."""
    name = f"Conn_{ncols:02d}x{npins // ncols:02d}_Pin"
    rows_h = npins // ncols
    fp_name = f"Connector_PinHeader_{ncols}x{rows_h:02d}_P2.54mm_Vertical"
    out.append(f'    (symbol "{name}" (in_bom yes) (on_board yes)')
    out.append(f'      (property "Reference" "J" (at 0 {npins + 2} 0)')
    out.append(f'        (effects (font (size 1.27 1.27))))')
    out.append(f'      (property "Value" "{name}" (at 0 -{npins + 2} 0)')
    out.append(f'        (effects (font (size 1.27 1.27))))')
    out.append(f'      (property "Footprint" "{fp_name}" (at 0 0 0)')
    out.append(f'        (effects (font (size 1.27 1.27)) hide))')
    h = npins // ncols
    out.append(f'      (symbol "{name}_0_1"')
    out.append(f'        (rectangle (start -2.54 {h * 1.27 + 1.27}) (end {(ncols - 1) * 5.08 + 2.54} {-h * 1.27 - 1.27})')
    out.append(f'          (stroke (width 0.254) (type default))')
    out.append(f'          (fill (type background))))')
    out.append(f'      (symbol "{name}_1_1"')
    pin_num = 1
    for row in range(h):
        for col in range(ncols):
            px = -5.08 if col == 0 else (ncols - 1) * 5.08 + 5.08
            py = (h // 2 - row) * 2.54
            angle = 0 if col == 0 else 180
            out.append(f'        (pin passive line (at {px} {py} {angle}) (length 2.54)')
            out.append(f'          (name "Pin_{pin_num}" (effects (font (size 1.27 1.27))))')
            out.append(f'          (number "{pin_num}" (effects (font (size 1.27 1.27)))))' )
            pin_num += 1
    out.append('      )')
    out.append('    )')
    return name


def emit_lib_symbol_passive(out, sym_name, ref_prefix):
    """Emit a passive component (R or C) library symbol."""
    out.append(f'    (symbol "{sym_name}" (in_bom yes) (on_board yes)')
    out.append(f'      (property "Reference" "{ref_prefix}" (at 0 2.54 0)')
    out.append(f'        (effects (font (size 1.27 1.27))))')
    out.append(f'      (property "Value" "{sym_name}" (at 0 -2.54 0)')
    out.append(f'        (effects (font (size 1.27 1.27))))')
    out.append(f'      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 0 0)')
    out.append(f'        (effects (font (size 1.27 1.27)) hide))')
    out.append(f'      (symbol "{sym_name}_0_1"')
    out.append(f'        (rectangle (start -1.016 1.27) (end 1.016 -1.27)')
    out.append(f'          (stroke (width 0.254) (type default))')
    out.append(f'          (fill (type background))))')
    out.append(f'      (symbol "{sym_name}_1_1"')
    out.append(f'        (pin passive line (at -3.81 0 0) (length 2.794)')
    out.append(f'          (name "1" (effects (font (size 1.27 1.27))))')
    out.append(f'          (number "1" (effects (font (size 1.27 1.27)))))' )
    out.append(f'        (pin passive line (at 3.81 0 180) (length 2.794)')
    out.append(f'          (name "2" (effects (font (size 1.27 1.27))))')
    out.append(f'          (number "2" (effects (font (size 1.27 1.27)))))' )
    out.append(f'      )')
    out.append(f'    )')


def emit_label(out, net_name, x, y, angle=0):
    """Emit a net label at the given position."""
    if net_name.startswith('NC'):
        return
    out.append(f'  (label "{net_name}" (at {x} {y} {angle}) (fields_autoplaced)')
    out.append(f'    (effects (font (size 1.27 1.27)) (justify left))')
    out.append(f'    (uuid {uid()}))')


def emit_power_label(out, net_name, x, y):
    """Emit a power flag/label."""
    out.append(f'  (global_label "{net_name}" (shape passive) (at {x} {y} 0) (fields_autoplaced)')
    out.append(f'    (effects (font (size 1.27 1.27)) (justify left))')
    out.append(f'    (uuid {uid()}))')


def build_schematic():
    out = []

    # Header
    out.append('(kicad_sch (version 20230121) (generator build_kicad_sch)')
    out.append('')
    out.append('  (uuid ' + uid() + ')')
    out.append('')
    out.append('  (paper "A1")')
    out.append('')

    # Library symbols
    out.append('  (lib_symbols')
    emit_lib_symbol_sn74(out)
    emit_lib_symbol_passive(out, 'C_0603', 'C')
    emit_lib_symbol_passive(out, 'R_0603', 'R')

    # Mounting hole lib symbol
    out.append('    (symbol "MountingHole" (in_bom no) (on_board yes)')
    out.append('      (property "Reference" "H" (at 0 3.81 0)')
    out.append('        (effects (font (size 1.27 1.27))))')
    out.append('      (property "Value" "MountingHole" (at 0 -3.81 0)')
    out.append('        (effects (font (size 1.27 1.27))))')
    out.append('      (property "Footprint" "MountingHole:MountingHole_3.2mm_M3" (at 0 0 0)')
    out.append('        (effects (font (size 1.27 1.27)) hide))')
    out.append('      (symbol "MountingHole_0_1"')
    out.append('        (circle (center 0 0) (radius 1.27)')
    out.append('          (stroke (width 0.254) (type default))')
    out.append('          (fill (type none))))')
    out.append('      (symbol "MountingHole_1_1"')
    out.append('        (pin passive line (at 0 -3.81 90) (length 2.54)')
    out.append('          (name "1" (effects (font (size 1.27 1.27))))')
    out.append('          (number "1" (effects (font (size 1.27 1.27)))))' )
    out.append('      )')
    out.append('    )')

    # Connector symbols — collect unique types
    conn_lib_names = {}
    for ref, info in CONNECTORS.items():
        npins = len(info['pins'])
        ncols = 2 if ref in ('J9', 'J10') else 1
        key = (npins, ncols)
        if key not in conn_lib_names:
            conn_lib_names[key] = emit_lib_symbol_conn(out, npins, ncols)

    out.append('  )')  # end lib_symbols
    out.append('')

    # Place shifter symbols
    sx_base, sy_base = 50, 50
    for idx, uref in enumerate(['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10']):
        col = idx % 5
        row = idx // 5
        sx = sx_base + col * 55
        sy = sy_base + row * 75

        out.append(f'  (symbol (lib_id "SN74LVC8T245PW") (at {sx} {sy} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes)')
        out.append(f'    (uuid {uid()})')
        out.append(f'    (property "Reference" "{uref}" (at {sx} {sy - 18} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "SN74LVC8T245PW" (at {sx} {sy + 18} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm" (at {sx} {sy} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        # Pin instances
        for pin_num in range(1, 25):
            out.append(f'    (pin "{pin_num}" (uuid {uid()}))')
        out.append(f'  )')
        out.append('')

        # Net labels on each pin
        sn = SHIFTER_NETS[uref]
        left_pins = [
            (1, sn['dir_net'], -12.7, 13.97),
            (2, sn['a'][0], -12.7, 11.43),
            (3, sn['a'][1], -12.7, 8.89),
            (4, sn['a'][2], -12.7, 6.35),
            (5, sn['a'][3], -12.7, 3.81),
            (6, 'GND', -12.7, 1.27),
            (7, sn['a'][4], -12.7, -1.27),
            (8, sn['a'][5], -12.7, -3.81),
            (9, sn['a'][6], -12.7, -6.35),
            (10, sn['a'][7], -12.7, -8.89),
            (11, 'GND', -12.7, -11.43),
            (12, 'GND', -12.7, -13.97),
        ]
        right_pins = [
            (13, sn['b'][7], 12.7, -8.89),
            (14, sn['b'][6], 12.7, -6.35),
            (15, sn['b'][5], 12.7, -3.81),
            (16, sn['b'][4], 12.7, -1.27),
            (17, '+5V', 12.7, 1.27),
            (18, sn['b'][3], 12.7, 3.81),
            (19, sn['b'][2], 12.7, 6.35),
            (20, sn['b'][1], 12.7, 8.89),
            (21, sn['b'][0], 12.7, 11.43),
            (22, '+3V3', 12.7, 13.97),
            (23, '+3V3', 12.7, -11.43),
            (24, '+5V', 12.7, -13.97),
        ]
        for pin_num, net, px, py in left_pins:
            lx = sx + px - 2
            ly = sy + py
            if net in POWER_NETS:
                emit_power_label(out, net, lx, ly)
            else:
                emit_label(out, net, lx, ly, 180)

        for pin_num, net, px, py in right_pins:
            lx = sx + px + 2
            ly = sy + py
            if net in POWER_NETS:
                emit_power_label(out, net, lx, ly)
            else:
                emit_label(out, net, lx, ly)

    # Place capacitors
    cx_base, cy_base = 50, 210
    cap_num = 1
    for idx, uref in enumerate(['U1','U2','U3','U4','U5','U6','U7','U8','U9','U10']):
        # VCCA cap
        cref_a = f'C{cap_num}'
        cx = cx_base + idx * 25
        cy = cy_base
        out.append(f'  (symbol (lib_id "C_0603") (at {cx} {cy} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{cref_a}" (at {cx} {cy - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "0.1uF" (at {cx} {cy + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {cx} {cy} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (pin "1" (uuid {uid()}))')
        out.append(f'    (pin "2" (uuid {uid()}))')
        out.append(f'  )')
        emit_power_label(out, '+3V3', cx - 5.81, cy)
        emit_power_label(out, 'GND', cx + 5.81, cy)
        cap_num += 1

        # VCCB cap
        cref_b = f'C{cap_num}'
        cy2 = cy_base + 12
        out.append(f'  (symbol (lib_id "C_0603") (at {cx} {cy2} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{cref_b}" (at {cx} {cy2 - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "0.1uF" (at {cx} {cy2 + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {cx} {cy2} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (pin "1" (uuid {uid()}))')
        out.append(f'    (pin "2" (uuid {uid()}))')
        out.append(f'  )')
        emit_power_label(out, '+5V', cx - 5.81, cy2)
        emit_power_label(out, 'GND', cx + 5.81, cy2)
        cap_num += 1

    # Extra power caps (C21-C29)
    for i in range(9):
        cref = f'C{cap_num}'
        cx = cx_base + i * 25
        cy = cy_base + 28
        pwr = '+3V3' if i % 2 == 0 else '+5V'
        out.append(f'  (symbol (lib_id "C_0603") (at {cx} {cy} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{cref}" (at {cx} {cy - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "0.1uF" (at {cx} {cy + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {cx} {cy} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (pin "1" (uuid {uid()}))')
        out.append(f'    (pin "2" (uuid {uid()}))')
        out.append(f'  )')
        emit_power_label(out, pwr, cx - 5.81, cy)
        emit_power_label(out, 'GND', cx + 5.81, cy)
        cap_num += 1

    # Place resistors (R1-R10)
    rx_base, ry_base = 50, 250
    for i in range(10):
        rref = f'R{i+1}'
        uref = f'U{i+1}'
        rx = rx_base + i * 25
        ry = ry_base
        out.append(f'  (symbol (lib_id "R_0603") (at {rx} {ry} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{rref}" (at {rx} {ry - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "10K" (at {rx} {ry + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {rx} {ry} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (pin "1" (uuid {uid()}))')
        out.append(f'    (pin "2" (uuid {uid()}))')
        out.append(f'  )')
        emit_label(out, SHIFTER_NETS[uref]['dir_net'], rx - 5.81, ry, 180)
        emit_power_label(out, 'GND', rx + 5.81, ry)

    # Place connectors
    jx_base, jy_base = 330, 30
    for jidx, ref in enumerate(['J1','J2','J3','J4','J5','J6','J7','J8','J9','J10','J11']):
        info = CONNECTORS[ref]
        pins = info['pins']
        npins = len(pins)
        ncols = 2 if ref in ('J9', 'J10') else 1
        key = (npins, ncols)
        lib_name = conn_lib_names[key]

        jx = jx_base + (jidx % 4) * 65
        jy = jy_base + (jidx // 4) * 80

        rows_h = npins // ncols
        fp_name = f"Connector_PinHeader_{ncols}x{rows_h:02d}_P2.54mm_Vertical"

        out.append(f'  (symbol (lib_id "{lib_name}") (at {jx} {jy} 0) (unit 1)')
        out.append(f'    (in_bom yes) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{ref}" (at {jx} {jy - npins - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "{info["val"]}" (at {jx} {jy + npins + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "{fp_name}" (at {jx} {jy} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        for p in range(1, npins + 1):
            out.append(f'    (pin "{p}" (uuid {uid()}))')
        out.append(f'  )')

        # Net labels on connector pins
        rows = npins // ncols
        pin_num = 1
        for row in range(rows):
            for col in range(ncols):
                net = pins[pin_num - 1]
                if col == 0:
                    lx = jx - 7.08
                    angle = 180
                else:
                    lx = jx + (ncols - 1) * 5.08 + 7.08
                    angle = 0
                ly = jy + (rows // 2 - row) * 2.54
                if net == 'NC' or net == 'VIN':
                    pass
                elif net in POWER_NETS:
                    emit_power_label(out, net, lx, ly)
                else:
                    emit_label(out, net, lx, ly, angle)
                pin_num += 1

    # Mounting holes
    for i in range(4):
        href = f'H{i+1}'
        hx = 330 + i * 20
        hy = 280
        out.append(f'  (symbol (lib_id "MountingHole") (at {hx} {hy} 0) (unit 1)')
        out.append(f'    (in_bom no) (on_board yes) (uuid {uid()})')
        out.append(f'    (property "Reference" "{href}" (at {hx} {hy - 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "MountingHole_3.2mm" (at {hx} {hy + 4} 0)')
        out.append(f'      (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "MountingHole:MountingHole_3.2mm_M3" (at {hx} {hy} 0)')
        out.append(f'      (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (pin "1" (uuid {uid()}))')
        out.append(f'  )')

    # Title block
    out.append('')
    out.append('  (text "GigaShield v0.4 - Arduino Giga R1 Level Shifter Shield" (at 150 290 0)')
    out.append('    (effects (font (size 3 3) bold)))')
    out.append('  (text "10x SN74LVC8T245PW, 72 channels, 3.3V <-> 5V" (at 150 296 0)')
    out.append('    (effects (font (size 2 2))))')

    out.append('')
    out.append(')')

    return '\n'.join(out)


if __name__ == '__main__':
    outfile = sys.argv[1] if len(sys.argv) > 1 else 'giga_shield_v04.kicad_sch'
    content = build_schematic()
    with open(outfile, 'w') as f:
        f.write(content)
    print(f"Generated {outfile}")
    print(f"10x SN74LVC8T245PW, 29 caps, 10 resistors, 11 connectors")
