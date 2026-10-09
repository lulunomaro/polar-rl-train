"""Explicit full collection timing, excluding diagnostic post-step scoring.

Candidate adapter and task remain byte-identical to the SDK-reviewed packages.
"""
from pathlib import Path
import json,zipfile,hashlib,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'COLLECTION_PACKAGES.json').exists()
sha=lambda b:hashlib.sha256(b).hexdigest();packages={}
for variant in ('baseline','optimized'):
 base=D/('d7-reset-performance-'+variant+'-frozen.zip')
 with zipfile.ZipFile(base) as z:
  m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
 assert all(sha(b)==m['files'][n] for n,b in payload.items())
 k='runtime/isaac/mod4/frozen_history_flat.py';s=payload[k].decode()
 old='    for step in range(args.steps):\n        reset_performance_proof.before_control(step)'
 assert s.count(old)==1
 s=s.replace(old,'    for step in range(args.steps):\n        torch.cuda.synchronize();performance_start=time.perf_counter()\n        reset_performance_proof.before_control(step)')
 old='            torch.cuda.synchronize();performance_start=time.perf_counter()\n            _,_,done,_=vec.step(action)';assert s.count(old)==1
 s=s.replace(old,'            _,_,done,_=vec.step(action)');compile(s,k,'exec');payload[k]=s.encode()
 k='runtime/isaac/mod4/reset_performance_proof.py';s=payload[k].decode()
 old='            self.env._mild_dr.audit()';assert s.count(old)==1
 s=s.replace(old,'            # Full parameter audits remain at initial/final boundaries and every COM reset.')
 s=s.replace("return dict(variant=self.variant,actual_num_envs=self.env.num_envs,actual_steps=len(self.step_seconds),", "return dict(variant=self.variant,actual_num_envs=self.env.num_envs,actual_steps=len(self.step_seconds),\n            timed_region='manual subset reset + command + frozen policy + action trace CPU copy + env.step; GPU synchronized endpoints',")
 compile(s,k,'exec');payload[k]=s.encode()
 manifest=dict(m,files={n:sha(b) for n,b in payload.items()},base_SDK_review_archive_SHA=sha(base.read_bytes()),
    collection_timer_includes_stress_reset_and_frozen_inference=True,task_reward_adapter_byte_exact_to_SDK=True)
 p=D/('d7-reset-collection-'+variant+'-frozen.zip');assert not p.exists()
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in payload.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
 packages[variant]=dict(filename=p.name,sha256=sha(p.read_bytes()),bytes=p.stat().st_size)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
try:
 with c.open_sftp() as f:
  for v,row in packages.items():
   dest=E+'/artifacts/'+row['filename']
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Collection immutable artifact already staged')
   f.put(str(D/row['filename']),dest+'.partial');assert sha(f.open(dest+'.partial').read())==row['sha256'];f.rename(dest+'.partial',dest);row['path']=dest
  receipt=dict(epoch=time.time(),packages=packages,no_GPU_job_yet=True,production_mutations=0)
  (R/'COLLECTION_PACKAGES.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
  print(json.dumps(receipt))
finally:c.close()
