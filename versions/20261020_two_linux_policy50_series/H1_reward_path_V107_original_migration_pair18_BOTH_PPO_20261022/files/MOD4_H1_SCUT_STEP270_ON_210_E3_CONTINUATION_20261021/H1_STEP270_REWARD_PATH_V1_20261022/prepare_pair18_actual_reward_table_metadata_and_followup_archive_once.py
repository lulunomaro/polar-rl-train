from pathlib import Path
import ast,hashlib,json,shutil,time
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';N=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
p=N/'collect_pair_first_actual_GO_positive_PPO_once.py';unused=N/'collect_pair_first_actual_GO_positive_PPO_UNUSED_WITHOUT_REWARD_TABLE.py';shutil.copy2(p,unused)
s=p.read_text('utf8');needle="print(json.dumps(dict(epoch=time.time(),owner=expected,current=current,canonical_active=a,"
addition="""table={};table_lines=[]
with (H/'job0/production_WORKER.log').open(encoding='utf8',errors='replace') as f:
 for line in f:
  if '|' not in line:continue
  fields=[x.strip() for x in line.split('|')]
  if len(fields)>=5:
   try:weight=float(fields[3])
   except ValueError:continue
   table[fields[2]]=weight;table_lines.append(line.rstrip())
expected_rewards={'h1_step270_path_progress':1.,'h1_step270_requested_forward':3.,'h1_scut_fudan_air_wheel_zero_torque':.5,'h1_scut_fudan_leg_tuck':.5,'h1_scut_fudan_wheel_below_base':.5}
assert all(table.get(k)==value for k,value in expected_rewards.items()),table
assert table.get('h1_control_events',0.)==0.
"""
assert s.count(needle)==1;s=s.replace(needle,addition+needle)
s=s.replace("H1_actual_GO=actual,H1_actual_own_compute=own,not_skill", "H1_actual_GO=actual,H1_actual_own_compute=own,H1_actual_registered_reward_weights=table,H1_actual_reward_table_lines=table_lines,reward_table_matches_authorized_recipe=True,not_skill")
p.write_text(s,encoding='utf8');ast.parse(s)
archive=(C/'append_H1_complete122_replay_peer_pair15_PPO_V105_ordinary_once.py').read_text('utf8')
archive=archive.replace('H1_STEP270_E3_BOUNDED_TRACE_PAIR_V14_20261022','H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022')
archive=archive.replace('H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
archive=archive.replace('NEXT_ACTUAL_RECORDED_REPLAY_DIAG_PAIR14_COMPLETE_PAIR15_BOTH_PPO_V105_WORK_ORDER.json','NEXT_ACTUAL_REWARD_PATH_ORIGINAL_MIGRATION_PAIR18_BOTH_PPO_V107_WORK_ORDER.json')
archive=archive.replace('H1_complete122_E3_complete77_recorded_replay_diagnosis_and_peer_storage_pair15_BOTH_PPO','human_authorized_reward_path_original_migration_pair18_BOTH_PPO')
archive=archive.replace('current_pair15_actual_GO_PPO_reference','current_pair18_actual_GO_PPO_and_reward_table_reference')
needle=" for suffix,local in (('', 'shared_H1_native13_actual')"
addition=" for model in json.loads((T/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022/reports/E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(model['final']['local_path']).resolve())]=model['final']['SHA']\n"
assert archive.count(needle)==1;archive=archive.replace(needle,addition+needle)
archivepath=C/'append_H1_reward_path_original_migration_pair18_V107_ordinary_once.py';archivepath.write_text(archive,encoding='utf8');ast.parse(archive)
put(R/'PAIR18_ACTUAL_REWARD_TABLE_AND_ORDINARY_FOLLOWUP_UNUSED_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed=True,metadata_reader=dict(path=str(p),SHA=H(p)),old_unused_reader=dict(path=str(unused),SHA=H(unused)),archive_helper=dict(path=str(archivepath),SHA=H(archivepath)),no_helper_remote_or_GO_run=True,no_new_record_or_tag_to_be_created=True))
put(R/'REWARD_V106_UNIQUE_GIT_ACTUAL_TOOL_RECEIPT.json',dict(remote_main='0fdb24bd67cbb0442c706de643aa7cc3b15cb989',unique_annotated_repair_record_once=True,new_trial_tag='refs/tags/trial-20261022-h1-step270-forward-clearance-reward-v1',old_tag_count=1421,new_total_tag_count=1422,all_old_tag_objects_and_peels_unchanged=True,all_new_Git_blobs_and_full_parts_verified=True,source_text_entries=39789,new_Git_files=406,new_full_large_logs=2,exact_tool_exit_code=0,later_followup_ordinary_only=True))
print(json.dumps(dict(metadata_reward_table_reader_AST=True,ordinary_archive_prepared=True)))
