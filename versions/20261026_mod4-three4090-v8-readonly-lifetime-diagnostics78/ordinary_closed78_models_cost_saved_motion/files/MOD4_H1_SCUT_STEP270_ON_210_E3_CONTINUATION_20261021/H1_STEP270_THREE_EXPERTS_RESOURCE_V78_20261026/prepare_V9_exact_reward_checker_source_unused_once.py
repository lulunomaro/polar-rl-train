"""Source-only SDK-checker preparation for the uninstalled V9 reward math hypothesis."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026'
p=N/'payloads/h1/step270_reward_installed_CPU_v1.py';old=p.read_text('utf8');s=old
helper='''def normalize_V9_reward_AST(tree):
    recipe=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
    version=next(k for k in recipe.keywords if k.arg=='version')
    assert ast.literal_eval(version.value)=='step270_full_path_clearance_carry_v9_reward_only'
    version.value=ast.Constant('step270_sampled_leg_excess_v8_reward_only')
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='path_increment')
    joint=next(n for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='joint' for t in n.targets))
    assert ast.dump(joint)==ast.dump(ast.parse("joint=((current-.10)/(RECIPE['path_target_x_m']-.10)).clamp(0.,1.)*clearance.square()").body[0])
    joint.value=ast.parse('((current-.10)/.25).clamp(0.,1.)*clearance.square()',mode='eval').body
    return tree

def check_V9_carry_actual_SDK_compute(reward,env,compute,term):
    n=env.num_envs;yes=torch.ones(n,dtype=torch.bool);no=~yes;front=torch.full((n,2),.35);target=torch.full((n,2),.60);bottom=torch.full((n,2),.27)
    value=reward.path_increment(previous_front=front,current_front=target,wheel_bottom=bottom,origin_x=torch.zeros(n),active=yes,airborne=yes,launched=yes,clean_upright=yes,vx=torch.full((n,),.8),takeoff=no,edge_event=no,landing=no,recovery=no,previous_joint_potential=torch.full((n,),.5))
    assert torch.equal(value['clearance_transport'],torch.full((n,),4.))
    previous=getattr(env.h1_phase,'progress_control',None);dt=getattr(env,'step_dt',None)
    try:
        env.h1_phase.progress_control=value['total'];env.step_dt=.01
        assert term.func is reward.measured_rate and term.params=={'name':'path_progress'} and term.weight==1.
        rm=types.SimpleNamespace(_env=env,_term_names=['path_progress'],_term_cfgs=[term],_reward_buf=torch.zeros(n),_step_reward=torch.zeros(n,1),_episode_sums={'path_progress':torch.zeros(n)})
        out=compute(rm,.01);assert torch.allclose(out,value['total'],atol=1e-6,rtol=1e-6)
        return dict(passed=True,synthetic_existing_path_target=.60,clearance_transport_increment4=True,actual_SDK_term_rewards=out.tolist(),not_learning_or_runtime_motion=True)
    finally:
        if previous is None:del env.h1_phase.progress_control
        else:env.h1_phase.progress_control=previous
        if dt is None:del env.step_dt
        else:env.step_dt=dt

'''
assert s.count('def normalize_V8_reward_AST(tree):')==1;s=s.replace('def normalize_V8_reward_AST(tree):',helper+'def normalize_V8_reward_AST(tree):',1)
assert s.count('    b=normalize_V8_reward_AST(b)')==1;s=s.replace('    b=normalize_V8_reward_AST(b)','    b=normalize_V8_reward_AST(normalize_V9_reward_AST(b))',1)
needle="    assert reward.RECIPE['version']=='step270_sampled_leg_excess_v8_reward_only' and reward.RECIPE['sampled_leg_action_excess_weight']==-.001";assert s.count(needle)==1;s=s.replace(needle,needle.replace('step270_sampled_leg_excess_v8_reward_only','step270_full_path_clearance_carry_v9_reward_only'),1)
s=s.replace('sdk_sha=None;out=None;excess_SDK=None','sdk_sha=None;out=None;excess_SDK=None;carry_SDK=None',1)
needle="            excess_SDK=check_V8_actual_SDK_compute(reward,env,ns['compute'],cfg.rewards.h1_step270_sampled_leg_action_excess)";assert s.count(needle)==1;s=s.replace(needle,needle+"\n            carry_SDK=check_V9_carry_actual_SDK_compute(reward,env,ns['compute'],cfg.rewards.h1_step270_path_progress)",1)
s=s.replace('retained_V6A_sagittal_metric_and_explicit_V7_gate_with_V8_excess_only=True','retained_V6A_V7_V8_with_explicit_V9_carry_math=True',1)
needle='        sampled_excess_CPU=excess_CPU,sampled_excess_SDK=excess_SDK,';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        full_path_clearance_carry_SDK=carry_SDK,actual_installed_V9_carry_SDK_compute_tested=carry_SDK is not None and not allow_local_fixture,',1)
ast.parse(s);out=M/'candidate_v1/step270_reward_installed_CPU_v1.py'
with out.open('x',encoding='utf8',newline='\n') as f:f.write(s)
with (M/'reference_sources/actual78_V8_reward_checker.original_bytes.txt').open('xb') as f:f.write(p.read_bytes())
with (M/'reports/V9_EXACT_CHECKER_SOURCE_PREPARED_NOT_INSTALLED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,candidate=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest(),old_V8_checks_retained_after_exact_two_AST_normalization=True,no_current78_or_future79_mutation=True,no_actual_target_SDK_or_deployment_claim=True),f,indent=2)
print(json.dumps(dict(V9_checker_source_only=True)))
