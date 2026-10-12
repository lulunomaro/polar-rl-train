from route_repair_io import *
import ast
P=D/'payload';C=P/'isaac/mod4';C.mkdir(parents=True,exist_ok=True)
B=W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012/payload'
def put(name,text):
 p=P/name;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);ast.parse(text);p.write_text(text,encoding='utf8',newline='\n')
def main():
 assert not (R/'BUILD_STARTED.json').exists();save('BUILD_STARTED.json',dict(epoch=time.time(),new_route_lifecycle_only=True,old426_not_modified=True))
 modules=('wave50_route_state.py','wave50_route_runtime.py','wave50_route_full_checkpoint.py','wave50_route_fullsave_cpu.py','test_wave50_route_target_cpu.py')
 names={}
 for old in ('train_wave50_direction_fresh_preflight_ppo.py','train_wave50_direction_resume_ppo.py','probe_wave50_direction_fresh_process_full_resume.py'):
  new=old.replace('wave50_direction','wave50_route');names[old]=new;s=(B/'isaac/mod4'/old).read_text()
  s=s.replace('from wave50_direction_runtime import','from wave50_route_runtime import').replace('from wave50_direction_full_checkpoint import','from wave50_route_full_checkpoint import')
  if old.startswith('train_'):
   anchor='    manifest["src_sha256"] = snapshot';assert s.count(anchor)==1
   s=s.replace(anchor,"    from wave50_route_runtime import audit as audit_route\n    manifest['actual_route_lifecycle']=audit_route(env)\n    manifest['new_route_lifecycle_axis']=True\n    for name in "+repr(modules)+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n"+anchor)
  else:
   anchor="    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']";assert anchor in s
   s=s.replace(anchor,"    route=json.loads((log_dir/'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json').read_text())\n    assert route['passed'] and route['predecessor_route_state_restored_exact'] and not route['explicit_new_route_lifecycle_scope'] and route['actual_CUDA_route_disk_roundtrip_exact'] and route['saved_source_episode_plus_one_verified']\n"+anchor).replace('proof=proof,terrain=terrain,','proof=proof,terrain=terrain,route=route,')
  put('isaac/mod4/'+new,s)
 native=(B/'native_e1_wave50_direction_scope_probe.py').read_text().replace('from wave50_direction_runtime import','from wave50_route_runtime import')
 anchor=" report['episode_direction']=env.command_manager.get_term('twist').audit_direction()";assert native.count(anchor)==1
 native=native.replace(anchor,anchor+"\n from wave50_route_runtime import audit as audit_route,verify_GPU_boundary_fixture\n report['route_lifecycle']=audit_route(env)\n report['route_lifecycle_GPU_boundary_fixture']=verify_GPU_boundary_fixture(env)")
 put('native_e1_wave50_route_lifecycle_scope_probe.py',native)
 put('wave50_route_source_guard.py', '''from wave50_direction_source_guard import verify_original_records as original
def verify_original_records(q,D):
 original(q,D);a=q.w.read(D/'reports/COMPLETE151_ROUTE_AXIS_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['forward_complete']==9 and a['reverse_complete']==26
 assert a['default_source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd' and a['new_route_only_scope_authorized_by004005']
''')
 ctrl=(B/'supervise_wave50_direction_once.py').read_text().replace('from wave50_direction_source_guard import','from wave50_route_source_guard import').replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012')","OLD=Path("+repr(OLD)+")").replace('len(old)==412','len(old)==426').replace('wave50_direction_fullsave_cpu','wave50_route_fullsave_cpu')
 for a,b in names.items():ctrl=ctrl.replace(a,b)
 ctrl=ctrl.replace('native_e1_wave50_direction_scope_probe.py','native_e1_wave50_route_lifecycle_scope_probe.py')
 start=ctrl.index('def wait_existing():');end=ctrl.index('\ndef runtime():',start)
 ctrl=ctrl[:start]+'''def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');passed=read(OLD/'reports/e1_WAVE50_direction_second_bounded_observation_PASSED.json')
 assert st['phase']=='E1_WAVE50_direction_second_bounded_saved_review_ready' and st['child'] is None
 assert passed['checkpoint']['sha256']=='830f46548d3206bded67f9f244f085b7dbbe8f2c35f90faa84c983c4ba3c94c8' and len(passed['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=92072342)):
  actual=identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
''' +ctrl[end:]
 anchor="        entryproof=read(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');";assert anchor in ctrl
 ctrl=ctrl.replace(anchor,"        route=read(run/'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json');assert route['passed'] and route['explicit_new_route_lifecycle_scope'] and not route['predecessor_route_state_restored_exact'] and route['actual_CUDA_route_disk_roundtrip_exact'] and route['saved_source_episode_plus_one_verified']\n"+anchor)
 anchor="        audit_native_trace(outpath,v)";assert anchor in ctrl
 ctrl=ctrl.replace(anchor,anchor+"\n        assert v['route_lifecycle']['Wave_inward_limit_m']==4. and v['route_lifecycle_GPU_boundary_fixture']['passed'] and v['route_lifecycle_GPU_boundary_fixture']['actual_bound_CUDA_state']\n        write(label+'_ROUTE_GPU_SCOPE_PASSED.json',dict(passed=True,physical_callbacks_verified=v['physical_callback_count'],route_audit=v['route_lifecycle'],actual_GPU_boundary_fixture=v['route_lifecycle_GPU_boundary_fixture'],not_full_physical_route_certificate=True))")
 anchor=" assert proof['direction']['predecessor_direction_state_restored_exact'] and not proof['direction']['explicit_new_episode_direction_scope'] and proof['direction']['actual_CUDA_direction_disk_roundtrip_exact']";assert anchor in ctrl
 ctrl=ctrl.replace(anchor,anchor+"\n assert proof['route']['predecessor_route_state_restored_exact'] and not proof['route']['explicit_new_route_lifecycle_scope'] and proof['route']['actual_CUDA_route_disk_roundtrip_exact']")
 ctrl=ctrl.replace('e1-wave50-direction-own-','e1-wave50-route-own-').replace('e1-wave50-direction-repair','e1-wave50-route-lifecycle-repair').replace('E1_WAVE50_direction_saved_review_ready','E1_WAVE50_route_lifecycle_saved_review_ready').replace('e1_WAVE50_direction_observation','e1_WAVE50_route_lifecycle_observation').replace('bounded_E1_WAVE50_episode_direction_learning','bounded_E1_WAVE50_route_lifecycle_learning').replace('old412_ownsave_unique_settled_actual_exits_two_OS_locks_held_active_empty','old426_ownsave_unique_settled_actual_exits_two_OS_locks_held_active_empty')
 put('supervise_wave50_route_lifecycle_once.py',ctrl)
 files={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in P.rglob('*') if p.is_file()}
 assert len(files)==11
 for p in P.rglob('*.py'):ast.parse(p.read_text())
 save('ROUTE_LIFECYCLE_COMPONENTS_PREPARED.json',dict(epoch=time.time(),passed=True,files=files,new_scope='Wave inward4m route, other outward/lateral/nonWave2m exact, all other axes unchanged',new_independent_components_workers_native_fresh_controller=True,old426_allbytes_will_be_reused_immutable=True,target_CPU_CUDA_GPU_PPO_not_yet_admitted=True,no_new_rng_or_actor_gate_truth=True))
 print(json.dumps(dict(prepared=True,components=len(files),target_CPU_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_CPU_GPU=True));raise
