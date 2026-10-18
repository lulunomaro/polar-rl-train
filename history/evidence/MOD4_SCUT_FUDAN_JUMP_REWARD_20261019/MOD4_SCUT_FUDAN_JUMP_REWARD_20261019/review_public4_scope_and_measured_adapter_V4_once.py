from pathlib import Path
import json,time,hashlib,shutil,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import os;os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch;from types import SimpleNamespace as S
 rng=torch.get_rng_state().clone();p=B/'h1_scut_fudan_jump_reward_v1.py';shutil.copy2(p,B/'initial_prepared_sources_before_Fudan_clip_and_worker_whitespace_review/reward_before_public4_only_scope.py')
 t=p.read_text('utf8');assert t.count('p.attempt & (p.request_for_action | (p.launched & ~p.landed))')==2;t=t.replace('p.attempt & (p.request_for_action | (p.launched & ~p.landed))','p.attempt & p.request_for_action');t=t.replace("    no_assist_force_or_air_reset_or_privileged_actor_observation=True,","    no_assist_force_or_air_reset_or_privileged_actor_observation=True,\n    active_scope='H1 public4 request rows with an actual ready attempt; every normal action row retains its original reward',")
 p.write_text(t,'utf8');shutil.copy2(p,B/'reward_runtime_overlay'/p.name)
 import h1_scut_fudan_jump_reward_v1 as m
 n=4;active=torch.tensor([True,True,False,False]);air=torch.tensor([False,True,True,False]);root=torch.zeros(n,13);root[:,2]=.3;root[:,6]=1.;root[:,9]=torch.tensor([.7,.5,-.2,0.]);pos=torch.zeros(n,2,3);pos[:,:,2]=.08;pos[:,0,1]=.08;pos[:,1,1]=-.08;force=torch.zeros(n,3,2,3);force[~air,0,:,2]=10.;wc=torch.where(air[:,None],torch.full((n,2),.02),torch.zeros(n,2));pg=torch.tensor([[0.,0.,-1.]]).repeat(n,1);av=torch.zeros(n,3)
 robot=S(body_names=['left_wheel','right_wheel'],joint_names=['left_wheel_spin','right_wheel_spin'],data=S(root_state_w=root,body_pos_w=pos,applied_torque=torch.zeros(n,2),projected_gravity_b=pg,root_ang_vel_b=av))
 env=S(num_envs=n,device='cpu',_sim_step_counter=4,scene={'robot':robot},_h1_scut_last_wheel_clearance=wc,_integrated_contact=S(history=force),h1_phase=S(attempt=torch.ones(n,dtype=torch.bool),request_for_action=active,launched=air,landed=torch.zeros(n,dtype=torch.bool)))
 v=m._current(env);assert v['flight'][1]==1 and v['push_vz'][0]>.6 and all(not x[~active].any() for x in v.values())
 # Flight after the public4 window has ended remains a NORMAL row, not a new reward exception.
 old=lambda env:torch.arange(n,dtype=torch.float32)+.123
 masked=m.mask_replaced_jump_cost(env,old,{})
 assert torch.equal(masked[~active],old(env)[~active])
 for name,w in m.PROFILE['weights'].items():
  a=m.measured_reward(env,name)*w;assert torch.isfinite(a).all() and not a[~active].any()
  if name in m.FUDAN_TERMS:assert a.abs().max()<=2.500001
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 p=B/'prepare_next_three_closed_sources_one_hour_CPU_once.py';p.write_text(p.read_text('utf8').replace('SCUT_FUDAN_FUDAN_CLIP_WORKER_RUNTIME_CPU_V3_ACTUAL.json','SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json'),'utf8')
 report=dict(epoch=time.time(),passed=True,upstream_formula_differential_CPU_report_SHA=H(R/'SCUT_FUDAN_JUMP_REWARD_SOURCE_DIFFERENTIAL_CPU_ACTUAL.json'),Fudan_clip_worker_AST_config_CPU_V3_report_SHA=H(R/'SCUT_FUDAN_FUDAN_CLIP_WORKER_RUNTIME_CPU_V3_ACTUAL.json'),measured_adapter_fields_executed=True,actual_joint_names_from_current_mod4_task=['left_wheel_spin','right_wheel_spin'],normal_action_rows_including_after_flight_public_window_byteexact=True,no_new_actor_input_or_RNG_or_optimizer=True,profile=m.PROFILE,overlay=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in (B/'reward_runtime_overlay').glob('*.py')],not_GPU_or_skill_PASS=True)
 with (R/'SCUT_FUDAN_PUBLIC4_MEASURED_RUNTIME_CPU_V4_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
 print('Final public4-only reward adapter CPU passed; normal rows, including post-request flight, unchanged.')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('REWARD_PUBLIC4_CPU_V4_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU=True),f,indent=2)
  raise
