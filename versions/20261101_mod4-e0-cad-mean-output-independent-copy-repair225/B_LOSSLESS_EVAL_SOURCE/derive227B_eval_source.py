"""New bounded eval source; observer math/commands/physics stay original222."""
from pathlib import Path
import hashlib
import json
import traceback

B = Path(__file__).resolve().parent
N = B.parent
P222 = N.parent/'W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101'


def write(p, data):
    with p.open('xb') as f:
        f.write(data)


def ref(p):
    b = p.read_bytes()
    return dict(path=str(p), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def main():
    old_observer = P222/'rm70_intervals222.py'
    old_worker = P222/'evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py'
    assert ref(old_observer)['SHA'] == '000e14607137c9d0221211da9ac6b86bc08deb6c3f4fdd380366fb4c9e8c5e12'
    assert ref(old_worker)['SHA'] == '4ed4dfa428c94c79ddd8e31012d91fc39daa07c5b3711759b1b6a05f17eb22ae'
    text = old_observer.read_text(encoding='utf8')
    a = text.index('class Rows222:')
    z = text.index('class RM70Intervals222:')
    text = text[:a]+'from positional_rows227 import PositionalRows227 as Rows227\n\n\n'+text[z:]
    assert text.count('class RM70Intervals222:') == 1 and text.count('Rows222(out,model)') == 1
    text = text.replace('class RM70Intervals222:', 'class RM70Intervals227:').replace('Rows222(out,model)', 'Rows227(out,model)')
    write(B/'rm70_intervals227.py', text.encode())
    text = old_worker.read_text(encoding='utf8')
    # All replaced222 tokens are this observer/Task/output namespace; no model,
    # runtime, math, sampler, physical term, constant or counter has token222.
    text = text.replace('222', '227')
    assert text.count('deadline=time.time()+1680') == 1
    text = text.replace('deadline=time.time()+1680', 'deadline=time.time()+3600')
    old = "assert task['controls_max']==1600 and task['no_new_learning_or_GO'] and task['actual_current_CNone_private_shared_resources_admitted']"
    new = old+"\n assert task['worker_seconds']==3600 and task['parent_seconds']==3780 and task['actual_saved_LR']==.00017085937500000009\n assert task['telemetry_producer']['format']=='mod4.227.lossless_fieldset_positional_jsonl.v1'\n for key,name in [('observer_SHA','rm70_intervals227.py'),('writer_SHA','positional_rows227.py'),('decoder_SHA','decode227_positional.py')]:assert H(job/name)==task['telemetry_producer'][key]"
    assert text.count(old) == 1
    text = text.replace(old, new)
    old = 'from rm70_intervals227 import RM70Intervals227'
    assert text.count(old) == 1
    text = text.replace(old, old+'\n from positional_rows227 import configure227_producer\n configure227_producer(dict(task[\'telemetry_producer\'],source_model_SHA=MODEL))')
    write(B/'evaluate227_CLOSED_W35_FULL_RM70_LOSSLESS_UNUSED_once.py', text.encode())
    # Saved qualified metadata checker is reused by source bytes, not by a new
    # model load. Its owner-ABI constants are not used by this eval-only case.
    write(B/'qualified227.py', (N/'A_PPO_SOURCE/contract227.py').read_bytes())
    write(B/'reports/DERIVE227B_SOURCE_BINDINGS.json', json.dumps(dict(
        status='NEW_SOURCE_ONLY_NOT_SDK_OR_CASE_EXECUTED', sources=[ref(old_observer),ref(old_worker)],
        observer_changes='Only Rows222 class replaced by positional writer import/constructor and class namespace;all UID/pre-reset/axis/route/failure math unchanged',
        worker_changes='New227 namespace,wall3600,parent3780 assertion and source-bound producer schema metadata;1600controls/32s/max12800physics unchanged',
        old222_source_partial_JSONL_modified_or_read=False, no_new_learning_GO=True), indent=2).encode())


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (B/'reports').mkdir(exist_ok=True)
        write(B/'reports/DERIVE227B_ORIGINAL_ERROR.json', json.dumps(dict(error=traceback.format_exc(),no_automatic_retry=True),indent=2).encode())
        raise
