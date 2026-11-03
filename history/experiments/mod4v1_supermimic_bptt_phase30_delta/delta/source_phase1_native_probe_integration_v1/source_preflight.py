"""Read-only .py / explicit SOURCE-JSON audit. Does not stage or import native code."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
from capture_contract import need, validate_source_request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = ROOT / 'source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json'
INDEX_PIN = (6085, 'd0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a')
PARTITION_ROOT = '0feb70e552a915ca698b87cdc7a4e3b22ee614e86ce55c2b9677a6f0e9c30bdf'


def source_bytes(path):
    path = Path(path).resolve()
    need(path.is_relative_to(ROOT), 'SOURCE read escaped declared workspace subtree')
    need(path.suffix in ('.py', '.json') and 'budget' not in path.name.lower(), 'only explicit SOURCE .py/.json')
    return path.read_bytes()


def identity(path):
    raw = source_bytes(path)
    return dict(path=str(Path(path).resolve()), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def _function(path, name):
    tree = ast.parse(source_bytes(path).decode('utf-8'))
    return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)


def _signature(path, name):
    node = _function(path, name)
    return dict(name=name, args=ast.unparse(node.args), first_line=node.lineno, last_line=node.end_lineno)


def audit_source():
    request = validate_source_request(json.loads(source_bytes(HERE / 'SOURCE_REQUEST.json')))
    index_id = identity(INDEX)
    need((index_id['bytes'], index_id['SHA256']) == INDEX_PIN, 'original17 index pin differs')
    index = json.loads(source_bytes(INDEX))
    need(len(index['entries']) == 17, 'retain full seventeen mappings')
    verified = []
    for row in index['entries']:
        need(Path(row['path']).suffix == '.py', 'index only original full Python sources')
        observed = identity(row['path'])
        need(observed['bytes'] == row['bytes'] and observed['SHA256'] == row['SHA256'],
             'original full source pin differs: ' + row['relative'])
        ast.parse(source_bytes(row['path']).decode('utf-8'))
        verified.append(dict(observed, installed_alias=row['relative']))
    parent = ROOT / 'source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py'
    text = source_bytes(parent).decode('utf-8')
    for critical in ('len(children)==len(requested)==2', 'rc=p.wait();semantic=evaluate_waited_eval_case',
                     'wait_until=time.monotonic()+1800', 'if waited:',
                     "for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN)",
                     'original_single_GPU_private_EX_released=waited'):
        need(critical in text, 'original complete parent guard/wait/release anchor missing')
    partition = ROOT / 'source_phase1_state_context_partition_v1/SOURCE_SEAL.json'
    seal = json.loads(source_bytes(partition))
    need(seal['content_root_sha256'] == PARTITION_ROOT and seal['gate1_admitted'] is False,
         'frozen partition source seal identity differs')
    sensor = ROOT / 'source_phase1_passive_sensor_capture_v1'
    install = _signature(sensor / 'passive_capture.py', 'install_passive_capture')
    need(install['args'].startswith('env, bridge, feedback_module, role_api, bridge_pin, *,'),
         'known stable sensor install API differs; parent review needed')
    stage = ROOT / 'source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
    stage_tree = ast.parse(source_bytes(stage).decode('utf-8'))
    vendor_pin = next(ast.literal_eval(n.value) for n in stage_tree.body
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VENDOR_PIN' for t in n.targets))
    need(vendor_pin == (7, 'ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0'),
         'complete native vendor7 inventory pin differs')
    return dict(kind='READONLY_SOURCE_PREFLIGHT_NOT_NATIVE_ADMISSION', source_request=request,
                original17_index=index_id, original17_sources=verified,
                partition_seal=identity(partition), partition_seal_declared_content_root=PARTITION_ROOT,
                complete_static_banks_runtime_worker_files='RETAIN_ORIGINAL_FULL_STAGE_INVENTORY_NOT_COPIED_HERE',
                complete_vendor_tree_declared_pin=list(vendor_pin), original_stage_source=identity(stage),
                parent_source_preserved=True, old_fixed_two_member_guard_still_active=True,
                sensor_api_observed_signature=install,
                sensor_source_status='PENDING_PARENT_SEAL_REVIEW_NO_FLOATING_SHA_PIN',
                action_observer_status='DEFERRED_UNSEALED_NO_API_GUESSED',
                app_final_predicate=_signature(ROOT / 'source_app_close_runtime_compat_v6/app_close_semantics_v6.py',
                                               '_validate_final_for_intent'),
                native_enabled=False, actual_PT_reads=0, actual_SDK_imports=0,
                actual_native_runs=0, actual_resource_gate_runs=0, actual_stage_dispatch=0,
                canonical_reads=0, canonical_writes=0, exact=False, gate1='UNKNOWN',
                cpu_native_authorization_required_after_parent_review=True)


if __name__ == '__main__':
    print(json.dumps(audit_source(), indent=2, ensure_ascii=False, allow_nan=False))
