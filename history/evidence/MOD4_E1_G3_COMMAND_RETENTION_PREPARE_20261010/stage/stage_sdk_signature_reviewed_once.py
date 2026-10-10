"""Create one new isolated root and admit source/schema on CPU, no GPU dispatch."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
OLD='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_20261010';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_SDK_REVIEWED_20261010';E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def call(c,code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=180);b=o.read();err=e.read();status=o.channel.recv_exit_status();assert status==0,(b+err).decode(errors='replace');return json.loads(b)
def put(f,p,b):
 with f.open(p,'wbx') as q:q.write(b)
 assert f.open(p).read()==b
def main():
 assert not (R/'SDK_REPAIR_STAGE_STARTED.json').exists();save('SDK_REPAIR_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-RETENTION-STAGE-01',old=OLD,new=NEW,CPU_only=True,new_budget_seconds=0))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  row=call(c,r'''from pathlib import Path
import json,hashlib,shutil,time,fcntl
old=Path(OLD_VALUE);new=Path(NEW_VALUE);assert not new.exists(),str(new)
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=b.read_bytes();j=json.loads(before);assert j['active_segment'] is None and j['authorized_training_seconds']==828000
state=json.loads((old/'reports/E1_STATE.json').read_bytes());assert state['phase']=='E1_G3_native_interface_no_PPO' and json.loads((old/'reports/E1_ATTENTION.json').read_bytes())['active_segment'] is None
for lock in (b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
source=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(source['sha256'])==348
new.mkdir();(new/'reports').mkdir()
for n,h in source['sha256'].items():
 p=old/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
 q=new/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert b.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),source338_byteexact=True,canonical_bytes_unchanged=True,new_root=str(new))))
'''.replace('OLD_VALUE',repr(OLD)).replace('NEW_VALUE',repr(NEW)))
  save('SDK_REPAIR_OLD348_COPIED.json',row)
  build=json.loads((R/'SDK_SIGNATURE_REPAIR_PREPARED.json').read_bytes());files={n:(D/'signature_repair_payload'/n).read_bytes() for n in build['sha256']}
  assert all(H(b)==build['sha256'][n] for n,b in files.items())
  with c.open_sftp() as f:
   old=json.loads(f.open(OLD+'/reports/SOURCE_FREEZE.json').read());assert not set(files).intersection(old['sha256'])
   for n,b in files.items():put(f,NEW+'/'+n,b)
   freeze=dict(old,candidate_root=NEW,sha256=dict(old['sha256'],**build['sha256']),original338_byteexact=True,new_command_scope=True,new_command_file_count=len(files))
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('SDK_REPAIR_SOURCE_FREEZE.json',freeze)
   for n in ('SELECTED_E1_G3_SOURCE.json','G3_FROZEN_SCOPE_ADMITTED.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):
    put(f,NEW+'/reports/'+n,f.open(OLD+'/reports/'+n).read())
   put(f,NEW+'/reports/RETENTION_TARGET_CPU_ORIGINAL.json',f.open(OLD+'/reports/RETENTION_TARGET_CPU_PASSED.json').read())
   put(f,NEW+'/reports/COMMAND_SCOPE_BUILD.json',json.dumps(build,indent=2).encode())
   package=dict(path=E+'/artifacts/e1-g3-derived35mm-paired-approach040-frozen-v2.zip',bytes=36393703,sha256='858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b');raw=f.open(package['path']).read();assert len(raw)==package['bytes'] and H(raw)==package['sha256']
   put(f,NEW+'/reports/G3_BEHAVIOR_PACKAGE_READY.json',json.dumps(dict(runtime=package,already_complete128_source_reused_not_replayed=True,candidate_future_four_cases_required=True),indent=2).encode())
   for n in ('E1_G3_128_COMPLETE_RETENTION_DECISION.json','NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json'):
    put(f,NEW+'/reports/'+n,f.open(E+'/reports/'+n).read())
  admitted=call(c,r'''from pathlib import Path
import sys,json,subprocess,torch,time,ast
D=Path(NEW_VALUE);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
for p in D.glob('isaac/mod4/retention*.py'):ast.parse(p.read_text())
proof=json.loads((D/'reports/RETENTION_TARGET_CPU_ORIGINAL.json').read_bytes());assert proof['passed'] and proof['new_command_schema_rejection_tests']==14
tree=ast.parse((D/'isaac/mod4/retention_flat_runtime_sdk_reviewed.py').read_text());fn=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='inactive_retention_rolling_sdk'][0]
assert [x.arg for x in fn.args.args]==['env','speed_scale','yaw_min','support_weight'] and fn.args.kwarg is None and [ast.literal_eval(x) for x in fn.args.defaults]==[.15,3.5,.25]
ns={'inactive_retention_rolling':lambda env,**kw:(env,kw)};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<signature>','exec'),ns)
assert ns['inactive_retention_rolling_sdk']('fixture')==('fixture',dict(speed_scale=.15,yaw_min=3.5,support_weight=.25))
proof=dict(proof,prior_CPU14_exact_reuse=True,new_SDK_callable_parameter_contract_CPU_verified=True,no_actual_GPU_claim=True);assert torch.__version__.startswith('2.10') and not torch.cuda.is_initialized()
(D/'reports/RETENTION_TARGET_CPU_PASSED.json').write_text(json.dumps(proof,indent=2))
import supervise_e1_command_retention_sdk_reviewed_once as m
m.verify();m.wait_existing();source=m.source();full=m.fullsave(source);assert full['finite_tensors']==96 and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,CPU=proof,full_source=full,old338_boundary_verified=True,source_map_verified=len(m.read(D/'reports/SOURCE_FREEZE.json')['sha256']),no_CUDA_initialized=True,no_GPU_SDK_native_PPO_launched=True)))
'''.replace('NEW_VALUE',repr(NEW)),PY)
  save('SDK_REPAIR_TARGET_CPU_ADMITTED.json',admitted);print(json.dumps(admitted))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('SDK_REPAIR_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_new_root_retained=True,no_blind_retry=True,no_budget_extension=True));raise
