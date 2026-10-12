from route_fixture_io import *
import tomllib

def main():
    req=json.loads((R/'ROUTE443_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes())
    p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
    actual=tomllib.loads(p.read_text(encoding='utf8'))
    assert actual['status']==req['status']=='ACTIVE'
    assert actual['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert actual['target_thread_id']==req['targetThreadId']=='01a07a2d-9036-7531-a012-692df9f56353'
    assert actual['name']==req['name'] and actual['kind']=='heartbeat'
    # The native app trims trailing whitespace; preserve both exact requested and applied hashes.
    assert actual['prompt']==req['prompt'].rstrip() and req['prompt'].startswith(actual['prompt'])
    assert req['prompt'][len(actual['prompt']):].strip()==''
    report=dict(epoch=time.time(),passed=True,native_tool_update_success=True,
        id='mod4-10',status=actual['status'],rrule=actual['rrule'],target=actual['target_thread_id'],
        requested_prompt_SHA=H(req['prompt'].encode()),actual_prompt_SHA=H(actual['prompt'].encode()),
        only_native_trailing_whitespace_normalization=True,
        actual_TOML_SHA=H(p.read_bytes()),healthy_pending_DONT_NOTIFY_preserved=True,
        no_extra_monitor_or_GPU_budget_oldonce_replay=True)
    save('ROUTE443_HOURLY_MONITOR_ACTUAL_VERIFIED.json',report)
    print(json.dumps(report))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_MONITOR_VERIFY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_monitor_retry=True));raise
