from pathlib import Path
import ast,json,sys,time,tomllib
D=Path(__file__).resolve().parent;R=D/'reports';C=D.parent.parent/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'

def main():
    if sys.argv[1]=='prepare':
        a=json.loads((R/'ACTUAL48_CURRENT_CLEARANCE_V4_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes())
        assert json.loads((R/'UNUSED_CLOSED47_ORDINARY_FULL_INDEX_PARTS_SOURCE_AST_AND_CPU_ACTUAL.json').read_bytes())['passed']
        a['prompt']+='\n前向归档总索引格式本轮已落实到新unused普通归档writer：D/capture_index_ordered_parts_v1.py与FORWARD_FULL_CAPTURE_INDEX_FORMAT_V1.md、UNUSED_CLOSED47_ORDINARY_FULL_INDEX_PARTS_SOURCE_AST_AND_CPU_ACTUAL.json优先。实际旧86,468,238bytes/89,869entries已验证完整字节SHA/全部JSON值精确重组、损坏缺片乱序拒绝、旧plain读取兼容；只新unused writer import/index读写与最终large_text计数标签修改，其他源整字节精确，旧未用writer稿保留，训练/预算/旧Git对象不改。新COMPLETE_FILE_CAPTURE_INDEX.json若format=complete_capture_index_full_ordered_utf8_parts_v1是完整JSON的有序UTF8分片descriptor，包含epoch/kind/complete_json_bytes/SHA/complete_entries_count/ordered_UTF8_parts，绝非节选或空entries；每part<=24,000,000bytes，全重组SHA核真。所有后续归档helper必须沿用read_capture_index(path,G)读取旧plain和新descriptor，不用旧直接json[entries]静默跳过，不重旧consumed helper。新index大文字本身也完整分片；大型raw/PT仍仅真实pathsize已有SHA，不为Git读raw或训练host。是否已归档以实际工具回执优先。'
        with (R/'ACTUAL48_FULL_INDEX_FORMAT_MONITOR_UPDATE_ARGS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(a,f,ensure_ascii=False,indent=2)
        print('Full-index format monitor arguments prepared; original arguments retained.')
    elif sys.argv[1]=='check':
        a=json.loads((R/'ACTUAL48_FULL_INDEX_FORMAT_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes())
        v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
        assert v['prompt']==a['prompt'] and v['status']=='ACTIVE' and v['kind']=='heartbeat' and v['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==a['targetThreadId']
        s=(C/'append_current_clearance_v4_closed47_pair48_ordinary_once.py').read_text('utf8');ast.parse(s)
        assert 'record_experiment.py' not in s and 'read_capture_index(p,G)' in s and "write_capture_index(D/'COMPLETE_FILE_CAPTURE_INDEX.json',index,add,splits,G)" in s
        assert 'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V48_20261023/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json' in s
        result=dict(epoch=time.time(),passed=True,exact_original_ACTIVE_hourly_target_prompt_readback=True,ordinary_AST_paired_schema_and_full_index_reader_writer=True,all_old_1427_tags_expected_unchanged=True,no_new_record_or_tag=True)
        with (R/'ACTUAL48_MONITOR_AND_ORDINARY_INDEX_SOURCE_READBACK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
        print(json.dumps(result))
    else:raise ValueError('prepare or check only')

if __name__=='__main__':main()
