#!/usr/bin/env python3
"""Find a multi-layer route for D15 (J6-3 to U5-4 net trace)."""
import re
import heapq

with open('giga_shield.pcb', 'r') as f:
    pcb = f.read()

layer_starts = [(m.start(), m.group(1), m.group(2)) 
                for m in re.finditer(r'Layer\((\d+)\s+"([^"]+)"\)', pcb)]
layers = {}
for i, (start, num, name) in enumerate(layer_starts):
    end = layer_starts[i+1][0] if i+1 < len(layer_starts) else len(pcb)
    layers[name] = pcb[start:end]

GRID = 200000  # 0.2mm
TRACE_W = 254000
MIN_CLR = 200000
VIA_COST = 20  # penalty for layer transition

# Separate blocked sets per layer
blocked = {0: set(), 1: set()}  # 0=top, 1=bottom

def pt_seg(px,py,x1,y1,x2,y2):
    dx,dy=x2-x1,y2-y1
    if dx==0 and dy==0: return ((px-x1)**2+(py-y1)**2)**0.5
    t=max(0,min(1,((px-x1)*dx+(py-y1)*dy)/(dx*dx+dy*dy)))
    return ((px-x1-t*dx)**2+(py-y1-t*dy)**2)**0.5

def block_seg(x1,y1,x2,y2,w,layer):
    hw=w//2+MIN_CLR+TRACE_W//2
    dx,dy=x2-x1,y2-y1
    ln=max(abs(dx),abs(dy),1)
    steps=max(ln//(GRID//2),1)
    for s in range(steps+1):
        t=s/steps;cx,cy=x1+dx*t,y1+dy*t
        rc=int(hw/GRID)+2
        gcx,gcy=int(round(cx/GRID)),int(round(cy/GRID))
        for gx in range(gcx-rc,gcx+rc+1):
            for gy in range(gcy-rc,gcy+rc+1):
                if pt_seg(gx*GRID,gy*GRID,x1,y1,x2,y2)<hw:
                    blocked[layer].add((gx,gy))

def block_circ_both(cx,cy,r):
    rt=r+MIN_CLR+TRACE_W//2
    rc=int(rt/GRID)+2
    gcx,gcy=int(round(cx/GRID)),int(round(cy/GRID))
    for gx in range(gcx-rc,gcx+rc+1):
        for gy in range(gcy-rc,gcy+rc+1):
            if ((gx*GRID-cx)**2+(gy*GRID-cy)**2)**0.5<rt:
                blocked[0].add((gx,gy))
                blocked[1].add((gx,gy))

print("Building dual-layer obstacle map...")

# Top layer traces -> block layer 0
for m in re.finditer(r'Line\[(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm', layers['top']):
    x1,y1,x2,y2,w,clr=[int(m.group(j)) for j in range(1,7)]
    block_seg(x1,y1,x2,y2,w,0)

# Bottom layer traces -> block layer 1
for m in re.finditer(r'Line\[(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm', layers['bottom']):
    x1,y1,x2,y2,w,clr=[int(m.group(j)) for j in range(1,7)]
    block_seg(x1,y1,x2,y2,w,1)

# Vias block both layers
for m in re.finditer(r'Via\[(\d+)nm\s+(\d+)nm\s+(\d+)nm\s+(\d+)nm', pcb):
    vx,vy,dia,clr=int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
    block_circ_both(vx,vy,dia//2)

# Through-hole pins block both layers (except J6-3)
j6x, j6y = 93710000, 71010000
for m in re.finditer(r'Element\["[^"]*"\s+"[^"]*"\s+"([^"]+)"[^"]*"\s+(\d+)nm\s+(\d+)nm', pcb):
    ref=m.group(1);ex=int(m.group(2));ey=int(m.group(3))
    es=m.start();ee=pcb.find('\n)',es)+2;eb=pcb[es:ee]
    for pm in re.finditer(r'Pin\[(-?\d+)nm\s+(-?\d+)nm\s+(\d+)nm',eb):
        px,py,pd=int(pm.group(1)),int(pm.group(2)),int(pm.group(3))
        ax,ay=ex+px,ey+py
        if ref=='J6' and abs(ax-j6x)<100000 and abs(ay-j6y)<100000: continue
        block_circ_both(ax,ay,pd//2)

# Unblock J6-3 area on both layers (larger radius - include clearance zone)
for layer in [0, 1]:
    for gx in range(int(round(j6x/GRID))-8, int(round(j6x/GRID))+9):
        for gy in range(int(round(j6y/GRID))-8, int(round(j6y/GRID))+9):
            if ((gx*GRID-j6x)**2+(gy*GRID-j6y)**2)**0.5 < 1200000:  # 1.2mm
                blocked[layer].discard((gx,gy))

# Unblock D15 net trace area (target, on top layer)
ty_g = int(round(13575000/GRID))
for tx in range(int(80000000/GRID), int(95000000/GRID)+1):
    for ty in range(ty_g-5, ty_g+6):
        blocked[0].discard((tx,ty))  # top layer only

print(f"Blocked: top={len(blocked[0])}, bottom={len(blocked[1])}")

# A* with layer dimension: state = (x, y, layer)
sx = int(round(j6x/GRID))
sy = int(round(j6y/GRID))

targets = set()
for tx in range(int(82070000/GRID), int(93000000/GRID)+1):
    targets.add((tx, ty_g, 0))  # target is on top layer (layer 0)
min_tx = min(t[0] for t in targets)
max_tx = max(t[0] for t in targets)

def h(x,y):
    cx = max(min_tx, min(max_tx, x))
    return abs(cx-x) + abs(ty_g-y)

DIRS = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
COSTS = [1,1,1,1,1.414,1.414,1.414,1.414]

# Start on both layers (J6-3 is through-hole)
open_set = []
for start_layer in [0, 1]:
    if (sx, sy) not in blocked[start_layer]:
        heapq.heappush(open_set, (h(sx,sy), 0, sx, sy, start_layer))
came_from = {}
g_score = {}
for sl in [0,1]:
    g_score[(sx,sy,sl)] = 0
visited = set()
found = False; end_pos = None; iters = 0

print(f"A* dual-layer from ({sx*GRID/1e6:.1f},{sy*GRID/1e6:.1f})...")

while open_set:
    f,g,x,y,layer = heapq.heappop(open_set)
    state = (x,y,layer)
    if state in visited: continue
    visited.add(state)
    iters += 1
    if iters % 200000 == 0:
        best_y = min(vy for vx,vy,vl in visited)
        print(f"  {iters} iters, best_y={best_y*GRID/1e6:.1f}mm, layer={layer}")
    if state in targets:
        found = True; end_pos = state
        print(f"Found after {iters} iters!")
        break
    
    # Move on same layer
    for (dx,dy), cost in zip(DIRS, COSTS):
        nx,ny = x+dx, y+dy
        if (nx,ny) in blocked[layer]: continue
        if nx<0 or ny<0 or nx>775 or ny>450: continue
        ns = (nx,ny,layer)
        if ns in visited: continue
        ng = g + cost
        if ns not in g_score or ng < g_score[ns]:
            g_score[ns] = ng
            heapq.heappush(open_set, (ng+h(nx,ny), ng, nx, ny, layer))
            came_from[ns] = state
    
    # Layer transition (via)
    other = 1 - layer
    if (x,y) not in blocked[other]:
        ns = (x,y,other)
        if ns not in visited:
            ng = g + VIA_COST
            if ns not in g_score or ng < g_score[ns]:
                g_score[ns] = ng
                heapq.heappush(open_set, (ng+h(x,y), ng, x, y, other))
                came_from[ns] = state
    
    if iters > 5000000: break

if found:
    path = []
    pos = end_pos
    while pos != (sx,sy,0) and pos != (sx,sy,1):
        path.append(pos)
        pos = came_from[pos]
    path.append(pos)
    path.reverse()
    
    print(f"Path: {len(path)} steps")
    
    # Extract via positions and trace segments per layer
    vias = []
    segments = {0: [], 1: []}  # layer -> list of (x1,y1,x2,y2)
    
    for i in range(len(path)-1):
        x1,y1,l1 = path[i]
        x2,y2,l2 = path[i+1]
        if l1 != l2:
            vias.append((x1*GRID, y1*GRID))
        else:
            segments[l1].append((x1*GRID,y1*GRID,x2*GRID,y2*GRID))
    
    # Simplify segments per layer
    for layer in [0,1]:
        segs = segments[layer]
        if not segs: continue
        # Merge collinear segments
        merged = [segs[0]]
        for s in segs[1:]:
            px1,py1,px2,py2 = merged[-1]
            sx1,sy1,sx2,sy2 = s
            dx1,dy1 = px2-px1, py2-py1
            dx2,dy2 = sx2-sx1, sy2-sy1
            # Same direction and connected
            if px2==sx1 and py2==sy1 and dx1*(dy2 or 1)==(dx2 or 1)*dy1 if (dx2 and dy1) else (dx1==0 and dx2==0) or (dy1==0 and dy2==0):
                merged[-1] = (px1,py1,sx2,sy2)
            else:
                merged.append(s)
        segments[layer] = merged
    
    # Output
    layer_names = {0: 'top', 1: 'bottom'}
    with open('d15_route.txt', 'w') as f:
        for vx,vy in vias:
            f.write(f'Via[{vx}nm {vy}nm 508000nm 127000nm 558000nm 254000nm "" ""]\n')
        for layer in [0,1]:
            for x1,y1,x2,y2 in segments[layer]:
                f.write(f'LAYER:{layer_names[layer]}\tLine[{x1}nm {y1}nm {x2}nm {y2}nm 254000nm 200000nm "clearline"]\n')
    
    print(f"\n{len(vias)} vias, {len(segments[0])} top traces, {len(segments[1])} bottom traces")
    # Print summary
    for i, (x,y,l) in enumerate(path):
        if i == 0 or i == len(path)-1 or (i > 0 and path[i-1][2] != l):
            print(f"  {'START' if i==0 else 'VIA' if path[i-1][2]!=l else 'END'}: ({x*GRID/1e6:.1f},{y*GRID/1e6:.1f}) layer={layer_names[l]}")
    print(f"  END: ({end_pos[0]*GRID/1e6:.1f},{end_pos[1]*GRID/1e6:.1f}) layer={layer_names[end_pos[2]]}")
else:
    print("No path found!")
    for layer in [0,1]:
        cells = [(x,y) for x,y,l in visited if l==layer]
        if cells:
            best = min(cells, key=lambda p: abs(p[1]-ty_g))
            print(f"  Layer {layer}: closest=({best[0]*GRID/1e6:.1f},{best[1]*GRID/1e6:.1f}), {len(cells)} cells")
