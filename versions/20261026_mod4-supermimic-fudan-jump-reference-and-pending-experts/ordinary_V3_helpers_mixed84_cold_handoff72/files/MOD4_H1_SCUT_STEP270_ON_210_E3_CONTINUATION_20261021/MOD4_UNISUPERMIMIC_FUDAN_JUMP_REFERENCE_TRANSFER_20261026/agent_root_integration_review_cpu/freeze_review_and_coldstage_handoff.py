"""Freeze this review directory. Coldstage facts are root-supplied, no remote query."""
from pathlib import Path
import ast
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
T=HERE.parent.parent
N=T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026'
pair_source=T.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/two_policy50_original_account_controllers/three_slot_finite_owner_v1.py'
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
sub=HERE/('DUAL72_COLDSTAGE_SINGLE_WRITER_PENDING_'+str(time.time_ns()))
sub.mkdir()
owner=N/'controllers/three_slot_finite_owner_v1.py'
common=N/'controllers/three_slot_common_v1.py'
forward=N/'controllers/forwarded_original_owner_control_v1.py'
owner_text=owner.read_text('utf8');pair_text=pair_source.read_text('utf8')
assert "set(specs)=={'h1','e2','recovery'}" in owner_text and "cfg['deferred_experts']==[]" in owner_text
assert "set(specs)=={'e2','recovery'}" in pair_text and "cfg['deferred_experts']==['h1']" in pair_text
assert "authorized_training_seconds']==1548000" in pair_text and "budget_extensions'])==8" in pair_text
assert "authorized_training_seconds']==2268000" in owner_text and "budget_extensions'])==9" in owner_text
for text in (owner_text,pair_text,common.read_text('utf8'),forward.read_text('utf8')):ast.parse(text)
design=dict(epoch=time.time(),attempt_id='temporary-dual72-coldstage-single-original-writer-source-design',
    status='STAGED_ONLY_ORIGINAL_WRITER_UNREACHABLE_PENDING',
    user_steering_as_reported_by_root='The single4090 host210 will be fully powered off/disconnected temporarily',
    root_supplied_coldstage_facts=dict(files=2407,all_bytes_and_full_SHA_verified=True,
        destination='independent coldstaging on dual72',
        original84_deployer_executed=False,owner_launched=False,GO=False,canonical_copied=False,
        evidence_scope='Parent/root report only; this agent made no remote checks'),
    actual83B_closed_snapshot=dict(owner_pid=1493851,owner_creation=1792994651.61,
        original_fee=10943.796510219574,remaining=595256.8240613937,
        authority='Historical closed evidence only; never a substitute for fresh live canonical before a future GO'),
    minimal_safe_state=['Retain all full payload/controller/source/ref/provenance pins in coldstaging',
        'Do not execute84 deployer, launch any owner/node, emit GO, or create an offline charging segment',
        'Do not copy canonical, substitute another ledger path, mirror locks, or repurpose historical reconciliation receipts as a live ledger',
        'Do not create a72 writer, fakeh1 registration/termination, reuse an old GO/token, or backdate charges after reconnect'],
    later_two_GPU_route=dict(
        native_H1=dict(logical_slot='e2',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',
            source='qualified83B H1 frozen PPO Adam829700',source_SHA='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',
            physical_previous='healthy successful83B normalE2 root; separate from H1 bootstrap'),
        normal_E3=dict(logical_slot='recovery',GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
            source_Adam=860800,source_SHA='68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49'),
        single_writer='Original canonical and the original two fcntl locks on210; one CPU owner on210, no210 GPU workload required',
        deferred='normal H1 GPU task explicitly deferred; normalE2 qualified83B source remains paused',
        reachable_owner_required=True,
        unavailable_whole210_host_result='No new training can be admitted under the existing single-writer protocol; STAGED_ONLY',
        current84_controller_limitation='Hardassert all3 specs and empty deferred list; supplying only2 slots rejects before ownership/GO',
        old_pair_controller_limitation='Correct pair selection exists historically, but stale1548000/8extensions and old listener binding cannot be used unchanged',
        future_source_review_needed='After original writer is reachable, a separately reviewed new namespace may narrow current owner scheduling selectors to e2/recovery and explicit deferredh1; preserve current2268000/9extensions, original C/LOCKS/HMAC/charge_values and receipt settlement; keep conservative strict86412.86069250107 entry floor',
        no_pair_code_implemented=True),
    facts_required_before_any_future_run=[
        'Original210 host/canonical and pinned control route actually reachable; original latestowner actualout, canonicalNone and original2locks free freshly verified',
        'No84 owner/node/GO began during migration; distinguish coldstaging roots from fresh execution roots',
        'Both72 physical privateGPU locks and brief shared admission lock actually free; expected GPUs empty and nativeH1>15669MiB/E3>7000MiB, RAM>8GiB, postcopy disk>25GiB',
        'Fresh installed manifest/fullsource/SDK/RSL/native-reference/partial-loss CPU passes; offline order remains offline and actual runtime named order is checked before firststep/Pi',
        'One current original writer gives new signed run/GO and retains3900 lifecycle/3600save/300exit; no budget increase or offline/retrospective grant',
        'Later collector must wait actual children, actual terminal receipts and original settlement; do not infer completion from schedule/rc0/staged files'],
    disconnection_behavior='Existing nodes request complete saved-stop after120s control loss. This is not an offline-run permission; unavailable terminal handoff can delay original settlement and must remain raw error evidence.',
    source_metadata=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)) for path in (owner,common,forward,pair_source)],
    no_remote_GPU_model_checkpoint_raw_NPZ_USD_content_or_Git_budget_lock_action=True,
    no_training_or_pair_owner_implementation=True,
    Git_status='LOCAL_PENDING_ROOT_ORDINARY_PHASE_ARCHIVE')
