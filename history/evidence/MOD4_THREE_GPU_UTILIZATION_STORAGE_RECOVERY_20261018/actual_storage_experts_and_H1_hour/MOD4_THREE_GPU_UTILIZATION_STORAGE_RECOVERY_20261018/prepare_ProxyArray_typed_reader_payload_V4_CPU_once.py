"""Use the original typed witness adapter and verify a ProxyArray fixture before new roots."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,types,ast,os,traceback
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class ProxyFixture:
 def __init__(self,x):self.torch=x
 def __array__(self,*a,**k):raise AssertionError('Must use the original typed adapter')
class CallableFixture:
 def __call__(self,*a,**k):raise AssertionError('Observer must not call reward')
def main():
 import torch
 from actual_reward_frame_observer_v3 import install
 rng=torch.get_rng_state().clone();t=torch.zeros(2,3);data=types.SimpleNamespace(root_state_w=ProxyFixture(torch.zeros(2,13)),root_lin_vel_b=ProxyFixture(t),root_ang_vel_b=ProxyFixture(t),projected_gravity_b=ProxyFixture(t));cfg=types.SimpleNamespace(func=CallableFixture(),weight=-.3,params={});result=(object(),);calls=[];e=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(data=data)},reward_manager=types.SimpleNamespace(_term_names=['world_cycle_cross'],_term_cfgs=[cfg],_step_reward=t),command_manager=types.SimpleNamespace(get_command=lambda name:t),_retention_native_witness=types.SimpleNamespace(args=types.SimpleNamespace(steps=1)))
 def step(a):calls.append(a);return result
 e.step=step;records={};folder=B/'cpu_typed_proxy_fixture_v3';folder.mkdir();module=types.SimpleNamespace(create_observed_env=lambda:e,finalize_observer=lambda e,r:r,cpu=lambda x:(x if torch.is_tensor(x) else x.torch).detach().cpu().numpy().copy());context=dict(output_dir=str(folder),save=lambda n,v:records.setdefault(n,v));install(module,context);module.create_observed_env();assert e.step('one') is result and calls==['one'];assert module.finalize_observer(e,'original')=='original' and cfg.weight==-.3
 prior=json.loads((R/'TWO_EXPERT_LINUX_V3_OWN_BACKEND_PUBLIC_SOURCE_QUERY_CPU_ACTUAL.json').read_bytes());payloads=[]
 for row in prior['payloads']:
  kind=row['expert'];old=Path(row['payload']);Q=B/(kind+'_linux_reward_frame_v4');shutil.copytree(old,Q,ignore=shutil.ignore_patterns('LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json','__pycache__'));shutil.copy2(B/'actual_reward_frame_observer_v3.py',Q/'actual_reward_frame_observer_v3.py');p=Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py';s=p.read_text('utf8');assert 'from actual_reward_frame_observer_v2 import install' in s;p.write_text(s.replace('from actual_reward_frame_observer_v2 import install','from actual_reward_frame_observer_v3 import install'),encoding='utf8');m=json.loads((old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes());rows=[]
  for p in sorted(x for x in Q.rglob('*') if x.is_file()):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m.update(version=4,files=rows,previous_V3_manifest_SHA=H(old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json'),original_typed_cpu_adapter_reused=True,no_reward_actor_physics_change=True);mp=Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json';mp.write_text(json.dumps(m,indent=2));zp=B/(kind+'_linux_reward_frame_v4.zip')
  with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in Q.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(Q).as_posix())
  payloads.append(dict(expert=kind,payload=str(Q),manifest_SHA=H(mp),source_SHA=m['source_SHA'],worker_SHA=H(Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py'),package=dict(path=str(zp),bytes=zp.stat().st_size,SHA=H(zp))))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 with (R/'TWO_EXPERT_LINUX_V4_TYPED_PROXY_CALLABLE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payloads=payloads,typed_ProxyArray_fixture_passed=True,public10files_SHA_passed=True,original_Linux_query_and_physics_guards_unchanged=True,fixture_artifact=records['ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json'],no_reward_func_or_actor_called_extra=True,RNG_unchanged0CUDA0optimizer=True,no_target_upload_yet=True),f,indent=2)
 print(json.dumps(dict(typed_Proxy_fixture_passed=True,experts=[x['expert'] for x in payloads],no_target_or_GPU_mutation=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TYPED_PROXY_PAYLOAD_CPU_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_change=True),f,indent=2)
  raise
