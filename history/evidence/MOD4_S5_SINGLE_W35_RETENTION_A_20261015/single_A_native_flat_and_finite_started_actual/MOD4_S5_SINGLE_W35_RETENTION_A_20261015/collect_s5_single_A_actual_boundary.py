"""Read only this new originalV8 single-policy scope; no dispatch."""
from pathlib import Path
import importlib.util,sys
D=Path(__file__).resolve().parent;W=D.parent
import transport_s5_single_retention_A_actual as t
sys.modules['transport_249_own_phase_final_retention']=t
p=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015/collect_bodyframe_retention_actual_boundary.py'
s=importlib.util.spec_from_file_location('S5_single_retention_A_readonly_scope',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.D=D;m.W=W;m.R=D/'reports';m.t.ROOT='D:/MOD4_async_eval/'+D.name
if __name__=='__main__':m.main()
