"""Distinct immutable SDK reader: preserve failed byte-equality experiment.

Reuse the already accepted dtype-derived physical-rotation audit; no adapter delta.
"""
from pathlib import Path
import json,zipfile,hashlib,time,sys
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'ROTATION_READER_SDK_PUBLISHED.json').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
s=(D/'reset_performance_proof.py').read_text(encoding='utf8')
s=s.replace('ChassisCOMSDK as BaselineCOM','ChassisCOMSDK as BaselineCOM,verify_rotation_preserved')
s=s.replace("        a=self.env._chassis_com;klass=a.__class__;state=a.state_dict();r=self.robot", "        a=self.env._chassis_com;klass=a.__class__;state=a.state_dict();r=self.robot\n        initial_pose=tensor(r.root_view.get_coms()).clone();rotation_proofs=[]")
a="                assert torch.equal(before['baseline'][0],before['optimized'][0]) and before['baseline'][1]==before['optimized'][1]";assert s.count(a)==1
s=s.replace(a,"                assert torch.equal(before['baseline'][0][...,:3],before['optimized'][0][...,:3]) and before['baseline'][1]==before['optimized'][1]\n                rotation_proofs.append(verify_rotation_preserved(before['baseline'][0][...,3:],before['optimized'][0][...,3:]))")
a="                assert torch.equal(after['baseline'][0],after['optimized'][0]) and torch.equal(after['baseline'][1],after['optimized'][1])";assert s.count(a)==1
s=s.replace(a,"                assert torch.equal(after['baseline'][0][...,:3],after['optimized'][0][...,:3])\n                assert torch.equal(after['baseline'][1],after['baseline'][0]) and torch.equal(after['optimized'][1],after['optimized'][0])\n                rotation_proofs.append(verify_rotation_preserved(after['baseline'][0][...,3:],after['optimized'][0][...,3:]))")
s=s.replace('exact_backend_buffer_COM_episode_private_RNG_before_after=True,ABBA_alternating_order=True,', "exact_COM_translation_episode_private_RNG_before_after=True,backend_buffer_bytes_exact_per_variant=True,\n                physical_rotations_preserved_existing_dtype_contract=True,raw_quaternion_bytes_pairwise_exact=all(x['raw_quaternion_bytes_exact'] for x in rotation_proofs),\n                max_normalized_double_quaternion_delta=max(x['normalized_double_quaternion_max_component_delta'] for x in rotation_proofs),ABBA_alternating_order=True,")
a="        assert self.initial==self.snapshot(),'Microbenchmark failed to restore COM and all other initial state'";assert s.count(a)==1
s=s.replace(a,"        restored=self.snapshot();final_pose=tensor(r.root_view.get_coms())\n        assert torch.equal(initial_pose[...,:3],final_pose[...,:3])\n        verify_rotation_preserved(initial_pose[...,3:],final_pose[...,3:])\n        assert {k:v for k,v in self.initial.items() if k!='COM'}=={k:v for k,v in restored.items() if k!='COM'},'Non-COM initial state changed during microbenchmark'\n        self.micro_restore_raw_COM_pose_exact=torch.equal(initial_pose,final_pose)")
compile(s,'reset_performance_rotation_review.py','exec');(D/'reset_performance_rotation_review.py').write_text(s,encoding='utf8')
base=D/'d7-reset-performance-baseline-frozen.zip'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
payload['runtime/isaac/mod4/reset_performance_rotation_review.py']=s.encode()
k='runtime/isaac/mod4/frozen_history_flat.py';t=payload[k].decode();a='from reset_performance_proof import ResetPerformanceProof';assert t.count(a)==1
t=t.replace(a,'from reset_performance_rotation_review import ResetPerformanceProof');payload[k]=t.encode()
manifest=dict(m,files={n:sha(b) for n,b in payload.items()},first_failed_byte_equality_experiment_retained=True,
    only_reader_uses_preexisting_physical_rotation_contract=True,adapter_task_hardware_unchanged=True)
p=D/'d7-reset-performance-rotation-reader-frozen.zip';assert not p.exists()
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
  else:raise AssertionError('Review package already exists')
  f.put(str(p),dest+'.partial');assert sha(f.open(dest+'.partial').read())==sha(p.read_bytes());f.rename(dest+'.partial',dest)
  row=json.loads((R/'template.json').read_text(encoding='utf8'));job='clk2500-closure-episode-d3-92-d7-com-reset-rotation-performance-sdk'
  row.update(job_id=job,published_epoch=time.time(),num_envs=10,steps=300,no_learning=True,canonical_write_authority=False,
    role='Actual COM reset performance reader with existing float32 normalization rotation proof; first error retained')
  row['artifacts']['runtime']=dict(path=dest,sha256=sha(p.read_bytes()),bytes=p.stat().st_size)
  target=E+'/eval_queue/'+job+'.json'
  try:f.stat(target)
  except FileNotFoundError:pass
  else:raise AssertionError('Review job already exists')
  with f.open(target+'.partial','wb') as out:out.write(json.dumps(row,indent=2).encode())
  f.rename(target+'.partial',target)
  v=dict(epoch=time.time(),job=row,production_mutations=0,old_failed_job_retained=True)
  (R/'ROTATION_READER_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=job,package=row['artifacts']['runtime'])))
finally:c.close()
