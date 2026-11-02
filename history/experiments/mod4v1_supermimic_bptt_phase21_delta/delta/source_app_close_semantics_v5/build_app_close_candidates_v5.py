"""Bounded source-text transformer only. Never import/execute any worker/owner."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'source_resume_runtime_v2'
WORKER_OLD = 'worker_supermimic_bptt_pre_reset_candidate_v4.py'
WORKER_NEW = 'worker_supermimic_bptt_app_close_candidate_v5.py'
OWNERS = (
    ('supermimic_original_owner_pre_reset_candidate_v4.py',
     'supermimic_original_owner_app_close_candidate_v5.py'),
    ('supermimic_original_owner_shared_pre_reset_candidate_v4.py',
     'supermimic_original_owner_shared_app_close_candidate_v5.py'),
)


def replace_one(text, old, new):
    if text.count(old) != 1:
        raise ValueError('exact source anchor count differs: ' + old[:100])
    return text.replace(old, new, 1)


def record(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def normalized_source(text, *, undo_worker=False, undo_owner=False):
    if undo_worker:
        text = replace_one(text, 'from resume_runtime_app_close_v5 import (', 'from resume_runtime_install_hook_v4 import (')
        text = replace_one(text, ',BoundedPoseCacheEventsV5,force_pose_cache_event_receipt_v5)', ')')
        text = replace_one(text, "pose_cache_events=BoundedPoseCacheEventsV5(lambda value:put(out/'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json',value))", 'pose_cache_events=[]')
        text = replace_one(text, '  record_pose_cache_event=pose_cache_events',
            "  def record_pose_cache_event(event):\n   pose_cache_events.append(dict(event));put(out/'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json',dict(events=pose_cache_events,no_extra_observation_getters=True))")
        text = replace_one(text, "  pose_cache_flush_error=force_pose_cache_event_receipt_v5(pose_cache_events,out,role=role);error=error or pose_cache_flush_error\n", '')
        text = replace_one(text, 'closure=close_original_resources(bridge,env,ns,lambda name,value:put(out/name,value),job_root=J,task=task,primary_error=error)',
                           'closure=close_original_resources(bridge,env,ns,lambda name,value:put(out/name,value))')
    if undo_owner:
        text = replace_one(text, 'from resume_runtime_app_close_v5 import ', 'from resume_runtime_install_hook_v4 import ')
        text = replace_one(text, WORKER_NEW, WORKER_OLD)
    return ast.dump(ast.parse(text), include_attributes=False)


def main():
    originals = [OLD / WORKER_OLD] + [OLD / old for old, _ in OWNERS]
    before = [record(path) for path in originals]
    worker = (OLD / WORKER_OLD).read_text(encoding='utf-8')
    candidate = replace_one(worker, 'from resume_runtime_install_hook_v4 import (', 'from resume_runtime_app_close_v5 import (')
    candidate = replace_one(candidate, 'preserve_worker_error,close_original_resources)',
                            'preserve_worker_error,close_original_resources,BoundedPoseCacheEventsV5,force_pose_cache_event_receipt_v5)')
    candidate = replace_one(candidate, 'pose_cache_events=[]',
                            "pose_cache_events=BoundedPoseCacheEventsV5(lambda value:put(out/'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json',value))")
    candidate = replace_one(candidate,
        "  def record_pose_cache_event(event):\n   pose_cache_events.append(dict(event));put(out/'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json',dict(events=pose_cache_events,no_extra_observation_getters=True))",
        '  record_pose_cache_event=pose_cache_events')
    candidate = replace_one(candidate, '  closure=close_original_resources(bridge,env,ns,lambda name,value:put(out/name,value))',
        "  pose_cache_flush_error=force_pose_cache_event_receipt_v5(pose_cache_events,out,role=role);error=error or pose_cache_flush_error\n  closure=close_original_resources(bridge,env,ns,lambda name,value:put(out/name,value),job_root=J,task=task,primary_error=error)")
    if normalized_source(candidate, undo_worker=True) != ast.dump(ast.parse(worker), include_attributes=False):
        raise ValueError('worker AST contains a change outside the explicit witness/recorder whitelist')
    (HERE / WORKER_NEW).write_text(candidate, encoding='utf-8')
    for old, new in OWNERS:
        original = (OLD / old).read_text(encoding='utf-8')
        candidate_owner = replace_one(original, 'from resume_runtime_install_hook_v4 import ', 'from resume_runtime_app_close_v5 import ')
        candidate_owner = replace_one(candidate_owner, WORKER_OLD, WORKER_NEW)
        if normalized_source(candidate_owner, undo_owner=True) != ast.dump(ast.parse(original), include_attributes=False):
            raise ValueError('owner AST contains a change outside shim import / worker filename')
        (HERE / new).write_text(candidate_owner, encoding='utf-8')
    after = [record(path) for path in originals]
    if before != after:
        raise ValueError('old V4 source changed during source-copy build')
    inputs = originals + [OLD / name for name in (
        'resume_runtime_install_hook_v4.py', 'resume_runtime_contracts_v3.py', 'resume_runtime_contracts_v2.py')]
    inputs += [ROOT / 'discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py',
               ROOT / 'reports/SDK_WARP_BUFFER_APPCLOSE_SOURCE_V3.json',
               ROOT / 'source_pose_cache_runtime_adapter_v3/DELIVERABLES_SHA256_V3.json',
               ROOT / 'source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py']
    receipt = dict(kind='NEW_ONLY_APP_CLOSE_SOURCE_THIN_PATCH_V5_NOT_EXECUTED',
                   original_V4_reverified_unchanged=True, normalized_whole_AST_equal_after_whitelist_undo=True,
                   whitelist_worker=['shim import', 'bounded first3/last/counters pose recorder',
                                     'forced final/error pose receipt flush', 'close evidence keyword arguments'],
                   whitelist_owners=['shim import', 'new worker filename'],
                   accounting_lock_deadline_admission_wait_save_learner_physics_changes=0,
                   SDK_Torch_native_PT_GPU_or_training_execution=0,
                   inputs=[record(path) for path in inputs],
                   outputs=[record(HERE / name) for name in [WORKER_NEW] + [new for _, new in OWNERS]])
    (HERE / 'BUILD_APP_CLOSE_CANDIDATES_V5.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(old_sources=len(before), new_source_copies=3,
                          protected_AST_equal=True, SDK_Torch_PT_training_executed=0)))


if __name__ == '__main__':
    main()
