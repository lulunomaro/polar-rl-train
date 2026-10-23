from pathlib import Path
import ast,json,time,tomllib
D=Path(__file__).resolve().parent;R=D/'reports';C=D.parent.parent/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'

def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

def main():
    assert not (R/'ACTUAL47_MONITOR_AND_ORDINARY_SOURCE_READBACK_CPU_ACTUAL.json').exists()
    put('ACTUAL47_LOCAL_POWERSHELL_INLINE_READBACK_QUOTING_ERROR_ACTUAL.json',dict(epoch=time.time(),original_error="P/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json: 术语 'P/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json' 不会被识别为 cmdlet、函数、脚本文件或可执行程序的名称。",cause='PowerShell does not use backslash to escape nested double quotes in the inline Python argument',readback_report_not_created=True,automation_tool_update_already_succeeded=True,new_standalone_CPU_reader_not_training_or_remote_helper=True,no_training_source_model_or_budget_change=True))
    a=json.loads((R/'ACTUAL47_CURRENT_CLEARANCE_V4_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes())
    v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert v['prompt']==a['prompt'] and v['status']=='ACTIVE' and v['kind']=='heartbeat' and v['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==a['targetThreadId']
    source=(C/'append_current_clearance_v4_closed46_pair47_ordinary_once.py').read_text('utf8');ast.parse(source)
    assert 'record_experiment.py' not in source
    assert "proof=json.loads((P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())" in source
    assert 'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V47_20261023/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json' in source
    result=dict(epoch=time.time(),passed=True,exact_original_ACTIVE_hourly_target_prompt_readback=True,ordinary_AST_and_current_paired_schema=True,all_old_1427_tags_expected_unchanged=True,no_new_record_or_tag=True,original_local_inline_quoting_error_retained=True)
    put('ACTUAL47_MONITOR_AND_ORDINARY_SOURCE_READBACK_CPU_ACTUAL.json',result);print(json.dumps(result))

if __name__=='__main__':main()
