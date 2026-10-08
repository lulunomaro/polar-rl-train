"""Generate new D5 entries; original D4 source is left byte-for-byte intact."""
from pathlib import Path
import ast,json,shutil
D=Path(__file__).resolve().parent;W=D.parent;C=D/'isaac/mod4';R=D/'reports';R.mkdir(exist_ok=True)
assert not (R/'LOCAL_FULL_CONTRACT_BUILT.json').exists()
old=W/'MOD4_D4_FULL_CONTRACT_20261008';prep=W/'MOD4_D5_SPRING_LAW_PREPARE_20261008'
for name in ('spring_pressure_component.py','spring_pressure_index_runtime.py','spring_pressure_audit_runtime.py','spring_nominal_sdk_readback.py'):
    shutil.copyfile(prep/name,C/name)
for kind in ('resume','fresh_preflight'):
    source=(old/'isaac/mod4'/f'train_action_{kind}_ppo.py').read_text(encoding='utf8')
    before='from action_delay_training_env import ActionDelayMod4Env as Mod4Env'
    assert source.count(before)==1;source=source.replace(before,'from spring_pressure_training_env import SpringPressureMod4Env as Mod4Env')
    if kind=='resume':
        source=source.replace('from action_delay_checkpoint import resume_action_new_episode','from spring_pressure_checkpoint import resume_spring_new_episode').replace('resume_action_new_episode(runner,env,args.init_checkpoint,log_dir)','resume_spring_new_episode(runner,env,args.init_checkpoint,log_dir)')
    source=source.replace('from action_delay_checkpoint import install_action_save_contract','from spring_pressure_checkpoint import install_spring_save_contract').replace('install_action_save_contract(runner,env)','install_spring_save_contract(runner,env)')
    anchor='    manifest["src_sha256"] = snapshot';assert source.count(anchor)==1
    extra='''    manifest["spring_pressure_recipe"]=env.spring_pressure_recipe()
    for name in ("spring_pressure_component.py","spring_pressure_index_runtime.py","spring_pressure_audit_runtime.py","spring_nominal_sdk_readback.py","spring_pressure_training_env.py","spring_pressure_checkpoint.py","train_spring_'''+kind+'''_ppo.py"):
        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)
'''
    source=source.replace(anchor,extra+anchor);ast.parse(source)
    (C/f'train_spring_{kind}_ppo.py').write_text(source,encoding='utf8')
native=(old/'native_d4_physical_probe.py').read_text(encoding='utf8')
native=native.replace('from action_delay_training_env import ActionDelayMod4Env as Mod4Env','from spring_pressure_training_env import SpringPressureMod4Env as Mod4Env')
anchor=" report['final_root_state']=";assert native.count(anchor)==1
native=native.replace(anchor," report['spring_pressure_recipe']=env.spring_pressure_recipe();report['spring_pressure_audit']=env._spring_pressure.audit()\n"+anchor)
ast.parse(native);(D/'native_d5_spring_probe.py').write_text(native,encoding='utf8')
source=(old/'supervise_d4_full_contract.py').read_text(encoding='utf8').replace('D4','D5').replace('d4','d5')
source=source.replace("OLD=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008')","OLD=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008')")
source=source.replace("from action_delay_physics_queue import PhysicsActionQueue","from action_delay_physics_queue import PhysicsActionQueue\nfrom spring_pressure_checkpoint import validate_saved_pressure")
source=source.replace("    return e\n","    e['RM_SPRING_PRESSURE_PROFILE']='gas_stiffness_independent_episode_090_110_v1'\n    e['RM_SPRING_INITIAL_ADMISSION']='D4_to_D5'\n    return e\n",1)
source=source.replace("'train_action_resume_ppo.py','train_action_fresh_preflight_ppo.py'","'train_action_resume_ppo.py','train_action_fresh_preflight_ppo.py','train_spring_resume_ppo.py','train_spring_fresh_preflight_ppo.py'")
tree=ast.parse(source)
def replace_func(name,text):
    global source
    tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines=source.splitlines(keepends=True);source=''.join(lines[:node.lineno-1])+text+'\n'+''.join(lines[node.end_lineno:])
