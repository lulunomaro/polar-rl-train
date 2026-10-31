"""Final metadata-only indices; no actual capture, model, asset or test replay."""
from pathlib import Path
import hashlib
import json
import time

N = Path(__file__).resolve().parent
B = N/'B_LOSSLESS_EVAL_SOURCE'


def ref(p):
    raw = p.read_bytes()
    return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def put(p, value):
    with p.open('x',encoding='utf8') as f:
        json.dump(value,f,indent=2,allow_nan=False)


def main():
    proof = json.loads((B/'reports/CPU227B_LOSSLESS_ROUNDTRIP_AND_LIMIT_ACTUAL.json').read_bytes())
    assert proof['passed']
    rows = []
    for p in sorted(B.rglob('*')):
        if not p.is_file() or p.suffix not in ('.py','.json','.md'):
            continue
        assert not p.name.endswith(('.partial','.active'))
        rows.append(dict(relative=p.relative_to(B).as_posix(),**ref(p)))
    value = dict(schema='mod4.227B.lossless_original_RM70_eval_source_index.v1',frozen_epoch=time.time(),
        status='SOURCE_AND_SYNTHETIC_WRITER_CPU_FROZEN_ACTUAL_SDK_CASE_PENDING',files=rows,file_count=len(rows),
        actual_byte_coverage='UNKNOWN',wall_seconds=dict(worker=3600,parent=3780,original_finite_ceiling=3900),
        simulation_max=dict(envs=20000,controls=1600,physics=12800,feedback=3200,seconds=32),
        format='mod4.227.lossless_fieldset_positional_jsonl.v1',retained_byte_limit=192*1024**2,
        synthetic_artifacts_metadata_only=[proof['roundtrip_producer'],proof['synthetic_4KiB_limit_producer']],
        CPU=dict(groups=proof['groups'],source_AST_count=proof['source_AST_count'],read_counts=proof['read_counts']),
        original222_source_partial_and_JSONL_modified_or_read=False,old_fixture_replays=0,
        child_model_raw_asset_Torch_SDK_GPU_SSH_Git_calls=0,no_new_learning_GO_or_budget_grant=True,
        full_expert_skill='UNKNOWN',full_SuperMimic=False,
        actual_new_Task_CNone_CIM_resource_model_SDK_execution='PENDING_ROOT_ONLY',
        Git_status='PENDING_ROOT_ORDINARY_APPEND_OR_NEXT_REAL_PHASE')
    p = B/'INDEX227B_FROZEN.json'
    put(p,value)
    br = ref(p)
    ar = ref(N/'A_PPO_SOURCE/INDEX227A_FROZEN.json')
    assert ar['SHA']=='b71e3df7327b93c3849eb1ced2ba002e004d714e69b444b0ab08914d18676ed6'
    master = dict(schema='mod4.227.independent_A_B_frozen_index.v1',frozen_epoch=time.time(),
        A=ar,B=br,A_independent_of_B=True,
        A_status='SOURCE_FROZEN_QUALIFIED_FULL_PPO_NEXT_SOLE_WINDOW_ROOT_ONLY',
        B_status='SOURCE_FROZEN_ACTUAL32S_COVERAGE_AND_SKILL_PENDING',
        top_level_files=[ref(Path(__file__)),ref(N/'reports/INDEX227_ORIGINAL_METADATA_FREEZE_ERROR.json')],
        not_executed=['new remote admission','new learning GO','new SDK skill case','actual capture decode'],
        preserved_false_partial=['Original219 preGO sender refusal','Original222740control bounded_window_complete=false',
                                'All prior physical/source/report errors remain original','First index assembly syntax error preserved'],
        Git_status='PENDING_ROOT_NEXT_ORDINARY_APPEND_OR_REAL_PHASE')
    put(N/'INDEX227_FROZEN.json',master)
    print(json.dumps(dict(B_INDEX=br,B_files=len(rows),CPU=value['CPU'],master_INDEX=ref(N/'INDEX227_FROZEN.json'))))
    names=('evaluate227_CLOSED_W35_FULL_RM70_LOSSLESS_UNUSED_once.py','rm70_intervals227.py',
           'positional_rows227.py','decode227_positional.py','make227B_qualified_eval_TASK_SOURCE_ONLY.py')
    for name in names:
        row=next(r for r in rows if r['relative']==name)
        print(json.dumps({k:row[k] for k in ('relative','bytes','SHA')}))


if __name__=='__main__':
    main()
