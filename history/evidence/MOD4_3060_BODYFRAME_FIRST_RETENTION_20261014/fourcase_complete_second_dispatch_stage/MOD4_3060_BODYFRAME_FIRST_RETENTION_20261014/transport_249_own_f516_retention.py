from pathlib import Path
import sys
W=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as base
PY=base.PY;ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_FIRST_RETENTION_20261014'
connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():
 base.ROOT=ROOT
 return base.guard_code()
