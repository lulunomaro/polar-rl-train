"""Ordinary supplement to the existing white_v2 trial; never record or tag again."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import time
import tomllib
import traceback

D = Path(__file__).resolve().parent
R = D / 'reports'
REPO = D.parent / 'polar-rl-train'
p = D / 'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py'
s = importlib.util.spec_from_file_location('whitev2_pure_capture_complete30', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
BASE = 'd3b0066cc49284b7b1a21c1efb7ebe66d4f1baab'
TAG = 'trial-20261015-s5-two-devseeds-reviewed-whitev2-frozen-abc-started'
TAGOBJECT = '0b9f7b0a5b29d4cb124cb8ed40ffa0cca98c6b60'


def save(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2)


def main():
    assert m.g('rev-parse', 'HEAD') == BASE and not m.g('status', '--porcelain')
    assert m.g('rev-parse', TAG) == TAGOBJECT
    assert json.loads((R / 'WHITEV2_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes())['actual_owner_absent']
    prompt = D / 'MONITOR_S5_WHITEV2_COMPLETE30_NOMINAL_LOW_STEP_PREPARATION_ACTUAL_20261015.txt'
    cfgpath = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'automations/mod4-10/automation.toml'
    cfg = tomllib.loads(cfgpath.read_text(encoding='utf8'))
    assert cfg['id'] == 'mod4-10' and cfg['kind'] == 'heartbeat' and cfg['status'] == 'ACTIVE'
    assert cfg['rrule'] == 'FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    assert cfg['prompt'].encode('utf8') == prompt.read_bytes()
    save('WHITEV2_COMPLETE30_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json', dict(
        epoch=time.time(), passed=True, same_id_status_rrule_target=True,
        prompt_path=str(prompt), prompt_SHA=m.H(prompt), native_tool_updated=True,
        exact_UTF8_bytes_no_trailing_LF=True, no_extra_monitor_or_budget=True))
    old = {}
    for line in m.g('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags/').splitlines():
        v = line.split()
        old[v[0]] = (v[1], v[2] if len(v) > 2 else v[1])
    assert len(old) == 1346
    rawrefs = m.g('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*')
    remote = dict(line.split()[::-1] for line in rawrefs.splitlines())
    assert remote['refs/heads/main'] == BASE
    for tag, (obj, peeled) in old.items():
        assert remote[tag] == obj and remote.get(tag + '^{}', obj) == peeled
    dest = REPO / 'history/evidence' / D.name / 'ordinary_complete30_two_profile_audit_and_next_admission_v1'
    assert not dest.exists()
    save('WHITEV2_COMPLETE30_ORDINARY_APPEND_STARTED_ACTUAL.json', dict(
        epoch=time.time(), base=BASE, stage_tag=TAG, stage_object=TAGOBJECT,
        pre_commit_remote_main_and_all1346oldtags_verified=True,
        ordinary_only_no_trial_tag_record=True, capture=str(dest),
        all30_actual_completed_and_CPU_admitted=True))
    rows, files = m.capture_saved_completed_and_metadata(dest)
    subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'],
                   input=b''.join(x.encode() + b'\0' for x in files), capture_output=True, check=True)
    m.g('commit', '-m', 'Audit completed white_v2 thirty-case comparisons and preserve next admission handoff')
    head = m.g('rev-parse', 'HEAD')
    m.g('push', 'origin', 'HEAD')
    m.cap.a.verify(rows, old, head, TAG, TAGOBJECT)
    print(json.dumps(dict(epoch=time.time(), ordinary_commit=head,
        actual_remote_main_stage_tag_peeled_all1346oldtags_and_trackedSHA_verified=True,
        saved_sources=len(rows), no_new_trial_tag=True, complete30_and18pairs=True,
        no_GPU_SSH210_249_PPO_or_budget_action=True,
        formal_remote_receipt_is_this_tool_output_to_avoid_infinite_receipt_chain=True)))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        save('WHITEV2_COMPLETE30_ORDINARY_APPEND_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
             dict(error=traceback.format_exc(), resume_existingobjects_ifcommit_created=True,
                  no_record_tag_commit_replay=True))
        raise
