"""Actual getter is CPU, SDK cache is CUDA; align independent reader tensors.

Earlier reader failures remain immutable. Candidate adapter does not change.
"""
from pathlib import Path
import json,zipfile,hashlib,time,sys
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'DEVICE_ALIGNED_SDK_PUBLISHED.json').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
s=(D/'reset_performance_rotation_review.py').read_text(encoding='utf8')
s=s.replace('tensor(r.root_view.get_coms()).clone()','tensor(r.root_view.get_coms()).clone().cpu()')
s=s.replace('tensor(r.data.body_com_pose_b).clone()','tensor(r.data.body_com_pose_b).clone().cpu()')
s=s.replace('final_pose=tensor(r.root_view.get_coms())','final_pose=tensor(r.root_view.get_coms()).cpu()')
s=s.replace('initial_pose=tensor(r.root_view.get_coms()).clone().cpu();rotation_proofs=[]', 'initial_pose=tensor(r.root_view.get_coms()).clone().cpu();initial_inertia=tensor(r.root_view.get_inertias()).clone().cpu();rotation_proofs=[]')
a="        assert {k:v for k,v in self.initial.items() if k!='COM'}=={k:v for k,v in restored.items() if k!='COM'},'Non-COM initial state changed during microbenchmark'";assert s.count(a)==1
s=s.replace(a,"        assert {k:v for k,v in self.initial.items() if k not in ('COM','inertia')}=={k:v for k,v in restored.items() if k not in ('COM','inertia')},'Non-COM initial state changed during microbenchmark'\n        final_inertia=tensor(r.root_view.get_inertias()).cpu()\n        self.restore_inertia_delta=float((initial_inertia-final_inertia).abs().max())\n        assert self.restore_inertia_delta<=1e-6,'Inertia exceeds original frozen mild_dr numeric contract'\n        self.env._mild_dr.audit()\n        self.restore_inertia_raw_bytes_exact=torch.equal(initial_inertia,final_inertia)")
s=s.replace('microbench=self.micro,initial=self.initial,final=self.snapshot(),action_trace_sha256=self.actions.hexdigest(),',"microbench=self.micro,initial=self.initial,final=self.snapshot(),action_trace_sha256=self.actions.hexdigest(),\n            restore_inertia_raw_bytes_exact=getattr(self,'restore_inertia_raw_bytes_exact',None),restore_inertia_delta=getattr(self,'restore_inertia_delta',None),\n            original_full_parameter_audit_preserved=True,actual_backend_device=str(tensor(self.robot.root_view.get_coms()).device),actual_cache_device=str(tensor(self.robot.data.body_com_pose_b).device),")
compile(s,'reset_performance_device_review.py','exec');(D/'reset_performance_device_review.py').write_text(s,encoding='utf8')
base=D/'d7-reset-performance-rotation-reader-frozen.zip'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
payload['runtime/isaac/mod4/reset_performance_device_review.py']=s.encode()
k='runtime/isaac/mod4/frozen_history_flat.py';t=payload[k].decode();a='from reset_performance_rotation_review import ResetPerformanceProof';assert t.count(a)==1
payload[k]=t.replace(a,'from reset_performance_device_review import ResetPerformanceProof').encode()
manifest=dict(m,files={n:sha(b) for n,b in payload.items()},reader_CPU_getter_CUDA_cache_alignment=True,original_mild_numeric_inertia_contract_preserved=True)
p=D/'d7-reset-performance-device-reader-frozen.zip';assert not p.exists()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
try:
 with c.open_sftp() as f:
  dest=E+'/artifacts/'+p.name
  try:f.stat(dest)
  except FileNotFoundError:pass
  else:raise AssertionError('Device-aligned package already staged')
  f.put(str(p),dest+'.partial');assert sha(f.open(dest+'.partial').read())==sha(p.read_bytes());f.rename(dest+'.partial',dest)
  row=json.loads((R/'template.json').read_text(encoding='utf8'));job='clk2500-closure-episode-d3-92-d7-com-reset-device-performance-sdk'
  row.update(job_id=job,published_epoch=time.time(),num_envs=10,steps=300,no_learning=True,canonical_write_authority=False,
    role='Actual CPU PhysX readback vs CUDA cache aligned performance SDK; old errors retained')
  row['artifacts']['runtime']=dict(path=dest,sha256=sha(p.read_bytes()),bytes=p.stat().st_size)
  target=E+'/eval_queue/'+job+'.json'
  try:f.stat(target)
  except FileNotFoundError:pass
  else:raise AssertionError('Device-aligned SDK already staged')
  with f.open(target+'.partial','wb') as out:out.write(json.dumps(row,indent=2).encode())
  f.rename(target+'.partial',target)
  v=dict(epoch=time.time(),job=row,production_mutations=0,previous_reader_errors_retained=True)
  (R/'DEVICE_ALIGNED_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=job,package=row['artifacts']['runtime'])))
finally:c.close()
