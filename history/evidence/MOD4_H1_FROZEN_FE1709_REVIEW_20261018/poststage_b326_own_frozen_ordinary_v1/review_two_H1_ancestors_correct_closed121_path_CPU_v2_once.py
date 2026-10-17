"""Read existing ancestors on recorded inputs; no robot replay or policy change."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017'
sys.path.insert(0,str(B/'h1_b326_linux4090_v7/payload'))
from h1_frozen_mean35_exact_v1 import FrozenMean35

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 j=json.loads((R/'LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());row=next(r for r in j['files'] if r['relative'].endswith('/retention_full_control_substep_actual.npz'));assert row['twohost_complete_SHA']
 assert json.loads((R/'H1_B326_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes())['passed_complete_data_and_source_CPU']
 with np.load(row['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy()
 base=torch.from_numpy(obs.reshape(-1,35));request=obs[...,32].reshape(-1)>0;assert request.sum()==1600
 sources=[('H1_OLD_CLOSED121',B.parent/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017/actual_window_v2_closed_finals/h1/model_update121.pt','3f7feb09c0034d0d902526c2f03a36e84db37d3d93b68b380a2ed844eb063a75',643700),('M_CLOSED24',M/'actual_closed24_and_native_models/h1/model_update24.pt','c5f1f7a6d8eb4a05a2301e116d3c75ce496c61f73f4e0a283dfe6bfb87de5a51',644180)]
 rows=[]
 for label,p,sha,adam in sources:
  assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
  ck=torch.load(p,map_location='cpu',weights_only=False);assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
  assert len(ck['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={adam}
  model=FrozenMean35(ck['actor_state_dict']);before=model.snapshot();mu=model(base).numpy();assert np.isfinite(mu).all()
  assert all(torch.equal(v,model.snapshot()[k]) for k,v in before.items())
  rows.append(dict(label=label,path=str(p),SHA=sha,Adam=adam,actor9_STD_critic8_optimizer17_source_identity_checked=True,stored_STD_parameter0=float(ck['actor_state_dict']['distribution.std_param'][0]),actual_public4_raw_action0_min_median_max=[float(mu[request,0].min()),float(np.median(mu[request,0])),float(mu[request,0].max())],actual_public4_clipped_action0_values=np.unique(np.clip(mu[request,0],-6,6)).tolist(),actual_public4_left_crank_negative_saturation_fraction=float((mu[request,0]<=-6).mean()),all_actor9_STD_initial_final_literalexact=True))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_existing_ancestor_conditional_source_CPU=True,source_rows=rows,recorded_input_source='B326 own native120 actual9600x35',recorded_raw_path=row['path'],recorded_raw_SHA=row['SHA'],same_actual_public4_observation_count=int(request.sum()),no_old_GPU_Task_native_or_remote_model_raw_replay=True,no_closed_loop_ancestor_skill_or_unique_cause_proof=True,not_all_earlier_ancestry_examined=True,no_STDs_rewards_guards_or_checkpoint_change=True,RNG_unchanged0CUDA0optimizer=True)
 with (R/'H1_OLD121_M24_SAME_B326_OBSERVATIONS_ANCESTOR_LEFT_CRANK_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(ancestor_CPU=True,rows=rows)),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_ANCESTOR_CONDITIONAL_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_policy_change=True),f,indent=2)
  raise
