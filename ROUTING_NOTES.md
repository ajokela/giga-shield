# Giga Shield v0.3: Routing Journey

Notes for a future blog post. Covers everything tried to get a fully-routed 6-layer level shifter board.

## The Board

Arduino Giga R1 WiFi shield with 10x SN74LVC8T245PW driven level shifters (TSSOP-24). Replaces the original TXB0108PW auto-sensing design, which fails during Z80 bus tri-state periods. 155mm x 90mm, 80 channels of 3.3V/5V level shifting, 161 nets, 39 SMD components, 10+ through-hole connectors.

## The Core Problem: GND

The board has 72 GND pads across 10 TSSOP-24 ICs (pins 6, 11, 12 on each), 29 decoupling caps, and 10 pull-down resistors. In a normal KiCad workflow, you'd route signals and then flood the board with a GND copper pour. Freerouting (the open-source Specctra autorouter) cannot do copper pours. It treats every net, including GND, as point-to-point traces.

The TSSOP-24 package makes this worse. At 0.65mm pitch, there's only ~0.25mm between pad edges. A via needs ~0.9mm diameter (drill + annular ring + clearance). There is physically no room to place a via next to a TSSOP-24 GND pad without violating DRC. Freerouting reports "via mask not found for net" and leaves GND connections unrouted.

## The Toolchain

The board was designed entirely in Python. `build_giga_shield.py` generates a pcb-rnd native `.pcb` file from scratch, with all component positions, footprints, and netlists defined programmatically. Component positions were extracted from an earlier KiCad 9.0 design, but pcb-rnd 3.1.4 can't read KiCad 9.0 files, so everything was regenerated.

The routing pipeline:
```
build_giga_shield.py -> giga_shield.pcb
                           |
                    pcb-rnd DSN export
                           |
                    giga_shield.dsn
                           |
                    Freerouting 1.9.0
                           |
                    giga_shield.ses
                           |
                    ses_to_pcb.py -> routed giga_shield.pcb
```

pcb-rnd runs on a remote Linux machine (10.1.1.27, Ryzen AI MAX+ 395) via SSH since it's not available on macOS.

## Attempt 1: 2-Layer with Freerouting

The simplest approach. Exclude GND from routing, let freerouting handle all signal and power nets on 2 layers, then add GND connections afterward.

**Config:**
```python
POWER_NETS = {'GND', 'VIN'}  # excluded from routing
```

Freerouting 1.9.0 with `-mp 100` (100 optimization passes). Single run: ~55 minutes. Result: 6 unrouted nets on the best run. The remaining 6 were always signal traces boxed in by other routes with no path to their destination.

**Verdict:** Close but not clean. 6 unrouted is 6 too many for production.

## Attempt 2: Manual GND Post-Processing (add_gnd.py)

