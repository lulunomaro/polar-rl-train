"""Child-only SOURCE derivation. Known text inputs, no PT/SSH/SDK/C/owner run."""
from pathlib import Path
import ast, difflib, hashlib, json
B=Path(__file__).resolve().parent
D=B.parent
S=D/'source_w35'

def h(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
def replace_once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)

SAVE=r'''                full=cache.state
                immutable_truth=copy.deepcopy(full)
                raw_save=runner.save  # eight original full-state installers already active
                required_live={'actor_state_dict','critic_state_dict','optimizer_state_dict','iter',
                    'sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state',
                    'sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state',
                    'spring_pressure_state','gas_damping_state','chassis_PD_state',
                    'E1_terrain_state','E1_retained_flat_command_state'}
                counter=FiniteUpdateCounter(task['max_additional_updates'])
                def complete_save_path(path,*args,**kwargs):
                    assert not counter.active,'Never certify a partial original PPO update'
                    assert exact(cache.state,immutable_truth),'Immutable selected-source truth changed'
                    path=Path(path).resolve()
                    assert path.is_relative_to(OUT) and (path.suffix=='.pt' or path.name.endswith('.pt.partial'))
                    assert path!=source.resolve(),'Never overwrite mother'
                    path.parent.mkdir(parents=True,exist_ok=True)
                    tmp=path.with_name(path.name+'.fullstate.partial');assert not tmp.exists()
                    raw_save(str(tmp),*args,**kwargs)
                    live=cached_load(tmp,map_location='cpu',weights_only=False)
                    assert required_live<=set(live),('Original LIVE save omitted fields',required_live-set(live))
                    for key,obj in [('actor_state_dict',runner.alg.actor),('critic_state_dict',runner.alg.critic),('optimizer_state_dict',runner.alg.optimizer)]:
                        assert exact(live[key],obj.state_dict()),key
                    # The ORIGINAL runner publishes this value before logger.log.
                    # Record it as-is: no assignment to saved iter or live runner iteration.
                    assert live['iter']==int(runner.current_learning_iteration) and live['iter']>=ITER
                    current=[int(v['step']) for v in live['optimizer_state_dict']['state'].values()]
                    assert len(current)==17 and set(current)=={ADAM+20*counter.completed}
                    assert all(g['lr']==runner.alg.learning_rate for g in live['optimizer_state_dict']['param_groups'])
                    for key,adapter in [('sensor_DR_state',real._sensor_mild),('physical_action_delay_state',real._physics_action_delay),
                        ('spring_pressure_state',real._spring_pressure),('gas_damping_state',real._gas_damping)]:
                        assert exact(live[key],adapter.state_dict()),key
                    assert exact(live['chassis_PD_state']['COM'],real._chassis_com.state_dict())
                    assert exact(live['chassis_PD_state']['PD'],real._explicit_pd.state_dict())
                    from checkpoint_cache208_v3 import current_state as current_terrain
                    assert exact(live['E1_terrain_state'],current_terrain(real))
                    assert exact(live['E1_retained_flat_command_state'],real.command_manager.get_term('twist').state_dict_retention())
                    state=merge_original_omissions(full,live)
                    state['posttrain_live_runner_counter_at_save']=int(runner.current_learning_iteration)
                    state['posttrain_iteration_semantics']='Unmodified original RSL iteration; separately counted completed PPO updates; no arithmetic backfill'
                    state['posttrain_cumulative_new_PPO_updates']=PRIOR_CUMULATIVE+counter.completed
                    state['typed_W35_RM70_task']=merge_original_omissions(full.get('typed_W35_RM70_task',{}),typed)
                    state['actual_new_PPO_updates']=counter.completed
                    from mod4v1_w35_asset_compat import record_historical_source_metadata
                    record_historical_source_metadata(state,full)
                    state=merge_original_omissions(full,state)  # preserve even original historical root omissions
                    state['posttrain_source_cache_truth_unchanged']=True
                    state['mod4v1_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
                    torch.save(state,tmp)
                    roundtrip=cached_load(tmp,map_location='cpu',weights_only=False)
                    assert exact(roundtrip,state) and exact(cache.state,immutable_truth)
                    assert roundtrip['iter']==int(runner.current_learning_iteration)
                    tmp.replace(path)
                    row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),
                        source_SHA=SHA,actual_new_PPO_updates=counter.completed,
                        saved_iteration=roundtrip['iter'],actual_live_runner_iteration=int(runner.current_learning_iteration),
                        Adam_min=min(current),Adam_max=max(current),actual_saved_LR=roundtrip['optimizer_state_dict']['param_groups'][0]['lr'],
                        actual_optimizer_step_calls=counter.steps,
                        full_core_STD_optimizer_and_targetDR_saved=True,
                        source_prior_window_updates=PRIOR_WINDOW,source_prior_cumulative_updates=PRIOR_CUMULATIVE,
                        cumulative_new_PPO_updates=PRIOR_CUMULATIVE+counter.completed,
                        source_cache_truth_all_roots_unchanged=True,all_original_source_root_keys_retained=set(full)<=set(roundtrip),
                        same_RM70_course_assignment_command_fullstate_restored=True,
                        original_rescue_rename_pending=path.name.endswith('.pt.partial'))
                    put('latest_complete.json',row);last_complete[0]=row;last_saved[0]=time.time()
                    return row
                def save(label):return complete_save_path(OUT/(label+'.pt'))
'''
TRAIN=r'''                original_update=runner.alg.update;original_step=runner.alg.optimizer.step;original_log=runner.logger.log
                def update(*args,**kwargs):
                    counter.before_update()
                    losses=original_update(*args,**kwargs)
                    counter.after_update();updates[0]=counter.completed
                    return losses
                def optimizer_step(*args,**kwargs):
                    result=original_step(*args,**kwargs);counter.step_returned();return result
                def log(*args,**kwargs):
                    result=original_log(*args,**kwargs)
                    assert counter.completed==counter.logged+1,'One original completed PPO update per log boundary'
                    counter.logged=counter.completed
                    if counter.completed==1 or counter.completed%5==0:save('model_update'+str(counter.completed)+'_complete')
                    put('LATEST_PROGRESS.json',dict(epoch=time.time(),actual_new_PPO_updates=counter.completed,
                        actual_optimizer_step_calls=counter.steps,actual_live_runner_iteration=int(runner.current_learning_iteration),
                        actual_Adam_steps=[int(v['step'])for v in runner.alg.optimizer.state_dict()['state'].values()]))
                    stop=(counter.completed>=task['max_additional_updates'] or time.time()>=go['save_deadline']
                        or Path(task['stop_file']).exists() or (OUT/'STOP_AFTER_SAVE.json').exists()
                        or (Path(log_dir)/'STOP_AFTER_SAVE').exists() or shutil.disk_usage(job).free<8*1024**3)
                    if stop:save('model_final_complete');raise SavedStop()
                    return result
                runner.save=complete_save_path
                runner.alg.update=update;runner.alg.optimizer.step=optimizer_step;runner.logger.log=log
                try:
                    if (time.time()<go['save_deadline'] and not Path(task['stop_file']).exists()
                        and not (OUT/'STOP_AFTER_SAVE.json').exists() and not (Path(log_dir)/'STOP_AFTER_SAVE').exists()):
                        # Original rescue_training.learn installs its atomic/deadline
                        # hook and calls original runner.learn(..., init_at_random_ep_len=True).
                        original_bounded_learn(runner,n,log_dir)
                except SavedStop:pass
                finally:
                    runner.alg.update=original_update;runner.alg.optimizer.step=original_step;runner.logger.log=original_log
                    runner.save=raw_save
                assert not counter.active and counter.completed<=task['max_additional_updates']
                assert exact(cache.state,immutable_truth)
                final=save('model_final_complete')
                put('FINAL.json',dict(epoch=time.time(),passed=counter.completed>0,actual_new_PPO_updates=counter.completed,
                    new_environment_transitions=counter.completed*20000*task['steps_per_env'],source_SHA=SHA,final=final,
                    actual_optimizer_step_calls=counter.steps,actual_live_runner_iteration=int(runner.current_learning_iteration),
                    source_cache_truth_all_roots_unchanged=True,source_cache=cache.receipt(),whole_RM70_skill=False,
                    complete_SuperMimic_conversion=False,no_extra_training_window=True,
                    original_finite_owner_GO=dict(run_id=go['run_id'],role_key=go['role_key'],max_parent_seconds=go['max_parent_seconds'],
                        save_deadline=go['save_deadline'],nominal_end_epoch=go['nominal_end_epoch'],one_original_writer=True)))
'''
COUNTER=r'''class FiniteUpdateCounter:
    """stdlib-only observer. Performs no optimizer operation; checks real returns."""
    def __init__(self,limit):
        assert type(limit)is int and 1<=limit<=20
        self.limit=limit;self.completed=0;self.steps=0;self.logged=0;self.active=False
    def before_update(self):
        assert self.completed<self.limit and not self.active
        self.active=True
    def step_returned(self):
        assert self.active
        self.steps+=1
    def after_update(self):
        assert self.active and self.steps==20*(self.completed+1)
        self.completed+=1;self.active=False


'''

