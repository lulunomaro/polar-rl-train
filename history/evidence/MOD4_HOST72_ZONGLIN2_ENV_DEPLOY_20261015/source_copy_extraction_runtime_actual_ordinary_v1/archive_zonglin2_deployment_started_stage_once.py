"""Record the actual new deployment stage once while its copy continues independently."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import tomllib
import traceback

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
REPO = W / 'polar-rl-train'
BASE = '0b82a73263d954ad71c42bd79de1f3762aec57f6'
ID = 'host72-zonglin2-isolated-environment-deploy-started'
DEST = REPO / 'history/evidence' / D.name / 'isolated_new_root_source_copy_and_runtime_preparation_actual_v1'
s = importlib.util.spec_from_file_location('zonglin2_pure_archive_helpers',
    W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/archive_nominal_isolated_source_target_native_and_unused29_stage_once.py')
n = importlib.util.module_from_spec(s)
s.loader.exec_module(n)
git = n.git


def put(name, value):
    with (R/name).open('x',encoding='utf8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False)


def main():
    assert git('rev-parse','HEAD') == BASE and not git('status','--porcelain')
    assert not git('tag','--list','*'+ID) and not DEST.exists()
    root = json.loads((R/'TARGET_ZONGLIN2_ROOT_CREATED_ACTUAL.json').read_bytes())
    assert root['root'] == '/home/lc01/Zonglin Li/zonglin2' and root['no_existing_item_deleted_or_overwritten']
    started = json.loads((R/'SOURCE4090_TO_ZONGLIN2_TRANSFER_V2_STARTED.json').read_bytes())
    assert started['pid'] == 37248 and started['no_deletion_or_existing_file_overwrite']
    cfg = tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    prompt = D/'MONITOR_HUMAN_ZONGLIN2_DEPLOY_ACTIVE_TRANSPORT_OWNER_ACTUAL_20261015.txt'
    assert cfg['prompt'].encode('utf8') == prompt.read_bytes()
    assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    put('ZONGLIN2_DEPLOY_HUMAN_SCOPE_AND_SAME_MONITOR_TOML_VERIFIED_ACTUAL.json',dict(epoch=time.time(),
        human_target_root_only_and_no_deletion=True,same_hourly_monitor_status_target=True,
        exact_prompt_SHA=hashlib.sha256(prompt.read_bytes()).hexdigest(),
        copy_owner_creationargv_and_later_actual_priority=True,not_new_monitor_PPO_or_budget=True))
    note = D/'ZONGLIN2_DEPLOYMENT_STARTED_STAGE_NOTE.txt'
    with note.open('x',encoding='utf8') as f:
        f.write('''Human explicitly authorized deployment at10.24.0.72 only below /home/lc01/Zonglin Li/, creating a new work directory zonglin2, with no deletion of anything, and allowed copying from the existing4090 host. Target exactresolved directory /home/lc01/Zonglin Li/zonglin2 was created with exclusive guards; original base directory entries retained. All new remote archives, environments, sources, HOME/XDG/cache/temp/log/runtime support must stay below this root. No system/driver/profile/oldconda mutation, no deletion or cleanup, no newPPO/S8/budget action. Credentials entered hidden, never saved.

Read-only source210 actual environment is Python3.12.14/Torch2.10cu128/TensorDict0.14.1/RSL5.0.1/Sim6.0.1metadata/Lab6.1.14, actualLab imports from the original3beta path. Source40.7GB plus selected originalLab/MOD4isaac/robot/cad/scripts/train paths; sourceUbuntu24.10/glibc2.40/driver560.35.05, no source compute jobs at snapshot. TargetUbuntu20.04/glibc2.31/driver535.54.03/two4090 requires actual ABI/runtime validation. No metadata, prepared code or copy is counted as GPU/physics/training admission. OfficialIsaac6 docs require Python3.12/glibc2.35 and list testedUbuntu22/24 anddriver580.95; sourceactual560runtime evidence and targetactual535 status remain separate, no unapproved system upgrade or SDKguard bypass.

Original first transfer failed before source payload because localWindows Path produced backslash Linux-C path. Preserve original source/error and original small targettar. IndependentV2 only fixes explicitPOSIX sourcepath handling and uses newarchive/receipt namespace; it is actively streaming source readonly through one human-authorized root-owned210-to72 relay. Actual PID37248/create2026-10-15T22:26:50.459891+08 argvtransfer_source_environment_to_zonglin2_finite_v2_linuxpaths_once.py exclusiveowner while actualcreationargv alive. No other root/agent connects210/249/72; no secondcoordinator/watcher or denseSSH. Actual STARTED/CURRENT/COMPLETE/ORIGINAL_ERROR/CIM and same-root actual receipts govern later handoff. Archive compressed size/SHA remains unknown until stream closes and targetSHA verifies; currentpartial retained, no blindtransfer replay. Prepared safe extraction writes only newownedpaths, checks link/hardlink destinations and preserves originaltar. Prepared originalcondapack prefix tool preserves BSDlicense and SHA; only newcopy path relocation, quoted launcher handles spaces and redirectsHOME/XDG/temp/cache/logs tozonglin2. NativeCPUdoctor and conditional independent privateuserspaceglibc preparation are future-only, not executed/admitted here; no systemlibc/kernel/NVIDIA libraries modifications. Compatibilityerrors must be preserved, no fakeGPUready result.

Priorhost72inspection uniquecommit0b82a73263d954ad71c42bd79de1f3762aec57f6/tagtrial-20261015-host72-dual4090-readonly-environment-audit/object23eb360044c45ffb8e161b7ed998c859dc3d0241 verifiedremote main/peel/all1347oldtags/tracked10. Priornominalcompleteordinary411ca16b760c43aaea4454485604e6e6a434ee46 verifiedremote/all1347oldtagpeels/tracked19677; S5 scope remains unfinished and temporarily secondary to this human deployment. Same mod4-10 ACTIVE/hourly/target updated to respect newhuman scope and livecopyowner, no secondmonitor. Solecanonical1188000s/sevenextensions unchanged, frozen/CPU/deployment0PPO uncharged, no accountingcopy/clear/refund/tail. LaptopGPU stillpaused; source4090 remains untouched; no oldGPU/Task/once replay or otherAI/WASD intervention.

All saved successes/failures/path-reader repairs/sources/unused preparations/actualsource-target receipts/scope/monitor captured at snapshot. New real deployment stage recorded once, latercopy/extraction/runtime results and receipts ordinarysupplements. Pushfailure resumes existingobjects only, neverrepeatrecord/tag/commit. Credentials excluded; remote largearchives indexed only after actualpath-size-SHA receipt and retained. Git does not block transfer or runtime. This archive is a started-stage record, not deployment completion.
''')
    old = {}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
        v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
    assert len(old)==1348
    sys.path.insert(0,str(REPO/'archive_tools'))
    from capture_history import redact
    DEST.mkdir(parents=True)
    rows,files=[],[]
    for p in sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        raw=p.read_bytes();clean,count=redact(raw.decode('utf8'));data=clean.encode('utf8') if count else raw
        out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        rel=out.relative_to(REPO).as_posix();files.append(rel)
        rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),capture='redacted_full' if count else 'complete_exact_bytes',redactions=count))
    index=DEST/'REPORT_CAPTURE_INDEX.json'
    index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,credentials_excluded=True,
        mutable_transfer_CURRENT_frozen_only_at_snapshot=True,later_completion_runtime_receipts_require_ordinary_supplement=True,
        incomplete_remote_archive_not_falsely_given_final_SHA=True),indent=2),encoding='utf8')
    files.append(index.relative_to(REPO).as_posix())
    n.m.cap.g=git;n.m.cap.a.gitio.g=git
    rec=importlib.import_module('record_experiment');rec.git=git
    sys.argv=['record_experiment.py','--id',ID,'--title','Create human-scoped zonglin2 and start source4090 environment migration without deletion',
        '--kind','deployment','--note-file',str(note),'--files',*files,
        '--validation','Actual exact new targetroot created and originalbase retained. Source4090 readonly stack versions/paths/size checked; V1Windows-POSIX tar path failure preserved, V2newarchive streams under actualsolecopyowner. Prepared guarded extraction/newcopy prefix relocation/quoted isolatedHOME-cache launcher/nativeCPU and conditionalprivateGLIBC helpers are unused, not runtime pass. Same hourlymonitor honors newhuman priority; no system/driver/profile/source mutation, delete, GPUtraining or budget. CurrentpartialSHA unknown until actualclosed targetverification.','--push']
    rec.main()
    head=git('rev-parse','HEAD');tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;obj=git('rev-parse',tag)
    n.m.cap.a.verify(rows,old,head,tag,obj)
    value=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,
        actual_remote_main_tag_peel_all1348_oldtags_and_trackedSHA_verified=True,saved_sources=len(rows),
        later_transfer_extraction_runtime_and_this_receipt_need_ordinary_supplement=True)
    put('ZONGLIN2_DEPLOY_STARTED_STAGE_GIT_RECORDED_ACTUAL.json',value)
    print(json.dumps(value),flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:
        put('ZONGLIN2_DEPLOY_STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),
            resume_existing_objects_if_created=True,no_repeat_record_tag_commit_or_runtime=True))
        raise