Wrote a script to add GND after routing. Strategy:
1. Calculate exact GND pad positions from component geometry
2. Place a via near each SMD GND pad (offset ~0.5mm to avoid other pads)
3. Connect all vias on the bottom layer using a Minimum Spanning Tree (Prim's algorithm)

The MST approach minimizes total trace length while connecting all 72+ GND points. IC GND pads get vias offset to the left (away from IC body), cap/resistor pads get vias offset downward.

**Problem:** The vias still couldn't fit in the 0.65mm pitch gaps between TSSOP-24 pads. Even with the offset, they collided with adjacent signal pads. The script produced a connected GND network but with DRC violations everywhere.

**Verdict:** Clever but geometry wins. Can't squeeze a 0.9mm via into a 0.25mm gap.

## Attempt 3: Copper Pour + Stitching Vias (add_pours.py)

Instead of point-to-point GND traces, add a full copper polygon on the bottom layer and stitch it with vias:
- Full-board GND polygon on Layer 2 with 0.5mm edge margin
- 30 vias near IC GND pads (1.5mm offset from pad center)
- 20 vias near cap GND pads (1.2mm offset)
- Grid of stitching vias every 15mm across the board

**Problem:** pcb-rnd polygons in the native format don't have net assignment in the way that matters for DRC. The polygon existed but wasn't treated as part of the GND net by the autorouter or DRC checker. The GND pads were still electrically floating.

**Verdict:** pcb-rnd's polygon support isn't designed for this workflow.

## Attempt 4: 4-Layer Board

Added two inner layers: one for GND plane, one for power (+3V3/+5V). This is the "standard" solution for dense SMD boards.

**Config:**
```python
# 4 layers: top(1), GND(2), power(3), bottom(4), outline(5)
out.append('Groups("1,c:2:3:4,s:5")')
```

Freerouting still couldn't use the inner GND layer as a plane. It only does point-to-point routing. The extra layers gave more room for signal traces, but the fundamental GND problem remained. Best result: still 5-6 unrouted.

**Verdict:** More layers don't help when the tool can't do planes.

## Attempt 5: 6-Layer Board

Six copper layers: top, GND, signal, signal, GND, bottom.

Same fundamental limitation. Freerouting had more routing channels but still couldn't handle GND as a plane. Best result with 6 layers: 5 unrouted.

**Verdict:** Diminishing returns. The problem is the tool, not the layer count.

## Attempt 6: Massively Parallel Routing

The insight: freerouting converges to a local optimum. Different net ordering in the DSN file produces different initial routing solutions, which converge to different local optima. If you run enough parallel jobs, one might find the global optimum (0 unrouted).

### Net Shuffling (shuffle_dsn.py)

Wrote a script to generate N copies of the DSN file with randomized net ordering:
```python
random.seed(i * 31337 + 42)  # deterministic but different per copy
random.shuffle(shuffled_nets)
```

Generated 128+ shuffled copies. Each one routes nets in a different order, exploring a different region of the solution space.

### Infrastructure: 3 Machines

- **Local Mac** (M3 Max): 8 parallel jobs
- **10.1.1.24** (64-core, 4x Tesla P40): 64 parallel jobs
- **10.1.1.27** (32-core, Ryzen AI MAX+ 395): 64 parallel jobs

Total: 128+ simultaneous freerouting instances.

### Deployment Hurdles

**Java version mismatch.** Freerouting 1.9.0 was compiled targeting Java 24 (class file version 68.0). The servers had Java 21 (max class version 65.0). Error: `UnsupportedClassVersionError: class file version 68.0`. Fixed by modifying `freerouting/build.gradle`:
```groovy
// Changed from VERSION_24 to VERSION_21
sourceCompatibility = JavaVersion.VERSION_21
targetCompatibility = JavaVersion.VERSION_21
// Commented out java.toolchain block
```
Then rebuilt: `./gradlew executableV19Jar --no-configuration-cache`

**Gradle toolchain error.** `JvmVendorSpec IBM_SEMERU field not found` when building. Fixed by commenting out the entire `java.toolchain` block.

**X11 headless requirement.** Freerouting's GUI code initializes even in batch mode (`-de`, `-do` flags). On headless servers: `HeadlessException: No X11 DISPLAY variable was set`. Fix: install full JRE (`openjdk-21-jre`, not `-headless`) and use `xvfb-run -a` or a shared Xvfb display.

Two scripts for this:
- `run_batch.sh`: Single shared `Xvfb :99` display for all 64 jobs
- `run_batch_xvfb.sh`: `xvfb-run -a` per job (auto-allocated display numbers, more robust)

**Disk space on 10.1.1.27.** 1.9TB disk was at 100% (191GB old logs, large TTS wav files from previous projects). Had to clean up before jobs could write output.

**scp brace expansion.** `scp shuffled_runs/run_{000..031}.dsn user@host:` doesn't work on macOS zsh (brace expansion happens before scp processes the argument). Used `scp shuffled_runs/*.dsn` instead.

### Results: 2-Layer Parallel

Best result across 128 runs: **6 unrouted**. Multiple runs hit 6, none hit 0. The 2-layer board appears to have a hard floor around 6 unrouted nets.

### Results: 6-Layer Parallel

Best result: **5 unrouted**. Marginal improvement but still not clean.

### Freerouting 2.1.0: A Regression

Tried the newer Freerouting v2.1.0 hoping for better results. It was dramatically worse: **152+ unrouted** after 250 passes on the same 2-layer board where v1.9.0 hit 6. Immediately went back to v1.9.0.

**Verdict:** Massive parallelism finds better solutions but can't break through the fundamental floor. The problem is GND routing in TSSOP-24 pitch, and no amount of net shuffling fixes that.

## Attempt 7: Quilter.ai (The Winner)

Quilter.ai is an AI-powered PCB router. Uploaded the KiCad board (generated by `build_kicad.py`) to their service.

### What Quilter Produced

6-layer board, fully routed:
- **0 unrouted nets**
- 2,433 trace segments
- 334 vias
- 2 GND copper zones (on In1.Cu and In4.Cu)

Layer stackup:
| Layer | Purpose |
|-------|---------|
| F.Cu | Signals (top) |
| In1.Cu | GND plane |
| In2.Cu | Signals |
| In3.Cu | Signals |
| In4.Cu | GND plane |
| B.Cu | Signals (bottom) |

The key difference: Quilter understands copper zones. It placed GND planes on In1.Cu and In4.Cu, then used vias to connect TSSOP-24 GND pads down to the plane. This is the standard approach that freerouting simply cannot do.

### Verification

Exported the Quilter board's DSN and fed it back into freerouting to confirm: 0 unrouted, all nets complete.

Ran a signal integrity analysis:
- All 10 ICs' net assignments match the original design
- No bus contention (each Arduino pin maps to exactly one level shifter channel)
- Power integrity verified (GND, +3V3, +5V all correct)
- Direction control properly wired with pull-down resistors
- U9 has 6 NC spare pads, U10 has 8 NC spare pads (intentional; 80 GPIO don't divide evenly into 10x 8-channel ICs)

### Fabrication Output

Used KiCad CLI for fabrication files:
```bash
kicad-cli pcb export gerbers giga_shield_v03_final.kicad_pcb -o fabrication/
kicad-cli pcb export drill giga_shield_v03_final.kicad_pcb -o fabrication/
kicad-cli pcb export pos giga_shield_v03_final.kicad_pcb -o fabrication/giga_shield_v03_final_cpl.csv
```

13 Gerber files (6 copper + 2 solder mask + 2 silk + 2 paste + 1 edge cuts), drill file, pick-and-place CSV, and BOM. Packaged into `giga_shield_v03_gerbers.zip` (293KB) for PCBWay upload.

## Lessons Learned

1. **Freerouting can't do copper pours.** This is its biggest limitation for modern SMD boards. Any design with dense GND connections (which is basically every board with fine-pitch ICs) will struggle.

2. **TSSOP-24 at 0.65mm pitch is too tight for via-in-pad with freerouting's constraints.** The ~0.25mm gap between pads won't fit a via. The autorouter hits a hard geometric limit, not just a search problem.

3. **Net shuffling + parallel runs is a legitimate technique for exploring routing solution space.** Different net ordering produces meaningfully different results. But it can't overcome fundamental geometric constraints.

4. **Freerouting 1.9.0 >> 2.1.0** for this board, by a factor of 25x in terms of unrouted nets (6 vs 152+).

5. **Quilter.ai solved in one shot what 128+ parallel freerouting runs couldn't.** The difference is copper zone support, not routing algorithm cleverness. The right abstraction (planes) matters more than brute-force search.

6. **The open-source PCB toolchain has real gaps.** pcb-rnd can't read KiCad 9.0. Freerouting can't do copper pours. There's no open-source equivalent to Quilter.ai. For a hobbyist project, this meant writing hundreds of lines of Python glue code and custom post-processing scripts.

7. **Headless Java GUI apps are annoying.** Freerouting initializes Swing even in batch mode. xvfb-run works but adds deployment complexity to what should be a command-line tool.

8. **The Python-generated PCB approach is powerful.** Being able to regenerate the entire board programmatically made it easy to try different layer configurations, adjust component positions, and iterate rapidly. The build script is the single source of truth.

## Scripts Written

| Script | Purpose | Used in final? |
|--------|---------|---------------|
| `build_giga_shield.py` | Generate pcb-rnd board from Python | Yes (for pcb-rnd workflow) |
| `build_kicad.py` | Generate KiCad board from Python | Yes (input to Quilter) |
| `shuffle_dsn.py` | Randomize net order in DSN files | No (Quilter won) |
| `add_gnd.py` | MST-based GND routing post-processor | No (geometric limit) |
| `add_pours.py` | Copper pour + stitching vias | No (pcb-rnd polygon limitation) |
| `add_power_nets.py` | Inject +3V3/+5V nets into netlist | Yes (for pcb-rnd workflow) |
| `route_d15.py` | A* pathfinder for one stuck net | No (single-net fix attempt) |
| `run_batch.sh` | 64 parallel freerouting (shared Xvfb) | Yes (on remote servers) |
| `run_batch_xvfb.sh` | 64 parallel freerouting (xvfb-run) | Yes (on remote servers) |
| `ses_to_pcb.py` | Import freerouting results to pcb-rnd | Yes (for pcb-rnd workflow) |
| `strip_traces.py` | Remove routes for re-routing | Yes (for iteration) |

## Timeline

All of this happened in a single working session. From "let's run freerouting" to "fabrication package ready for PCBWay" took one extended session, with most of the time spent discovering freerouting's GND limitation, trying workarounds, scaling up parallel runs, and finally getting the clean result from Quilter.ai.

## Final BOM (39 SMD + 4 mounting holes)

| Qty | Part | Package | Value | MPN |
|-----|------|---------|-------|-----|
| 29 | Ceramic cap | 0603 | 100nF | GRM188R71C104KA01D |
| 10 | Resistor | 0603 | 10K | RC0603FR-0710KL |
| 10 | Level shifter | TSSOP-24 | SN74LVC8T245PW | SN74LVC8T245PW |
| 4 | Mounting hole | 3.2mm | - | - |
