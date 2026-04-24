"""Patch a pcb-rnd .pcb file with new placements from placements.json.

pcb-rnd Element syntax:
    Element["flags" "package" "ref" "value" xmark_nm ymark_nm text_x text_y text_dir text_size "text_flags"]

xmark_nm and ymark_nm are the component's position in nanometers.
Inside the Element block, pins/pads are relative to the mark.

For rotation, pcb-rnd rotates all pin/pad coordinates during generation. Since our KiCad
pyplacer operates on components with already-rotated pad coordinates (baked into the
generated Element block), we only need to update the (x, y) mark position to match
pyplacer's output — EXCEPT when pyplacer rotated the component to a different angle.

For components where pyplacer changed rotation: the pad layout in pcb-rnd is wrong for
the new orientation. We'd need to regenerate those from scratch. Easiest handling:
skip rotation changes from pyplacer, keeping original orientation. This is a mild
suboptimality but avoids the footprint-regeneration headache.
"""
import json
import re
from pathlib import Path

placements = json.loads(Path('/Users/alexjokela/projects/giga-shield/benchmark/pyplacer/placements.json').read_text())

pcb_src = Path('/Users/alexjokela/projects/giga-shield/benchmark/base/giga_shield.pcb').read_text()

# Find all Element[...] opening lines, extract the ref, and rewrite x/y.
# Element line format:
#   Element["" "TSSOP24" "U1" "SN74LVC8T245PW" 152300000nm 45800000nm ...]
element_re = re.compile(
    r'(Element\[\s*"[^"]*"\s+"[^"]*"\s+"([^"]+)"\s+"[^"]*"\s+)'
    r'(\d+nm)\s+(\d+nm)(\s+)',
)

patched_count = 0
skipped_rot = []

def replace(m):
    global patched_count
    ref = m.group(2)
    if ref not in placements:
        return m.group(0)
    p = placements[ref]
    new_x_nm = int(round(p['x'] * 1_000_000))
    new_y_nm = int(round(p['y'] * 1_000_000))
    if int(p['rot']) % 360 != 0:
        # Note rotation change — we're keeping the original pcb-rnd orientation
        skipped_rot.append((ref, p['rot']))
    patched_count += 1
    return f"{m.group(1)}{new_x_nm}nm {new_y_nm}nm{m.group(5)}"

new_pcb = element_re.sub(replace, pcb_src)

out_path = Path('/Users/alexjokela/projects/giga-shield/benchmark/pyplacer/giga_shield_pyplaced.pcb')
out_path.write_text(new_pcb)

print(f"Patched {patched_count} elements")
if skipped_rot:
    print(f"WARNING: {len(skipped_rot)} components had non-zero rotation from pyplacer (rotation NOT applied to pcb-rnd):")
    for ref, rot in skipped_rot:
        print(f"  {ref}: pyplacer wanted rot={rot}°")
print(f"Wrote {out_path}")
