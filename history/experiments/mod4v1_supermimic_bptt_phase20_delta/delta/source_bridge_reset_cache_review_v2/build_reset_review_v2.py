"""Bounded local source/closed metadata join; never imports audited sources."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
from reset_cache_and_failclosed_candidates_v2 import terminal_receipt_decision

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT.parent/'mod4v1_experts_fulldr_rm70_20261101'
CLOSED_DIR=ROOT/'reports'/'ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527'
GET=OLD/'diagnostics'/'W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1'
AUD=ROOT/'discovery'/'reward_command_audit_v1'

def put(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser();p.add_argument('--extra-source',action='append',default=[]);a=p.parse_args()
    closed=json.loads((CLOSED_DIR/'CLOSED_RESULT.json').read_text(encoding='utf-8'))
    paths=[CLOSED_DIR/'CLOSED_RESULT.json',
           ROOT/'source_runtime'/'worker_supermimic_bptt.py',
           ROOT/'source_runtime'/'native_supermimic_bridge.py',
           ROOT/'source_runtime'/'supermimic_original_owner.py',
           ROOT/'source_runtime'/'supermimic_original_owner_shared_v2.py',
           ROOT/'source_core_review'/'evidence'/'geometry.py',
           ROOT/'discovery'/'sdk_reward_command_call_order_v1'/'envs'/'manager_based_rl_env.py',
           GET/'ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json',
           GET/'actual_module_spec_v2'/'0'/'articulation.py',
           GET/'actual_module_spec_v2'/'1'/'articulation_data.py',
           GET/'base_factory_v4'/'assets'/'articulation'/'base_articulation_data.py',
           GET/'base_factory_v4'/'utils'/'backend_utils.py',
           AUD/'E0'/'runtime'/'isaac'/'mod4'/'mod4_task.py',
           AUD/'E3'/'runtime'/'isaac'/'mod4'/'e3_recovery_runtime_v1.py',
           AUD/'W35'/'runtime'/'isaac'/'mod4'/'reset208_v3.py',
           AUD/'CURB_PROTECTED878'/'runtime'/'isaac'/'mod4'/'curb20_entry_v3_full_pose_reset.py',
           ROOT/'reports'/'SDK_RESET_CACHE_BACKEND_SOURCE_V2.json',
           ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'backend'/'articulation.py',
           ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'backend'/'articulation_data.py',
           ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'base'/'manager_based_env.py',
           ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'base'/'timestamped_buffer.py',
           ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'isaacsim'/'package_init.py']
    rows=[]
    for row in closed['rows']:
        role=row['role'];waitpath=CLOSED_DIR/'roles'/role/'PARENT_WAITED_ACTUAL.json'
        paths.append(waitpath);waited=json.loads(waitpath.read_text(encoding='utf-8'))
        trace=(row.get('error') or {}).get('error','')
        match=re.search(r"AssertionError: \('SDK quaternion convention', ([0-9.eE+-]+)\)",trace)
        rows.append(dict(role=role,original_status=row['status'],
                         actual_BPTT_policy_steps_as_produced=row['actual_BPTT_policy_steps'],
                         producer_counts=row['counts'],FINAL_present=row['final'] is not None,
                         WORKER_ERROR_present=row['error'] is not None,
                         guard_error_from_actual_trace=None if match is None else float(match.group(1)),
                         startup_guard_error=(row.get('startup') or {}).get('quaternion_gravity_max_error'),
                         actual_returncode=waited['returncode'],original_error_reported=waited['original_error'],
                         no_update_before_learner_constructed_inference=bool(match),
                         BPTT_zero_is_producer_measurement=False if match else None,
                         candidate_owner_reclassification=terminal_receipt_decision(waited['returncode'],row['final'],row['error'],role)))
    for value in a.extra_source:
        q=Path(value).resolve()
        if q.suffix not in ('.py','.json','.md') or not q.is_file():
            raise ValueError('extra source must be an existing small text source')
        paths.append(q)
    evidence=[]
    for path in sorted(set(q.resolve() for q in paths),key=str):
        payload=path.read_bytes()
        if len(payload)>3_000_000:raise ValueError('unexpected large source: '+str(path))
        evidence.append(dict(path=str(path),bytes=len(payload),SHA256=hashlib.sha256(payload).hexdigest(),
                             line_count=payload.count(b'\n')+int(not payload.endswith(b'\n'))))
    put('AUDIT_INPUTS_SHA256_V2.json',dict(kind='BOUNDED_TEXT_SOURCE_INPUTS_ONLY',input_count=len(evidence),files=evidence,
                                        SDK_imports=0,model_or_raw_opens=0,accounting_modified=False))
    put('CLOSED_FAILURE_CHAIN_SOURCE_V2.json',dict(kind='CLOSED_PRODUCER_METADATA_AND_SOURCE_INFERENCE_NOT_NEW_TRAINING',rows=rows,
             all_original_children_waited=closed['parent_exit']['all_own_children_waited'],
             original_cost_settled=closed['parent_exit']['original_cost_settled'],
             original_leases_released=closed['parent_exit']['original_leases_released'],
             original_blocked_after_real_error=closed['parent_current']['blocked_after_real_error'],
             candidate_blocked_error_roles=[r['role'] for r in rows if r['candidate_owner_reclassification']['effective_error']],
             physical_cache_root_cause=None,actual_app_close_masking_mechanism=None,
             source_only=True,accounting_rewrite=False,new_runtime_executed=False))
    print(json.dumps(dict(roles=len(rows),bounded_inputs=len(evidence),candidate_failures=sum(r['candidate_owner_reclassification']['effective_error'] for r in rows))))

if __name__=='__main__':main()
