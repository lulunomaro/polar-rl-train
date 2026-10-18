from pathlib import Path
import sys,json,hashlib,ast,time,shutil,traceback,types
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 import os;os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch;torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 import h1_scut_fudan_jump_reward_v1 as m
 refs=W/'MOD4_LOCAL_MUJOCO_DRIVE_MOE_CORRECTION_20261018/reference_source_snapshots';snapshot=B/'reference_source_snapshots';snapshot.mkdir()
 for name in ('scut_jump_takeoff.py','scut_airborne.py','scut_V14_cfg.py','fudan_jump_robot.py','fudan_jump_config.py'):
  shutil.copy2(refs/name,snapshot/name)
 # Execute the actual selected upstream functions, without importing its SDK/robot.
 def method(path,cls,name):
  tree=ast.parse(path.read_text('utf8'));c=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==cls);f=next(x for x in c.body if isinstance(x,ast.FunctionDef) and x.name==name);ns={'torch':torch};exec(compile(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])),str(path),'exec'),ns);return ns[name]
 jt=method(snapshot/'scut_jump_takeoff.py','JumpTakeoffStateMachine','apply_reward_term_scales')
 ab=method(snapshot/'scut_airborne.py','AirborneStateMachine','apply_reward_term_scales')
 fr={n:method(snapshot/'fudan_jump_robot.py','LeggedRobot','_reward_'+n) for n in ('line_z','leg_tuck','takeoff_extend','flight','orientation','ang_vel_xy')}
 # Physical counterfactual fixtures include idle, push up/down, flight, touchdown,
 # short/extended legs, tilted body, wheel torque and actual body-rate spikes.
 n=12;active=torch.tensor([0,1,1,1,1,1,1,1,1,1,0,0],dtype=torch.bool);air=torch.tensor([0,0,0,1,1,1,0,1,1,1,1,0],dtype=torch.bool);support=~air
 vz=torch.tensor([0.,.7,-.4,.7,-.3,0.,.7,1.,.7,.7,1.,-2.]);legs=torch.tensor([[.22,.22],[.31,.31],[.31,.31],[.22,.22],[.31,.31],[.22,.22],[.22,.22],[.22,.22],[.22,.22],[.22,.22],[.31,.31],[.22,.22]])
 z=torch.full((n,2),-.22);torque=torch.zeros(n,2);torque[8]=3.;pg=torch.zeros(n,3);pg[:,2]=-1.;pg[9,0]=.5;av=torch.zeros(n,3);av[7,1]=5.
 inputs=dict(active=active,airborne=air,supported=support,vz=vz,leg_lengths=legs,wheel_bottom_relative_z=z,wheel_torque=torque,projected_gravity=pg,angular_velocity_body=av);out=m.terms(**inputs)
 S=types.SimpleNamespace;root=torch.zeros(n,13);root[:,9]=vz;root[:,2]=.3;phase=torch.where(active,torch.where(air,2,1),0)
 e=S(num_envs=n,device='cpu',step_dt=.01,jump_takeoff_phase=phase,jump_takeoff_prev_vel_z=vz.clone(),robot=S(data=S(root_lin_vel_w=root[:,7:10],root_pos_w=root[:,:3],body_pos_w=torch.zeros(n,2,3),applied_torque=torque)),_wheel_link_idx=[0,1],_wheel_idx=[0,1],height_reward_airborne_state=active&air)
 e.robot.data.body_pos_w[:,:,2]=root[:,None,2]+z+.06
 e._get_root_quat_inv_and_wheel_pos_b=lambda:(None,None,torch.stack((torch.zeros_like(legs),torch.zeros_like(legs),-legs),dim=-1),None,None)
 cfg={'push':{'reward_additions':{'push_vz':{'type':'takeoff_vel_z'}}},'tuck':{'reward_additions':{'wheel_below_base':{'type':'wheel_height_below_base_exp','target':.22,'sigma':.01}}}}
 j=S(PHASE_IDLE=0,PHASE_PUSH=1,PHASE_TUCK=2,_cfg=lambda env:cfg,_get_reward_addition_mask=lambda env,cfg,a,mask:mask,_get_wheel_radius=lambda env:.06)
 original=jt(j,e,{})
 # Original PUSH has no contact gate: compare only the explicit MOD4 supported mask.
 assert torch.equal(out['push_vz'],original['push_vz']*support.float())
 assert torch.allclose(out['wheel_below_base'],original['wheel_below_base'],atol=2e-6,rtol=0)
 acfg={'reward_additions':{'air_wheel_zero_torque':{'type':'wheel_zero_torque_exp','sigma':1.5}}};e.cfg=S(rewards={'air_wheel_zero_torque':20.})
 a=S(_cfg=lambda env:acfg,_get_reward_window_mask=lambda env,cfg:env.height_reward_airborne_state)
 assert torch.equal(out['air_wheel_zero_torque'],ab(a,e,{})['air_wheel_zero_torque'])
 # Fudan exact targets .16 / .31 are checked first; MOD4 tuck target .22 is an explicit geometry adaptation.
 f=S(root_states=root,was_in_flight=active&air,L0=legs,contact_filt=(active&~air&support)[:,None].expand(-1,2),projected_gravity=pg,base_ang_vel=av)
 assert torch.equal(out['flight_vz'],fr['line_z'](f)) and torch.equal(out['flight'],fr['flight'](f).float())
 assert torch.equal(out['takeoff_extend'],fr['takeoff_extend'](f))
 f.L0=legs+(.16-.22);assert torch.allclose(out['leg_tuck'],fr['leg_tuck'](f),atol=1e-6,rtol=0)
 assert torch.equal(out['orientation'],fr['orientation'](f)*active.float()) and torch.equal(out['angular_velocity_xy'],fr['ang_vel_xy'](f)*active.float())
 assert all(torch.isfinite(v).all() and v.shape==(n,) and not v[~active].any() for v in out.values())
 assert out['takeoff_extend'][1]>out['takeoff_extend'][6] and out['leg_tuck'][3]>out['leg_tuck'][4] and out['air_wheel_zero_torque'][3]>out['air_wheel_zero_torque'][8]
 assert out['angular_velocity_xy'][7]>out['angular_velocity_xy'][3] and out['orientation'][9]>out['orientation'][3]
 # Normal-row old costs remain bit exact, including nonzero old function values.
 env=S(h1_phase=S(attempt=active,request_for_action=active,launched=torch.zeros_like(active),landed=torch.zeros_like(active)))
 old=lambda env,offset:torch.arange(n,dtype=torch.float32)+offset
 masked=m.mask_replaced_jump_cost(env,old,{'offset':.123});assert torch.equal(masked[~active],old(env,.123)[~active]) and not masked[active].any()
 oldroot=W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018/payload/h1/job0/runtime/isaac/mod4';overlay=B/'reward_runtime_overlay';overlay.mkdir()
 p=oldroot/'train_H1_ground_prelaunch_fullstate_v2.py';t=p.read_text('utf8');s='from h1_takeoff_progress_reward_v2 import configure as configure_h1_rewards';assert t.count(s)==1;(overlay/p.name).write_text(t.replace(s,'from h1_scut_fudan_jump_reward_v1 import configure as configure_h1_rewards'),'utf8')
 p=oldroot/'h1_takeoff_progress_environment_v2.py';t=p.read_text('utf8');s='self.h1_callback_count+=1';assert t.count(s)==1;(overlay/p.name).write_text(t.replace(s,'self._h1_scut_last_wheel_clearance=wc;'+s),'utf8');shutil.copy2(B/'h1_scut_fudan_jump_reward_v1.py',overlay/'h1_scut_fudan_jump_reward_v1.py')
 for p in overlay.glob('*.py'):ast.parse(p.read_text('utf8'))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('SCUT_FUDAN_JUMP_REWARD_SOURCE_DIFFERENTIAL_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,fixture_rows=n,original_upstream_functions_executed=list(fr)+['SCUT.apply_reward_term_scales.jump','SCUT.apply_reward_term_scales.airborne'],normal_old_cost_bitexact=True,source_weight_attribution={'SCUT_airborne_zero_torque':20.,'Fudan_flight':.15,'Fudan_line_z':6.,'Fudan_tuck':1.7,'Fudan_takeoff_extend':.5,'Fudan_orientation':-25.,'Fudan_ang_vel_xy':-.1,'MOD4_push_vz':1.,'MOD4_wheel_below_base':2.},explicit_adaptations=['Fudan L0 .16 -> MOD4 3D body-wheel .22; SCUT default target','Fudan fixed .65 root height omitted because robot/map dimensions differ','SCUT phase determined by existing H1 public request, measured contact/clearance; no extra actor state','old orientation/legacy rate terms replaced only on active jump rows','original H1 event/progress rewards retained'],profile=m.PROFILE,overlay=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in overlay.glob('*.py')],source_index=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in snapshot.glob('*.py')],RNG_unchanged=True,CUDA_initialized=False,optimizer_steps=0,not_GPU_training_or_skill_PASS=True))
 print(json.dumps(dict(reward_CPU_passed=True,fixtures=n,terms=list(out))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('REWARD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_account_change=True));raise
