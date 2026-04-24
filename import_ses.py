"""Import Specctra SES (routed traces) into a KiCad PCB and save."""
import sys
import pcbnew

pcb_in = sys.argv[1]
ses_in = sys.argv[2]
pcb_out = sys.argv[3]

board = pcbnew.LoadBoard(pcb_in)
ok = pcbnew.ImportSpecctraSES(board, ses_in)
print(f"ImportSpecctraSES returned: {ok}")
pcbnew.SaveBoard(pcb_out, board)
print(f"wrote {pcb_out}")
