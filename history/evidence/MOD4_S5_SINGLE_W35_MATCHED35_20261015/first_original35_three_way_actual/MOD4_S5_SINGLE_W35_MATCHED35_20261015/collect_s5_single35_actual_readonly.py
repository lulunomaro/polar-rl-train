"""Collect this new scope once after its actual parent and worker have exited."""
from pathlib import Path
import importlib.util,sys
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as t
sys.modules['transport_249_own_phase_final_retention']=t
p=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015/collect_bodyframe_retention_actual_boundary.py'
s=importlib.util.spec_from_file_location('S5_actual_readonly_new_single_route',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.D=D;m.W=W;m.R=D/'reports';m.t.ROOT='D:/MOD4_async_eval/'+D.name
if __name__=='__main__':m.main()
