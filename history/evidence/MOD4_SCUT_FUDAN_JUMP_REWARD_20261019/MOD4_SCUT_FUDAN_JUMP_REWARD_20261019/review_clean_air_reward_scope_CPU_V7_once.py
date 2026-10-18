from pathlib import Path
import json,time,hashlib,shutil,traceback
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import os;os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch;from types import SimpleNamespace as S
 rng=torch.get_rng_state().clone();p=B/'h1_scut_fudan_jump_reward_v1.py';shutil.copy2(p,B/'initial_prepared_sources_before_Fudan_clip_and_worker_whitespace_review/reward_before_clean_air_scope.py')
 t=p.read_text('utf8');old='airborne=(forces<=1.).all(-1)&(wc>0.).all(-1)';assert t.count(old)==1;t=t.replace(old,"airborne=p.air_ticks>0  # existing callback truth: both wheels clear, all34 clear, nonwheel clean, prior positive vz")
 t=t.replace("    active_scope=", "    flight_mask='existing H1 air_ticks>0; measured both-wheel clearance, all34 clearance, nonwheel clean and positive-vz history; no new success threshold',\n    active_scope=")
 p.write_text(t,'utf8');shutil.copy2(p,B/'reward_runtime_overlay'/p.name)
 import h1_scut_fudan_jump_reward_v1 as m
 n=4;root=torch.zeros(n,13);root[:,2]=.3;root[:,6]=1;root[:,9]=.7;pos=torch.zeros(n,2,3);pos[:,:,2]=.08
 robot=S(body_names=['left_wheel','right_wheel'],joint_names=['left_wheel_spin','right_wheel_spin'],data=S(root_state_w=root,body_pos_w=pos,applied_torque=torch.zeros(n,2),projected_gravity_b=torch.tensor([[0.,0.,-1.]]).repeat(n,1),root_ang_vel_b=torch.zeros(n,3)))
 env=S(num_envs=n,device='cpu',_sim_step_counter=4,scene={'robot':robot},_h1_scut_last_wheel_clearance=torch.full((n,2),.02),_integrated_contact=S(history=torch.zeros(n,3,2,3)),h1_phase=S(attempt=torch.ones(n,dtype=torch.bool),request_for_action=torch.tensor([True,True,False,False]),launched=torch.ones(n,dtype=torch.bool),landed=torch.zeros(n,dtype=torch.bool),air_ticks=torch.tensor([0,1,0,1])))
 v=m._current(env);assert v['flight'].tolist()==[0.,1.,0.,0.] and v['leg_tuck'][0]==0 and v['air_wheel_zero_torque'][0]==0
 # Row0 has wheel clearance but dirty/invalid original air truth: no flight bonus.
 for name,w in m.PROFILE['weights'].items():
  rate=m.measured_reward(env,name)*w;assert torch.isfinite(rate).all() and not rate[2:].any()
  if name in m.FUDAN_TERMS:assert rate.abs().max()<=2.500001
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 p=B/'prepare_next_three_closed_sources_one_hour_CPU_once.py';p.write_text(p.read_text('utf8').replace('SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json','SCUT_FUDAN_CLEAN_AIR_REWARD_FINAL_CPU_V7_ACTUAL.json'),'utf8')
 out=dict(epoch=time.time(),passed=True,formula_and_weight_clip_CPU_V4_report_SHA=H(R/'SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json'),worker_and_migration_CPU_V6_report_SHA=H(R/'SCUT_FUDAN_REWARD_MIGRATION_PROVENANCE_CPU_V6_ACTUAL.json'),new_reward_flight_mask_uses_existing_physical_air_truth_without_changing_event_threshold=True,clear_wheels_but_dirty_original_air_truth_not_rewarded=True,normal_rows_including_post_request_flight_unchanged=True,profile=m.PROFILE,overlay=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in (B/'reward_runtime_overlay').glob('*.py')],RNG_unchanged0CUDA0optimizer=True,no_new_GPU_or_training_PASS=True)
 with (R/'SCUT_FUDAN_CLEAN_AIR_REWARD_FINAL_CPU_V7_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2,ensure_ascii=False)
 print('Final clean-air reward CPU passed: wheel clearance alone cannot receive flight credit; original event truth unchanged.')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLEAN_AIR_REWARD_CPU_V7_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU=True),f,indent=2)
  raise
