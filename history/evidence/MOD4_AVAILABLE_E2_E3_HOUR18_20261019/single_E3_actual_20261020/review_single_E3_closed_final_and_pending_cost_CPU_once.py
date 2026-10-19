"""Prepared only: full final CPU and actual pending interval; never canonical settlement."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((R/'SINGLE_E3_CLOSED_FINAL_AND_PENDING_COST_COLLECTION_ACTUAL.json').read_bytes());d=json.loads((R/'APPROVED_SINGLE_E3_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());assert v['actual_closed'] and v['model'] and v['original_canonical_settled'] is False;r=v['model'];p=Path(r['local_path']);assert H(p)==r['SHA'] and p.stat().st_size==r['bytes'];s=torch.load(p,map_location='cpu',weights_only=False);spec=d['specs']['recovery'];src=Path(d['payloads']['recovery'])/'job0/source'/spec['source_filename'];assert H(src)==spec['source_SHA'];old=torch.load(src,map_location='cpu',weights_only=False);counts=[0,0];tensors(s,counts);updates=s['E3_production_updates'];assert s['E3_phase']=='production' and updates>0 and not s.get('failed_partial_prefix',False)
 start={int(x['step']) for x in old['optimizer_state_dict']['state'].values()};end={int(x['step']) for x in s['optimizer_state_dict']['state'].values()};assert len(old['optimizer_state_dict']['state'])==len(s['optimizer_state_dict']['state'])==17 and start=={spec['source_Adamstep']} and end=={spec['source_Adamstep']+20*updates};changes={g:[n for n in old[g] if not eq(old[g][n],s[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 co=v['actual']['owner']['rows']['COHORT_FINAL.json'];go=co['go']['recovery'];cost=co['pending_cost']['cost'];assert cost['actual_returncode']==0 and cost['duration_bound_passed'] and abs(cost['started_epoch']-go['learning_started_epoch'])<1e-6 and abs(cost['actual_production_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5;assert co['original_cost_settled'] is False and not co['pending_cost']['canonical_settled'];assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed=True,final=r,source_SHA=spec['source_SHA'],updates=updates,whole_tensor_counts=counts,all_model_runtime_finite=True,all17Adam_before=next(iter(start)),all17Adam_after=next(iter(end)),all17_changes=changes,pending_cost=co['pending_cost'],original_canonical_settled=False,no_automatic_second_window=True,no_original_canonical_copy_write_or_reconciliation=True,CPU_RNG_unchanged_0CUDA_0optimizer=True,not_frozen_skill_PASS=True)
 with (R/'SINGLE_E3_CLOSED_FINAL_WHOLE_MODEL_AND_PENDING_COST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(whole_final_CPU_passed=True,updates=updates,Adam=next(iter(end)),actual_pending_seconds=cost['actual_production_seconds'],original_canonical_settled=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SINGLE_E3_CLOSED_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_canonical_write=True),f,indent=2)
  raise
