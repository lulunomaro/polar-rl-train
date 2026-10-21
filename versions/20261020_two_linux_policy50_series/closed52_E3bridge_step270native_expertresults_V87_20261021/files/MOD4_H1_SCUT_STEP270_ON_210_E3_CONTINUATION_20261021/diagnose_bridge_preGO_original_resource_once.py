from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
code=r'''
from pathlib import Path
import json,time,shutil,psutil,hashlib
root=Path('/mnt/mod4_linux_durable_20261013');C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);own=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if any(x.startswith('/mnt/mod4_linux_durable_20261013/T3sf17_1910v22/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
q=Path('/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2110v1/owner');print(json.dumps(dict(epoch=time.time(),D_is_mounted=root.is_mount(),disk_free_bytes=shutil.disk_usage(root).free,disk_required_bytes=25*1024**3,old_T3sf17_actual_own=own,canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],authorized=c['authorized_training_seconds'],extensions=len(c['budget_extensions']),canonical_SHA=hashlib.sha256(raw).hexdigest(),bridge_owner_root_exists=q.exists(),no_account_GPU_or_file_mutation=True)))
'''
try:
 c=d.t.connect()
 try:v=d.code(c,d.t.PY,code,{},timeout=45)
 finally:c.close()
 (B/'reports/RECOVERY_BRIDGE_PREGO_RESOURCE_DIAGNOSIS_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(v))
except BaseException:
 (B/'reports/RECOVERY_BRIDGE_RESOURCE_DIAGNOSIS_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc()),indent=2));raise