def main():
    old=(S/'worker_mod4v1_w35_posttrain20_v1.py').read_text(encoding='utf-8-sig')
    text=replace_once(old,'import argparse,hashlib,json,os,runpy,shutil,subprocess,sys,time,traceback','import argparse,copy,hashlib,json,os,runpy,shutil,subprocess,sys,time,traceback')
    text=replace_once(text,'OUT=None','PRIOR_WINDOW=82; PRIOR_CUMULATIVE=162\nOUT=None')
    text=replace_once(text,'def read(path):',COUNTER+'def read(path):')
    text=replace_once(text,'from mod4v1_w35_posttrain_protocol_v1 import validate_new_job','from mod4v1_w35_posttrain_protocol_v2 import validate_new_job')
    text=replace_once(text,"assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==82","assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==PRIOR_WINDOW")
    text=replace_once(text,'new_physical_episode_and_query_cache_after_restore=True,source_prior_new_PPO_updates=162,','new_physical_episode_and_query_cache_after_restore=True,source_prior_new_PPO_updates=PRIOR_CUMULATIVE,\n        source_prior_window_PPO_updates=PRIOR_WINDOW,source_prior_cumulative_PPO_updates=PRIOR_CUMULATIVE,')
    text=replace_once(text,"'--num_envs','20000','--seed','20260928'","'--num_envs','20000','--seed',str(task['seed'])")
    text=replace_once(text,"'--steps_per_env','24'","'--steps_per_env',str(task['steps_per_env'])")
    text=replace_once(text,"'--additional_iterations','20'","'--additional_iterations',str(task['max_additional_updates'])")
    text=replace_once(text,'                runner.alg.learning_rate=runner.alg.optimizer.param_groups[0][\'lr\']','                assert n==task[\'max_additional_updates\'] and runner.alg.learning_rate==LR\n                assert all(g[\'lr\']==LR for g in runner.alg.optimizer.param_groups)')
    a=text.index('                def save(label):');z=text.index('                runner._new208_save_complete=save',a)
    text=text[:a]+SAVE+text[z:]
    a=text.index('                original_update=runner.alg.update');z=text.index('            rescue_training.learn=work',a)
    text=text[:a]+TRAIN+text[z:]
    text=replace_once(text,'            def work(runner,n,log_dir):','            original_bounded_learn=rescue_training.learn\n            def work(runner,n,log_dir):')
    ast.parse(text)
    (B/'worker_mod4v1_w35_posttrain20_v2.py').write_text(text,encoding='utf-8')
    proto_old=(S/'mod4v1_w35_posttrain_protocol_v1.py').read_text(encoding='utf-8-sig')
    proto=replace_once(proto_old,"                    original_canonical_generation=GENERATION, canonical_path=CANONICAL,\n                    source_read_purpose={'physical_byte_opens': 1, 'decodes': 1, 'source_bytes': SOURCE_BYTES})","                    original_canonical_generation=GENERATION, canonical_path=CANONICAL)")
    proto=replace_once(proto,"    require(task['role_key'] == go['role_key'], 'ROOT actual role key join')","    require(task['source_read_purpose']=='NEW_W35_FULL20K_POSTTRAIN20_'+task['run_id'], 'Original parent string read-purpose contract')\n    require(task['source_read_plan']==dict(physical_byte_opens=1,decodes=1,source_bytes=SOURCE_BYTES), 'Independent selected-source plan, never parent string field')\n    require(task['source_prior_window_PPO_updates']==82 and task['source_prior_cumulative_PPO_updates']==162, 'Separate prior window and cumulative')\n    require(task['seed']==go['seed']==20260928 and task['steps_per_env']==go['steps_per_env']==24, 'Explicit seed and original rollout length')\n    require(task['role_key'] == go['role_key'], 'ROOT actual role key join')")
    proto=replace_once(proto,"    require(ih == task['derivation_index_SHA'] == manifest['derivation_index_SHA'], 'Frozen derivation index join')","    require(ih == task['derivation_index_SHA'], 'Dedicated new derivation index Task join')\n    index_rows=[r for r in manifest['files'] if r['relative']=='MOD4V1_W35_POSTTRAIN_DERIVATION_INDEX.json']\n    require(len(index_rows)==1 and index_rows[0]['SHA']==ih, 'Generic original stager binds dedicated derivation through files[], not nonexistent manifest.derivation_index_SHA')")
    proto=replace_once(proto,"    require(task['max_additional_updates']==go['max_additional_updates']==20,'Finite20actualPPOcap')","    certificate,certificate_sha=job_json(job,'INPUT8D_GPU_FULLRESTORE_ACTUAL.json')\n    require(certificate_sha==GPU_RESTORE_SHA and certificate['passed'] and certificate['source_SHA']==SOURCE_SHA, 'Actual historical8d GPU certificate')\n    require(certificate['iteration']==ITER and certificate['Adam17']==ADAM and certificate['actual_LR']==LR and certificate['actor_critic_STD_optimizer_verified'], 'Actual historical8d core counters/LR')\n    require(certificate['source_cache']['source_bytes']==SOURCE_BYTES, 'Certificate whole selected source byte metadata')\n    require(task['max_additional_updates']==go['max_additional_updates']==20,'Finite20actualPPOcap')")
    proto=replace_once(proto,"    require(len(task['inherited_lock_fds'])>=4,'Original twoownerEX plusGPUprivateEX plusfiniteSH inherited')","    require(task['owner_parent_pid']==os.getppid(), 'Actual direct original owner, not source Draft PID')\n    require(len(task['inherited_lock_fds'])>=4,'Original twoownerEX plusGPUprivateEX plusfiniteSH inherited')")
    ast.parse(proto)
    (B/'mod4v1_w35_posttrain_protocol_v2.py').write_text(proto,encoding='utf-8')
    certificate=(S/'INPUT8D_GPU_FULLRESTORE_ACTUAL.json').read_bytes();assert h(certificate)=='eb7818657e17c5ef649770f608aceb1231042160f30b9b329519151495037f34'
    (B/'INPUT8D_GPU_FULLRESTORE_ACTUAL.json').write_bytes(certificate)
    changes=list(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='source_w35/worker_v1',tofile='source_w35_v2/worker_v2'))+list(difflib.unified_diff(proto_old.splitlines(True),proto.splitlines(True),fromfile='source_w35/protocol_v1',tofile='source_w35_v2/protocol_v2'))
    (B/'SOURCE_V1_TO_V2_DIFF.patch').write_text(''.join(changes),encoding='utf-8')
    put('SOURCE_REVIEW_ERRORS_AND_FIXES_V2.json',dict(status='SOURCE_ONLY_NO_PT_SDK_OR_GO',catalog=dict(matched_skill=None,available='Office/ACL do not match RL/source integration',used='FS+stdlib AST/mock; no DSH plugins'),
        input_constants_actually_8d=True,old_source_edited=False,parent_owner_or_stager_edited=False,
        fixes=['Parent source_read_purpose string vs old dict clash fixed with independent source_read_plan',
            'Generic stager manifest lacks derivation_index_SHA: bind dedicated index through manifest.files[] actual row',
            'Removed arithmetic saved iter AND all assignments to live runner current_learning_iteration; raw original value only',
            'Removed manual alg.learning_rate overwrite; require exact original restored LR',
            'Save/stop moved from alg.update internal return to original logger boundary',
            'Known original live roots checked BEFORE merge; core/terrain/command/DR live comparisons',
            'Unknown source root/nested dictionaries and original historical omissions retained',
            'Full-root RAM immutable truth audit; actual optimizer-step returns count20 per original update'],
        discovery=['Sealed W35 runtime directory is an overlay; two direct helper reads were not found there. Exact INSTALL227 source map resolved only checkpoint_cache208_v3/spring_pressure_checkpoint208_v3/rescue_training (no82module closure scan).'],
        inspected_parent_source=str(D/'parent_source/eight_posttrain_original_owner_v1.py'),inspected_stager=str(D/'parent_source/stage_generic_nonpt_roles_v2.py'),
        old_inputs=[dict(path=str(S/n),SHA=h((S/n).read_bytes()))for n in ('worker_mod4v1_w35_posttrain20_v1.py','mod4v1_w35_posttrain_protocol_v1.py','W35_POSTTRAIN_SOURCE_DESCRIPTOR_V1.json','INPUT8D_GPU_FULLRESTORE_ACTUAL.json')],
        model_PT_open_stat_hash_decode=0,SSH_SDK_GPU_C_GO_Git_operations=0,new_agents=0))
    print(json.dumps(dict(status='NEW_SOURCE_W35_V2_DERIVED',root=str(B),PT_SDK_GO=0),indent=2))

if __name__=='__main__':main()
