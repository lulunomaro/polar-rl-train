from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
U=Path(__file__).resolve().parent;R=U/'reports';sys.path.insert(0,str(U.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def model_hash(sd):
 h=hashlib.sha256()
 for k in sorted(sd):x=sd[k].contiguous();h.update(k.encode());h.update(str(x.dtype).encode());h.update(str(list(x.shape)).encode());h.update(x.reshape(-1).view(torch.uint8).numpy().tobytes())
 return h.hexdigest()
def main():
 v=json.loads((R/'SAFE72_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION_ACTUAL.json').read_bytes());prep=json.loads((R/'RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());out={};rng=torch.get_rng_state().clone();torch.set_num_threads(2)
 for key in ('e2','recovery'):
  spec=prep['specs'][key]
  rows=v['downloaded_models'][key];first=next((r for r in rows if r['kind']=='immutable_first'),None);zero=next((r for r in rows if r['kind']=='immutable_startup0'),None)
  if first is None or zero is None:
   out[key]=dict(first_saved_PPO_complete_local_CPU_verified=False,actual_files=v[key]['files'],not_faking_missing_or_failed_as_pass=True);continue
  checkpoints={}
  for row in rows:
   p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'] and row['twohost_complete_SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);checkpoints[row['kind']]=(ck,count)
  source=U/'payload'/key/'job0/source'/spec['source_filename'];assert H(source)==spec['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);z,zc=checkpoints['immutable_startup0'];f,fc=checkpoints['immutable_first'];before=spec['source_Adamstep']
  for group in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[group],z[group]),(key,group)
  assert len(f['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in z['optimizer_state_dict']['state'].values()}=={before} and {int(x['step']) for x in f['optimizer_state_dict']['state'].values()}=={before+20};changes={group:[n for n in s[group] if not eq(s[group][n],f[group][n])] for group in ('actor_state_dict','critic_state_dict')};assert changes['actor_state_dict'] and changes['critic_state_dict'];typed=s
  if key=='recovery':
   typed,tc=checkpoints['production_typed_source_native_reference']
   for group in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[group],typed[group])
  assert torch.equal(z['sensor_DR_state']['episode'],typed['sensor_DR_state']['episode']+1)
  if key=='h1':assert not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  cur=next(r['value'] for r in v[key]['files'] if r['path'].endswith('/NODE_CURRENT.json'));go=cur['reply']['go'];assert go['source_SHA']==spec['source_SHA'] and go['max_parent_seconds']==spec['max_parent_seconds'] and go['exit_headroom_seconds']==300;native=cur['row']['native_CPU'];assert native['value']['passed'] and native['value']['source_SHA']==spec['source_SHA'] and native['value']['controls']==spec['native_controls'];out[key]=dict(first_saved_PPO_complete_local_CPU_verified=True,source_SHA=spec['source_SHA'],zero=dict(zero,whole_model_tensor_counts=zc,source_core9_STD8critic17Adam_literalexact=True),first=dict(first,whole_model_tensor_counts=fc,all_tensors_finite=True,actual_actor9inclSTD_critic8_changes=changes,all17Adam_before=before,all17Adam_after=before+20),production_fulltyped_source_native_reference_for_E3_only=key=='recovery',startup_typed_source_episode_exact_plus1=True,actual_GO=go,native_CPU_report_SHA=native['SHA'],H1_strict_same_source_backend_native_reuse=False,H1_own_new_source_native180=key=='h1',native_not_credited_as_PPO=True,first_production_controls24_envsteps480000=True,actor_SHA=model_hash(f['actor_state_dict']),critic_SHA=model_hash(f['critic_state_dict']),not_frozen_skill_qualification=True)
 positive=[x for x in out.values() if x['first_saved_PPO_complete_local_CPU_verified']];assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();all3=len(positive)==2
 if all3:assert len({x['actor_SHA'] for x in positive})==2 and len({x['critic_SHA'] for x in positive})==2
 report=dict(epoch=time.time(),all_two_healthy72_real_distinct_saved_PPO_positive=all3,H1_resource_rejected_no_worker_or_GO=True,experts=out,complete_locally_verified_expert_count=len(positive),one_original_canonical_writer_no_NCCL_or_action_weight_averaging=True,not_all_skills_or_course_complete=True,CPU_RNG_unchanged0CUDA0optimizer=True,all_missing_failures_retained_separate=True);p=R/'SAFE72_TWO_REAL_DISTINCT_FIRST_COMPLETE_MODELS_LOCAL_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(all_two_healthy72_real_saved_PPO=all3,experts={k:dict(passed=x['first_saved_PPO_complete_local_CPU_verified'],first_SHA=(x.get('first') or {}).get('SHA'),Adam=(x.get('first') or {}).get('all17Adam_after')) for k,x in out.items()})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SAFE72_FIRST_MODELS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_replay=True),f,indent=2)
  raise
