"""New isolated immutable performance SDK; existing evaluator schedules its GPU."""
from pathlib import Path
import sys,json,zipfile,hashlib,os,time,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SDK_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
base=D/'d7-original-frozen.zip';sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(sha(b)==m['files'][n] for n,b in payload.items())
for name in ('selected_com_readback.py','reset_performance_proof.py'):
 b=(D/name).read_bytes();compile(b.decode('utf8'),name,'exec');payload['runtime/isaac/mod4/'+name]=b
k='runtime/isaac/mod4/frozen_history_flat.py';s=payload[k].decode()
a='    for step in range(args.steps):';assert s.count(a)==1
s=s.replace(a,"    from reset_performance_proof import ResetPerformanceProof\n    reset_performance_proof=ResetPerformanceProof(env)\n"+a+"\n        reset_performance_proof.before_control(step)")
a='            _,_,done,_=vec.step(action)';assert s.count(a)==1
s=s.replace(a,"            reset_performance_proof.after_action(action)\n            torch.cuda.synchronize();performance_start=time.perf_counter()\n"+a+"\n            torch.cuda.synchronize();reset_performance_proof.step_seconds.append(time.perf_counter()-performance_start)")
a="    result['D7_closed_loop_chassis_COM_explicit_PD_engineering_pressure']=True";assert s.count(a)==1
s=s.replace(a,a+"\n    result['D7_reset_performance_review']=reset_performance_proof.finish()")
compile(s,k,'exec');payload[k]=s.encode()
for variant in ('baseline','optimized'):
 this=dict(payload);cfg=json.loads(this['runtime/isaac/mod4/env.json']);cfg['RM_COM_PERFORMANCE_VARIANT']=variant
 this['runtime/isaac/mod4/env.json']=json.dumps(cfg,indent=2).encode()
 if variant=='optimized':
  k='runtime/isaac/mod4/chassis_pd_training_env.py';t=this[k].decode()
  a='from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK';assert t.count(a)==1
  t=t.replace(a,'from selected_com_readback import SelectedCOMSDK as ChassisCOMSDK');compile(t,k,'exec');this[k]=t.encode()
 manifest=dict(m,files={n:sha(b) for n,b in this.items()},performance_variant=variant,base_D7_archive_SHA=sha(base.read_bytes()),
               no_training_runtime_change=True,task_hardware_bounds_unchanged=True,no_new_learning=True,
               performance_stress_not_skill_graduation=True)
 p=D/('d7-reset-performance-'+variant+'-frozen.zip');assert not p.exists()
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in this.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';remote='/home/egde/rl_candidates/'+D.name
try:
 with c.open_sftp() as f:
  for root in (remote,remote+'/reports'):
   try:f.mkdir(root)
   except OSError:f.stat(root)
  for variant in ('baseline','optimized'):
   p=D/('d7-reset-performance-'+variant+'-frozen.zip');dest=E+'/artifacts/'+p.name
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Immutable performance package already exists')
   f.put(str(p),dest+'.partial');assert sha(f.open(dest+'.partial').read())==sha(p.read_bytes());f.rename(dest+'.partial',dest)
  row=json.loads((R/'template.json').read_text(encoding='utf8'));job='clk2500-closure-episode-d3-92-d7-com-reset-performance-sdk'
  p=D/'d7-reset-performance-baseline-frozen.zip'
  row.update(job_id=job,published_epoch=time.time(),num_envs=10,steps=300,
      role='Isolated actual COM ABBA reset optimization SDK, no new skill acceptance',no_learning=True,canonical_write_authority=False)
  row['artifacts']['runtime']=dict(path=E+'/artifacts/'+p.name,sha256=sha(p.read_bytes()),bytes=p.stat().st_size)
  dest=E+'/eval_queue/'+job+'.json'
  try:f.stat(dest)
  except FileNotFoundError:pass
  else:raise AssertionError('Performance SDK job already exists')
  raw=json.dumps(row,indent=2).encode()
  with f.open(dest+'.partial','wb') as out:out.write(raw)
  f.rename(dest+'.partial',dest)
  receipt=dict(epoch=time.time(),job=row,packages={v:dict(path=E+'/artifacts/d7-reset-performance-'+v+'-frozen.zip',sha256=sha((D/('d7-reset-performance-'+v+'-frozen.zip')).read_bytes())) for v in ('baseline','optimized')},
      existing_evaluator_unchanged=True,main_training_and_canonical_transactions=0)
  raw=json.dumps(receipt,indent=2).encode();(R/'SDK_PUBLISHED.json').write_bytes(raw)
  with f.open(remote+'/reports/SDK_PUBLISHED.json','wb') as out:out.write(raw)
  print(json.dumps(dict(job=job,packages=receipt['packages'],production_mutations=0)))
finally:c.close()
