from pathlib import Path
import ast,hashlib,json,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 old=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024/repair_sources/h1_step270_path_reward_v1.py'
 a=old.read_text('utf8');assert hashlib.sha256(old.read_bytes()).hexdigest()=='42a6a4bf690d474dcb2359609dfcb189df2b7aaf0ee229f74a286fcc3a9bda76'
 extra="""
def infeasible_leg_target_cost(*, raw_actions, scale, offset, lower, upper, diff_min, diff_max):
    # A reward reference only. Never replace or edit the applied action.
    # The measured delayed action term retains the original scale/default offset.
    target=raw_actions*scale+offset
    feasible=torch.maximum(torch.minimum(target,upper),lower)
    for crank,hip in ((0,1),(2,3)):
        lo=torch.maximum(lower[crank],feasible[:,hip]+diff_min)
        hi=torch.minimum(upper[crank],feasible[:,hip]+diff_max)
        feasible[:,crank]=torch.maximum(torch.minimum(feasible[:,crank],hi),lo)
    return ((target-feasible)/scale).square().mean(-1)


def airborne_leg_target_overdrive_rate(env):
    from h1_takeoff_progress_environment_v2 import tensor
    from mod4_task import CONTRACT, LEG_ORDER
    p=env.h1_phase
    term=env.action_manager.get_term('legs')
    if tuple(term._joint_names)!=tuple(LEG_ORDER):
        raise RuntimeError('Unexpected leg action order')
    raw=tensor(term.raw_actions)
    lower=raw.new_tensor([CONTRACT['joints'][n]['limits_si'][0] for n in LEG_ORDER])
    upper=raw.new_tensor([CONTRACT['joints'][n]['limits_si'][1] for n in LEG_ORDER])
    # raw_actions is AFTER the original delay line; _offset is the actual
    # default pose captured by the installed SDK JointPositionAction.
    cost=infeasible_leg_target_cost(raw_actions=raw,scale=term._scale,offset=term._offset,
        lower=lower,upper=upper,diff_min=term.diff_min,diff_max=term.diff_max)
    current_clear=(p.last_measured['step_wheel_min'][:,:,2]>.005).all(-1)
    active=p.attempt & (p.air_ticks>0) & current_clear & ~p.landed & ~p.crossed.all(-1)
    return active.to(raw.dtype)*cost


"""
 b=a.replace("version='step270_current_clearance_airborne_tuck_v4'","version='step270_airborne_feasible_target_v5'")
 b=b.replace("    leg_tuck_weight=1.7, wheel_below_base_weight=.5,","    leg_tuck_weight=1.7, wheel_below_base_weight=.5,\n    airborne_leg_target_overdrive_weight=-.05,")
 assert b.count('\ndef configure(cfg):')==1
 b=b.replace('\ndef configure(cfg):','\n'+extra+'def configure(cfg):')
 needle="    cfg._h1_step270_path_reward_recipe=dict(RECIPE)"
 insert="    cfg.rewards.h1_step270_airborne_leg_target_overdrive=RewardTermCfg(\n        func=airborne_leg_target_overdrive_rate,weight=RECIPE['airborne_leg_target_overdrive_weight'],params={})\n"
 assert b.count(needle)==1;b=b.replace(needle,insert+needle)
 def normalize(text,new):
  tree=ast.parse(text)
  if new:
   tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name not in ('infeasible_leg_target_cost','airborne_leg_target_overdrive_rate')]
   for n in ast.walk(tree):
    if isinstance(n,ast.Constant) and n.value=='step270_airborne_feasible_target_v5':n.value='step270_current_clearance_airborne_tuck_v4'
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict':n.keywords=[k for k in n.keywords if k.arg!='airborne_leg_target_overdrive_weight']
    if isinstance(n,ast.FunctionDef) and n.name=='configure':n.body=[q for q in n.body if not isinstance(q,ast.Assign) or not any(isinstance(t,ast.Attribute) and t.attr=='h1_step270_airborne_leg_target_overdrive' for t in q.targets)]
  return ast.dump(tree)
 assert normalize(a,False)==normalize(b,True)
 dest=S/'reward_candidate_V5';dest.mkdir()
 p=dest/'h1_step270_path_reward_v1.py'
 with p.open('x',encoding='utf8') as f:f.write(b)
 put('V5_AIRBORNE_TARGET_OVERDRIVE_REWARD_ONLY_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),source=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),previous_source=str(old),previous_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),all_previous_V4_reward_functions_and_config_AST_exact=True,only_new_reward_term='h1_step270_airborne_leg_target_overdrive',weight=-.05,scope='existing measured airborne tuck activation mask; delayed applied action target residual to original authored joint/CAD limits; no action projection write',PPO_loss_STD_17Adam_actor_inputs_command_mesh_physics_runtime_save_account_unchanged=True,no_skill_or_training_outcome_claim=True))
 print(json.dumps(dict(candidate_source=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),AST_passed=True,no_training_launched=True)))
except BaseException:
 put('V5_SOURCE_BUILDER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

