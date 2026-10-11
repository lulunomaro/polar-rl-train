from direction_io import *
import ast
P=D/'payload';C=P/'isaac/mod4';I=D/'inherited_source';IC=I/'isaac/mod4'

def put(name,t):
 p=P/name;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);ast.parse(t);p.write_bytes(t.encode())

def replace(t,a,b,count=1):
 assert t.count(a)==count,(a,t.count(a),count);return t.replace(a,b)

def main():
 extra=['curb20_direction_state.py','curb20_direction_runtime.py','curb20_direction_full_checkpoint.py','curb20_direction_fullsave_cpu.py']
 for old in ('train_curb20_entry_fresh_preflight_ppo.py','train_curb20_entry_resume_ppo.py','probe_curb20_entry_fresh_process_full_resume.py'):
  t=(IC/old).read_text();new=old.replace('curb20_entry','curb20_direction')
  t=t.replace('from curb20_entry_v3_runtime import','from curb20_direction_runtime import').replace('from curb20_entry_full_checkpoint import','from curb20_direction_full_checkpoint import')
  if old.startswith('train_'):
   anchor='    manifest["src_sha256"] = snapshot'
   add='    for name in '+repr(tuple(extra))+':\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest["actual_CURB_episode_direction_scope"]=env.command_manager.get_term("twist").audit_direction()\n'
   t=replace(t,anchor,add+anchor)
  else:
   anchor="    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']"
   t=replace(t,anchor,"    direction=json.loads((log_dir/'E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json').read_text())\n    assert direction['passed'] and direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope']\n"+anchor)
  put('isaac/mod4/'+new,t)
 t=(I/'native_curb20_entry_origin_bound_sdk_probe.py').read_text()
 t=replace(t,'from curb20_entry_v3_runtime import','from curb20_direction_runtime import')
 t=replace(t," report['command_retention']=env.command_manager.get_term('twist').audit_retention()"," report['command_retention']=env.command_manager.get_term('twist').audit_retention()\n report['CURB_direction_audit']=env.command_manager.get_term('twist').audit_direction()")
 put('native_curb20_direction_probe.py',t)
 t=(I/'supervise_curb20_entry_fullstate_once.py').read_text()
 t=replace(t,"OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_REPAIR_20261011')","OLD=Path("+repr(OLD)+")")
 t=t.replace('from curb20_entry_fullsave_cpu import fullsave as core','from curb20_direction_fullsave_cpu import fullsave as core')
 start=t.index(" assert read(R/'ENTRY_TARGET_FULLSTATE_CPU_PASSED.json')");end=t.index(' for n,h in own.items():',start)
 t=t[:start]+" assert read(R/'DIRECTION_TARGET_CPU_PASSED.json')['passed']\n own=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==410 and all(own[n]==h for n,h in old.items())\n"+t[end:]
 start=t.index('def wait_existing():');end=t.index('\ndef runtime():',start)
 t=t[:start]+'''def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_CURB20_entry_repair_saved_review_ready' and st['child'] is None
 ready=read(OLD/'reports/E1_REVIEW_READY.json');assert ready['automatic_more_PPO_disallowed']
 for v in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),read(OLD/'reports/e1_CURB20_entry_repair_observation_PASSED.json')['own_PID_bound_receipt']):
  a=identity(v['pid']);assert not a or a['state']=='Z' or a.get('start_ticks')!=v.get('start_ticks')
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
'''+t[end:]
 t=t.replace('train_curb20_entry_fresh_preflight_ppo.py','train_curb20_direction_fresh_preflight_ppo.py').replace('train_curb20_entry_resume_ppo.py','train_curb20_direction_resume_ppo.py').replace('probe_curb20_entry_fresh_process_full_resume.py','probe_curb20_direction_fresh_process_full_resume.py')
 t=replace(t,"verify();assert read(R/'ENTRY_ORIGIN_BOUND_SDK10_PASSED.json')['passed'];", "verify();assert read(R/'ENTRY_ORIGIN_BOUND_SDK10_PASSED.json')['passed'] and read(R/'DIRECTION_NATIVE20K_PASSED.json')['passed'];")
 t=replace(t,"    a=read(run/'RETENTION_COMMAND_ACTUAL.json');", "    own_direction=read(run/'CURB_DIRECTION_ACTUAL.json');assert own_direction['all_episode_identity_exact'] and own_direction['no_new_rng']\n    if count==20000:\n        direction=read(run/'E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json');assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and direction['actual_CUDA_direction_disk_roundtrip_exact']\n    a=read(run/'RETENTION_COMMAND_ACTUAL.json');")
 t=t.replace('139-e1-curb20-entry-repair', 'JOBNUMBER-e1-curb20-direction-repair').replace('E1_CURB139_ASYNC_PUBLISHED','E1_CURB_DIRECTION_ASYNC_PUBLISHED').replace('requires_actual139_fourcase_review','requires_actual_candidate_fourcase_review')
 t=replace(t,"job='clk2500-closure-episode-d3-JOBNUMBER-e1-curb20-direction-repair'", "job='clk2500-closure-episode-d3-'+str(read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number'])+'-e1-curb20-direction-repair'")
 t=t.replace('native_curb20_entry_origin_bound_sdk_probe.py','native_curb20_direction_probe.py')
 start=t.index('def origin_bound_SDK10():');end=t.index('\ndef fresh_same_scope(',start)
 t=t[:start]+'''def direction_native(count,warm,steps,label):
 import numpy as np
 assert not (R/(label+'_PID_RECEIPT.json')).exists()
 output=D/(label+'.json');log=D/(label+'.log');before=s.q.ctl.CANONICAL.read_bytes()
 args=[s.q.base.PY,str(D/'native_curb20_direction_probe.py'),'--headless','--dt','.0025','--checkpoint',str(source()),'--output',str(output),'--num_envs',str(count),'--warmup',str(warm),'--steps',str(steps),'--profile_steps','0']
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 loc=identity(p.pid);write(label+'_PID_RECEIPT.json',dict(epoch=time.time(),child=loc,argv=args,no_PPO=True,new_direction_scope_only=True))
 phase(label+'_no_PPO',child=loc,active_log=str(log))
 while p.poll() is None:time.sleep(2)
 assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 assert s.q.ctl.CANONICAL.read_bytes()==before
 v=read(output);h=v['health'];assert v['PPO_update_count']==0 and not v['nonfinite'] and v['actual_task_failed_environments']==0
 assert v['physical_callback_count']==4*steps and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4*(warm+steps)
 assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and h['stop_reason'] is None
 assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6 and v['actual_solver_readback']['all_position32_velocity4']
 a=v['CURB_direction_audit'];assert a['all_episode_identity_exact'] and a['no_new_rng'] and a['non_CURB_commands_unchanged']
 trace=output.with_name(output.stem+'_trace');audit=read(trace/'RETENTION_COMMAND_ACTUAL.json');x=np.concatenate([np.load(trace/n)['rows'] for n in audit['trace_files']]);assert x.shape==(warm+steps,count,16)
 root=np.array(v['reset_root_before_physics'],dtype='<f4');from curb20_direction_state import bind_numpy
 mask,sign=bind_numpy(root[:,:2],v['actual_generated_family_assignments']);assert mask.sum()==a['actual_CURB_environments']
 assert np.all(x[:,mask,7]*sign[mask]>=-1e-7) and np.max(abs(x[:,mask,8:10]))==0
 if count==10:
  assert mask.all() and v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact'] and v['CURB_entry_map']['changed_environments']==10
 else:
  assert mask.sum()==2820 and a['positive_entry_direction']>0 and a['negative_entry_direction']>0
  hist=np.array(a['control_histogram']);assert hist[0,1]>0 and hist[1,0]>0 and hist[:,2].min()>0
 row=dict(epoch=time.time(),passed=True,path=str(output),bytes=output.stat().st_size,sha256=s.q.base.sha(output),no_PPO=True,actual_child=loc,health=h,actual_direction=a,complete_trace_original_path=str(trace),only_command_direction_axis=True)
 write(label+'_PASSED.json',row)
'''+t[end:]
 t=replace(t,"'--num_envs','20000','--max_iterations','0','--log_root'", "'--num_envs','20000','--max_iterations','0','--seed','20260928','--log_root'")
 t=replace(t,' origin_bound_SDK10()'," direction_native(10,0,300,'ENTRY_ORIGIN_BOUND_SDK10')\n direction_native(20000,24,120,'DIRECTION_NATIVE20K')")
 t=replace(t,"native_exact_reused=read(R/'ENTRY_REUSED_NATIVE20K.json')","new_direction_native=read(R/'DIRECTION_NATIVE20K_PASSED.json')")
 t=t.replace('entry_discard128','direction_discard128').replace('entry_discard20k','direction_discard20k').replace('e1_CURB20_entry_repair_observation','e1_CURB20_direction_repair_observation').replace('bounded_E1_CURB20_entry_repair_learning','bounded_E1_CURB20_direction_repair_learning').replace('E1_CURB20_entry_repair_saved_review_ready','E1_CURB20_direction_repair_saved_review_ready')
 # Old completion predicate is literal and must still identify the immutable predecessor.
 t=replace(t,"st['phase']=='E1_CURB20_direction_repair_saved_review_ready'", "st['phase']=='E1_CURB20_entry_repair_saved_review_ready'")
 t=replace(t,"read(OLD/'reports/e1_CURB20_direction_repair_observation_PASSED.json')", "read(OLD/'reports/e1_CURB20_entry_repair_observation_PASSED.json')")
 t=t.replace('no_SDK_native_clock_replay=True','new_direction_SDK_native_only_no_clock_replay=True')
 put('supervise_curb20_direction_once.py',t)
 save('DIRECTION_PAYLOAD_BUILT.json',dict(epoch=time.time(),new_files={str(p.relative_to(P)):H(p.read_bytes()) for p in P.rglob('*') if p.is_file()},old_source_bytes_preserved=True,only_CURB_episode_command_direction_axis=True,no_GPU_or_PPO=True))
 save('DIRECTION_LOCAL_READER_PATH_ERRORS.json',dict(epoch=time.time(),errors=[dict(paths=['curb20_entry_full_checkpoint.py','curb20_command_migration_environment_view.py','curb20_entry_v3_runtime.py','curb20_entry_current_state.py'],attempted_base='inherited_source',actual_base='inherited_source/isaac/mod4',error='Get-Content path not found',before_any_GPU_or_stage=True)]))
 print(json.dumps(dict(payload_files=len(list(P.rglob('*.py'))),prepared_only=True)))
if __name__=='__main__':main()
