"""Flip U7, U9, U10 and their supporting caps/resistors to the bottom copper layer.

This opens up the right-side U6-U10 cluster on the top layer by moving 3 of the
5 shifters (plus their VCCA/VCCB bypass caps and DIR pull-down resistors) to the
back. pcbnew.FOOTPRINT.Flip() handles layer transitions for pads, silk, mask, and
paste in one call."""
import sys
import pcbnew

SRC = '/Users/alexjokela/projects/giga-shield/giga_shield_v04.kicad_pcb'
DST = '/Users/alexjokela/projects/giga-shield/giga_shield_v05.kicad_pcb'

# Shifters to flip, plus their 2 VCCA/VCCB caps and DIR resistor.
#   U7 -> C13 (VCCA), C14 (VCCB), R7 (DIR)
#   U9 -> C17 (VCCA), C18 (VCCB), R9 (DIR)
#   U10 -> C19 (VCCA), C20 (VCCB), R10 (DIR pad)
REFS_TO_FLIP = {
    'U7', 'C13', 'C14', 'R7',
    'U9', 'C17', 'C18', 'R9',
    'U10', 'C19', 'C20', 'R10',
}

board = pcbnew.LoadBoard(SRC)
flipped = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in REFS_TO_FLIP:
        fp.Flip(fp.GetPosition(), False)
        flipped.append(ref)

pcbnew.SaveBoard(DST, board)
print(f"flipped {len(flipped)} footprints: {sorted(flipped)}")
print(f"wrote {DST}")
