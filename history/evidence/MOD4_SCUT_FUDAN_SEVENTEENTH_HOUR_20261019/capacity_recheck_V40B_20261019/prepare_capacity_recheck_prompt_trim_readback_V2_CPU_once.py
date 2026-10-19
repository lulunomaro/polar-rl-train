"""Retain the failed strict readback and normalize only the app-trimmed terminal LF."""
from pathlib import Path
import ast,hashlib,json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
p=B/'AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_ARGS.json';a=json.loads(p.read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['prompt'].endswith('\n') and a['prompt'][:-1]==actual['prompt']
for k in ('name','kind','status','rrule'):assert a[k]==actual[k]
assert a['targetThreadId']==actual['target_thread_id']
report=dict(epoch=time.time(),trial_id='capacity-recheck-V40B-app-terminal-LF-strict-readback',original_args=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes())),original_prompt_characters=len(a['prompt']),original_prompt_SHA=H(a['prompt'].encode()),actual_prompt_characters=len(actual['prompt']),actual_prompt_SHA=H(actual['prompt'].encode()),only_actual_difference_is_one_terminal_LF=True,all_other_app_fields_exact=True,original_archive_failed_before_note_DEST_git_add_commit_push=True,original_archive_source_and_error_retained=True,no_GPU_Task_native_transport_or_account_replay=True,repair='New V2 arguments remove the terminal LF and add a factual readback-error appendix without trailing whitespace. Original arguments/source/error are retained; do not rerun the original failed archive helper.')
with (R/'CAPACITY_RECHECK_V40B_TERMINAL_LF_ORIGINAL_ERROR_AND_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
a['prompt']=a['prompt'][:-1]+'\n本轮V40B首次ordinary补档的严格appreadback发现应用仅裁去prompt末尾一个LF，旧args/失败helper/error均保留；V2修正该末LF并追加此事实后重新exact readback，未重容量reader/GPU/Task/native/轨迹/账。补档仍同pending阶段ordinary提交，不新record/tag；以later实际Git回执为准。'
q=B/'AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_V2_ARGS.json'
with q.open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
s=(B/'archive_capacity_recheck_V40B_ordinary_supplement_once.py').read_text('utf8')
s=s.replace('AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_ARGS.json','AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_V2_ARGS.json').replace('AUTOMATION_V40B_CAPACITY_RECHECK_ACTUAL_READBACK_CPU.json','AUTOMATION_V40B_V2_CAPACITY_RECHECK_ACTUAL_READBACK_CPU.json').replace('CAPACITY_RECHECK_V40B_GIT_ORIGINAL_ERROR.json','CAPACITY_RECHECK_V40B_V2_GIT_ORIGINAL_ERROR.json')
ast.parse(s)
with (B/'archive_capacity_recheck_V40B_ordinary_supplement_V2_once.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
print(json.dumps(dict(only_terminal_LF_actual_difference=True,original_error_retained=True,V2_args_and_archive_prepared=True,no_training_or_capacity_reader_replay=True)))
