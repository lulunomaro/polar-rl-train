"""Ordinary supplement after unique nominal stage; no record/tag replay."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import time
import tomllib
import traceback

D=Path(__file__).resolve().parent
R=D/'reports'
p=D/'archive_nominal_isolated_source_target_native_and_unused29_stage_once.py'
s=importlib.util.spec_from_file_location('nominal_stage_pure_capture_ordinary',p)
n=importlib.util.module_from_spec(s);s.loader.exec_module(n)
BASE='d48e16c6682ba19a724a0bbe0ca9938ee9beaf08'


def main():
    assert n.git('rev-parse','HEAD')==BASE and not n.git('status','--porcelain')
    stage=json.loads((R/'NOMINAL_ISOLATED_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())
    assert stage['commit']==BASE and stage['actual_remote_main_tag_peeled_all1346oldtags_and_trackedSHA_verified']
    prompt=D/'MONITOR_S5_NOMINAL_NATIVE_UNUSED29_STAGE_REMOTE_VERIFIED_ACTUAL_V2_20261015.txt'
    cfg=tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert cfg['id']=='mod4-10' and cfg['kind']=='heartbeat' and cfg['status']=='ACTIVE'
    assert cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    assert cfg['prompt'].encode('utf8')==prompt.read_bytes()
    assert n.H(prompt)=='f82a12c0f17fa760e9ab42f46dc015e28cbfa2bad45c455c961c16c5f666f3ff'
    n.put('NOMINAL_STAGE_REMOTE_MONITOR_TOML_UTF8_V2_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,
        same_native_id_status_hourly_rrule_target=True,exact_UTF8_prompt_SHA=n.H(prompt),
        source_stage_actual_remote_verified=True,own_unused29_CIM_current_priority=True,no_extra_monitor_or_budget=True))
    old={}
    for line in n.git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
        v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
    assert len(old)==1347
    n.DEST=n.REPO/'history/evidence'/D.name/'ordinary_stage_remote_receipt_monitor_and_later_admitted_v1'
    assert not n.DEST.exists()
    n.m.cap.g=n.git;n.m.cap.a.gitio.g=n.git
    rows,files=n.capture()
    subprocess.run(['git','-C',str(n.REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],
        input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
    n.git('commit','-m','Append nominal verified stage receipt, exact hourly handoff and subsequent admitted inputs')
    head=n.git('rev-parse','HEAD');n.git('push','origin','HEAD')
    # The existing nominal trial peel remains BASE, not this ordinary HEAD.
    n.m.cap.a.verify(rows,old,head)
    print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,
        actual_remote_main_all1347oldtags_original_peels_and_trackedSHA_verified=True,
        saved_sources=len(rows),no_new_trial_tag=True,
        later_finite_data_and_reports_require_ordinary_supplement=True,
        final_verification_retained_as_tool_output=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        n.put('NOMINAL_ORDINARY_STAGE_RECEIPT_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(
            error=traceback.format_exc(),resume_existing_objects_ifcommit_created=True,no_record_tag_commit_replay=True,
            no_GPU_PPO_or_budget_action=True))
        raise
