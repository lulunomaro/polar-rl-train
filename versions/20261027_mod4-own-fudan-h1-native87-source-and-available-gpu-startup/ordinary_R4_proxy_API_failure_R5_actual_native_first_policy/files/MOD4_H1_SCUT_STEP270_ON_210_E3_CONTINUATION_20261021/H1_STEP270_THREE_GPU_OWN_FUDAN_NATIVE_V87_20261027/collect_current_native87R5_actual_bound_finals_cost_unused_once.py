"""UNUSED actual GO-bound R5 close; original local+remote900 gates retained."""
from pathlib import Path
import sys,runpy
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021')
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native87R5_closing_typed_source'
if __name__=='__main__':
 sys.argv=[str(D/'collect_H1_native87R5_finals_actual_cost_unused_once.py'),'--stage',str(N),'--detached-report',str(N/'reports/AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json'),'--go-report',str(N/'reports/AVAILABLE_TWO_NATIVE87R5_FIRST_OWNER_SIGNED_GO_METADATA_RETURNED_ACTUAL.json')]
 runpy.run_path(sys.argv[0],run_name='__main__')
