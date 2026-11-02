"""Finish464's unused transfer/CPU/eval after the original owner closed.

The original normal collector failed importing a text-only classifier before
node collection or model transfer. Keep that failure and every consumed marker.
Reference the existing exact classifier; do not mutate the frozen run package.
"""
from pathlib import Path
import ast
import importlib.util
import json
import os
import subprocess
import time
import traceback

N = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('closed464_unused_completion', N/'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main():
    R = m.R
    assert not (R/'CLOSED_TRANSFER_EVAL_COMPLETION_ONCE.json').exists()
    assert (R/'NORMAL_ONCE.json').exists() and (R/'OWNER_CLOSED_ACTUAL.json').exists()
    assert not any((R/name).exists() for name in (
        'NODE_CLOSED_FULLTEXT_ACTUAL.json',
        'ROOT464_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json',
        'CPU464_NEW_FINAL_CONSUMED.json', 'EVAL_ONCE.json'))
    assert not (N/'evaluation/actual_capture').exists()
    prior_error = m.read(R/'CALLER_ERROR_1793648195557150200.json')['error']
    assert 'ModuleNotFoundError' in prior_error and 'report_classification312' in prior_error
    owner = m.read(R/'OWNER_CLOSED_ACTUAL.json')
    assert owner['passed'] and owner['canonical_None'] and owner['shared_locks_free']
    assert owner['cohort_final']['rows']['jump_72']['terminal_all_own_children_waited']
    m.verify_index('4e8adaf084f3620f1d108a8bde467101f61e822952f978939142c2167ec1e704')
    binding = m.read(R/'OWNER_LAUNCH_ACTUAL.json')
    task = m.read(N/'TASK464_FROZEN.json')
    original = m.read(m.OLD/'TASK455_FROZEN.json')
    classifier = m.OLD/'control455/report_classification312.py'
    classifier_sha = '50223444323c1898af61b34821f486d9b6e524425ef5cef191dce87c7d69e78f'
    assert m.H(classifier) == classifier_sha
    tree = ast.parse((m.OLD/'normal455/collect455_fullclose_transfer_once.py').read_text('utf8'))
    code = next(ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'COLLECT_NODE' for target in node.targets))
    code = code.replace('455', '464').replace('36159', '41575')
    missing_import = 'import sys;sys.path.insert(0,str(C));from report_classification312 import classify_error_reports'
    assert code.count(missing_import) == 1
    code = code.replace(missing_import,
        "import sys;classifier=Path(v['shared_classifier']);assert hashlib.sha256(classifier.read_bytes()).hexdigest()==v['classifier_SHA'];sys.path[:0]=[str(C),str(classifier.parent)];from report_classification312 import classify_error_reports")
    with m.connection('CLOSED_UNUSED_TRANSFER') as (client, d):
        m.put('CLOSED_TRANSFER_EVAL_COMPLETION_ONCE.json', dict(
            epoch=time.time(), PID=os.getpid(), original_owner_already_closed=True,
            old_NORMAL_not_replayed=True, only_unused_transfer_CPU_eval=True,
            shared_classifier_local=str(classifier), shared_classifier_SHA=classifier_sha))
        authority = m.module('closed464_authority_shared', m.T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
        m.put('CLOSED_UNUSED_TRANSFER_AUTHORITY_ACTUAL.json', d.code(client, d.PY72, authority.AUTH, {}, timeout=45))
        role = d.code(client, d.PY72, code, dict(
            spec=binding['specs']['jump_72'],
            shared_classifier=original['job_root']+'/control455/report_classification312.py',
            classifier_SHA=classifier_sha), timeout=210)
        m.put('NODE_CLOSED_FULLTEXT_ACTUAL.json', role)
        assert role['qualified_formal'] and role['private_EX_free']
        formal = role['formal']
        dest = N/'current_closed464_models/jump_72/formal/model_final.pt'
        dest.parent.mkdir(parents=True, exist_ok=False)
        sf = client.open_sftp()
        try:
            sf.get(formal['path'], str(dest))
        finally:
            sf.close()
        assert dest.stat().st_size == formal['bytes'] and m.H(dest) == formal['SHA']
        transferred = dict(path=str(dest), source=formal['path'], bytes=formal['bytes'], SHA=formal['SHA'],
                           transfers=1, two_host_SHA_equal=True)
        m.put('ROOT464_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json', dict(
            passed_collection=True, run_id=task['run_id'], owner_closed=owner,
            roles={'jump_72': role}, formals={'jump_72': transferred}, skill_not_inferred=True))
    final = m.cpu_final()
    assert final['passed']
    m.wait_local()
    result = m.evaluate(final)
    render = subprocess.run([m.CONTROL, '-B', '-X', 'utf8', str(N/'render_saved_evaluation.py')],
                            cwd=N, capture_output=True, text=True, encoding='utf8')
    m.put('RENDER_PROCESS.json', dict(returncode=render.returncode, stdout=render.stdout, stderr=render.stderr))
    assert render.returncode == 0, render.stderr
    m.put('POSTROUND_RL_DECISION.json', dict(
        epoch=time.time(), status='EVALUATED_PENDING_NATIVE_REVIEW', final=final,
        strict=result['strict_successes'], terminations=result['terminations'], evalroot=str(N/'evaluation'),
        next='Native review saved465 poses/manifold; compare actual early yaw/clearance/first ground with455; evidence-directed reward repair authorized'))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        m.put('CLOSED_UNUSED_COMPLETION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json', dict(
            epoch=time.time(), error=traceback.format_exc(), no_automatic_replay=True))
        raise