with (sub/'DUAL72_COLDSTAGE_SINGLE_ORIGINAL_WRITER_PENDING_DESIGN_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(design,stream,indent=2)
note='''当前安全终态为 STAGED_ONLY：root报告双72冷迁2407个文件，字节/fullSHA全部通过，84未部署、无owner/GO、原canonical未复制。本代理未做远端核验。

用户确认210整机将关机/断网，因此原单writer不可达期间不能在72新开训或补造预算。可保持迁移资产，待210原账本/原两锁/固定控制通道恢复后，再以新命名空间做真实准入。

以后若只运行双72的nativeH1(e2)+E3，唯一CPU owner仍可留在210，无需使用210GPU；但现84 owner硬断言三槽且deferred为空，不能直接传两槽。历史双槽owner又含旧1548000/8extensions和旧监听绑定，不可直接搬用。这里只提出待审源码路线，没有实施双槽代码、没有复制canonical、没有起第二writer。

首次observer导入路径修正版已在本目录 observe_mixed84_baselines_native_first_finite_V2_UNUSED.py。除该已修复reader问题，独立本机AST/CPU元数据审查未发现其他bridge/preGO接口静态阻塞；真实目标SDK/RSL/原资源准入仍未被本代理替代。

本目录至此冻结，不再写入。全部source/报告、原observer快照、最小diff、fixture与本子目录交接均待root普通阶段Git归档。
'''
with (HERE/'FINAL_FROZEN_REVIEW_AND_COLDSTAGE_HANDOFF.md').open('x',encoding='utf8') as stream:stream.write(note)
files=[]
for path in sorted(HERE.rglob('*')):
    if not path.is_file():continue
    text=path.suffix in ('.py','.json','.md','.txt','.diff')
    files.append(dict(path=str(path),relative=path.relative_to(HERE).as_posix(),bytes=path.stat().st_size,
                      SHA=H(path) if text else None,
                      archive='SOURCE_REPORT_REQUIRED' if text else 'GENERATED_CACHE_INDEX_ONLY'))
manifest=HERE/'FINAL_FROZEN_DIRECTORY_MANIFEST_PENDING_ROOT_GIT.json'
with manifest.open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),status='FROZEN_NO_FURTHER_AGENT_WRITES',files=files,
                   self_index_not_self_hashed=True,no_actual_model_or_oldraw_content_read=True,
                   Git_status='LOCAL_PENDING_ROOT_ORDINARY_PHASE_ARCHIVE'),stream,indent=2)
print(json.dumps(dict(frozen=True,no_further_writes=True,manifest=str(manifest),
                      files=len(files),coldstage_design=str(sub),live_state='STAGED_ONLY')))
