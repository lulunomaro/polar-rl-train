"""Read only the restarted player's existing snapshots for a bounded 45 seconds."""
from pathlib import Path
import json,time,os,traceback
B=Path(__file__).resolve().parent
out=B/'reports/FIXED_PLAYER_BOUNDED_STATUS_OBSERVATION_ACTUAL.json';assert not out.exists()
start=json.loads((B/'reports/REQUESTED_PLAYER_V2_LAUNCH_AND_CURRENT_ACTUAL.json').read_text('utf-8-sig'))
run=Path(start['run_path']);pid=start['interactive_current']['pid'];samples=[];read_errors=[]
began=time.monotonic()
try:
    while time.monotonic()-began<45:
        assert not (run/'INTERACTIVE_ERROR.txt').exists(),(run/'INTERACTIVE_ERROR.txt').read_text('utf8') if (run/'INTERACTIVE_ERROR.txt').exists() else ''
        try:
            packet=json.loads((run/'INTERACTIVE_CURRENT.json').read_text('utf8'))
        except (OSError,json.JSONDecodeError) as exc:
            read_errors.append(dict(epoch=time.time(),error=repr(exc)));time.sleep(.1);continue
        assert packet['pid']==pid and packet['finite']
        assert packet['checkpoint']=='latest_moe_scut_fudan_hour7_20261019.onnx'
        assert time.time()-packet['epoch']<3,packet
        samples.append(packet);time.sleep(1)
    assert len(samples)>=40 and samples[-1]['epoch']-samples[0]['epoch']>40
    result=dict(status='PASS',epoch=time.time(),run_path=str(run),pid=pid,elapsed_seconds=time.monotonic()-began,
        fresh_complete_snapshots=len(samples),first=samples[0],last=samples[-1],
        source_checkpoint_bound=True,no_interactive_error_file_observed=True,
        status_write_warnings_path=str(run/'STATUS_WRITE_WARNINGS.jsonl'),
        status_write_warnings_present=(run/'STATUS_WRITE_WARNINGS.jsonl').exists(),read_errors=read_errors,
        did_not_send_input_or_change_pause_or_control=True,not_a_skill_qualification=True)
    with out.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))
except BaseException:
    with (B/'reports'/('FIXED_PLAYER_OBSERVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),run_path=str(run),error=traceback.format_exc(),samples=samples,read_errors=read_errors),f,ensure_ascii=False,indent=2)
    raise
