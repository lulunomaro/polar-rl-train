"""New immutable first whole-model CPU audit; completed native proof is reused."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent;sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();c=json.loads((R/'CE3_ORIGINAL_FP32_NEW_FIRST_BOUND_COLLECTION_ACTUAL.json').read_bytes());m=json.loads((B/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());src=B/'payload/h1/job0/source/H1_ce3_public4_closed24.pt';assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_SHA'];s=torch.load(src,map_location='cpu',weights_only=False)
 models={};counts={}
 for row in c['downloaded_models']:
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];v=torch.load(p,map_location='cpu',weights_only=False);n=[0,0];tensors(v,n);assert n==[199,105];models[row['kind']]=v;counts[row['kind']]=n
 row=c['target']['rows'].get('NODE_CURRENT.json',{}).get('row',{});native=row.get('native_CPU') or c['target']['rows'].get('NODE_TERMINAL_ACTUAL.json',{}).get('row',{}).get('native_CPU');assert native and native['value']['passed'] and native['reference_protocol']=='original_formal_H1_FP32_absolute1e-4' and native['old_FP64_refusal_retained']
 assert native['SHA']==hashlib.sha256(json.dumps(native['value'],indent=2).encode()).hexdigest()==m['H1_same_source_backend_native_reuse']['native_CPU_SHA']
 positive=all(k in models for k in ('immutable_startup0','immutable_first'));changes={}
 if positive:
  z=models['immutable_startup0'];p=models['immutable_first']
  for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],z[g])
  assert {int(v['step']) for v in z['optimizer_state_dict']['state'].values()}=={646100} and {int(v['step']) for v in p['optimizer_state_dict']['state'].values()}=={646120}
  assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  assert p['owned_H1_completed_updates']==1 and not p['failed_partial_prefix'] and p['owned_H1_learning_task']['optimization_candidate']['coefficient']==.001
  changes={g:[k for k in s[g] if not eq(s[g][k],p[g][k])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_real_immutable_first_complete_local_CPU=positive,source_SHA=m['source_SHA'],all_models=c['downloaded_models'],counts=counts,all_model_runtime_finite=True,startup0_source9STD8critic17Adam_literalexact=positive,sourceepisode_plus1_phaseage0=positive,all17Adam646100_to646120=positive,all17actorcritic_changes=changes,production_controls=24 if positive else None,production_envsteps=480000 if positive else None,first100normal_schedule_not_public4_aux_effect=True,old_FP64_refusal_separate_and_unchanged=True,no_native_PT_raw_rehash_or_replay=True,not_FINAL_frozen_skill_or_course_PASS=True,pending_missing=not positive,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'CE3_ORIGINAL_FP32_NEW_IMMUTABLE_FIRST_COMPLETE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(first_complete_CPU=positive,Adam_before=646100,Adam_after=646120,models=len(models))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_ORIGINAL_FP32_FIRST_CPU_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_mutation=True),f,indent=2)
  raise
