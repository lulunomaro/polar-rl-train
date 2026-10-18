"""Prepared only: whole-model CPU after each actual one-hour final, no optimizer/CUDA."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((R/'THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').read_bytes());d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert v['actual_closed'] and d['owner']['detached_pid']==258398
 c=v['account']['original_canonical'];seg=next(x for x in c['completed_segments'] if x.get('owner_parent_pid')==258398);assert set(seg['experts'])=={'h1','e2','recovery'};results={}
 for key in ('h1','e2','recovery'):
  spec=d['specs'][key];r=next(x for x in v['models'] if x['key']==key);p=Path(r['local_path']);assert r['twohost_complete_SHA'] and p.stat().st_size==r['bytes'] and H(p)==r['SHA'];s=torch.load(p,map_location='cpu',weights_only=False);src=B/'payload'/key/'job0/source'/spec['source_filename'];assert H(src)==spec['source_SHA'];before=torch.load(src,map_location='cpu',weights_only=False);counts=[0,0];tensors(s,counts)
  phase=s['owned_H1_phase'] if key=='h1' else s['owned_phase'] if key=='e2' else s['E3_phase'];updates=s['owned_H1_completed_updates'] if key=='h1' else s['owned_phase_complete_updates'] if key=='e2' else s['E3_production_updates'];assert phase=='production' and updates>0 and not s.get('failed_partial_prefix',False)
  start={int(x['step']) for x in before['optimizer_state_dict']['state'].values()};end={int(x['step']) for x in s['optimizer_state_dict']['state'].values()};assert len(before['optimizer_state_dict']['state'])==17 and start=={spec['source_Adamstep']} and len(s['optimizer_state_dict']['state'])==17 and end=={spec['source_Adamstep']+20*updates}
  changes={g:[n for n in before[g] if not eq(before[g][n],s[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
  go=v['experts'][key]['rows']['job0/GO_PRODUCTION.json'] if 'job0/GO_PRODUCTION.json' in v['experts'][key]['rows'] else v['owner']['rows']['COHORT_FINAL.json']['go'][key];charge=seg['experts'][key];assert charge['actual_returncode']==0 and charge['duration_bound_passed'] and charge['max_parent_seconds']==3900 and abs(charge['started_epoch']-go['learning_started_epoch'])<1e-6
  results[key]=dict(final=r,whole_tensor_counts=counts,all_model_runtime_finite=True,updates=updates,production_envsteps=480000*updates,all17Adam_before=next(iter(start)),all17Adam_after=next(iter(end)),all17_actual_changes=changes,actual_original_independent_cost_once=charge)
 assert abs(seg['charged_expert_seconds']-sum(x['charged_seconds'] for x in seg['experts'].values()))<1e-6 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_all_three_whole_final_models_CPU=True,experts=results,one_original_writer_actual_segment=seg,remaining_snapshot=c['remaining_training_seconds'],all_actual_owner_nodes_children_out_canonicalNone_real_locks_free=True,not_frozen_behavior_or_skill_qualification=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(all_three_closed_final_CPU=True,experts={k:dict(updates=x['updates'],SHA=x['final']['SHA'],Adam=x['all17Adam_after']) for k,x in results.items()},actual_cost_once=seg['charged_expert_seconds'],remaining_snapshot=out['remaining_snapshot'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_HOUR_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only_no_GPU_or_account_mutation=True),f,indent=2)
  raise
