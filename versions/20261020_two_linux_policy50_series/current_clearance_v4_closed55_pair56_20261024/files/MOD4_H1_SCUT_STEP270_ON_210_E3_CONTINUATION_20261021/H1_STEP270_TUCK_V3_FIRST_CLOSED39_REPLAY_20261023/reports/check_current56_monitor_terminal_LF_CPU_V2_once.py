from pathlib import Path
import ast,hashlib,json,time,tomllib
R=Path(__file__).resolve().parent;T=R.parent.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
read=lambda p:json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
p=R/'check_current56_monitor_and_ordinary_CPU_once.py'
trace='''Traceback (most recent call last):
  File "C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023\\reports\\check_current56_monitor_and_ordinary_CPU_once.py", line 6, in <module>
    assert v['prompt']==a['prompt'] and v['status']==a['status'] and v['rrule']==a['rrule']
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
'''
put('CURRENT56_MONITOR_FIRST_READER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),actual_returncode=1,original_reader=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_error_verbatim=trace,no_reader_rerun=True,no_training_failure_or_host_query=True))
a=read(R/'CURRENT56_WITH_UNUSED_DRAFT_SCOPE_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json')
v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['prompt'].endswith('\n') and v['prompt']==a['prompt'][:-1]
assert v['status']==a['status'] and v['rrule']==a['rrule'] and v['target_thread_id']==a['targetThreadId']
requested_SHA=hashlib.sha256(a['prompt'].encode('utf8')).hexdigest();actual_SHA=hashlib.sha256(v['prompt'].encode('utf8')).hexdigest()
normalized=dict(a,prompt=v['prompt']);put('CURRENT56_APP_TRIMMED_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json',normalized)
helper=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'read_capture_index(p,G)' in s and 'write_capture_index' in s
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED55_114_75_OLD52_53_PEER_PAIR56_BOTH_PPO_WORK_ORDER.json';assert name in s and (T/'reports'/name).is_file()
cfg=read(C/'reports/CURRENT_CLEARANCE_V4_CLOSED55_PAIR56_ORDINARY_CONFIG.json')
assert cfg['destination']=='current_clearance_v4_closed55_pair56_20261024' and cfg['title']=='Archive closed55 complete models, verified old52/53 NPZ relocation and paired56'
assert not (C/'reports/append_current_clearance_v4_closed55_pair56_ordinary_once_STARTED_ACTUAL.json').exists()
report=dict(epoch=time.time(),passed=True,actual_monitor_readback=True,original_raw_prompt_exact=False,only_difference_one_terminal_LF_removed_by_app=True,requested_prompt_SHA=requested_SHA,actual_prompt_SHA=actual_SHA,actual_prompt_chars=len(v['prompt']),requested_prompt_chars=len(a['prompt']),normalized_prompt_exact=True,ACTIVE=True,hourly=True,original_target=v['target_thread_id'],ordinary_AST=True,ordinary_config=cfg,part_aware_complete_capture_index=True,work_order=name,source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),no_monitor_reupdate_or_training_host_query=True)
put('CURRENT56_MONITOR_TERMINAL_LF_NORMALIZATION_AND_ORDINARY_AST_ACTUAL.json',report)
print(json.dumps(report))
