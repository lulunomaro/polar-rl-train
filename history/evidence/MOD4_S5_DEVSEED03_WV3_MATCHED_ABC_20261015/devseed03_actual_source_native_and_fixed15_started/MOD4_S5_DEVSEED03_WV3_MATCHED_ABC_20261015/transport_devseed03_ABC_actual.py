"""Root-only existing transport, with a new explicit unused scope."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as base
ROOT='D:/MOD4_async_eval/MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015'
PY=base.PY;connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():
    base.ROOT=ROOT
    return base.guard_code()
