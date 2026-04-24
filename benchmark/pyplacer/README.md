# pyplacer

A simulated-annealing PCB component placer in ~500 lines of Python.

**Purpose:** Provide an open-source alternative to commercial ML placers (Quilter.ai) for
benchmark comparison with Freerouting. Takes a KiCad PCB file with components moved off-board
and produces a placed PCB file. Does not route — pair with Freerouting for that.

## Algorithm

Classic Kirkpatrick-style simulated annealing:

1. **Initial state**: random placement of movable components inside the board outline
   (fixed components — connectors and mounting holes — stay where they are).
2. **Cost function**: Half-Perimeter Wire Length (HPWL) over all nets + overlap penalty
   + out-of-bounds penalty.
3. **Moves**: translate, rotate (90° increments), or swap two components.
4. **Acceptance**: if ΔE ≤ 0 always accept; else accept with probability e^(-ΔE / T).
5. **Cooling**: exponential T ← αT with α ≈ 0.95, N moves per temperature plateau.
6. **Termination**: T below threshold or no improvement for K plateaus.

## Data model

Components are parsed from the `.kicad_pcb` file. Each has:
- reference designator
- position (x, y), rotation (0/90/180/270)
- pads with local coordinates and assigned nets
- local bounding box (for overlap check)
- fixed flag (connectors J*, mounting holes H*)

Nets are lists of (component_ref, pad_id) pairs from the file's net table.

## File I/O

Parses KiCad 9 format (version 20241229). The parser preserves everything except
footprint positions — we only rewrite the top-level `(at X Y [rot])` of each movable
footprint. Non-movable footprints and all other content pass through untouched.

## Usage

```bash
python3 run.py input.kicad_pcb output.kicad_pcb
```

Optional flags:
- `--iterations N` — number of SA moves per temperature (default 5000)
- `--t-init T` — initial temperature (default: auto from initial cost)
- `--cooling A` — cooling rate 0.0-1.0 (default 0.95)
- `--seed S` — random seed for reproducibility
- `--plot` — dump a PNG of the final placement
