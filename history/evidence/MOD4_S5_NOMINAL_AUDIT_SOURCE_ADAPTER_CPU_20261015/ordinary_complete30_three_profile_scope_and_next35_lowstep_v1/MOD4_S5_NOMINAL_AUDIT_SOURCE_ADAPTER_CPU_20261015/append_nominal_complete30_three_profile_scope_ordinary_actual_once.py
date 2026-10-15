"""One ordinary append to the existing nominal trial; never record/tag the stage again."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import tomllib
import traceback

D = Path(__file__).resolve().parent
R = D / 'reports'
BASE = 'a65958ef845173bf3adf24cfe043f41b475cffe1'
p = D / 'archive_nominal_isolated_source_target_native_and_unused29_stage_once.py'
s = importlib.util.spec_from_file_location('nominal_complete_pure_capture_helpers', p)
n = importlib.util.module_from_spec(s)
s.loader.exec_module(n)


def main():
    assert n.git('rev-parse', 'HEAD') == BASE and not n.git('status', '--porcelain')
    assert json.loads((R / 'NOMINAL_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes())['actual_owner_absent']
    prompt = D / 'MONITOR_S5_NOMINAL_COMPLETE30_THREE_PROFILE_AND_NEXT35_LOW_STEP_ACTUAL_20261015.txt'
    c = tomllib.loads((Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) /
                      'automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert c['id'] == 'mod4-10' and c['kind'] == 'heartbeat' and c['status'] == 'ACTIVE'
    assert c['rrule'] == 'FREQ=HOURLY;INTERVAL=1' and c['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    assert c['prompt'].encode('utf8') == prompt.read_bytes()
    assert hashlib.sha256(prompt.read_bytes()).hexdigest() == 'f53fcf8bd3ddec9e843635330705f34111b17c265cc3f59ebdc77a9bcc89840b'
    n.put('NOMINAL_COMPLETE30_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json', dict(epoch=time.time(), passed=True,
        same_id_ACTIVE_hourly_target=True, prompt_SHA=n.H(prompt), complete30_and_actual_CIM_handoff=True,
        no_new_monitor_GPU_PPO_or_budget=True))
    old = {}
    for line in n.git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags/').splitlines():
        v = line.split()
        old[v[0]] = v[1], v[2] if len(v) > 2 else v[1]
    assert len(old) == 1347
    n.DEST = n.REPO / 'history/evidence' / D.name / 'ordinary_complete30_three_profile_scope_and_next35_lowstep_v1'
    assert not n.DEST.exists()
    n.m.cap.g = n.git
    n.m.cap.a.gitio.g = n.git
    rows, files = n.capture()
    subprocess.run(['git', '-C', str(n.REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'],
                   input=b''.join(x.encode() + b'\0' for x in files), capture_output=True, check=True)
    n.git('commit', '-m', 'Complete nominal frozen comparisons, preserve all30 evidence and review three profiles')
    head = n.git('rev-parse', 'HEAD')
    print(json.dumps(dict(ordinary_created_once=head, saved_sources=len(rows), files=len(files))), flush=True)
    n.git('push', 'origin', 'HEAD')
    # Original trial still peels to d48e16c; ordinary HEAD must not replace that peel.
    n.m.cap.a.verify(rows, old, head)
    print(json.dumps(dict(ordinary_commit=head, saved_sources=len(rows),
        actual_remote_main_all1347_original_tag_objects_peels_and_trackedSHA_verified=True,
        no_new_trial_tag_or_GPU_PPO_budget=True, final_verification_retained_as_tool_output=True)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        n.put('NOMINAL_COMPLETE30_ORDINARY_APPEND_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json', dict(
            error=traceback.format_exc(), resume_existing_objects_if_commit_created=True,
            no_repeat_record_tag_commit_or_first_append_helper=True, no_GPU_PPO_budget_action=True))
        raise