replace_func('verify','''def verify():
    verify_original_records(s.q,D)
    a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
    for n,h in f.items():assert s.q.base.sha(D/n)==h,n
    for n,h in old.items():assert s.q.base.sha(OLD/n)==h and f[n]==h,n
    assert read(CODE/'env.json')==read(OLD/'isaac/mod4/env.json')
    assert read(R/'SPRING_CHECKPOINT_CPU_PASSED.json')['passed']
    assert read(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json')['SDK_limited_parameter_lifecycle_scope_accepted']
    assert read(R/'SELECTED_D4_BEHAVIOR_SOURCE.json')['behavior_scope_accepted']
    assert runtime()['RM_SPRING_PRESSURE_PROFILE']=='gas_stiffness_independent_episode_090_110_v1'
''')
source=source.replace('def fullsave(path,count=20000,require_action=True):','def fullsave(path,count=20000,require_action=True,require_spring=True):')
source=source.replace('    return info\n',"    if require_spring:\n        validate_saved_pressure(ck['spring_pressure_state'],count)\n        assert ck['spring_pressure_recipe']['profile']=='gas_stiffness_independent_episode_090_110_v1'\n    else:assert 'spring_pressure_state' not in ck\n    return info\n",1)
replace_func('source','''def source():
    row=read(R/'SELECTED_D4_BEHAVIOR_SOURCE.json');p=Path(row['checkpoint']['path'])
    assert row['behavior_scope_accepted'] and s.q.base.sha(p)==row['checkpoint']['sha256']
    fullsave(p,require_spring=False);assert learning_health_pass(row['health']) and len(row['unique_completed_segment'])==1
    return p
''')
replace_func('wait_existing','''def wait_existing():
    while True:
        st=read(OLD/'reports/D4_STATE.json')
        if (OLD/'reports/D4_ATTENTION.json').exists():raise AssertionError('Existing D4 attention requires actual review, no automatic takeover')
        if st['phase']=='E0_D4_saved_review_ready':
            old=[st['owner'],read(OLD/'reports/D4_GUARDIAN_STARTED.json')]
            exited=all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in old)
            if exited and not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training'):
                assert (OLD/'reports/D4_REVIEW_READY.json').exists();return
        phase('waiting_existing_D4_complete_saved_boundary',child=None,production_unchanged=True)
        time.sleep(15)
''')
source=source.replace('native_d5_physical_probe.py','native_d5_spring_probe.py')
source=source.replace("    write('D5_NATIVE20K_PASSED.json'", "    assert r['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and r['spring_pressure_audit']['preload_damping_force_limit_armature_unchanged']\n    write('D5_NATIVE20K_PASSED.json'")
source=source.replace("entry='train_action_fresh_preflight_ppo.py' if count==128 else 'train_action_resume_ppo.py'","entry='train_spring_fresh_preflight_ppo.py' if count==128 else 'train_spring_resume_ppo.py'")
source=source.replace("for n in ('train_action_resume_ppo.py','train_action_fresh_preflight_ppo.py')","for n in ('train_spring_resume_ppo.py','train_spring_fresh_preflight_ppo.py')")
source=source.replace("bounded_E0_D5_feedback_delay_learning","bounded_E0_D5_spring_stiffness_learning")
source=source.replace("plan_stage='S2 E0 D5 physical action0/2.5/5ms with D3 feedback0/10ms'","plan_stage='S2 E0 D5 independent episode spring stiffness.9-1.1 with D1-D4 retained'")
source=source.replace("original222_exact=True","all243_predecessor_exact=True")
source=source.replace("        startup=read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json');","        spring=read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json');assert spring['source_sha256']==s.q.base.sha(init) and spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once'] and spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']\n        startup=read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json');")
source=source.replace('fullsave(init,require_action=False)','fullsave(init,require_spring=False)')
source=source.replace("maximum_window_seconds=21600","maximum_window_seconds=21600")
source=source.replace("    package=read(R/'D5_FROZEN_BEHAVIOR_PACKAGE.json');", "    packages=read(R/'D5_FROZEN_BEHAVIOR_PACKAGES.json');")
source=source.replace("        row=dict(job_id=job", "        package=packages[kind]\n        row=dict(job_id=job")
source=source.replace("physics_dt_s=.0025,control_dt_s=.01,solver_position=32", "spring_pressure_profile='gas_stiffness_independent_episode_090_110_v1',physics_dt_s=.0025,control_dt_s=.01,solver_position=32")
source=source.replace("R/'D5_FROZEN_BEHAVIOR_PACKAGE.json'","R/'D5_FROZEN_BEHAVIOR_PACKAGES.json'")
source=source.replace("'clk2500-closure-episode-d3-'+label","'clk2500-closure-episode-d3-'+label")
source=source.replace("'40-d5-anchor'","'70-d5-anchor'").replace("'50-d5-b'","'75-d5-b'")
source=source.replace("role='Actual D5 physical action-delayed frozen skill, not fixed-clean SDK'","role='Actual D5 spring-stiffness pressure closedloop with D1-D4 retained, not SDK calibration'")
source=source.replace("next='Actual D5 skill retention/event review, then approved D5 group'","next='Actual D5 retention/event/engineering pressure review, then approved D6 group'")
source=source.replace("supervise_d5_full_contract.py","supervise_d5_full_contract.py")
ast.parse(source);(D/'supervise_d5_full_contract.py').write_text(source,encoding='utf8')
actual=json.loads((old/'reports/D4_BLOCKS_ACTUAL_VERIFIED.json').read_text(encoding='utf8'));review=json.loads((W/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008/reports/D4_LATER_BLOCKS_MATCHED_REVIEW.json').read_text(encoding='utf8'))
row=dict(actual['complete_blocks']['2']);assert row['checkpoint']['sha256']==review['later_blocks']['2']['checkpoint']['sha256']
cases=review['later_blocks']['2']['cases'];assert all(c['facts']['v4']['pass_'] for c in cases.values())
assert cases['world']['facts']['passed']==64 and all(r['passed']==r['count']==8 for r in cases['spin']['facts']['pure4pi'])
row.update(behavior_scope_accepted=True,actual_same3060_firstseed_white3_full_D4_scope=True,not_highest_directory_or_preflight=True,behavior_review=review['later_blocks']['2'],source_selection_reason='Model29690 complete D4 pairing keeps signedworld64/64 and both pure4pi8/8, improves positive straight error vs firstblock; block3 is not presumed mature from save')
(R/'SELECTED_D4_BEHAVIOR_SOURCE.json').write_text(json.dumps(row,indent=2),encoding='utf8')
for n in ('D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json','SPRING_PRESSURE_CPU_PASSED.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json'):
    shutil.copyfile(prep/'reports'/n,R/n)
(R/'LOCAL_FULL_CONTRACT_BUILT.json').write_text(json.dumps(dict(new_scope='D5 stiffness-only engineering pressure',original243_will_be_copied_exact=True,source=row['checkpoint'],GPU_or_PPO_started=False)),encoding='utf8')
print(json.dumps(dict(new_source=row['checkpoint'],new_training_entries_built=True,D5_GPU_started=False)))
