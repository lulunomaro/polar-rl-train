"""Publish new explicit-PD off/on immutable SDKs using reviewed D6 source; once."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'D7_EXPLICIT_PD_SDK_PUBLISHED.json';assert not receipt.exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  raw=(D/'explicit_pd_actual_sdk_proof.py').read_bytes();compile(raw.decode(),'proof','exec');path=root+'/explicit_pd_actual_sdk_proof.py'
  try:f.stat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('Proof already staged')
  with f.open(path,'wb') as o:o.write(raw)
  assert f.open(path).read()==raw
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D7_EXPLICIT_PD_SDK_PUBLISHED.json').exists()
cpu=read(R/'EXPLICIT_PD_ADAPTER_TARGET_CPU_PASSED.json');assert len(cpu['passed'])==15 and not cpu['CUDA_initialized']
base=E/'artifacts/d6-clock2500-solver32-gas265-closedloop-frozen.zip';assert sha(base)=='0f51e024c9f5c2cc7448b814203e2f21c810618fb246138c7cdcab92a5dbb3c7'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';t=payload[key].decode()
def once(old,new):
 global t
 assert t.count(old)==1,old;t=t.replace(old,new)
once('from gas_damping_training_env import GasDampingMod4Env as ActionDelayMod4Env','from explicit_pd_training_env import ExplicitPDMod4Env as ActionDelayMod4Env')
once('                self._reset_idx(ids)','                self._d7proof.before_selected_reset(ids)\n                self._reset_idx(ids)\n                self._d7proof.after_selected_reset(ids)')
once('            self._platform_sensor_sdk.append(self.sensor_sdk_audit())','            self._platform_sensor_sdk.append(self.sensor_sdk_audit())\n            self._d7proof.after_control()')
once('    for step in range(args.steps):','    from explicit_pd_actual_sdk_proof import ActualExplicitPDProof\n    env._d7proof=ActualExplicitPDProof(env)\n    for step in range(args.steps):')
once("    result['D6_closed_loop_gas_damping_engineering_pressure']=True","    result['D6_closed_loop_gas_damping_engineering_pressure']=True\n    result['D7_actual_explicit_PD_SDK']=env._d7proof.finish()")
compile(t,key,'exec');payload[key]=t.encode()
for name in ('explicit_pd_component.py','explicit_pd_sdk_adapter.py','explicit_pd_training_env.py','explicit_pd_actual_sdk_proof.py','chassis_pd_nominal_readback.py'):
 raw=(D/name).read_bytes();compile(raw.decode('utf8'),name,'exec');payload['runtime/isaac/mod4/'+name]=raw
prior=read(E/'eval_queue/clk2500-closure-episode-d3-90-d7-chassis-pd-frame-sdk.json');checkpoint=prior['artifacts']['checkpoint'];assert sha(Path(checkpoint['path']))==checkpoint['sha256']=='df0654a6eaf7c62933b869043a340333391f60b44fae184ef0bb458c1f1fc4e5'
jobs=[]
for label,profile in (('off','off'),('on','explicit_motor_PD_independent_095_105_v1')):
 this=dict(payload);env=json.loads(this['runtime/isaac/mod4/env.json']);env['RM_EXPLICIT_PD_PROFILE']=profile;this['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
 manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in this.items()},base_D6_archive_SHA=sha(base),D7_explicit_PD_SDK_only=True,D7_profile=profile,no_COM_group_installed=True)
 dest=E/'artifacts'/('d7-explicit-pd-actual-sdk-'+label+'-frozen.zip');assert not dest.exists()
 with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in this.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
 os.replace(str(dest)+'.partial',dest)
 job='clk2500-closure-episode-d3-92-d7-pd-sdk-'+label
 row=dict(prior,job_id=job,published_epoch=time.time(),role='Actual explicit motor PD '+label+' SDK only, zero implicit drives and private CUDA reset/disk contract',explicit_PD_profile=profile,artifacts=dict(runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size),checkpoint=checkpoint))
 target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target);jobs.append(row)
v=dict(epoch=time.time(),jobs=jobs,production_GPU_PPO_canonical_changes=0,SDK_pending=True,D7_learning_deployed=False)
(R/'D7_EXPLICIT_PD_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);receipt.write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(jobs=[dict(id=j['job_id'],package=j['artifacts']['runtime']) for j in v['jobs']],no_training_or_budget_change=True)))
finally:c.close()
