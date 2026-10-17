"""Keep H1 control frame until its original reward wrapper finishes; no plant/source patch."""
from pathlib import Path
import ast,json,time,hashlib,shutil,zipfile,types,traceback
import torch
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'h1_fe1709_frozen_v1/payload';E=B/'h1_fe1709_frozen_v2';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,indent=2))
def main():
 assert not E.exists();rng=torch.get_rng_state().clone()
 # Execute the actual source reward wrapper against the prematurely cleared V1 frame.
 source=A/'frozen_shared/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py'
 fun=next(n for n in ast.walk(ast.parse(source.read_text('utf8'))) if isinstance(n,ast.FunctionDef) and n.name=='reward')
 def fixture(frame):
  self=types.SimpleNamespace(h1_capture=True,h1_stepping=True,h1_control_frame=frame,h1_reward_readout_scale=.01,reward_manager=types.SimpleNamespace(_term_names=['h1_control_events','h1_prelaunch_progress'],_step_reward=torch.tensor([[2.,3.],[4.,5.]])))
  ns=dict(self=self,tensor=lambda x:x,original_reward=lambda *a,**k:torch.zeros(2));exec(compile(ast.Module(body=[fun],type_ignores=[]),'actual_source_H1_reward_wrapper_CPU','exec'),ns);return self,ns['reward']
 original=None
 try:fixture(None)[1](.01)
 except TypeError:original=traceback.format_exc()
 assert original and "NoneType" in original
 E.mkdir();shutil.copytree(A,Q,ignore=shutil.ignore_patterns('__pycache__','H1_FE1709_FROZEN_COMPLETE_MANIFEST_V1.json'))
 p=Q/'h1_frozen_witness_v1.py';s=p.read_text('utf8');needle="w.phase.update({'H1_phase_'+key:cpu(value) for key,value in e.h1_phase.tensors().items()});e.h1_control_frame=None";assert s.count(needle)==1
 s=s.replace(needle,"w.phase.update({'H1_phase_'+key:cpu(value) for key,value in e.h1_phase.tensors().items()})")
 marker=' e.termination_manager.compute=observed_termination\n return e'
 replacement=''' e.termination_manager.compute=observed_termination
 reward=e.reward_manager.compute
 def observed_reward(*args,**kwargs):
  value=reward(*args,**kwargs)
  if w.active:
   assert e.h1_control_frame is not None and 'event_applied' in e.h1_control_frame and 'progress_applied' in e.h1_control_frame
   w.phase.update({'H1_'+key:cpu(value) for key,value in e.h1_control_frame.items()});e.h1_control_frame=None
  return value
 e.reward_manager.compute=observed_reward
 return e'''
 assert s.count(marker)==1;s=s.replace(marker,replacement);ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
 # Execute new observer reward with the original source reward, including its mutation.
 fn=next(n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.FunctionDef) and n.name=='observed_reward')
 e,reward=fixture({'event_expected':torch.zeros(2),'progress_expected':torch.zeros(2)});w=types.SimpleNamespace(active=True,phase={});ns=dict(e=e,w=w,reward=reward,cpu=lambda x:x.detach().numpy().copy());exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_new_H1_observer_reward_CPU','exec'),ns)
 out=ns['observed_reward'](.01);assert out.shape==(2,) and e.h1_control_frame is None and torch.equal(torch.from_numpy(w.phase['H1_event_applied']),torch.tensor([.02,.04])) and torch.equal(torch.from_numpy(w.phase['H1_progress_applied']),torch.tensor([.03,.05]))
 for name in ('h1_frozen_worker_v1.py','h1_frozen_parent_v1.py'):
  p=Q/name;text=p.read_text('utf8').replace('H1_FE1709_FROZEN_COMPLETE_MANIFEST_V1','H1_FE1709_FROZEN_COMPLETE_MANIFEST_V2').replace('PUBLIC04_FROZEN_V1_20261018','PUBLIC04_FROZEN_V2_20261018');p.write_text(text,encoding='utf8',newline='\n')
 for name in ('h1_takeoff_progress_environment_v2.py','h1_takeoff_progress_phase_v2.py','h1_reward_scope_v1.py','h1_takeoff_progress_reward_v2.py'):assert H(A/'frozen_shared/runtime/isaac/mod4'/name)==H(Q/'frozen_shared/runtime/isaac/mod4'/name)
 m=json.loads((A/'H1_FE1709_FROZEN_COMPLETE_MANIFEST_V1.json').read_bytes());files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 m.update(version=2,files=files,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in files],original_source_H1_frame_preserved_until_reward_then_observed=True)
 mf=Q/'H1_FE1709_FROZEN_COMPLETE_MANIFEST_V2.json';put(mf,m);bundle=E/'H1_FE1709_COMPLETE_FROZEN_PAYLOAD_V2.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in files:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 old=json.loads((R/'H1_FE1709_COMPLETE_FROZEN_PUBLIC04_PACKAGE_CPU_PREPARED_ACTUAL.json').read_bytes());old.update(epoch=time.time(),manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),worker=dict(path=str(Q/'h1_frozen_worker_v1.py'),SHA=H(Q/'h1_frozen_worker_v1.py')),parent=dict(path=str(Q/'h1_frozen_parent_v1.py'),SHA=H(Q/'h1_frozen_parent_v1.py')),original_V1_observer_lifetime_CPU_reproduced_TypeError=original,new_V2_actual_source_and_observer_functions_CPU_passed=True,original_V1_sealed_package_and_transport_timeout_preserved=True,no_GPU_dispatch_from_this_preparation=True)
 put(R/'H1_FE1709_COMPLETE_FROZEN_V2_REWARD_READBACK_LIFETIME_CPU_ACTUAL.json',old)
 print(json.dumps(dict(V2_complete_payload_CPU=True,original_source_reward_and_observer_CPU_passed=True,no_source_or_physics_reward_change=True,no_GPU=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('H1_FROZEN_V2_LIFETIME_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
