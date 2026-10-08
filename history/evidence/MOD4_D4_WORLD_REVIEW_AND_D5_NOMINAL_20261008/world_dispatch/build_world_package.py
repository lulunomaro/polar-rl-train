"""Fix only the immutable frozen-world dispatcher, preserving production D4 source."""
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=E/'artifacts/d4-clock2500-solver32-physical243-initial-reviewed-frozen.zip'
assert sha(old)=='74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18'
with zipfile.ZipFile(old) as z:
    original=json.loads(z.read('SOURCE_MANIFEST.json'))
    payload={n:z.read(n) for n in original['files']}
for n,h in original['files'].items():assert hashlib.sha256(payload[n]).hexdigest()==h,n
name='runtime/isaac/mod4/frozen_history_world.py';text=payload[name].decode()
assert text.count('from feedback_delay_runtime import DelaySensorMod4Env as Mod4Env')==1
assert 'physical_action_delay_audit' not in text
old_sha=hashlib.sha256(payload[name]).hexdigest()
text=text.replace('from feedback_delay_runtime import DelaySensorMod4Env as Mod4Env','from action_delay_training_env import ActionDelayMod4Env as Mod4Env')
marker="    env.reset();cmd=env.command_manager.get_term('twist');initial_command_audit=audit(env);initial_parameters=parameter_audit(env)"
assert text.count(marker)==1
text=text.replace(marker,marker+"\n    initial_action_assignments={k:{'delay_us':(g['lag_steps']*2500).cpu().tolist(),'episode':g['episode'].cpu().tolist()} for k,g in env._physics_action_delay.queue.groups.items()}")
marker='    assert env._feedback_delay_mild.enabled and env.physics_dt==.0025'
assert text.count(marker)==1
text=text.replace(marker,marker+"\n    result['physical_action_delay_recipe']=env.action_delay_recipe()\n    result['physical_action_delay_audit']=env._physics_action_delay.audit()\n    result['physical_action_final_episode_assignments']={k:{'delay_us':(g['lag_steps']*2500).cpu().tolist(),'episode':g['episode'].cpu().tolist()} for k,g in env._physics_action_delay.queue.groups.items()}\n    result['physical_action_initial_episode_assignments']=initial_action_assignments\n    result['D4_closed_loop_actual_physical_target_delay']=True\n    result['inherited_feedback_recipe_action_delay0_is_D3_only']=True\n    assert all(v==args.steps*4 for v in env._physics_action_delay.calls.values())\n    assert result['physical_action_delay_audit']['application_formula_max_error']<=1e-6")
compile(text,name,'exec');payload[name]=text.encode()
manifest=dict(original,files={n:hashlib.sha256(v).hexdigest() for n,v in payload.items()},D4_world_actual_action_delay_dispatch_fixed=True,base_immutable_sha256=sha(old),only_one_world_dispatch_module_changed=True)
for n,h in original['files'].items():
    if n!=name:assert manifest['files'][n]==h,n
dest=E/'artifacts/d4-clock2500-solver32-world-dispatch-reviewed-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
    for n,b in payload.items():z.writestr(n,b)
    z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
v=dict(epoch=time.time(),path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size,base_sha256=sha(old),world_before_sha256=old_sha,world_after_sha256=manifest['files'][name],all_other_files_assets_clock_exact=True,production243_changed=False,old_world_case_is_D3_feedback_only_not_D4_evidence=True,old_flat_spin_D4_scope_remains_valid=True,no_new_clock_SDK_PPO_or_budget_write=True,real_corrected_world_scope_pending=True)
(R/'WORLD_DISPATCH_PACKAGE.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
