"""Explicit new namespace on root's sequential bounded transport only."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as base
ROOT='D:/MOD4_async_eval/MOD4_S5_SINGLE_W35_RETENTION_A_20261015'
PY=base.PY;connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():base.ROOT=ROOT;return base.guard_code()
