"""Correct unused future metadata; retain the exact unused first draft."""
from pathlib import Path
import ast,hashlib,json,time,shutil
B=Path(__file__).resolve().parent;R=B/'reports';N=B/'E3_bridge_continuation_V6'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
p=N/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json';old=json.loads(p.read_bytes());proof=json.loads((B/'E3_bridge_continuation_V5/reports/RECOVERY_BRIDGE_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json').read_bytes());owner=proof['source210']['owner'];assert proof['passed'] and old['sequence']==5 and old['previous_actual_owner']['pid']!=owner['pid'] and old['previous_stage_dir'].endswith('E3_bridge_continuation_V5');assert not (N/'two50_payloads').exists() and not (N/'reports/RECOVERY_BRIDGE_DEPLOY_STARTED_ACTUAL.json').exists()
draft=N/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN_V1_UNUSED_IDENTITY_ERROR.json';shutil.copy2(p,draft);priorSHA=H(p);old.update(epoch=time.time(),sequence=6,previous_actual_owner=owner,previous_actual_run_id=proof['source72']['actual_GO']['run_id']);p.write_text(json.dumps(old,indent=2),encoding='utf8');assert H(draft)==priorSHA
files=[]
for q in sorted(N.iterdir()):
 if q.is_file() and q.suffix=='.py':ast.parse(q.read_text('utf8'));files.append(dict(path=str(q),SHA=H(q),unused=True))
put(R/'V90_BRIDGE6_UNUSED_IDENTITY_METADATA_CORRECTION_ACTUAL.json',dict(epoch=time.time(),passed_source_metadata_only=True,original_unused_draft=dict(path=str(draft),SHA=priorSHA),corrected=dict(path=str(p),SHA=H(p),sequence=6,actual_previous_owner=owner,actual_previous_run_id=old['previous_actual_run_id']),original_error='Reserved copy updated predecessor root strings but retained bridge4 PID/create and sequence5; neither was a live process proof or used to launch. No bridge6 payload or remote task existed.',unchanged_execution_source_files=files,no_remote_task_or_GO_or_budget_write=True,all_prior_false_error_drafts_preserved=True))
print(json.dumps(dict(unused_config_corrected=True,previous_owner_pid=owner['pid'],no_bridge6_source_prepared_or_remote_Task=True)))
