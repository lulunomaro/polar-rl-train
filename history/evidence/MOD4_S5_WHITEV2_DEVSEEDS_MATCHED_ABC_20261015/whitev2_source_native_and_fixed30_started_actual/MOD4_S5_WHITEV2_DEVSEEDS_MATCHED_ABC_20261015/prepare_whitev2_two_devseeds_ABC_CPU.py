"""Registered white_v2 only. Actual original sampler CPU fixture; no GPU/network."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time,traceback,types,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';PREV=W/'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015';SHARED=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload';ROOT='D:/MOD4_async_eval/'+D.name
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 R.mkdir(exist_ok=True);prior=json.loads((PREV/'reports/DEVSEED03_COMPLETE15_TWO_DEVSEED_THREEWAY_SCOPE_TAIL_COST_CPU_ACTUAL.json').read_bytes());assert prior['actual_second_development_seed_threeway_complete'] and prior['second_gate_PPO_not_admitted']
 assert json.loads((PREV/'reports/DEVSEED03_COMPLETE15_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes())['actual_owner_absent']
 # Execute the exact existing sampler function in a CPU-only mock of its setters.
 src=SHARED/'runtime/isaac/mod4/mild_dr.py';policy=SHARED/'runtime/isaac/mod4/autonomy_policy.py';tree=ast.parse(src.read_text(encoding='utf8'));pt=ast.parse(policy.read_text(encoding='utf8'))
 recipes=ast.literal_eval(next(x.value for x in pt.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DR_PROFILES' for t in x.targets)))
 assert recipes['white_v2']==dict(mass=(.925,1.075),motor=(.925,1.075),friction=(.75,1.))
 klass=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='MildDR');fn=copy.deepcopy(next(x for x in klass.body if isinstance(x,ast.FunctionDef) and x.name=='__call__'));fn.name='sample_existing';module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]));ns=dict(torch=torch,tensor=lambda x:x,wp=types.SimpleNamespace(from_torch=lambda x,**k:x,float32=torch.float32,int32=torch.int32));exec(compile(module,'<exact original MildDR.__call__ CPU fixture>','exec'),ns)
 rng=torch.get_rng_state().clone();fixtures=[]
 for N in (80,88):
  for seed in (20261002,20261003):
   results=[]
   for profile in ('white_v2','white_v3'):
    robot=types.SimpleNamespace();robot.actuators={name:types.SimpleNamespace(episode_scale=torch.ones(N,width)) for name,width in [('legs',4),('wheels',2)]};robot.root_view=types.SimpleNamespace();state={'material':torch.full((N,3,3),.9)}
    robot.set_masses_index=lambda masses,env_ids:state.update(mass=masses.clone());robot.set_inertias_index=lambda inertias,env_ids:state.update(inertia=inertias.clone());robot.root_view.get_material_properties=lambda:state['material'];robot.root_view.set_material_properties=lambda material,ids:state.update(material=material.clone())
    self=types.SimpleNamespace(robot=robot,recipe=recipes[profile],generator=torch.Generator().manual_seed(seed+1717),cpu_generator=torch.Generator().manual_seed(seed+1818),mass=torch.ones(N,3),inertia=torch.ones(N,3,9),factor=torch.ones(N),nominal=torch.ones(N,dtype=torch.bool),mu=torch.full((N,),.9),reset_count=torch.zeros(N,dtype=torch.long),friction_buckets=torch.cat((torch.tensor([.9]),torch.linspace(*recipes[profile]['friction'],32))),wheel_shapes=[0,1])
    ns['sample_existing'](self,types.SimpleNamespace(num_envs=N,device='cpu'),None)
    assert torch.equal(self.reset_count,torch.ones_like(self.reset_count)) and torch.equal(state['mass'],self.factor[:,None].expand(N,3)) and torch.equal(state['inertia'],self.factor[:,None,None].expand(N,3,9))
    assert recipes[profile]['mass'][0]<=float(self.factor.min())<=float(self.factor.max())<=recipes[profile]['mass'][1] and torch.all(self.factor[self.nominal]==1)
    assert torch.equal(state['material'][:,0,0],self.mu) and torch.equal(state['material'][:,1,1],self.mu) and torch.all(state['material'][:,2]==.9)
    for a in robot.actuators.values():assert recipes[profile]['motor'][0]<=float(a.episode_scale.min())<=float(a.episode_scale.max())<=recipes[profile]['motor'][1] and torch.all(a.episode_scale[self.nominal]==1)
    results.append(dict(profile=profile,nominal=self.nominal.clone(),generator=self.generator.get_state().clone(),cpu_generator=self.cpu_generator.get_state().clone(),factor=self.factor.clone()))
   assert torch.equal(results[0]['nominal'],results[1]['nominal']) and torch.equal(results[0]['generator'],results[1]['generator']) and torch.equal(results[0]['cpu_generator'],results[1]['cpu_generator']) and not torch.equal(results[0]['factor'],results[1]['factor'])
   fixtures.append(dict(N=N,seed=seed,original_sampler_setter_formulas_and_bounds_CPU=True,same_draw_order_and_nextdraw_state_across_profiles=True,white_v2_factor_range=[float(results[0]['factor'].min()),float(results[0]['factor'].max())],nominal_rows=int(results[0]['nominal'].sum()),mock_setters_not_GPU_readback=True))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('WHITEV2_ORIGINAL_PROFILE_SOURCE_AND_SAMPLER_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,original_sampler_source_SHA=H(src),original_profile_source_SHA=H(policy),recipe=recipes['white_v2'],fixtures=fixtures,no_CUDA_optimizer_or_global_CPU_RNG_advance=True,not_GPU_physical_admission=True,nominal_profile_deferred_pending_own_readonly_audit_API_compatibility=True))
 assert not Q.exists();shutil.copytree(PREV/'payload',Q,ignore=shutil.ignore_patterns('__pycache__'))
 old=(PREV/'payload/retention_worker_v8.py').read_text(encoding='utf8');worker=old
 swaps=[(PREV.name,D.name),("default=20261003","default=20261002"),('assert a.seed==20261003','assert a.seed in (20261002,20261003)'),("os.environ['RM_MILD_DR_PROFILE']='white_v3'","os.environ['RM_MILD_DR_PROFILE']='white_v2'"),("a.dr_profile='white_v3'","a.dr_profile='white_v2'")]
 for a,b in swaps:assert a in worker;worker=worker.replace(a,b)
 inverse=worker
 for a,b in reversed(swaps):inverse=inverse.replace(b,a)
 assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(old));(Q/'retention_worker_v8.py').write_text(worker,encoding='utf8')
 old=(PREV/'payload/retention_native_witness_v8.py').read_text(encoding='utf8');new=old.replace("DR_profile='white_v3'","DR_profile='white_v2'");assert ast.dump(ast.parse(new.replace("DR_profile='white_v2'","DR_profile='white_v3'")))==ast.dump(ast.parse(old));(Q/'retention_native_witness_v8.py').write_text(new,encoding='utf8')
 def rewrite(v):
  if isinstance(v,str):return v.replace('D:/MOD4_async_eval/'+PREV.name,ROOT)
  if isinstance(v,dict):return {k:rewrite(x) for k,x in v.items()}
  if isinstance(v,list):return [rewrite(x) for x in v]
  return v
 for name in ('S4_PAIR_SOURCE_MANIFEST.json','S4_TRAINED_GATE_SOURCE_MANIFEST.json'):(Q/name).write_text(json.dumps(rewrite(json.loads((Q/name).read_bytes())),indent=2),encoding='utf8')
 oldm=json.loads((PREV/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes());m=rewrite(oldm);m.update(epoch=time.time(),namespace=D.name,approved_GPU=False,status='CPU_PREPARED_ONLY_NOT_ACTUAL_LEASE',declared_development_seeds=[20261002,20261003],DR_profile='white_v2',all_three_policies_frozen=True);m.pop('declared_new_development_seed',None)
 whole=[]
 for name,count,sha in [('E0_frozen_source.pt',94,'b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'),('E1_WAVE35_frozen_source.pt',102,'b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'),('S4_gate_first_final.pt',113,'02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3')]:
  p=Q/'source'/name;assert H(p)==sha;c=torch.load(p,map_location='cpu',weights_only=False);t=[]
  def walk(v):
   if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());t.append(v)
   elif hasattr(v,'items'):
    for x in v.values():walk(x)
   elif isinstance(v,(list,tuple)):
    for x in v:walk(x)
  walk(c);assert sum(x.is_floating_point() for x in t)==count;whole.append(dict(name=name,bytes=p.stat().st_size,sha256=sha,tensors=len(t),floating=count))
 exact=[]
 for kind in ('flat','spin','world'):
  p=Q/('retention_'+kind+'_native_v8.py');assert p.read_bytes()==(PREV/'payload'/p.name).read_bytes();exact.append(dict(kind=kind,sha256=H(p)))
 for name in ('s5_single_frozen35_v1.py','s4_shared_feedback_hardtop1_v1.py','s5_ABC_evaluation_adapter_v1.py','s5_retention_single_adapter_v1.py','s4_retention_pair_adapter_v1.py'):assert (Q/name).read_bytes()==(PREV/'payload'/name).read_bytes()
 for p in Q.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
 m['package_files_v8']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RETENTION_CPU_MANIFEST_V8.json'];(Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=D/'S5_WHITEV2_TWO_DEVSEEDS_ABC_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as f:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:f.write(p,p.relative_to(Q).as_posix())
 put('WHITEV2_ABC_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),worker_SHA=H(Q/'retention_worker_v8.py'),seeds=[20261002,20261003],profile='white_v2',whole_source_CPU=whole,original3_physical_main_bytes_exact=exact,original_control_adapters_bytes_exact=True,worker_AST_inverse_except_declared_profile_seed_namespace=True,witness_AST_inverse_except_profile_metadata=True,original_sampler_CPU_proof_SHA=H(R/'WHITEV2_ORIGINAL_PROFILE_SOURCE_AND_SAMPLER_CPU_ACTUAL.json'),shared_source_files=len(m['shared_source_freeze']),package_files=len(m['package_files_v8']),new_native_full30_pending=True,nominal_not_dispatched=True,no_PPO_budget_or_heldout=True));print(json.dumps(dict(prepared=True,package_SHA=H(z),no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put('WHITEV2_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_remote_or_budget=True));raise
