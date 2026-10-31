from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
s=(O/'collect194_original_formal_cost_normal900_UNUSED_once.py').read_text('utf8')
s=s.replace("N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'", "N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';OLD=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports'")
for name in ['ROOT194_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json','ROOT194_FIRSTV2_ORIGINAL72_OWNER_LAUNCH_ACTUAL.json','ROOT194_FIRSTV2_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json']:
 s=s.replace("read(R/'"+name+"')","read(OLD/'"+name+"')")
s=s.replace(" assert go['nominal_end_epoch']-time.time()<=900,'Original signed local earliest900 not yet eligible'", " admission=json.loads((T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031/reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json').read_bytes())\n assert admission['passed_execution'] and admission['all_own_children_waited'] and admission['private_EX_released']\n assert json.loads((R/'ROOT197_TWO_ROLE_TaskGO_SOURCE_CPU_ACTUAL.json').read_bytes())['passed']")
s=s.replace("'collect194_original_formal_cost_normal900_UNUSED_once|", "'request197_original194_saved_handoff_and_collect_once|install198_E0_72_source_CPU_native64_admission_once|start197_|run197_|collect194_original_formal_cost_normal900_UNUSED_once|")
s=s.replace('ROOT194_NORMAL900','ROOT197_HANDOFF194').replace('ROOT194_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL','ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL')
s=s.replace('normal194_session','handoff197_session').replace('normal194_auth','handoff197_auth')
s=s.replace("B=Path(v['owner']['root']);g=v['go'];assert g['nominal_end_epoch']-time.time()<=900", "B=Path(v['owner']['root']);g=v['go']\nassert v['human_requested_parallel_safe_handoff'] is True")
s=s.replace("dict(owner=owner,go=go),timeout=900", "dict(owner=owner,go=go,human_requested_parallel_safe_handoff=True),timeout=900")
s=s.replace("dest=N/'current_closed194_models/h1_210/formal/model_final.pt'", "dest=N/'qualified_saved194_input/h1_210/formal/model_final.pt'")
needle="  code=\"\"\"from pathlib import Path"
pos=s.index(needle)
prefix='''  auth="""from pathlib import Path
import json,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment']
current=json.loads((Path(v['owner']['root'])/'OWNER_CURRENT.json').read_bytes())
assert current['go']['h1_210']==v['go']
assert a is None or a['owner_parent_pid']==v['owner']['pid']
print(json.dumps(dict(epoch=time.time(),current194_matches_or_already_closed=True,canonical_None=a is None,no_account_write=True)))"""
  try:put('ROOT197_BEFORE_OWN_SAVE_FRESH194_AUTHORITY.json',d.code(client,d.PY72,auth,dict(owner=owner,go=go),timeout=45))
  finally:client.close();client=None
  client=route.connect()
  stop="""from pathlib import Path
import json,os,time,psutil
B=Path(v['job']);assert json.loads((B/'GO_PRODUCTION.json').read_bytes())==v['go']
C=B/'control';identity=json.loads((C/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json').read_bytes())
assert identity['pid']==3537082 and identity['creation']==1793443877.46
out=B/'production';p=out/'STOP_AFTER_SAVE.json';wrote=False;already_final=(out/'FINAL.json').is_file()
if not already_final:
 try:
  worker=psutil.Process(identity['pid']);assert worker.create_time()==identity['creation'] and worker.exe()==identity['exe'] and worker.cmdline()==identity['argv'] and worker.cwd()==identity['root']
 except psutil.NoSuchProcess:raise RuntimeError('Original worker gone without FINAL; no fabricated completion')
 if not p.exists():
  with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),reason='Human requested E0 on freeGPU now: complete own save and transfer to one unified two-role owner, preserve remaining194 time',request='ROOT197_SAFE_PARALLEL_HANDOFF',original_run_id=v['go']['run_id']),f)
  wrote=True
print(json.dumps(dict(epoch=time.time(),original_worker=identity,own_STOP_AFTER_SAVE_written=wrote,already_final=already_final,existing_signal_retained_without_overwrite=p.exists() and not wrote,not_killed_or_source_hotpatched=True,no_model_read=True)))"""
  try:put('ROOT197_ORIGINAL194_OWN_SAVED_STOP_REQUEST_ACTUAL.json',d.code(client,route.PY,stop,dict(job=spec['job_root'],go=go),timeout=45))
  finally:client.close();client=None
  client=d.connect72(sec.recover())
'''
s=s[:pos]+prefix+s[pos:]
s=s.replace('initial_CPU_not_yet_run=True,actual270_skill_not_inferred=True', 'initial_CPU_not_yet_run=True,actual270_skill_not_inferred=True,requested_two_hour_task_not_yet_complete=True,original_normal900_entry_not_executed=True,human_authorized_safe_parallel_handoff=True')
s=s.replace('"""UNUSED closing purpose. Signed local+remote900 gate; no extra training.', '"""NEW human-requested safe parallel handoff; not a replay of original normal900.\nOriginal900 entry remains unused; only completed saved source is collected after own stop.')
ast.parse(s);(N/'request197_original194_saved_handoff_and_collect_once.py').write_text(s,encoding='utf8')
s=(O/'review194_NEW_formal_initial_CPU_UNUSED_once.py').read_text('utf8')
s=s.replace("ROOT194_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL", "ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL")
s=s.replace('ROOT194_NEW_FORMAL_INITIAL_CPU_PURPOSE_CONSUMED','ROOT197_SAVED194_INITIAL_CPU_PURPOSE_CONSUMED').replace('ROOT194_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL','ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL').replace('ROOT194_NEW_FORMAL_CPU_ORIGINAL_ERROR','ROOT197_SAVED194_CPU_ORIGINAL_ERROR')
s=s.replace("skill270_success=False", "skill270_success=False,scope='Qualified actual saved194 prefix for learning-state-preserving parallel handoff, not completion of original two-hour objective',optimizer_LR=ck['optimizer_state_dict']['param_groups'][0]['lr']")
ast.parse(s);(N/'review197_NEW_saved194_initial_fullstate_CPU_once.py').write_text(s,encoding='utf8')
with (N/'reports/ROOT197_SAVED_HANDOFF_SOURCE_PREPARED_NOT_REQUESTED.json').open('x') as f:json.dump(dict(epoch=time.time(),human_authorized_parallel_handoff=True,
 original_normal194_entry_not_run=True,original194_not_stopped_yet=True,raw_charge_function_or_authority_not_modified=True,
 stop_only_own_configured_STOP_AFTER_SAVE_signal=True,collect_only_after_all_original_waits_and_locks_free=True,
 input_formal_transfers=1,input_CPU_decodes=1,model_reads_before_actual_closure=0),f,indent=2)
print(json.dumps(dict(prepared=True,old194_source_or_state_changes=0)))
