"""Source-only plan validation. Deliberately never installs or creates Task/GO."""
from pathlib import PurePosixPath
from native87_protocol_v1 import sha,worker_plan

REQUIRED_FRESH_HOOKS=('qualified_H1_wholepolicy_CPU','fresh4096_environment_and_D0_D7_CPU',
    'actual_runtime30joint_order','reference_future10_and_same_MDP_CPU','physics_and_clip6_source_exact',
    'source_payload_manifest_and_inventory','actual_resource_empty_GPU_RAM_disk',
    'new4096_fullsave_and_atomic_retention','original86_allout_cost_source_evidence')

def validate_exact_inventory(rows,approved_python):
    seen=set()
    for row in rows:
        name=row['relative'];p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or name in seen:raise ValueError('unsafe/duplicate relative path')
        if not sha(row['SHA']) or not isinstance(row['bytes'],int) or isinstance(row['bytes'],bool) or row['bytes']<0:raise ValueError('invalid file pin')
        if p.suffix=='.py' and approved_python.get(name)!=row['SHA']:raise ValueError('unapproved Python exactfile')
        seen.add(name)
    if set(approved_python)-seen:raise ValueError('approved Python missing from inventory')
    return True

def installer_plan(spec,inventory,approved_python,hooks):
    plan=worker_plan(spec);validate_exact_inventory(inventory,approved_python)
    if set(hooks)!=set(REQUIRED_FRESH_HOOKS):raise ValueError('explicit complete installer hook set required')
    if any(v not in ('pending','actual_passed_with_pinned_receipt') for v in hooks.values()):raise ValueError('invalid hook status')
    return dict(source_only=True,worker_plan=plan,exact_inventory=inventory,
        fresh_hooks=hooks,actual_install_performed=False,actual_Task_or_GO_created=False,
        ready_to_request_actual_installer=all(v=='actual_passed_with_pinned_receipt' for v in hooks.values()),
        warning='Hook strings are a plan only; owner readiness still requires actual typed CPU receipt and exact pins')
