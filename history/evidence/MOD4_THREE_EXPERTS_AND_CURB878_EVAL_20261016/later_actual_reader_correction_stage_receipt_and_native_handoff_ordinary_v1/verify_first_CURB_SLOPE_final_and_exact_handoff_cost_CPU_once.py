"""Final model tensors and actual unique two-expert cost closure; no replay or refund."""
from pathlib import Path
import os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 x=json.loads((R/'FIRST_CURB_SLOPE_FINAL_AND_WAVE_ACTUAL_CANONICAL_HANDOFF_COLLECTION.json').read_bytes());rows=[]
 for r in x['closed_experts']:
  p=Path(r['local_path']);f=r['final'];assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0]
  def finite(v):
   if torch.is_tensor(v):count[0]+=1;count[1]+=int(v.is_floating_point());assert not v.is_floating_point() or torch.isfinite(v).all()
   elif isinstance(v,dict):
    for z in v.values():finite(z)
   elif isinstance(v,(tuple,list)):
    for z in v:finite(z)
  finite(ck);initial=642840 if f['job']==0 else 642980;assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17;assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={initial+20*f['updates']}=={f['Adam_step']};assert f['controls']==120+24*f['updates'];rows.append(dict(**f,local_path=str(p),all_model_runtime_tensors_finite=True,tensor_counts=count,original20_minibatch_Adam_increment_exact=True,physical_controls_native120_plus24_per_update_exact=True,global_PPO_env_steps=f['updates']*24*20000))
 c=x['actual_canonical'];prior=c['previous_cohort'][0];e=prior['experts'];assert set(e)=={'0','1'} and all(z['returncode']==0 for z in e.values());assert all(abs(z['ended_epoch']-z['started_epoch']-z['charged_seconds'])<1e-6 for z in e.values());assert abs(sum(z['charged_seconds'] for z in e.values())-prior['charged_expert_seconds'])<1e-6;assert c['old_owner_absent'] and c['old_CURB_worker_absent'] and c['active']['owner_parent_pid']==466300;assert abs(c['charged']+c['remaining']-1188000)<1e-5
 overruns={k:z['charged_seconds']-1800 for k,z in e.items() if z['charged_seconds']>1800};assert not torch.cuda.is_initialized();v=dict(epoch=time.time(),model_and_optimizer_CPU_passed=True,closed_models=rows,original_cohort_unique_sum_actual_cost_seconds=prior['charged_expert_seconds'],per_expert_actual_intervals=e,nominal_1800_per_expert_duration_bound_all_passed=not bool(overruns),actual_overrun_seconds_not_hidden_or_capped=overruns,overrun_reason_scope='Saved-stop is checked at completed PPO update, followed by nonpreemptible fullsave/traceflush/SDKclose; exact per-phase contribution not independently measured',next_unused_block_exit_headroom_must_be_increased_from60_before_new_dispatch=True,no_live_runtime_hotpatch_or_refund_or_recharge=True,prior_failed_WAVE2_native0PPO_charge0=True,actual_original_ledger_handoff_new_WAVE_owner466300=True,current_WAVE_not_FINAL_or_cost_settled=True,new_WAVE_first_model_local_CPU_verified_report='THREE_DISTINCT_EXPERT_FIRST_FULL_MODELS_ACTUAL_LOCAL_CPU_VERIFIED.json',no_frozen_skill_pass_inferred_from_learning=True)
 out=R/'FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(closed=[{k:r[k] for k in ('job','kind','updates','Adam_step','SHA')} for r in rows],unique_actual_distinct_cost=prior['charged_expert_seconds'],actual_overruns=overruns,new_WAVE_active=True)),flush=True)
if __name__=='__main__':main()
