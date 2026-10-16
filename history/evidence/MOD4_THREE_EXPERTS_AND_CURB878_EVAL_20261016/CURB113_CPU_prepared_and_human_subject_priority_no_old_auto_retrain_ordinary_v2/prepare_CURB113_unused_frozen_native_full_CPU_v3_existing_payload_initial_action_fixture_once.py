"""New closed CURB113 source; reuse exact original frozen physical/query contracts."""
from pathlib import Path
import os,ast,json,hashlib,shutil,zipfile,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;E=D/'curb113_frozen_v1';Q=E/'eval_payload_v2';R=E/'reports';W=D.parent;ROOT='D:/MOD4_async_eval/'+D.name+'/curb113_frozen_v1'
OLD='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1';NEW='3d2b0b6d9260383031e0c198501224fdaedefef9c283b43ce588419319b5de88'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert E.exists() and Q.exists();src=D/'first_closed_expert_models/job0/model_update113.pt';assert H(src)==NEW and H(Q/'source/CURB113.pt')==NEW;old=D/'eval_payload_v2'
 for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py'):
  original=(old/name).read_text(encoding='utf8');expected=original.replace(OLD,NEW).replace('CURB878','CURB113').replace(D.name,D.name+'/curb113_frozen_v1');assert (Q/name).read_text(encoding='utf8')==expected
 # Original full physical loop and exact independent eight-triangle mirror query are unchanged.
 for name in ('full80_runtime_native_v1.py','curb_worldmesh_query_contract_v1.py','runtime/isaac/mod4/curb20_geometry.py','runtime/isaac/mod4/curb20_profile.json'):
  assert H(Q/name)==H(old/name)
 ck=torch.load(src,map_location='cpu',weights_only=False);ts=[]
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all();ts.append(x)
  elif isinstance(x,dict):
   for z in x.values():finite(z)
  elif isinstance(x,(tuple,list)):
   for z in x:finite(z)
 finite(ck);assert len(ts)==185 and sum(x.is_floating_point() for x in ts)==105;assert ck['independent_expert_task_contract']['kind']=='CURB20' and ck['E1_terrain_state']['num_envs']==20000;assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={645100};assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
 import sys
 sys.path[:0]=[str(Q),str(Q/'runtime/isaac/mod4')];from s5_single_frozen35_v1 import Single35
 rng=torch.get_rng_state().clone();x=torch.linspace(-.4,.4,80*35).reshape(80,35);x[:,28:]=0;x[:,28]=1;x[:,22:28]=0;a=Single35(Q/'source/CURB113.pt',80,'cpu');v=a.begin(0,lambda:x);y=x
 for i in (0,2,4,6):
  y=torch.nn.functional.linear(y,ck['actor_state_dict'][f'mlp.{i}.weight'],ck['actor_state_dict'][f'mlp.{i}.bias'])
  if i<6:y=torch.nn.functional.elu(y)
 assert torch.equal(y,v['raw_action']);a.finish(v['clipped_action'],torch.arange(80)%7==0);assert a.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 m=dict(epoch=time.time(),source_single_policy=dict(expert='CURB113_independent_first_block',local_path=ROOT+'/payload/source/CURB113.pt',sha256=NEW,bytes=src.stat().st_size,CPU_tensors=len(ts),CPU_floating=105),no_PPO=True,approved_GPU=False,original_physical_loop_and_query_bytes_exact=True,scope='New trained source on original CURB20 mirrored geometry; native120 then full1500/6000cb, no source/scene changed midcase')
 m['file_rows']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts];manifest=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';manifest.write_text(json.dumps(m,indent=2),encoding='utf8');z=E/'CURB113_FROZEN_3060_V1.zip'
 with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:out.write(p,p.relative_to(Q).as_posix())
 def adapt(name):
  s=(D/name).read_text(encoding='utf8');s=s.replace("W=D.parent;", "W=D.parents[1];").replace("str(D.parent/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')","str(D.parents[1]/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')");s=s.replace("ROOT='D:/MOD4_async_eval/'+D.name", "ROOT='"+ROOT+"'");s=s.replace('CURB878','CURB113').replace('curb_final878','curb_independent113').replace('CURB_final878.pt','CURB113.pt');s=s.replace("len(ts)==181 and sum(x.is_floating_point() for x in ts)==102", "len(ts)==185 and sum(x.is_floating_point() for x in ts)==105").replace('floating=102','floating=105');compile(s,name,'exec');p=E/name.replace('curb878','curb113');p.write_text(s,encoding='utf8');return p
 scripts=[adapt(n) for n in ('dispatch_curb878_frozen3060_unused_case_once.py','collect_curb878_own_case_actual_readonly.py','review_curb878_actual_physical_source_route_CPU.py')]
 r=dict(epoch=time.time(),passed_CPU_only=True,source=m['source_single_policy'],package=dict(path=str(z.resolve()),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(manifest),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),full_source_all185_tensor105_floating_finite=True,all17Adam645100=True,source9_STD_CPU_forward_exact=True,global_CPU_RNG_unchanged=True,CPU_no_CUDA_or_optimizer=True,original_physical_loop_query_geometry_bytes_exact=True,old878_native_full_consumed_never_replayed=True,new_target_CPU_native_resource_and_allactual_full_required=True,scripts=[str(p) for p in scripts]);(R/'CURB113_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  D.joinpath('reports','CURB113_FROZEN_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json').write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_dispatch=True),indent=2),encoding='utf8');raise
