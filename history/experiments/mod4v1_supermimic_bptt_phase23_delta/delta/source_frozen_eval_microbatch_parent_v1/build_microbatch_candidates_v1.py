"""Source-only thin copies. Never import/execute a parent or worker."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

B = Path(__file__).resolve().parent
R = B.parent
S = R / 'source_a1_frozen_eval_integration_v2'
INDEX_PIN = (5679, '2668c5804708cf99366f4c5233c4d34706ae4a2048c93037611015a4941fec99')
PARENT_PIN = (9346, '4b13181c5f60c939ceaca631aa26670d40ae1b39665f93a9a58ce072c2545995')
WORKER_PIN = (14962, '4188b7ab43a1e69a457bdf82db7c5c46fe700c1094e96b14eb1415d7349c5b62')
PARENT = 'single_gpu_e3_w35_a1_frozen_parent_v1.py'
WORKER = 'worker_formal_a1_microbatch_v1.py'


def read_pinned(name, pin):
    path = S / name
    raw = path.read_bytes()
    assert (len(raw), hashlib.sha256(raw).hexdigest()) == pin, 'sealed input differs: ' + name
    return raw.decode('utf-8').replace('\r\n', '\n')


def replacements(old):
    # Whitelist includes purpose/coverage/ready membership only. Resource blocks stay exact.
    pairs = [
        ('"""OneoriginalGPUprivateEX+globalfiniteEXowner, nineisolatedSDKworkers, honestreadybarrier/result/closewait. No learner/GO/ledgerwrite."""',
         '"""Independent requested E3/W35 candidate batch; original EX/readiness/wait blocks unchanged."""'),
        ('from a1_frozen_eval_runtime_v2 import make_task,ROLES,evaluate_waited_eval_case',
         'from frozen_eval_microbatch_runtime_v1 import make_task,ROLES,evaluate_waited_eval_case,select_requested_roles,batch_start,batch_result'),
        ("roles=plan['roles'];assert len(roles)==8 and {r['role']for r in roles}==set(ROLES);", "roles=select_requested_roles(plan);requested=tuple(plan['requested_roles']);"),
        ("kind='ONEGPU_EIGHT_A1_FROZEN80_NO_LEARNING_V2',GPU_UUID=uuid", "kind='ONEGPU_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1',requested_roles=list(requested),deferred_roles=plan['deferred_roles'],overall_eight_pass_rate=None,GPU_UUID=uuid"),
        ('assert len(children)==8;', 'assert len(children)==len(requested)==2;'),
        ('if len(ready)==8:', 'if len(ready)==len(requested) and set(ready)==set(requested):'),
        ("put('GROUP_EVAL_START.json',dict(group_id=plan['group_id'],GPU_UUID=uuid,members=ready,all_members_ready=True,epoch=group_start,source='All8originalSDKscenes+frozenA1pi+N80fullDRreadybeforeanycontrolledstep'))", "put('GROUP_EVAL_START.json',batch_start(plan,ready,group_start))"),
        ("'NineSDKstartupreadybarrier900s expired'", "'RequestedSDKstartupreadybarrier900s expired'"),
        ("put('FINAL.json',dict(kind='ACTUAL_SINGLE_GPU_EIGHT_A1_FROZEN80_SOURCE_CANDIDATE_V2',group_id=plan['group_id'],GPU_UUID=uuid,common_start_epoch=group_start,eight_ready_before_start=True,all_eight_actual_execution_complete=all(v['passed_execution']for v in terminal),rows=terminal,source20k_DR_history_sliced=False,source20k_histories_physically_applied=False,old20k_fullrestore_proof_preserved_separately=True,new_PPO_BPTT_GO=0,canonical_writes=0,epoch=time.time()))", "put('FINAL.json',batch_result(plan,terminal,group_start,epoch=time.time()))"),
    ]
    result = old
    for before, after in pairs:
        assert result.count(before) == 1, 'exact source anchor differs: ' + before
        result = result.replace(before, after, 1)
    return result, pairs


def worker_replacements(old):
    pairs = [
        ('from parallel_eval_safe import put,wait_start', 'from parallel_eval_safe import put\nfrom frozen_eval_microbatch_runtime_v1 import wait_start'),
        ('from a1_frozen_eval_runtime_v2 import task_args,A1CheckpointAdapter,install_paired_pose_before_original_reset,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence',
         'from frozen_eval_microbatch_runtime_v1 import task_args,A1CheckpointAdapter,install_paired_pose_before_original_reset,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence'),
    ]
    result = old
    for before, after in pairs:
        assert result.count(before) == 1, 'worker exact import anchor differs'
        result = result.replace(before, after, 1)
    return result, pairs


def undo_equal(old, new, pairs):
    for before, after in reversed(pairs):
        assert new.count(after) == 1
        new = new.replace(after, before, 1)
    assert ast.dump(ast.parse(new), include_attributes=False) == ast.dump(ast.parse(old), include_attributes=False)


def verify_validator():
    original = ast.parse((S / 'a1_frozen_eval_runtime_v2.py').read_text(encoding='utf-8'))
    candidate = ast.parse((B / 'frozen_eval_microbatch_runtime_v1.py').read_text(encoding='utf-8'))
    old = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_group_task')
    new = next(n for n in candidate.body if isinstance(n, ast.FunctionDef) and n.name == old.name)
    matches = [i for i, n in enumerate(old.body) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
               and len(n.value.args) > 1 and isinstance(n.value.args[1], ast.Constant)
               and n.value.args[1].value == 'one original parent must own all eight members']
    assert len(matches) == 1
    old.body[matches[0]] = ast.parse('_validate_batch_members(task, role)').body[0]
    assert ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False), 'non-membership validator logic changed'


def identity(path):
    raw = Path(path).read_bytes()
    return dict(path=str(Path(path)), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def build():
    assert not (B / 'DELIVERABLES_SHA256_V1.json').exists(), 'sealed output is immutable'
    read_pinned('FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json', INDEX_PIN)
    inputs = [('single_gpu_eight_a1_frozen_parent_candidate_v2.py', PARENT_PIN, PARENT, replacements),
              ('worker_formal_a1_frozen_candidate_v2.py', WORKER_PIN, WORKER, worker_replacements)]
    diffs, outputs = [], []
    for source, pin, target, transform in inputs:
        old = read_pinned(source, pin)
        new, pairs = transform(old)
        undo_equal(old, new, pairs)
        path = B / target
        if path.exists():
            assert path.read_text(encoding='utf-8') == new, 'existing generated copy differs; inspect before changing'
        else:
            path.write_text(new, encoding='utf-8', newline='\n')
        compile(new, str(path), 'exec')  # Syntax only, no execution/import.
        outputs.append(identity(path))
        diffs.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
            fromfile=str(S / source), tofile=str(path)))
    verify_validator()
    (B / 'MICROBATCH_WHITELIST_DIFF_V1.patch').write_text(''.join(diffs), encoding='utf-8', newline='\n')
    receipt = dict(kind='SOURCE_ONLY_REQUESTED_E3_W35_THIN_COPIES_NOT_ADMISSION',
        original_parent_whole_AST_equal_after_whitelist_undo=True,
        original_formal_worker_whole_AST_equal_after_import_undo=True,
        original_core_validator_AST_equal_except_one_membership_check=True,
        original_private_finite_C_readiness_timeout_actualwait_finally_blocks_unchanged=True,
        original_accepted_DR_physics_commands_controls_loops_unchanged=True,
        original_eight_parent_not_modified=True, original_role_dictionary_size=8,
        requested_roles=['E3', 'W35'], all_unrequested_are_deferred=True,
        source_index=identity(S / 'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json'), outputs=outputs,
        actual_dispatch_GPU_model_SDK_account_or_native_operations=0)
    (B / 'BUILD_MICROBATCH_SOURCE_V1.json').write_text(json.dumps(receipt, indent=2, allow_nan=False), encoding='utf-8')
    return receipt


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True))
