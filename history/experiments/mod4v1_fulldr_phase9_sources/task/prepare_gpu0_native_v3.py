"""Independent, model-free GPU0 probe while the other GPU's producer keeps its writer.
The v2 pair never started SDK: busy private lock. Preserve it; do not replay it.
"""
from pathlib import Path
import ast,json,runpy,sys
R=Path(__file__).resolve().parent
report=R/'reports/NATIVE_V2_BUSY_LOCK_AND_V3_SCOPE.json';assert not report.exists()
report.write_text(json.dumps({'v2':'Parent acquired no runnable pair; BlockingIOError at private GPU lock, no children/SDK/model reads; exit confirmed all own children waited and locks released','live_snapshot':'GPU0 free13MiB; GPU1 has PID1414879/4600MiB, not treated as idle','v3_scope':'Only GPU0, model-free8physics-step property probe, no canonical writer/charge/PPO/PT; preserve any existing production owner on other GPU','synchronization':'Original GPU0 private EX; shared finite-environment read lease, held through all own children; exclusive environment validators are excluded','not_production_admission':'No fullDR adaptation or training pass; any future production still requires original sole canonical owner and actual fullstate admission'},indent=2),encoding='utf-8')
src=(R/'native_probe_supervisor.py').read_text(encoding='utf-8')
src=src.replace('locks=[];children=[];errors=[]','locks=[];children=[];errors=[];shared=None')
src=src.replace("  assert budget['active_segment'] is None,'Original canonical is active; no native admission now'", "  put('PARALLEL_MODEL_FREE_SCOPE.json',{'canonical_writes':0,'other_owner_unchanged':True,'other_active_owner_pid':(budget['active_segment'] or {}).get('owner_parent_pid'),'native_property_probe_only':True})")
src=src.replace("  with (OWN/'state/finite_environment_validation.lock').open('rb+') as shared:\n   fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)","  shared=(OWN/'state/finite_environment_validation.lock').open('rb+');fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB)")
src=src.replace("  for fd in locks:fd.close()","  for fd in locks:fd.close()\n  if shared is not None:\n   if waited:fcntl.flock(shared,fcntl.LOCK_UN)\n   shared.close()")
p=R/'native_probe_supervisor_v3.py';assert not p.exists();ast.parse(src);p.write_text(src,encoding='utf-8')
src=(R/'deploy_native_pair_v2_once.py').read_text(encoding='utf-8')
src=src.replace("R/'native_probe_supervisor.py'","R/'native_probe_supervisor_v3.py'")
src=src.replace(",{'label':'gpu1','uuid':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}",'')
src=src.replace('MOD4V1_NATIVE0PT_PAIR_V2_','MOD4V1_NATIVE0PT_GPU0_V3_')
p=R/'deploy_gpu0_native_v3_once.py';assert not p.exists();ast.parse(src);p.write_text(src,encoding='utf-8');sys.path.insert(0,str(R));runpy.run_path(str(p),run_name='__main__')
