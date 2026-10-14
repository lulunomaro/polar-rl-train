"""Collect the observed immutable own25, not a drifting future latest."""
from pathlib import Path
import sys,json,time,shlex,hashlib
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015'
EXPECTED='218a637d9a85984ebf3dfae2536275b85ddb6b4bbcbb493da17e2db6a4afbda1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import json,time,hashlib,psutil
r=Path('''+repr(ROOT)+''');a=r/'learning_logs';ck=a/'model_25.pt'
assert ck.stat().st_size==24031387 and hashlib.sha256(ck.read_bytes()).hexdigest()=='''+repr(EXPECTED)+'''
names=['model_25.pt','S4_LEARNING_STARTUP_ADMITTED_ACTUAL.json','SENSOR_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json']
rows=[]
for p in [*(a/name for name in names),r/'S4_FIRST_FORMAL_ACTUAL_MANIFEST.json',r/'S4_FIRST_FORMAL_SOURCE_FREEZE.json',r/'DISPATCH_ACTUAL.json',r/'PARENT_IDENTITY_ACTUAL.json']:
 raw=p.read_bytes();rows.append(dict(path=str(p),relative=str(p.relative_to(r)),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
index=json.loads((a/'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json').read_bytes())
assert len(index['rows'])>=26 and all(v['optimizer_update_complete'] for v in index['rows'][:26])
for row in index['rows'][:26]:assert Path(row['path']).stat().st_size==row['bytes']
prefix=dict(rows=index['rows'][:26],source_SHA=index['source_SHA']);raw=json.dumps(prefix,indent=2).encode()
owner=json.loads((r/'PARENT_IDENTITY_ACTUAL.json').read_bytes());p=psutil.Process(owner['pid']);assert p.create_time()==owner['created']
print(json.dumps(dict(epoch=time.time(),root=str(r),pinned_checkpoint_SHA='''+repr(EXPECTED)+''',files=rows,
 actual_parent=dict(pid=p.pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd()),
 rollout_prefix26=prefix,rollout_prefix26_serialized_SHA=hashlib.sha256(raw).hexdigest(),
 raw_original_rollouts_remote_retained_actual_paths_sizes_existing_creation_SHA_not_redownloaded=True,
 actual_live_health_snapshot=json.loads((a/'CLOCK_TRAINING_HEALTH.json').read_bytes()),
 own_original_error_exists=(a/'S4_FORMAL_ORIGINAL_ERROR.json').exists(),parent_original_error_exists=(r/'PARENT_ORIGINAL_ERROR.json').exists(),
 canonical_learning_cost_owned_by_original_parent_no_budget_mutation=True)))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_FIRST_GATE_POSITIVE_COLLECTION_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2));assert rc==0,str(p)
  v=json.loads(raw);assert not v['own_original_error_exists'] and not v['parent_original_error_exists']
  out=D/'own_gate_positive25_actual'/stamp;out.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
  for row in v['files']:
   p=out/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];row.update(local_path=str(p),twohost_SHA_exact=True)
  p=D/'reports'/('S4_FIRST_GATE_OWN_MODEL25_ALL_INPUTS_TWOHOST_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2));print(json.dumps(dict(report=str(p),files=len(v['files']),pinned_SHA=EXPECTED,actual_parent=v['actual_parent'],original_error=False)))
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
