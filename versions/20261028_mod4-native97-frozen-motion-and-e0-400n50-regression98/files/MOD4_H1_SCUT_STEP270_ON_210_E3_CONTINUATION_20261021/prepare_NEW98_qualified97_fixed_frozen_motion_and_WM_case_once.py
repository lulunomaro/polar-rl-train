from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
old=T/'H1_NATIVE91_FLAT_FROZEN_WM_DIAG_N1_20261028';S=T/'H1_NATIVE97_FLAT_FROZEN_MOTION_WM_N1_V98_20261028';N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'
assert not S.exists();S.mkdir();(S/'code').mkdir();(S/'reports').mkdir()
qual=L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/reports/NATIVE97_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json';closed=L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1/reports/TWO97_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'
q=json.loads(qual.read_bytes());c=json.loads(closed.read_bytes());assert q['passed'] and c['canonical_None'] and c['all_two_original_owner_nodes_workers_out'] and q['model']['SHA']=='6b3c8e9ddb56cac053e7ab386a4ec89723b799a6d4147f65232ad1e889824074'
audit=[]
def write_new(source,destination,changes):
 raw=source.read_bytes();text=raw.decode('utf8');counts=[]
 for before,after in changes:
  count=text.count(before);assert count>0,(source.name,before);text=text.replace(before,after);counts.append(dict(before=before,after=after,count=count))
 ast.parse(text)
 with destination.open('x',encoding='utf8',newline='\n') as f:f.write(text)
 audit.append(dict(original=str(source),original_SHA=hashlib.sha256(raw).hexdigest(),new=str(destination),new_SHA=hashlib.sha256(destination.read_bytes()).hexdigest(),changes=counts))
common=[('flat91_eval_contract_v1','flat98_eval_contract_v1'),('flat91_eval_environment_v1','flat98_eval_environment_v1'),('flat91_frozen_diag_driver_v1','flat98_frozen_diag_driver_v1')]
for name in ('flat91_eval_contract_v1.py','flat91_eval_environment_v1.py','flat91_frozen_diag_driver_v1.py'):
 relevant=[x for x in common if x[0] in (old/'code'/name).read_text(encoding='utf8')]
 write_new(old/'code'/name,S/'code'/name.replace('flat91','flat98'),relevant)
entry=old/'code/run_native91_frozen_flat_WM_N1_once.py'
authority_old="""  active=c['active_segment']
  if active is not None:
   expected=q['allowed_active_W35_owner'];require(set(active['experts'])=={'w35'} and active['owner_parent_pid']==expected['pid'],'only separate genuine W35 owner allowed')
   p=psutil.Process(expected['pid']);require(p.create_time()==expected['creation'],'known sole-owner PID recycled')
   require(p.exe()==expected['exe'] and p.cmdline()==expected['argv'] and p.cwd()==expected['root'],'known sole W35 exact process identity')
  return dict(remaining_snapshot=c['remaining_training_seconds'],active_known_W35_only=active is not None,no_account_write=True)"""
authority_new="""  require(c['active_segment'] is None,'NEW98 requires original97 closed and no new learning owner')
  return dict(remaining_snapshot=c['remaining_training_seconds'],canonical_None=True,no_account_write=True)"""
write_new(entry,S/'code/run_native98_frozen_flat_WM_N1_once.py',common+[
 ('NEW qualified91 frozen','NEW qualified97 frozen'),('qualified91 formal source exact','qualified97 formal source exact'),('qualified91 output lineage','qualified97 output lineage'),
 ('An independently active, exactly identified sole W35 owner may keep running.','Requires no active learning account; this new frozen case never registers a learning owner.'),
 ('MOD4_H1_FLAT91_FROZEN_WM_DIAG_','MOD4_H1_FLAT97_FROZEN_MOTION_WM_DIAG_'),
 (authority_old,authority_new),
 ('bd36a58c6bb31471212f4329407e85113064337650e51fc3c1587995dc2e3d50','6b3c8e9ddb56cac053e7ab386a4ec89723b799a6d4147f65232ad1e889824074'),('256229065','256231497'),
 ('source_qualified91_CPU.json','source_qualified97_CPU.json'),("qualified['original_account_settled_and_allout']","qualified['original_normal_duration_account_settled_and_allout']"),
 ('admitted91 runtime','admitted97 runtime'),('FROZEN_NATIVE91_FLAT_WM_DIAGNOSTIC','FROZEN_NATIVE97_FLAT_MOTION_WM_DIAGNOSTIC'),('native91_frozen_N1_configuration_only','native98_frozen_N1_configuration_only'),
 ("native['iteration']==9256 and publication['world_updates']==92560 and publication['policy_updates']==9000","native['iteration']==12066 and publication['world_updates']==120660 and publication['policy_updates']==11682")])
