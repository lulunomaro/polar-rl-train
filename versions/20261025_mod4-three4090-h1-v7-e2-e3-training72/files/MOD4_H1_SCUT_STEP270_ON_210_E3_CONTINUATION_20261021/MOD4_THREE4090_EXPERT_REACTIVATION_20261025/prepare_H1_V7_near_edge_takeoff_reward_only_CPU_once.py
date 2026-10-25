"""Bounded H1 reward-only timing repair from saved70; keep actor35 and public commands."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import numpy as np
import torch
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports';P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025/payloads/h1';D=S/'H1_V7_reward_only_candidate';D.mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
try:
 old=(P/'h1_step270_path_reward_v1.py').read_text('utf8');new=old
 for a,b in [("version='step270_sagittal_tuck_geometry_v6a_unused'","version='step270_near_edge_takeoff_gate_v7_reward_only'"),('takeoff_gate_start_front_x_m=-.05, takeoff_gate_full_front_x_m=.15','takeoff_gate_start_front_x_m=.10, takeoff_gate_full_front_x_m=.25')]:assert new.count(a)==1;new=new.replace(a,b,1)
 with (D/'h1_step270_path_reward_v1.py').open('x',encoding='utf8') as f:f.write(new)
 checker=(P/'step270_reward_installed_CPU_v1.py').read_text('utf8')
 needle="    old={n.name:n for n in a.body if isinstance(n,ast.FunctionDef)}";assert checker.count(needle)==1
 normalization="""    recipe=next(n for n in b.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
    entries={k.arg:k for k in recipe.keywords}
    expected={'version':('step270_near_edge_takeoff_gate_v7_reward_only','step270_sagittal_tuck_geometry_v6a_unused'),'takeoff_gate_start_front_x_m':(.10,-.05),'takeoff_gate_full_front_x_m':(.25,.15)}
    for key,(actual,prior) in expected.items():
        assert ast.literal_eval(entries[key].value)==actual
        entries[key].value=ast.parse(repr(prior),mode='eval').body
"""
 checker=checker.replace(needle,normalization+needle,1)
 checker=checker.replace("assert reward.RECIPE['version']=='step270_sagittal_tuck_geometry_v6a_unused'","assert reward.RECIPE['version']=='step270_near_edge_takeoff_gate_v7_reward_only'",1)
 checker=checker.replace("assert reward.RECIPE['takeoff_gate_start_front_x_m']==-.05 and reward.RECIPE['takeoff_gate_full_front_x_m']==.15","assert reward.RECIPE['takeoff_gate_start_front_x_m']==.10 and reward.RECIPE['takeoff_gate_full_front_x_m']==.25",1)
 checker=checker.replace('single_V6A_sagittal_metric_change=True','retained_V6A_sagittal_metric_and_explicit_V7_gate_only=True',1).replace('original_release_shortfall_func_params_and_all_takeoff_timing_unchanged=True','original_release_shortfall_func_params_and_success_event_timing_unchanged=True,explicit_takeoff_reward_gate_changed_only=True',1)
 with (D/'step270_reward_installed_CPU_v1.py').open('x',encoding='utf8') as f:f.write(checker)
 torch.set_num_threads(2);mod=load(D/'step270_reward_installed_CPU_v1.py','v7_checker');result=mod.check(D,reference_path=P/'reference_sources/V5_h1_step270_path_reward_v1.py')
 reward=load(D/'h1_step270_path_reward_v1.py','v7_reward');oldreward=load(P/'h1_step270_path_reward_v1.py','v6a_reward')
 front=torch.tensor([-.05,0.,.10,.175,.25,.35]);wheel=front[:,None].repeat(1,2);origin=torch.zeros(6);vx=torch.full((6,),.8)
 gate=reward.forward_takeoff_factor(wheel_front=wheel,origin_x=origin,vx=vx);assert torch.allclose(gate,torch.tensor([0.,0.,0.,.5,1.,1.]),atol=1e-6,rtol=0)
 assert torch.equal(reward.forward_takeoff_factor(wheel_front=wheel,origin_x=origin,vx=-vx),torch.zeros(6))
 u=T/'H1_STEP270_CLOSED70_SAVED_REPLAY_AFTER_V6A_20261025';z=np.load(u/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False);kin=np.load(u/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False);des=json.loads((u/'reports/CLOSED70_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL.json').read_bytes());counter=[]
 for case in des['selected_continuous_qualified_launch_clearance_cases']:
  f=case['apex_row'];col=case['column'];front=torch.tensor(kin['wheel_max'][f,col,:,0],dtype=torch.float32)[None,:];speed=torch.tensor([float(z['root13'][f,col,7])]);zero=torch.zeros(1)
  before=float(oldreward.forward_takeoff_factor(wheel_front=front,origin_x=zero,vx=speed));after=float(reward.forward_takeoff_factor(wheel_front=front,origin_x=zero,vx=speed));counter.append(dict(env_id=case['env_id'],apex_gap_m=case['front_gap_at_apex_m'],old_push_reward_factor=before,new_push_reward_factor=after,not_new_action_or_physical_prediction=True))
 assert counter and all(x['new_push_reward_factor']==0 for x in counter)
 # Actual source AST permits only three RECIPE literals relative to qualified V6A.
 a=ast.parse(old);b=ast.parse(new);recipe=next(n for n in b.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
 restore={'version':'step270_sagittal_tuck_geometry_v6a_unused','takeoff_gate_start_front_x_m':-.05,'takeoff_gate_full_front_x_m':.15}
 for k in recipe.keywords:
  if k.arg in restore:k.value=ast.parse(repr(restore[k.arg]),mode='eval').body
 assert ast.dump(a)==ast.dump(b)
 report=dict(epoch=time.time(),passed=True,kind='H1_V7_reward_only_near_edge_takeoff_alignment_candidate',human_scope='Continue fixing H1 real step270; no actor input, command publisher, physics or success threshold change',old_start_front_x=-.05,old_full_front_x=.15,new_start_front_x=.10,new_full_front_x=.25,step_edge_x=.35,interpretation='Suppress existing upward-push reward while wheel-front is still more than.25m from edge; ramp to original full factor within.10m. Reward shaping constants only, no scripted force/action or new success gate.',source_AST_only_three_recipe_literals_changed=True,source_SHA=H(D/'h1_step270_path_reward_v1.py'),checker_SHA=H(D/'step270_reward_installed_CPU_v1.py'),source_baseline_SHA=H(P/'h1_step270_path_reward_v1.py'),CPU_integration=result,measured_saved70_kinematic_apex_counterfactual=counter,only_reward_factor_counterfactual_not_learning_or_skill_gain=True,actor35_no_edge_distance_observation_remains_limitation=True,public_commands_and_actor_STD_critic_17Adam_weights_physics_terrain_goal_unchanged=True,actual_installed_SDK_check_required_before_GO=True,no_local_policy_inference_PhysX_GPU_model_or_raw_rerun=True,no_remote_install_or_GO=True)
 with (R/'H1_V7_NEAR_EDGE_TAKEOFF_REWARD_ONLY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(passed=True,only_three_recipe_literals_changed=True,old_vs_new_gate=gate.tolist(),saved70_early_apex_cases_suppressed=len(counter),target_SDK_pending=True)))
except BaseException:
 with (R/('H1_V7_REWARD_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),old_source_not_overwritten=True,no_same_once_retry=True),f,indent=2)
 raise
