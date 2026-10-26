"""Bounded reward hypothesis from closed83B: use existing V7 distance ramp for tuck reward too."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import numpy as np
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';R.mkdir(exist_ok=True);N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026';B=N/'payloads/h1';C=M/'candidate_v1';C.mkdir()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 reward=(B/'h1_step270_path_reward_v1.py').read_text('utf8');assert reward.count("version='step270_sampled_leg_excess_v8_reward_only'")==1
 reward=reward.replace("version='step270_sampled_leg_excess_v8_reward_only'","version='step270_near_edge_tuck_alignment_v10_reward_only'",1)
 old='    return active.to(root.dtype)*compact'
 new="""    front=p.previous_front.amin(-1)-env.scene.env_origins[:,0]
    near=((front-RECIPE['takeoff_gate_start_front_x_m'])/(RECIPE['takeoff_gate_full_front_x_m']-RECIPE['takeoff_gate_start_front_x_m'])).clamp(0.,1.)
    return active.to(root.dtype)*compact*near"""
 assert reward.count(old)==1;reward=reward.replace(old,new,1);(C/'h1_step270_path_reward_v1.py').write_text(reward,'utf8')
 checker=(B/'step270_reward_installed_CPU_v1.py').read_text('utf8')
 normalize='''def normalize_V10_reward_AST(tree):
    recipe=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
    entries={k.arg:k for k in recipe.keywords};assert ast.literal_eval(entries['version'].value)=='step270_near_edge_tuck_alignment_v10_reward_only';entries['version'].value=ast.Constant('step270_sampled_leg_excess_v8_reward_only')
    func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='airborne_tuck_rate')
    expected=ast.parse("front=p.previous_front.amin(-1)-env.scene.env_origins[:,0]\\nnear=((front-RECIPE['takeoff_gate_start_front_x_m'])/(RECIPE['takeoff_gate_full_front_x_m']-RECIPE['takeoff_gate_start_front_x_m'])).clamp(0.,1.)\\nreturn active.to(root.dtype)*compact*near").body
    assert [ast.dump(x) for x in func.body[-3:]]==[ast.dump(x) for x in expected]
    func.body[-3:]=ast.parse('return active.to(root.dtype)*compact').body
    return tree

def check_V10_tuck_CPU(reward):
    n=20000;front=torch.linspace(-.10,.40,n);root=torch.zeros(n,13);root[:,6]=1.;body=torch.zeros(n,3,3);body[:,1:]=torch.tensor([[[0.,.2188,-.22],[0.,-.2188,-.22]]])
    p=types.SimpleNamespace(attempt=torch.ones(n,dtype=torch.bool),air_ticks=torch.ones(n,dtype=torch.long),landed=torch.zeros(n,dtype=torch.bool),crossed=torch.zeros(n,2,dtype=torch.bool),previous_front=front[:,None].expand(n,2).clone(),last_measured={'step_wheel_min':torch.ones(n,2,3)*.02})
    robot=types.SimpleNamespace(body_names=['chassis','left_wheel','right_wheel'],data=types.SimpleNamespace(root_state_w=root,body_pos_w=body));scene=type('Scene',(dict,),{})({'robot':robot});scene.env_origins=torch.zeros(n,3);env=types.SimpleNamespace(h1_phase=p,scene=scene,num_envs=n)
    snapshots=(root.clone(),body.clone(),p.previous_front.clone());actual=reward.airborne_tuck_rate(env);expected=((front-.10)/(.25-.10)).clamp(0.,1.)
    assert torch.allclose(actual,expected,atol=2e-6,rtol=0) and torch.isfinite(actual).all()
    assert all(torch.equal(a,b) for a,b in zip(snapshots,(root,body,p.previous_front)))
    return dict(passed=True,synthetic_float32_environments=n,existing_V7_gate_start=.10,existing_V7_gate_full=.25,far_zero_near_ramp_and_full_original_tuck=True,target_and_weight_unchanged=True,no_action_or_original_state_mutation=True)

'''
 needle='def allowlist(candidate,reference):';assert checker.count(needle)==1;checker=checker.replace(needle,normalize+needle,1)
 needle='    b=normalize_V8_reward_AST(b)';assert checker.count(needle)==1;checker=checker.replace(needle,'    b=normalize_V10_reward_AST(b)\n'+needle,1)
 needle="assert reward.RECIPE['version']=='step270_sampled_leg_excess_v8_reward_only'";assert checker.count(needle)==1;checker=checker.replace(needle,"assert reward.RECIPE['version']=='step270_near_edge_tuck_alignment_v10_reward_only'",1)
 needle="    env=types.SimpleNamespace(h1_phase=p,scene={'robot':robot},num_envs=m)";assert checker.count(needle)==1
 checker=checker.replace(needle,"    scene=type('Scene',(dict,),{})({'robot':robot});scene.env_origins=torch.zeros(m,3);p.previous_front=torch.full((m,2),.25)\n    env=types.SimpleNamespace(h1_phase=p,scene=scene,num_envs=m)",1)
 needle='        original_release_func=lambda env:torch.zeros(env.num_envs)';assert checker.count(needle)==1;checker=checker.replace(needle,'        V10_CPU=check_V10_tuck_CPU(reward)\n'+needle,1)
 needle="            term=cfg.rewards.h1_scut_fudan_leg_tuck";assert checker.count(needle)==1
 checker=checker.replace(needle,"            p.previous_front=torch.linspace(-.05,.40,m)[:,None].expand(m,2).clone();expected=expected*((p.previous_front.amin(-1)-.10)/(.25-.10)).clamp(0.,1.)\n"+needle,1)
 needle='    return dict(passed=True,retained_V6A';assert checker.count(needle)==1;checker=checker.replace(needle,'    return dict(passed=True,V10_near_edge_tuck_CPU=V10_CPU,actual_installed_V10_tuck_SDK_compute_tested=sdk_reward_path is not None and not allow_local_fixture,retained_V6A',1)
 ast.parse(checker);(C/'step270_reward_installed_CPU_v1.py').write_text(checker,'utf8')
 # Preserve exact reference bytes; the actual next payload must re-run the SDK branch.
 (C/'reference_sources').mkdir();(C/'reference_sources/V5_h1_step270_path_reward_v1.py').write_bytes((B/'reference_sources/V5_h1_step270_path_reward_v1.py').read_bytes())
 sp=importlib.util.spec_from_file_location('new_V10_reward_source_CPU',C/'step270_reward_installed_CPU_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);answer=m.check(C,reference_path=C/'reference_sources/V5_h1_step270_path_reward_v1.py')
 U=T/'H1_STEP270_CLOSED83B_SAVED_REPLAY_AFTER_V8_20261026';source=json.loads((U/'reports/CLOSED83B_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes());terms=source['reward_terms']
 with np.load(U/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
  front=k['wheel_max'][...,0].min(-1);gate=np.clip((front-.10)/(.25-.10),0,1);paid=z['reward_term_contribution'][...,terms.index('h1_scut_fudan_leg_tuck')];continuous=np.broadcast_to(z['continuous_no_reset'],paid.shape);active=continuous&(paid>0)
  counterfactual=dict(selected_continuous_paid_frames=int(active.sum()),paid_frames_with_reconstructed_front_before_gate=int((active&(front<=.10)).sum()),selected_recorded_tuck_sum=float(paid[continuous].sum()),candidate_counterfactual_tuck_sum=float((paid*gate)[continuous].sum()),only_selected_kinematic_counterfactual_not_original_callback_or_learning_gain=True)
 put('V10_NEAR_EDGE_TUCK_SOURCE_CPU_AND_SELECTED83B_COUNTERFACTUAL_ACTUAL.json',dict(epoch=time.time(),candidate_only_not_installed=True,base_reward_SHA=hashlib.sha256((B/'h1_step270_path_reward_v1.py').read_bytes()).hexdigest(),candidate_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in C.glob('*.py')},changes=['recipe version','multiply existing airborne sagittal tuck reward by unchanged V7 measured front .10 to .25 distance ramp'],same_target_22_weight1_7_V8_cost_and_all_other_reward_AST=True,CPU=answer,selected_counterfactual=counterfactual,no_actual_target_SDK_GPU_learning_or_convergence_claim=True,no_Fudan_reference_input_dataset_rollout_or_model_deployment=True,not_proven_single_rootcause_or_skill_gain=True))
 print(json.dumps(dict(candidate_CPU=True,counterfactual=counterfactual,actual_target_SDK_pending=True)))
except BaseException:
 put('V10_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),not_training_error=True,no_same_once_replay=True));raise
