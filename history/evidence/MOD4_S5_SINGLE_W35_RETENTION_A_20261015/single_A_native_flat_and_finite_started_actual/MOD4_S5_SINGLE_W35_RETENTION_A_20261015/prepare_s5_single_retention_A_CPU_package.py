"""Only missing A counterparts; exact original physical loops, no GPU/transport."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time,traceback,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';ROOT='D:/MOD4_async_eval/'+D.name
OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015/payload';FIRST=W/'MOD4_S5_SINGLE_W35_MATCHED35_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 R.mkdir(exist_ok=True);assert not Q.exists()
 prior=json.loads((FIRST/'reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json').read_bytes());assert prior['passed_actual_first_matched_three_configurations'] and not prior['S5_overall_complete']
 shutil.copytree(OLD,Q,ignore=shutil.ignore_patterns('__pycache__','S4_*','s4_*','E0_frozen_source.pt'))
 shutil.copy2(FIRST/'s5_single_frozen35_v1.py',Q/'s5_single_frozen35_v1.py');shutil.copy2(D/'s5_retention_single_adapter_v1.py',Q/'s5_retention_single_adapter_v1.py')
 witness=(Q/'retention_native_witness_v8.py').read_text(encoding='utf8');new=witness
 swaps=[('from s4_retention_pair_adapter_v1 import build_native_rule_pair','from s5_retention_single_adapter_v1 import build_retention_single'),('return build_native_rule_pair(vec,path,device)','return build_retention_single(vec,path,device)'),('only_actor_loaded=False,only_frozen_expert_actor_outputs_executed=True,new_gate_critic_fixture_present_untrained=True','only_actor_loaded=True,only_single_W35_actor_executed=True,no_gate_or_second_expert_forward=True')]
 for old,value in swaps:assert old in new;new=new.replace(old,value)
 inverse=new
 for old,value in reversed(swaps):inverse=inverse.replace(value,old)
 assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(witness));(Q/'retention_native_witness_v8.py').write_text(new,encoding='utf8')
 base=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014/payload/retention_worker_v8.py'
 worker=base.read_text(encoding='utf8').replace('MOD4_3060_LEFT_REPAIR_RETENTION_20261014',D.name)
 compile(worker,'retention_worker_v8.py','exec');(Q/'retention_worker_v8.py').write_text(worker,encoding='utf8')
 mainrows=[]
 for kind in ('flat','spin','world'):
  p=Q/('retention_'+kind+'_native_v8.py');assert p.read_bytes()==(OLD/p.name).read_bytes();mainrows.append(dict(kind=kind,sha256=H(p)))
 sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
 source=Q/'source/E1_WAVE35_frozen_source.pt';assert H(source)=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 ck=torch.load(source,map_location='cpu',weights_only=False);tensors=[]
 def walk(v):
  if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());tensors.append(v)
  elif hasattr(v,'items'):
   for x in v.values():walk(x)
  elif isinstance(v,(list,tuple)):
   for x in v:walk(x)
 walk(ck);assert sum(v.is_floating_point() for v in tensors)==102 and ck['E1_terrain_state']['num_envs']==20000
 g=torch.load(FIRST/'payload/source/S4_gate_first_final.pt',map_location='cpu',weights_only=False) if (FIRST/'payload/source/S4_gate_first_final.pt').exists() else torch.load(W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/source/S4_gate_first_final.pt',map_location='cpu',weights_only=False)
 rng=torch.get_rng_state().clone();negative=[]
 for n in (80,88):
  c=Single35(source,n,'cpu');x=g['S4_shared_control_state']['cache']['policy'][:n].clone();c.last=x[:,22:28].clone();p=c.begin(0,lambda:x)
  assert c.begin(0,lambda:(_ for _ in ()).throw(AssertionError('duplicate feedback draw'))) is p
  expected=x
  for layer in (0,2,4,6):
   expected=F.linear(expected,ck['actor_state_dict'][f'mlp.{layer}.weight'],ck['actor_state_dict'][f'mlp.{layer}.bias'])
   if layer!=6:expected=F.elu(expected)
  assert torch.equal(expected,p['raw_action']) and torch.equal(expected.clamp(-6,6),p['clipped_action'])
  ended=torch.arange(n)%3==0;c.finish(p['clipped_action'],ended);assert not c.last[ended].any() and torch.equal(c.last[~ended],p['clipped_action'][~ended]) and c.exact()
  for name in ('shape','previous_action','mode','nonfinite'):
   b=x.clone();a=Single35(source,n,'cpu');a.last=x[:,22:28].clone()
   if name=='shape':b=b[:,:34]
   if name=='previous_action':b[:,22]+=1
   if name=='mode':b[:,28:35]=0
   if name=='nonfinite':b[0,0]=float('nan')
   try:a.begin(0,lambda:b)
   except AssertionError:negative.append(dict(n=n,rejected=name))
   else:raise AssertionError(name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 old=json.loads((OLD/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());ref=dict(expert='S5_single_W35_A',local_path=ROOT+'/payload/source/'+source.name,sha256=H(source),bytes=source.stat().st_size)
 manifest={k:old[k] for k in ('shared_source_freeze','V7_actual_native_binding','v5_sdk_primary_stub')}
 manifest.update(epoch=time.time(),namespace=D.name,approved_GPU=False,status='CPU_PREPARED_ONLY_NOT_ACTUAL_LEASE',sources={'single_W35':ref},source_single=ref,only_actor_loaded=True,only_single_policy_executed=True,no_PPO=True,source_fullstate_not_restored=True,whole_source_float102_CPU_finite=True,original_mainloops_byteexact=mainrows,original_S4_main_manifest_provenance=dict(path=str(OLD/'RETENTION_CPU_MANIFEST_V8.json'),sha256=H(OLD/'RETENTION_CPU_MANIFEST_V8.json')),original35_single_actor_component_bytes_exact_to_admitted_scope=H(Q/'s5_single_frozen35_v1.py')==H(FIRST/'s5_single_frozen35_v1.py'))
 manifest['package_files_v8']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RETENTION_CPU_MANIFEST_V8.json']
 (Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 z=D/'S5_SINGLE_W35_RETENTION_A_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:archive.write(p,p.relative_to(Q).as_posix())
 out=dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),worker_SHA=H(Q/'retention_worker_v8.py'),source_single=ref,whole_source_floating102_and_actor9_STD_CPU_finite=True,same_admitted_single35_component_SHA=H(Q/'s5_single_frozen35_v1.py'),actual80_88_saved35_whole6_cache_reset_CPU_exact=True,negative_inputs=negative,CPU_RNG_unchanged_0optimizersteps=True,original3_physical_main_bytes_exact=mainrows,source_runtime_changes_only_single_adapter_import_and_explicit_metadata=True,exact_old_B_C_fulls_reused_not_GPU_replayed=True,new_cases_expected=6,new_native_and_full_admission_pending=True,template_approved_GPU_false=True)
 p=R/'S5_SINGLE_RETENTION_A_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,package_SHA=H(z),files=len(manifest['package_files_v8']),no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);p=R/('S5_SINGLE_A_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_or_transport=True),indent=2),encoding='utf8');raise
