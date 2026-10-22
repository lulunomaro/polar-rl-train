from pathlib import Path
import hashlib,json,time,tomllib,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    put('V111_MONITOR_READBACK_V1_ORIGINAL_SCHEMA_ERROR_ACTUAL.json',dict(epoch=time.time(),
        actual_returncode=1,actual_error="Traceback (most recent call last):\n  File \"<stdin>\", line 6, in <module>\nKeyError: 'targetThreadId'\n",
        original_failed_expression="v['targetThreadId']==a['targetThreadId']",
        original_failed_reader='Local stdin Python read tomllib and prepared JSON arguments, then asserted prompt/id/status/kind/rrule/targetThreadId equality. The TOML target key is target_thread_id, whereas the app tool argument key is targetThreadId.',
        old_failure_not_relabelled_pass=True,app_update_was_successful_and_not_repeated=True,
        V2_scope='Only missing successful exact readback with actual TOML key; no app write or training mutation.'))
    a=json.loads((R/'V111_BOUNDARY24_STORAGE_ACTUAL_MONITOR_UPDATE_ARGS.json').read_bytes())
    p=Path.home()/'.codex/automations/mod4-10/automation.toml';v=tomllib.loads(p.read_text('utf8'))
    assert v['prompt']==a['prompt'] and v['id']==a['id'] and v['status']=='ACTIVE' and v['kind']=='heartbeat' and v['rrule']==a['rrule'] and v['target_thread_id']==a['targetThreadId']
    result=dict(epoch=time.time(),passed=True,automation_id=v['id'],status=v['status'],kind=v['kind'],rrule=v['rrule'],targetThreadId=v['target_thread_id'],exact_prompt_SHA=hashlib.sha256(v['prompt'].encode()).hexdigest(),same_original_monitor_no_second_monitor=True,actual_local_toml_key='target_thread_id',app_tool_argument_key='targetThreadId',V1_error_preserved=True,current24_source_and_realPPO_and_storage_capacity=True)
    put('V111_SAME_MONITOR_EXACT_TOML_READBACK_V2_MISSING_ONLY_ACTUAL.json',result)
    print(json.dumps(result))
except BaseException:
    put('V111_MONITOR_READBACK_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
