#!/usr/bin/env python3
"""Create append-only local engineering provenance/index for root Git archive."""
import hashlib
import json
from pathlib import Path
import time

z=Path(__file__).resolve().parents[1]
w=z.parents[2]
def file_record(p):
    data=p.read_bytes()
    return dict(path=str(p),relative=str(p.relative_to(z)) if p.is_relative_to(z) else None,
                bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
errors=[
    dict(id='T2ZH1_ENG_READ_A1_SCOPE_OUTPUT_TRUNCATION',actual='Broad rg over parent task produced large/truncated tool output; no report/source was inferred from omitted text',tool_chunk='608b?',resolution='Switched to named feasibility/host72/resource reports; raw tool history retained'),
    dict(id='T2ZH1_ENG_PUBLIC_FETCH_A1_PRINT_SCHEMA',actual='Select-Object on ordered dictionaries printed blank rows; saved JSON/source files were valid',tool_chunk='900f3d',resolution='Re-read saved JSON as PSCustomObject; all20 HTTP artifacts valid and exact sizes recorded'),
    dict(id='T2ZH1_ENG_MANIFEST_A1_SUM_NULL',actual='Measure-Object did not read ordered-dictionary bytes; original manifest/capacity total emitted0',tool_chunk='43d0ad',source_delta='Original: $sum=($entries | Measure-Object -Property bytes -Sum).Sum; correction: typedlong accumulation foreach dictionary entry plus lowerbound assertion',original_reports=['reports/ORIGINAL_A1_WEIGHTS_MANIFEST_SUM_NULL_NOT_USABLE.json','reports/ORIGINAL_A1_CAPACITY_PLAN_SUM_NULL_NOT_USABLE.json'],resolution='Original reports preserved; corrected files total44253006084, validated against metadata; no weight/model deployment occurred'),
    dict(id='T2ZH1_ENG_LOCAL_SEARCH_A2_PERMISSION_DENIED',actual='Read-only rg discovery encountered rmuc2026_work/unpack_verify_4zomhj13 access denied; stopped reliance on broad output',tool_chunk='75a6b7',resolution='Read explicitly discovered MOD4_HOST72_DUAL4090_ENV_READONLY_20261015 reports only; no permission change'),
    dict(id='T2ZH1_ENG_PATCH_A3_WRONG_LOCAL_PATH',actual='apply_patch targeted nonexistent parent20261025 path; operation failed before file read/write',resolution='Corrected to parent20261021 and actual preparation directory; no other workspace files mutated'),
]
# Unknown tool ID is explicitly unknown, never fabricated.
errors[0]['tool_chunk']=None
ledger=dict(schema_version=1,id='T2ZH1_ENG_PREPARATION_LOCAL_FINAL_20261025_A4',epoch=time.time(),
    status='SOURCE_MANIFEST_AND_SCRIPTS_PREPARED_NOT_REMOTE_INSTALLED',
    git_status='LOCAL_PENDING_ROOT_UNIQUE_ANNOTATED_TRIAL_AND_REMOTE_VERIFICATION',
    actual_actions=dict(local_read=True,local_source_and_metadata_HTTP=True,source_snapshot_files=14,
        local_AST_help_digest_QA=True,remote_connection=False,source_clone=False,environment_install=False,
        weight_download=False,dataset_download=False,official_dependency_CPU_import=False,GPU_query=False,
        GPU_compute=False,training=False,inference=False,physics_rollout=False,process_signal=False,
        budget_or_canonical_change=False,Git_commit_or_push=False,subdelegation=False),
    errors=errors,
    corrected_manifest=file_record(z/'WEIGHTS_MANIFEST.json'),capacity_plan=file_record(z/'CAPACITY_PLAN.json'),
    immutable_upstream_commit='c72f051f5cffcb1f372a32bc488df273556d39b9',
    official_weights=dict(required_files=13,bytes=44253006084,status='NOT_DOWNLOADED',
        Wan_revision='921dbaf3f1674a56f47e83fb80a34bac8a8f203e',BWM_revision='738a8d3c008e637b8b1b18d5e98a82f6de9c04aa',
        Wan_license='Apache2DeclaredHFCard',BWM_checkpoint_license='NotDeclaredInHFCardMetadata',
        BWM_author_code_license='Apache2 at main; not assumed checkpoint license'),
    verification=dict(latest_receipt=str(sorted((z/'reports').glob('LOCAL_VALIDATION_*_ACTUAL.json'))[-1]),
        Python_AST_and_CLI_and_manifest_and_synthetic_digest='9checksPASS',PS_scripts_AST='2PASS',
        disabled_shell_bash_n='PASS',remote_environment_or_actual_models='NOT_TESTED'),
    resource_status=dict(preexisting_guard_GiB=25,current72_free='NOT_REMEASURED',
        driver_snapshot='535.54.03 on20261015; CUDA12.x minorcompat conditional, application cu128unknown',
        future_dual4090='Requires two actualUUID release receipts; unknownpeer not queried/reserved',
        official_DDP_24GB_fit='NOT_VERIFIED; static optimizer memory concern; no runnableclaim'),
    required_future_work=['RootserialCPUsource/environment/weight preparation afterM4resource release',
        'Archiveallremoteinstall/download/CPUcheckfailureorsuccessreceipts',
        'H1synchronizeddataandactionadapter/grouping/split',
        'ExplicitH1completionandcomplete-save boundary',
        'BothGPUUUIDownershiprelease and applicationmemory/driver strategy admission',
        'SeparatefuturetrainingGO;disabledlaunchdoesnotexecute'],
    policy_evidence=[])
for rel in ['AGENTS.md','polar-rl-train/AGENTS.md','polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md',
            'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_DUAL4090_ENVIRONMENT_SUMMARY_ACTUAL.json']:
    p=w/rel
    if p.is_file():
        ledger['policy_evidence'].append(file_record(p))
out=z/'reports/ENGINEERING_SCOPE_AND_ERROR_LEDGER_ACTUAL.json'
with out.open('x',encoding='utf-8') as stream:
    json.dump(ledger,stream,indent=2,ensure_ascii=False)
entries=[file_record(p) for p in sorted(z.rglob('*')) if p.is_file() and p.name!='ENGINEERING_FINAL_INDEX_ACTUAL.json']
idx=z/'reports/ENGINEERING_FINAL_INDEX_ACTUAL.json'
with idx.open('x',encoding='utf-8') as stream:
    json.dump(dict(schema_version=1,id='T2ZH1_ENG_ALL_LOCAL_FILES_INDEX_20261025_A4',epoch=time.time(),
                   archive_status='PENDING_ROOT_GIT',files=entries,index_self_excluded=True,
                   errors_and_originals_included=True,total_bytes=sum(x['bytes'] for x in entries)),stream,indent=2,ensure_ascii=False)
print(json.dumps(dict(ledger=str(out),index=str(idx),files=len(entries),bytes=sum(x['bytes'] for x in entries))))
