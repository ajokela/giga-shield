"""Export placed PCB to Specctra DSN for Freerouting."""
import sys
import pcbnew

pcb_in = sys.argv[1]
dsn_out = sys.argv[2]

board = pcbnew.LoadBoard(pcb_in)
pcbnew.ExportSpecctraDSN(board, dsn_out)
print(f"wrote {dsn_out}")
