"""Compute placement+routing benchmark metrics for each pipeline.

Reads SES (Specctra session) files and extracts:
  - total wire length (mm)
  - via count
  - net count (from DSN)
  - routed net count (distinct nets in wires/vias)

Also reads PCB/SES files to count layers actually used."""
import re
import math
import sys
from pathlib import Path


def parse_ses_wires_vias(ses_path):
    """Return (total_mm, via_count, routed_nets_set, wire_count, layers_used)."""
    text = Path(ses_path).read_text()
    # Resolution: (resolution mm N) or (resolution um N) - assume mm with integer multiplier
    res_m = re.search(r'\(resolution\s+(\S+)\s+(\d+)', text)
    unit = res_m.group(1) if res_m else 'um'
    div = int(res_m.group(2)) if res_m else 1000000
    to_mm = 1.0 / div if unit == 'mm' else 1.0 / (div * 1000.0)

    total_len = 0.0
    via_count = 0
    wire_count = 0
    layers = set()
    routed_nets = set()

    # net blocks: (net "NAME" (wire (path LAYER WIDTH x y x y ...)) (via ...) ...)
    # Scan for each `(net "..."` block
    for m in re.finditer(r'\(net\s+"?([^"\s]+)"?\s', text):
        net_name = m.group(1)
        # Find the extent of this net block (balanced parens)
        start = m.start()
        # Find the close paren
        depth = 0
        i = start
        while i < len(text):
            c = text[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = text[start:i + 1]

        has_content = False
        # Wires: (wire (path LAYER WIDTH x y x y ...))
        for pm in re.finditer(r'\(path\s+"?([^"\s]+)"?\s+\S+\s+((?:-?[\d.]+\s+)+)\)', block):
            layer = pm.group(1)
            coords = [float(c) for c in pm.group(2).split()]
            layers.add(layer)
            wire_count += 1
            has_content = True
            for j in range(0, len(coords) - 2, 2):
                x1, y1, x2, y2 = coords[j], coords[j+1], coords[j+2], coords[j+3]
                total_len += math.hypot(x2 - x1, y2 - y1) * to_mm

        # Vias: (via pstk_1 X Y ...)
        for pm in re.finditer(r'\(via\s+\S+\s+(-?[\d.]+)\s+(-?[\d.]+)', block):
            via_count += 1
            has_content = True

        if has_content:
            routed_nets.add(net_name)

    return {
        'total_mm': total_len,
        'via_count': via_count,
        'wire_count': wire_count,
        'routed_nets': routed_nets,
        'layers_used': len(layers),
    }


def count_nets_in_dsn(dsn_path):
    """Return the total number of nets declared in a DSN file."""
    text = Path(dsn_path).read_text()
    nets = set()
    for m in re.finditer(r'\(net\s+"?([A-Za-z+][A-Za-z0-9_+]*)"?\s', text):
        nets.add(m.group(1))
    return len(nets)


def report(label, ses_path, dsn_path):
    if not Path(ses_path).exists():
        print(f"{label:35s}  SES not found: {ses_path}")
        return
    stats = parse_ses_wires_vias(ses_path)
    total_nets = count_nets_in_dsn(dsn_path) if Path(dsn_path).exists() else None
    routed_n = len(stats['routed_nets'])
    ratio = (routed_n / total_nets * 100) if total_nets else None
    print(f"{label:35s}  "
          f"traces={stats['total_mm']:7.1f}mm  "
          f"vias={stats['via_count']:4d}  "
          f"layers={stats['layers_used']}  "
          f"routed_nets={routed_n}/{total_nets if total_nets else '?'}  "
          f"{f'({ratio:.1f}%)' if ratio else ''}")


def parse_kicad_pcb_routing(pcb_path):
    """Extract traces+vias from a routed KiCad PCB file.

    Segments: (segment (start x y) (end x y) (width W) (layer "...") (net N))
    Vias: (via (at x y) (size S) (drill D) (layers ...) (net N))"""
    text = Path(pcb_path).read_text()
    total_len = 0.0
    via_count = 0
    wire_count = 0
    layers = set()
    routed_nets = set()

    for m in re.finditer(
        r'\(segment\s*\(start\s+(-?[\d.]+)\s+(-?[\d.]+)\)\s*\(end\s+(-?[\d.]+)\s+(-?[\d.]+)\).*?\(layer\s+"([^"]+)"\).*?\(net\s+(\d+)\)',
        text, re.DOTALL):
        x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        total_len += math.hypot(x2 - x1, y2 - y1)
        layers.add(m.group(5))
        routed_nets.add(m.group(6))
        wire_count += 1

    for m in re.finditer(
        r'\(via\s*\(at\s+-?[\d.]+\s+-?[\d.]+\).*?\(net\s+(\d+)\)',
        text, re.DOTALL):
        via_count += 1
        routed_nets.add(m.group(1))

    return {
        'total_mm': total_len,
        'via_count': via_count,
        'wire_count': wire_count,
        'routed_nets': routed_nets,
        'layers_used': len(layers),
    }


def count_nets_in_kicad_pcb(pcb_path):
    """Count nets in a KiCad PCB file (excluding net 0, which is 'no net')."""
    text = Path(pcb_path).read_text()
    nets = set()
    for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]*)"\s*\)', text):
        nid = int(m.group(1))
        if nid != 0:
            nets.add(nid)
    return len(nets)


def report_kicad(label, pcb_path):
    if not Path(pcb_path).exists():
        print(f"{label:35s}  PCB not found: {pcb_path}")
        return
    stats = parse_kicad_pcb_routing(pcb_path)
    total_nets = count_nets_in_kicad_pcb(pcb_path)
    routed_n = len(stats['routed_nets'])
    ratio = (routed_n / total_nets * 100) if total_nets else None
    print(f"{label:35s}  "
          f"traces={stats['total_mm']:7.1f}mm  "
          f"vias={stats['via_count']:4d}  "
          f"layers={stats['layers_used']}  "
          f"routed_nets={routed_n}/{total_nets}  "
          f"{f'({ratio:.1f}%)' if ratio else ''}")


if __name__ == '__main__':
    base = '/Users/alexjokela/projects/giga-shield'
    report('base + Freerouting 100% (v04)',
           f'{base}/giga_shield_v04.ses',
           f'{base}/giga_shield.dsn')
    report('base + Freerouting (benchmark/)',
           f'{base}/benchmark/freerouting/giga_shield_v04.ses',
           f'{base}/benchmark/base/giga_shield.dsn')
    # Quilter writes .kicad_pcb (routed), not SES — skip for now, add pcb parser later
    report_kicad('Quilter auto-route',
           f'{base}/benchmark/quilter/Quilter_giga_shield_v04.kicad_pcb_Candidate_1/giga_shield_v04.kicad_pcb')
    pyplacer_ses = f'{base}/benchmark/pyplacer/giga_shield_v04_placed_v2.ses'
    report('pyplacer v2 + Freerouting', pyplacer_ses,
           f'{base}/benchmark/pyplacer/giga_shield_v04_placed_v2.dsn')
    # Also show pyplacer v1 (old cost function) for historical
    report('pyplacer v1 + Freerouting',
           f'{base}/benchmark/pyplacer/giga_shield_pyplaced.ses',
           f'{base}/benchmark/pyplacer/giga_shield_pyplaced.dsn')
