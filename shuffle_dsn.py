#!/usr/bin/env python3
"""Generate N copies of a DSN file with shuffled net ordering.

Each copy will route nets in a different order, leading to
different initial solutions and (hopefully) different local optima.
"""
import sys, re, random, os

def shuffle_dsn(input_dsn, output_dir, n_copies):
    with open(input_dsn) as f:
        dsn = f.read()

    # Find the network section and extract individual net blocks
    # Nets look like: (net NETNAME\n      (pins ...)\n    )
    net_pattern = re.compile(r'(\(net\s+[^\n]+\n\s+\(pins[^)]+\)\n\s+\))', re.MULTILINE)
    nets = net_pattern.findall(dsn)

    if not nets:
        print("ERROR: No nets found in DSN")
        sys.exit(1)

    # Find the network section boundaries
    network_start = dsn.find('(network')
    network_end = dsn.find('\n  )', network_start)

    # Extract everything before first net and after last net in network section
    first_net_pos = dsn.find(nets[0], network_start)
    last_net_end = dsn.rfind(nets[-1], network_start) + len(nets[-1])

    pre_nets = dsn[:first_net_pos]
    post_nets = dsn[last_net_end:]

    # Also extract class section (between nets and end of network)
    class_section = dsn[last_net_end:network_end + 3] if network_end > last_net_end else post_nets

    os.makedirs(output_dir, exist_ok=True)

    for i in range(n_copies):
        shuffled = nets.copy()
        random.seed(i * 31337 + 42)  # deterministic but different per copy
        random.shuffle(shuffled)

        new_dsn = pre_nets + '\n    '.join(shuffled) + post_nets

        out_path = os.path.join(output_dir, f'run_{i:03d}.dsn')
        with open(out_path, 'w') as f:
            f.write(new_dsn)

    print(f"Generated {n_copies} shuffled DSN files in {output_dir}/")
    print(f"  {len(nets)} nets per file")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} input.dsn output_dir n_copies")
        sys.exit(1)

    shuffle_dsn(sys.argv[1], sys.argv[2], int(sys.argv[3]))
