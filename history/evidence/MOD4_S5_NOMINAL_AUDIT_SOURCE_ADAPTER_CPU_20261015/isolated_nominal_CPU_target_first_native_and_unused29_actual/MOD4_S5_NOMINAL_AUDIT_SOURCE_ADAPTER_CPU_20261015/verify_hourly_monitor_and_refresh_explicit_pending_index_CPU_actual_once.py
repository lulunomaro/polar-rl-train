"""Verify same native hourly automation and index every saved postcapture file."""
from pathlib import Path
import hashlib
import json
import os
import time
import tomllib

D=Path(__file__).resolve().parent
W=D.parent
R=D/'reports'
M=W/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
REPO=W/'polar-rl-train'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


prompt=D/'MONITOR_S5_NOMINAL_ISOLATED_CPU_PASSED_TARGET_PENDING_VIDEO_HOP_SCOPE_ACTUAL_20261015.txt'
cfg=tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert cfg['id']=='mod4-10' and cfg['kind']=='heartbeat' and cfg['status']=='ACTIVE'
assert cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
assert cfg['prompt'].encode('utf8')==prompt.read_bytes()
assert sha(prompt)=='f94db9d4dec0700c4b4d8d64d01a0be7afee1af10e97f4c3834aeaf5451f59d5'
v=dict(epoch=time.time(),passed=True,same_native_id_kind_status_hourly_rrule_target=True,
       exact_UTF8_prompt_SHA=sha(prompt),no_trailing_LF=True,new_actual_CPU_passed_only=True,
       target_native_GPU_pending=True,old_M_e411_existing_objects_remote_pending=True,
       original_TLS_failures_and_V1_CPU_reader_error_preserved=True,Git_pending_not_claimed_recorded=True)
with (R/'NOMINAL_CPU_PASSED_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
index=REPO/'history/evidence'/M.name/'ordinary_complete30_two_profile_audit_and_next_admission_v1/REPORT_CAPTURE_INDEX.json'
captured={(x['source_path'],x['sha256']) for x in json.loads(index.read_bytes())['entries']}
pending_N=[]
for p in sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
    pending_N.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p),pending_Git=True))
pending_M=[]
paths=set([*M.glob('*.py'),*M.glob('*.txt'),*M.glob('*.json'),*(p for p in (M/'reports').rglob('*') if p.is_file())])
for p in sorted(paths):
    h=sha(p)
    if (str(p.resolve()),h) not in captured:
        pending_M.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=h,pending_ordinary_supplement=True))
value=dict(epoch=time.time(),N_entries=pending_N,M_post_e411_capture_entries=pending_M,
           this_index_itself_and_any_later_source_reports_monitor_receipts_also_pending=True,
           first_resume_existing_M_commit='e411cb07f275b287f3644a69c4159737a3b0edc3',
           after_actual_remote_verification_append_M_errors_then_record_unique_N_CPU_stage=True,
           no_new_record_tag_commit_until_existing_objects_resolved=True,
           local_source_and_reports_not_claimed_remote_Git=True,no_GPU_PPO_or_budget_action=True)
with (R/'NOMINAL_CPU_AND_M_POST_CAPTURE_PENDING_GIT_INDEX_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
print(json.dumps(dict(monitor_UTF8_verified=True,N_pending=len(pending_N),M_postcapture_pending=len(pending_M),new_GPU=False,remote_Git_pending=True)))
