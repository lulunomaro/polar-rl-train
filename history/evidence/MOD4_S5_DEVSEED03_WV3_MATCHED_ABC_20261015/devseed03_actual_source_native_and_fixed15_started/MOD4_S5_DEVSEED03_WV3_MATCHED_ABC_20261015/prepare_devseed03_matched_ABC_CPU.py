"""Next approved development seed only, frozen A/B/C; no network or GPU."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time,traceback,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015';A=W/'MOD4_S5_SINGLE_W35_RETENTION_A_20261015';ROOT='D:/MOD4_async_eval/'+D.name
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 R.mkdir(exist_ok=True)
 close=json.loads((A/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json').read_bytes());assert close['actual_four_domain_single_rule_gate_cellset_complete'] and close['second_gate_PPO_not_admitted']
 hand=json.loads((A/'reports/S5_SINGLE_A_FIXED_SIX_COMPLETE_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes());assert hand['actual_owner_absent'] and hand['root_reclaims_exclusive_sequential210_249_transport']
 assert not Q.exists();shutil.copytree(OLD/'payload',Q,ignore=shutil.ignore_patterns('__pycache__'))
 for name in ('s5_single_frozen35_v1.py','s5_retention_single_adapter_v1.py'):shutil.copy2(A/'payload'/name,Q/name)
 adapter='''"""Evaluation mode is lease configuration, never policy feedback or task truth."""
def build_frozen_ABC(vec,path,device):
 from retention_native_witness_v8 import CONTEXT
 mode=CONTEXT['router_mode'];assert mode in ('single_eval','rule_eval','gate_eval')
 if mode=='single_eval':
  from s5_retention_single_adapter_v1 import build_retention_single
  return build_retention_single(vec,path,device)
 from s4_retention_pair_adapter_v1 import build_native_rule_pair
 return build_native_rule_pair(vec,path,device)
'''
 (Q/'s5_ABC_evaluation_adapter_v1.py').write_text(adapter,encoding='utf8')
 oldw=(OLD/'payload/retention_native_witness_v8.py').read_text(encoding='utf8');new=oldw
 swaps=[('from s4_retention_pair_adapter_v1 import build_native_rule_pair','from s5_ABC_evaluation_adapter_v1 import build_frozen_ABC'),('return build_native_rule_pair(vec,path,device)','return build_frozen_ABC(vec,path,device)'),('only_actor_loaded=False,only_frozen_expert_actor_outputs_executed=True,new_gate_critic_fixture_present_untrained=True',"only_actor_loaded=CONTEXT['router_mode']=='single_eval',only_frozen_policy_outputs_executed=True,loaded_control_mode=CONTEXT['router_mode'],trained_gate_loaded_only_for_pair=CONTEXT['router_mode']!='single_eval'")]
 for before,after in swaps:
  assert before in new;new=new.replace(before,after)
 inverse=new
 for before,after in reversed(swaps):inverse=inverse.replace(after,before)
 assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(oldw));(Q/'retention_native_witness_v8.py').write_text(new,encoding='utf8')
 oldworker=(OLD/'payload/retention_worker_v8.py').read_text(encoding='utf8');worker=oldworker.replace(OLD.name,D.name).replace('20261002','20261003').replace("choices=('rule_eval','gate_eval')","choices=('single_eval','rule_eval','gate_eval')")
 before='only_actor_loaded=False,only_frozen_pair_actor_outputs_executed=True,new_gate_critic_fixture_present_untrained=True';after="only_actor_loaded=a.router_mode=='single_eval',declared_eval_mode=a.router_mode,trained_gate_source148_pair_modes_only=True"
 assert before in worker;worker=worker.replace(before,after)
 inv=worker.replace(after,before).replace("choices=('single_eval','rule_eval','gate_eval')","choices=('rule_eval','gate_eval')").replace('20261003','20261002').replace(D.name,OLD.name)
 assert ast.dump(ast.parse(inv))==ast.dump(ast.parse(oldworker));(Q/'retention_worker_v8.py').write_text(worker,encoding='utf8')
 def rewrite(v):
  if isinstance(v,str):return v.replace('D:/MOD4_async_eval/'+OLD.name,ROOT)
  if isinstance(v,dict):return {k:rewrite(x) for k,x in v.items()}
  if isinstance(v,list):return [rewrite(x) for x in v]
  return v
 for name in ('S4_PAIR_SOURCE_MANIFEST.json','S4_TRAINED_GATE_SOURCE_MANIFEST.json'):
  value=json.loads((Q/name).read_bytes());(Q/name).write_text(json.dumps(rewrite(value),indent=2),encoding='utf8')
 pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());gate=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
 expected=[('E0_frozen_source.pt','b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',94),('E1_WAVE35_frozen_source.pt','b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',102),('S4_gate_first_final.pt','02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3',113)]
 whole=[]
 for name,sha,count in expected:
  p=Q/'source'/name;assert H(p)==sha;c=torch.load(p,map_location='cpu',weights_only=False);t=[]
  def walk(v):
   if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());t.append(v)
   elif hasattr(v,'items'):
    for x in v.values():walk(x)
   elif isinstance(v,(list,tuple)):
    for x in v:walk(x)
  walk(c);assert sum(x.is_floating_point() for x in t)==count;whole.append(dict(name=name,bytes=p.stat().st_size,sha256=sha,tensors=len(t),floating=count))
 sys.path.insert(0,str(Q));from s4_shared_feedback_hardtop1_v1 import PairRouter
 from s4_eval_trained_gate_source_v1 import load_trained_gate
 from s5_single_frozen35_v1 import Single35
 refs=copy.deepcopy(pair['sources'])
 for row in refs:row['local_path']=str(Q/'source'/Path(row['local_path']).name)
 ck=torch.load(Q/'source/S4_gate_first_final.pt',map_location='cpu',weights_only=False);base=ck['S4_shared_control_state']['cache']['policy'];rng=torch.get_rng_state().clone();checks=[]
 for N in (80,88):
  for mode in ('single_eval','rule_eval','gate_eval'):
   x=base[:N].clone();done=torch.arange(N)%3==0
   if mode=='single_eval':
    r=Single35(Q/'source/E1_WAVE35_frozen_source.pt',N,'cpu');r.last=x[:,22:28].clone();v=r.begin(0,lambda:x);assert r.begin(0,lambda:(_ for _ in ()).throw(AssertionError('extra draw'))) is v;r.finish(v['clipped_action'],done);assert r.exact() and not r.last[done].any()
   else:
    r=PairRouter(refs,N,'cpu');load_trained_gate(r,dict(gate,local_path=str(Q/'source/S4_gate_first_final.pt')));r.last_action=x[:,22:28].clone();v=r.decide(0,lambda:x,mode)
    z=v['logits'].argmax(-1) if mode=='gate_eval' else ((x[:,0].abs()>0)&(x[:,0].abs()<=.300001)&(x[:,1:3].abs().amax(-1)<=1e-6)).long()
    assert torch.equal(z,v['z']) and torch.equal(v['raw_action'],v['expert_means'][torch.arange(N),z]);assert not r.optimizer.state
    r.finish(0,v['clipped_action'],done);assert not r.last_action[done].any()
   checks.append(dict(N=N,mode=mode,whole6_selected_original_clip_and_actualhistory_reset=True))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 exact=[]
 for kind in ('flat','spin','world'):
  p=Q/('retention_'+kind+'_native_v8.py');assert p.read_bytes()==(OLD/'payload'/p.name).read_bytes();exact.append(dict(kind=kind,sha256=H(p)))
 for p in Q.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
 old=json.loads((OLD/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes());m={k:old[k] for k in ('shared_source_freeze','V7_actual_native_binding','v5_sdk_primary_stub')}
 m.update(epoch=time.time(),namespace=D.name,approved_GPU=False,status='CPU_PREPARED_ONLY_NOT_ACTUAL_LEASE',sources={'W35_scene_anchor':pair['sources'][1]},source_single=pair['sources'][1],source_pair=pair['sources'],trained_gate=gate,source_fullstate_not_restored=True,declared_new_development_seed=20261003,DR_profile='white_v3',original_mainloops_byteexact=exact,allowed_router_modes=['single_eval','rule_eval','gate_eval'],whole_source_CPU=whole,all_three_policies_frozen=True)
 m['package_files_v8']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RETENTION_CPU_MANIFEST_V8.json'];(Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=D/'S5_DEVSEED03_MATCHED_ABC_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as f:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:f.write(p,p.relative_to(Q).as_posix())
 v=dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),worker_SHA=H(Q/'retention_worker_v8.py'),seed=20261003,profile='white_v3',whole_source_CPU=whole,sources=m['sources'],shared_source_files=len(m['shared_source_freeze']),package_files=len(m['package_files_v8']),worker_AST_inverse_exact_except_seed_namespace_mode_declaration=True,witness_AST_inverse_exact_except_adapter_metadata=True,original3_physical_main_bytes_exact=exact,all_shared_feedback_actors_and_pair_adapters_original_bytes_exact=True,CPU_actual_saved35_checks=checks,global_CPU_RNG_unchanged_noCUDA_or_updates=True,new_native_and_full15_pending=True,no_second_gate_PPO_or_budget_admitted=True,heldout_seeds_not_used=True,prior_complete_scope_SHA=H(A/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json'))
 put('DEVSEED03_ABC_CPU_PREPARED_ACTUAL.json',v);print(json.dumps(dict(prepared=True,package=v['package'],new_GPU_admitted=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put('DEVSEED03_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_remote_GPU_or_budget=True));raise