launcher=old/'run_new91_frozen_single_WM_paired_diagnostic_once.py'
text=launcher.read_text(encoding='utf8')
old_block=""" cpu=N/'reports/NATIVE91_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json';qual=json.loads(cpu.read_bytes());assert qual['passed']
 closed=json.loads((N/'reports/NATIVE91_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['canonical_None'] and closed['original_owner_private_shared_locks_free']
 launched=json.loads((T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_fixed92_single72_owner_source_v2/reports/W35_FIXED92_OWNER_NODE_LAUNCHED_ACTUAL.json').read_bytes())
 prep=json.loads((N/'reports/NATIVE91_SOURCE_PREPARED_ACTUAL.json').read_bytes());old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1'"""
new_block=f""" L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
 cpu=L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/reports/NATIVE97_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json';qual=json.loads(cpu.read_bytes());assert qual['passed']
 closed=json.loads((L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1/reports/TWO97_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['canonical_None'] and closed['original_private_shared_writer_locks_free'] and closed['all_two_original_owner_nodes_workers_out']
 prep=json.loads((N/'reports/NATIVE97_DIAGNOSTIC_IO_SOURCE_PREPARED_ACTUAL.json').read_bytes())['spec_pending_actual_new_source_CPU'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1'"""
write_new(launcher,S/'run_NEW98_qualified97_fixed_motion_WM_case_once.py',[
 ("MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027","MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028"),('MOD4_H1_FLAT91_FROZEN_WM_DIAG_20261028r1','MOD4_H1_FLAT97_FROZEN_MOTION_WM_DIAG_20261028r1'),
 ("if c['active_segment'] is not None:assert set(c['active_segment']['experts'])=={'w35'} and c['active_segment']['owner_parent_pid']==v['owner']['pid']","assert c['active_segment'] is None, 'NEW98 only after actual97 closed/no new learning owner'"),
 ("active_W35_allowed=c['active_segment'] is not None","canonical_None=c['active_segment'] is None"),
 ('run_native91_frozen_flat_WM_N1_once.py','run_native98_frozen_flat_WM_N1_once.py'),
 (old_block,new_block),
 (",allowed_active_W35_owner=launched['owner'],runtime_manifest_SHA=prep['manifest_SHA']",",runtime_manifest_SHA=prep['payload_manifest_SHA']"),
 (",owner=launched['owner'],manifest_SHA=prep['manifest_SHA']",",manifest_SHA=prep['payload_manifest_SHA']"),
 ('same_authorized_session_compressed_transport_v253.py','same_authorized_session_compressed_transport_v227.py'),
 ('source_qualified91_CPU.json','source_qualified97_CPU.json'),('FROZEN91','FROZEN98'),('qualified91 formal','qualified97 formal'),('known_zstd_memory_transport_for_new91_frozen_diag','known_zstd_memory_transport_for_new98_frozen_diag'),('frozen91_secret_memory_only','frozen98_secret_memory_only')])
with (S/'SOURCE_DERIVATION_AND_FIXED_PURPOSE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_qualification=str(qual),qualified_model_metadata=q['model'],purpose='One NEW97 frozen native mean physical N1 until original done or max500controls/2000callbacks5s plus same-case WM1/8 step predictions using actual executed actions; unchanged inherited driver',fixedseed=20260928,model_loads_planned=dict(qualified97=1,old91=0,old93=0),no_learning_GO_optimizer_normalizer_update_or_account_write=True,not_executed=True,changes=audit),f,indent=2)
(S/'HANDOFF.md').write_text('SOURCE PREPARED ONLY. Root global SSH lease required after child source210 finite returns. One NEW qualified97 case. No old91 experiment replay. Exact inherited full-motion driver and WM1/8 step actual-action diagnostics; source97 SDK/400 reset and native contract are checked before model forward. C72 must be None, private c27 EX and shared validation SH required; query only selected UUID. No learner/optimizer/normalizer update/account writer. Max500 controls/2000 callbacks/5s, fixedseed20260928, no retry.\n',encoding='utf8')
rows=[dict(relative=p.relative_to(S).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(S.rglob('*')) if p.is_file()]
with (S/'FROZEN_UNUSED_NEW98_FIXED_CASE_SOURCE_INDEX_V1.json').open('x',encoding='utf8') as f:json.dump(dict(frozen=True,unused=True,rows=rows,AST_passed=True,no_model_read_GPU_SDK_or_network=True),f,indent=2)
print(json.dumps(dict(prepared=True,entry=str(S/'run_NEW98_qualified97_fixed_motion_WM_case_once.py'),files=len(rows))))
