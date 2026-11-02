"""Separate once-only dispatch of an already staged A1/V5 shared ORIGINAL owner.

Default checks metadata/sources only. --dispatch requires an explicit parent marker,
unused stage/GO/owner, then one Popen. No SSH, C/lock/ledger work, polling, or signals.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

from stage_a1_native_v5 import (ROLE_ORDER, OWNER_NAME, ROOT_MANIFEST_NAME, STAGE_KIND, RAW35_VIEW, VARIANT,
    ALGORITHM_FAMILY, require, sha_bytes, is_sha, safe_relative, identity, read_metadata, put_once,
    source_only_owner_verify)

PARENT_KIND = 'PARENT_APPROVED_NEW_A1_NATIVE_V5_DISPATCH_ONCE'
CONSUMED_NAME = 'PARENT_DISPATCH_CONSUMED_V5.json'
DISPATCH_RESULT = 'OWNER_DISPATCH_ACTUAL_V5.json'


def verify_file_rows(root, rows):
    require(isinstance(rows, list), 'installed source manifest is not a file list')
    seen = set()
    for row in rows:
        relative = safe_relative(row['relative'])
        require(relative not in seen, 'duplicate staged manifest path')
        seen.add(relative)
        path = root / relative
        require(not path.is_symlink() and path.resolve(strict=True).is_relative_to(root.resolve()), 'staged source escaped owned root')
        actual = identity(path)
        require(actual['SHA'] == row['SHA'] and actual['bytes'] == row['bytes'], 'staged source changed: ' + relative)


def verify_stage(root, run_id, expected_stage_sha):
    root = root.resolve(strict=True)
    require(root.name == run_id and is_sha(expected_stage_sha), 'explicit staged run identity/SHA required')
    require(not (root / 'STAGE_ERROR_V5.json').exists(), 'failed staging is never dispatched')
    require(not (root / CONSUMED_NAME).exists() and not (root / DISPATCH_RESULT).exists(), 'dispatch already consumed')
    for name in ('OWNER_STARTED.json', 'OWNER_CURRENT.json', 'OWNER_ORIGINAL_ERROR.json', 'OWNER_EXIT_ACTUAL.json'):
        require(not (root / name).exists(), 'owner purpose is already consumed: ' + name)
    complete_raw = (root / 'STAGE_COMPLETE_V5.json').read_bytes()
    require(sha_bytes(complete_raw) == expected_stage_sha, 'parent stage-complete pin differs')
    complete = json.loads(complete_raw)
    require(complete.get('kind') == STAGE_KIND and complete.get('staged') is True, 'successful stage receipt missing')
    require(complete.get('root') == str(root) and complete.get('run_id') == run_id and complete.get('order') == list(ROLE_ORDER), 'stage root/run/order differs')
    require(complete.get('owner_launches') == 0 and complete.get('selected_PT_stat_read_copy') == 0, 'stage already launched or copied a model')
    require(complete.get('owner_relative') == OWNER_NAME, 'only original shared V5 owner is selected')
    root_manifest_raw = (root / ROOT_MANIFEST_NAME).read_bytes()
    require(sha_bytes(root_manifest_raw) == complete['root_manifest_SHA'], 'root source/config manifest changed')
    root_manifest = json.loads(root_manifest_raw)
    verify_file_rows(root, root_manifest['files'])
    plan = read_metadata(root / 'OWNER_PLAN.json')
    require(sha_bytes((root / 'OWNER_PLAN.json').read_bytes()) == complete['owner_plan_SHA'], 'staged OWNER_PLAN changed')
    require(sha_bytes((root / 'SCHEDULE_PUBLIC.json').read_bytes()) == complete['schedule_SHA'], 'original helper schedule config changed')
    require(plan['run_id'] == run_id and plan['H1_excluded'] is True and [e['role'] for e in plan['entries']] == list(ROLE_ORDER), 'new exact eight-role plan differs')
    rows = {row['role']: row for row in complete['rows']}
    require(set(rows) == set(ROLE_ORDER), 'stage manifest role set differs')
    for entry in plan['entries']:
        job = root / 'roles' / entry['role']
        require(entry['job_root'] == str(job), 'job root is not owned by this stage')
        require(entry['actor_view'] == RAW35_VIEW and entry['algorithm_variant'] == VARIANT and entry['algorithm_family'] == ALGORITHM_FAMILY and entry.get('resume_bptt') is None, 'only fresh A1 is staged')
        require(entry['num_envs'] == 1024 and entry['target_bptt_steps'] >= 3000, 'A1 batch/true target differs')
        require(not (job / 'GO_PRODUCTION.json').exists() and not (job / 'TASK.json').exists() and not (job / 'production').exists(), 'GO/model purpose was already consumed')
        raw = (job / 'INSTALL_MANIFEST.json').read_bytes()
        require(sha_bytes(raw) == rows[entry['role']]['manifest_SHA'], 'role INSTALL_MANIFEST changed')
        manifest = json.loads(raw)
        require(manifest['source_PT_copied'] is False and manifest['selected_PT_stat_read_or_copy'] is False, 'source install model flag differs')
        verify_file_rows(job, manifest['files'])
    # Original verify_sources AST only; does not import b, authority, owner or real C.
    source_only_owner_verify(root, root / OWNER_NAME, plan)
    return root, complete, plan


def verify_parent_marker(path, root, run_id, stage_sha):
    marker = read_metadata(path)
    require(marker.get('kind') == PARENT_KIND, 'explicit parent dispatch marker missing')
    require(marker.get('run_id') == run_id and marker.get('root') == str(root), 'parent marker run/root differs')
    require(marker.get('stage_complete_SHA') == stage_sha and marker.get('owner_relative') == OWNER_NAME, 'parent did not bind this exact stage/owner')
    require(isinstance(marker.get('dispatch_token'), str) and len(marker['dispatch_token']) >= 16, 'new one-purpose parent token missing')
    require(marker.get('actual_native_launch_requested') is True and marker.get('original_authority_gates_required') is True, 'parent has not selected native/original-gate dispatch')
    require(marker.get('no_foreign_owner_signal_or_C_steal') is True, 'parent marker original-owner rule differs')
    return marker, sha_bytes(path.read_bytes())


def child_identity_metadata(pid):
    value = dict(pid=pid, observed_epoch=time.time())
    try:
        # Metadata of this newly spawned owner only; no model/backend observation.
        text = (Path('/proc') / str(pid) / 'stat').read_text()
        value['linux_start_ticks'] = text[text.rfind(')') + 2:].split()[19]
    except (OSError, IndexError):
        value['linux_start_ticks'] = None
    return value


def dispatch_once(root, run_id, stage_sha, parent_path, python_runner):
    root, complete, plan = verify_stage(root, run_id, stage_sha)
    parent, parent_sha = verify_parent_marker(parent_path, root, run_id, stage_sha)
    require(sys.platform.startswith('linux'), 'native dispatch CLI is for the existing Linux host only')
    require(python_runner.is_file() and os.access(python_runner, os.X_OK), 'explicit existing original Python runner missing')
    # x-create is a purpose marker, NOT a new resource lock or accounting ledger.
    put_once(root / CONSUMED_NAME, dict(kind='ONE_PARENT_DISPATCH_PURPOSE_CONSUMED_V5', epoch=time.time(),
        run_id=run_id, stage_complete_SHA=stage_sha, parent_marker_SHA=parent_sha,
        dispatch_token_SHA=sha_bytes(parent['dispatch_token'].encode()), original_C_and_resource_gates_not_preclaimed=True))
    try:
        with (root / 'OWNER_A1_V5_STDOUT_STDERR.log').open('xb') as log:
            process = subprocess.Popen([str(python_runner), '-u', '-B', str(root / OWNER_NAME)],
                cwd=root, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True, close_fds=True)
        result = dict(kind='ACTUAL_NEW_A1_SHARED_V5_OWNER_DISPATCH_NOT_ADMISSION', root=str(root), run_id=run_id,
            owner_relative=OWNER_NAME, stage_complete_SHA=stage_sha, parent_marker_SHA=parent_sha,
            parent=child_identity_metadata(process.pid), actual_Popen_calls=1, dispatched_not_yet_actualGO=True,
            original_owner_gates_unchanged=True, C_GO_lock_reads_writes_by_dispatcher=0,
            model_polling_SDK_GPU_foreign_signals_by_dispatcher=0, native_skill_or_BPTT_claim=False)
        put_once(root / DISPATCH_RESULT, result)
        return result
    except BaseException:
        put_once(root / 'OWNER_DISPATCH_ERROR_V5.json', dict(kind='PRESERVED_DISPATCH_ERROR_NO_AUTOMATIC_RETRY',
            epoch=time.time(), error=traceback.format_exc(), consumed_marker_retained=True))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage-root', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--stage-complete-sha', required=True)
    parser.add_argument('--parent-marker', type=Path, required=True)
    parser.add_argument('--python-runner', type=Path, required=True)
    parser.add_argument('--dispatch', action='store_true', help='consume purpose and launch once; default is read-only checks')
    args = parser.parse_args()
    if args.dispatch:
        result = dispatch_once(args.stage_root, args.run_id, args.stage_complete_sha, args.parent_marker, args.python_runner)
    else:
        root, _, _ = verify_stage(args.stage_root, args.run_id, args.stage_complete_sha)
        verify_parent_marker(args.parent_marker, root, args.run_id, args.stage_complete_sha)
        result = dict(kind='READ_ONLY_DISPATCH_PREFLIGHT_V5', passed=True, root=str(root), run_id=args.run_id,
                      dispatch_consumed=False, owner_launches=0, C_GO_lock_model_SDK_GPU_operations=0)
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
