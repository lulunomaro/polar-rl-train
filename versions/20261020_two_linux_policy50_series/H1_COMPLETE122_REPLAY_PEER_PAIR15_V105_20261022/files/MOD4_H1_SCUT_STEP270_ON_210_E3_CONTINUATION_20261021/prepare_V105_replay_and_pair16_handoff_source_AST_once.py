from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;R=T/'reports';old=T/'prepare_V104_pair15_handoff_and_ordinary_archive_once.py';new=T/'prepare_V105_pair16_replay_handoff_and_ordinary_archive_once.py'
s=old.read_text('utf8').replace('V104','V105')
oldpaths="P=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V13_20261022';N=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V14_20261022';F=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022'"
newpaths="P=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V14_20261022';N=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022';F=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V16_20261022'"
assert s.count(oldpaths)==1;s=s.replace(oldpaths,newpaths).replace('sequence=15','sequence=16').replace('boundedtrace_2210v15','boundedtrace_2210v16')
s=s.replace('V105_CLOSED_PAIR13_','V105_CLOSED_PAIR14_').replace('V105_PAIR14_','V105_PAIR15_').replace('V105_SAME_APPROVED_RETENTION_PAIR15_','V105_SAME_APPROVED_RETENTION_PAIR16_').replace('V105_H1_COMPLETE122_HEALTH_EPISODE420_ACTUAL','V105_H1_COMPLETE122_HEALTH_EPISODE_ACTUAL')
s=s.replace('NEXT_ACTUAL_H1_COMPLETE122_EPISODE420_THREE_RAW_PEER_PAIR14_BOTH_PPO_V105_WORK_ORDER.json','NEXT_ACTUAL_RECORDED_REPLAY_DIAG_PAIR14_COMPLETE_PAIR15_BOTH_PPO_V105_WORK_ORDER.json')
s=s.replace('latest_V105_overrides_V103_pair13_active_pair14_reserved','latest_V105_overrides_V104_pair14_active_pair15_reserved')
needle='put(R/work,v)';assert s.count(needle)==1
s=s.replace(needle,"v['user_requested_recorded_replay_diagnosis']=read(T/'H1_STEP270_REPLAY_DIAG_20261022_V105/reports/RECORDED_STEP_REPLAY_DIAGNOSIS_AND_LIMITS_ACTUAL.json');v['replay_diagnosis_no_training_reward_request_or_clock_change']=True;"+needle)
start=s.index("s=(C/'append_");end=s.index("start=s.index(' index=dict(epoch=')",start)
s=s[:start]+'''s=(C/'append_H1_complete122_episode420_peer_pair14_PPO_V104_ordinary_once.py').read_text('utf8').replace("P=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V13_20261022'","P=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V14_20261022'").replace("B/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V14_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'","B/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'")
extra="""known={}
 for rp in (T/'H1_STEP270_REPLAY_DIAG_20261022_V105/reports').glob('*.json'):
  value=json.loads(rp.read_bytes());records=list(value.get('artifacts',[]))
  if isinstance(value.get('artifact'),dict):records.append(value['artifact'])
  if value.get('path') and value.get('SHA'):records.append(value)
  for row in records:
   if row.get('path') and row.get('SHA') and Path(row['path']).is_file():known[str(Path(row['path']).resolve())]=row['SHA']
"""
assert s.count(' known={}\\n')==1;s=s.replace(' known={}\\n',' '+extra)
'''+s[end:]
s=s.replace('current_pair14_actual_GO_PPO_reference','current_pair15_actual_GO_PPO_reference').replace('complete122_episode420_no_step_PASS_E3_complete76_three_retained_raw_peer_storage_pair14','complete122_E3_complete77_recorded_replay_diagnosis_and_peer_storage_pair15')
s=s.replace('append_H1_complete122_episode420_peer_pair14_PPO_V105_ordinary_once.py','append_H1_complete122_replay_peer_pair15_PPO_V105_ordinary_once.py').replace('V105_COMPLETE122_PEER_PAIR14_ORDINARY_ARCHIVE_ARGS.json','V105_COMPLETE122_REPLAY_PAIR15_ORDINARY_ARCHIVE_ARGS.json').replace('H1_COMPLETE122_EPISODE420_PEER_PAIR14_V105_20261022','H1_COMPLETE122_REPLAY_PEER_PAIR15_V105_20261022').replace('Record complete H1 122 E3 76, retained raw peer storage and pair14 both PPO','Record actual recorded step replay diagnosis, H1 122 E3 77 complete and pair15 both PPO')
ast.parse(s);new.open('x',encoding='utf8').write(s)
with (R/'V105_REPLAY_AND_CURRENT_PAIR_HANDOFF_SOURCE_AST_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),new_helper=str(new),SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_local_metadata_future_reserved_and_archive_preparation=True,no_new_training_reward_phase_or_actor_change=True,diagnostic_artifacts_producer_SHA_in_archive_index_without_rehash=True),f,indent=2)
print(json.dumps(dict(new_helper=str(new),source_AST_passed=True)))
