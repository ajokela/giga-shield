#!/usr/bin/env python3
"""Add +3V3 and +5V nets to the routed giga-shield PCB netlist.

Freerouting will route only these new nets, preserving existing signal traces.
"""
import re

with open('giga_shield.pcb', 'r') as f:
    pcb = f.read()

# +3V3 net connections:
# - Each IC's VCCA pins (22, 23)
# - Each IC's VCCA decoupling cap pin 1 (odd caps: C1,C3,C5,...,C19)
# - Connector pins: J5-4, J2-2, J2-3, J7-5
# - Extra caps (even index): C21,C23,C25,C27,C29 pin 1
v33_connections = []

# IC VCCA pins
for i in range(1, 11):
    v33_connections.append(f'U{i}-22')
    v33_connections.append(f'U{i}-23')

# VCCA decoupling caps (pin 1): C1,C3,C5,C7,C9,C11,C13,C15,C17,C19
for i in range(10):
    cap_num = i * 2 + 1  # 1,3,5,...,19
    v33_connections.append(f'C{cap_num}-1')

# Connector +3V3 pins
v33_connections.extend(['J5-4', 'J7-5'])

# Extra power caps that are +3V3 (alternating, even index i=0,2,4,6,8 -> C21,C23,C25,C27,C29)
for i in range(0, 9, 2):
    cap_num = 21 + i
    v33_connections.append(f'C{cap_num}-1')

# +5V net connections:
# - Each IC's VCCB pins (17, 24)
# - Each IC's VCCB decoupling cap pin 1 (even caps: C2,C4,C6,...,C20)
# - Connector pins: J5-5, J7-7, J9-1, J9-2, J10-1, J10-2
# - Extra caps (odd index): C22,C24,C26,C28 pin 1
v5_connections = []

# IC VCCB pins
for i in range(1, 11):
    v5_connections.append(f'U{i}-17')
    v5_connections.append(f'U{i}-24')

# VCCB decoupling caps (pin 1): C2,C4,C6,C8,C10,C12,C14,C16,C18,C20
for i in range(10):
    cap_num = i * 2 + 2  # 2,4,6,...,20
    v5_connections.append(f'C{cap_num}-1')

# Connector +5V pins
v5_connections.extend(['J5-5', 'J7-7', 'J9-1', 'J9-2', 'J10-1', 'J10-2'])

# Extra power caps that are +5V (alternating, odd index i=1,3,5,7 -> C22,C24,C26,C28)
for i in range(1, 9, 2):
    cap_num = 21 + i
    v5_connections.append(f'C{cap_num}-1')

# Build the net entries
v33_net = '\tNet("+3V3" "(unknown)")\n\t(\n'
for conn in v33_connections:
    v33_net += f'\t\tConnect("{conn}")\n'
v33_net += '\t)'

v5_net = '\tNet("+5V" "(unknown)")\n\t(\n'
for conn in v5_connections:
    v5_net += f'\t\tConnect("{conn}")\n'
v5_net += '\t)'

# Insert into netlist (before the closing parenthesis of NetList)
# Find the last ")" of the NetList block
netlist_end = pcb.rfind('\n)\n')
if netlist_end == -1:
    print("ERROR: Could not find NetList end")
    exit(1)

pcb_new = pcb[:netlist_end] + '\n' + v33_net + '\n' + v5_net + '\n' + pcb[netlist_end:]

with open('giga_shield.pcb', 'w') as f:
    f.write(pcb_new)

print(f"+3V3 net: {len(v33_connections)} connections")
print(f"+5V net: {len(v5_connections)} connections")
print("Power nets added to netlist. Now export DSN and run freerouting.")
