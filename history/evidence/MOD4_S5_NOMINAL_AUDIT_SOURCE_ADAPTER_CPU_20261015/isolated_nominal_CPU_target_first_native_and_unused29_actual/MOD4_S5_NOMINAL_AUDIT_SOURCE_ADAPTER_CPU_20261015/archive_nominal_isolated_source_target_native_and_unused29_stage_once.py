"""Unique real nominal stage; later actual results are ordinary supplements."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
import time
import traceback

D=Path(__file__).resolve().parent
W=D.parent
R=D/'reports'
REPO=W/'polar-rl-train'
M=W/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
BASE='5dc8cd77c32c4af8438a5024dd45b2e5eb36f9a1'
ID='s5-nominal-absent-mild-audit-source-cpu'
DEST=REPO/'history/evidence'/D.name/'isolated_nominal_CPU_target_first_native_and_unused29_actual'
p=M/'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py'
s=importlib.util.spec_from_file_location('nominal_archive_pure_capture_helpers',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
H=m.H


def git(*args):
    p=subprocess.run(['git','-c','http.sslBackend=openssl','-c','http.version=HTTP/1.1','-C',str(REPO),*args],
                     capture_output=True,text=True,encoding='utf8',timeout=120)
    assert p.returncode==0,p.stderr
    return p.stdout.strip()


def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)


def capture():
    prior=m.cap.a.prior_index();sys.path.insert(0,str(REPO/'archive_tools'))
    from capture_history import redact
    assert not DEST.exists();DEST.mkdir(parents=True)
    allowed=set()
    for p in list(R.glob('*_S5_SINGLE_CONTROL_CPU_ADMITTED.json'))+list(R.glob('*_S4_ROUTING_CPU_ADMITTED.json')):
        v=json.loads(p.read_bytes());q=R/(v['case']+'_ORIGINAL_PHYSICAL_CPU_REVIEW_V2.json')
        if v['passed'] and q.exists() and json.loads(q.read_bytes())['result']['data']['complete_data_contract']:
            allowed.add(v['case'])
    assert 's5_nominal_s20261002_single_eval_flat_120_v1' in allowed
    rows=[];files=[];deferred=[]
    for p in sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.partial'):
        rel=p.relative_to(D)
        if rel.parts[0]=='actual_collections' and rel.parts[1] not in allowed:
            deferred.append(str(p));continue
        size=p.stat().st_size
        large=p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.whl','.dmp','.mp4') or size>8000000
        if large:
            before=p.stat();h=H(p);after=p.stat()
            assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Mutable big artifact'
            row=dict(source_path=str(p.resolve()),bytes=size,sha256=h)
        else:
            raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h)
        if h in prior:
            old=prior[h];assert H(REPO/old['Git_path'])==old['archived_sha256']
            row.update(capture='same_SHA_existing_Git_reference',Git_path=old['Git_path'],archived_sha256=old['archived_sha256'])
        elif large:
            row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True,streaming_hash=True)
        else:
            try:text=raw.decode('utf8');encoding='utf8'
            except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
            clean,count=redact(text);data=clean.encode('utf8') if count else raw
            out=DEST/D.name/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            path=out.relative_to(REPO).as_posix();files.append(path)
            row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=path,
                       archived_sha256=hashlib.sha256(data).hexdigest(),encoding=encoding,redactions=count)
        rows.append(row)
    index=DEST/'REPORT_CAPTURE_INDEX.json'
    index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,
        all_saved_sources_reports_failures_false_unused_readers_deploy_cost_monitor_at_snapshot_captured=True,
        included_CPU_admitted_cases=sorted(allowed),unadmitted_or_incomplete_collection_paths_deferred=deferred,
        later_mutable_current_files_new_reports_raw_and_receipts_require_ordinary_supplement=True,
        large_originals_retained_and_credentials_excluded=True),indent=2),encoding='utf8')
    files.append(index.relative_to(REPO).as_posix());return rows,files


NOTE='''Approved master812a4b/004005/RM003002001 remains unchanged. S5 frozen A single W35/B E0+W35 rule/C firstgate148 fair comparisons. Existing white_v2 complete30 ordinary e411 was created only once; preserved RPC/TLS failures and V2 verification rejection wrongly equating the original stage57 tag peel with ordinary e411 HEAD. Independent read-only V3 correctly verified remote main e411, original stage object+peel, all1346 old tag pairs and4820 saved entries. Subsequent ordinary5dc8cd77c32c4af8438a5024dd45b2e5eb36f9a1 preserves later original errors/recovery/monitor/source and was actually verified remote main/all1346 old tags/tracked488 entries. No record/tag/commit or GPU rerun was used to recover existing objects.

Original nominal configure intentionally creates no MildDR. Existing four audit-hook constructors, factor params/private_rng and chassis audit assumed it existed. This new isolated candidate guards only absent-MildDR audit registration, keeps the original gas-to-spring D6 expected-damping overlay and reference restoration, captures actual D0 mass/inertia/materials once as a read-only reference and asserts exact unchanged readback plus actual unity motor output scales. D5/D6/D7 original numerical audit methods, samplers/RNG/physics setters/resets/clock/reward/commands/hardware remain inverse-AST exact. Nominal metadata is explicitly null/absent for nonexistent MildDR fields/generators; no fake randomizer or RNG is created. Original uniform-COM rejection remains preserved and reproducible; actual D7 per-clone COM/PD pressure remains strict rather than being declared off. Seven source inverses/fourN80/88-seed02/03 CPU tensor fixtures/60 negatives, original white_v2/v3 metadata/RNG/hook equivalence and disclosed parent-fixture Spring constructor checks passed with zero CUDA/globalCPU RNG advance/optimizer. V1 CPU reader missing os NameError and independent V2 reader-only fix preserved.

Complete new package65521714B SHA6799d6021cf833d87934e2f1bd82956de71155077f79fa28252deeb7e6bf44b0, manifest13148a150fbf425b7b7b41b89056a545de271c1f3b4c1b0eb7835cd91ef8872e; 518package files,476 original shared files alltargetSHA checked,477 copied isolated shared files with declared7 modified source candidates+new helper (eight explicit overlays overall). Original installed SDK/shared source unchanged, original three V8 physical mainloop bytes/five control adapters exact, worker AST inverse only nominal/profile/namespace/explicit isolated paths, witness only explicit profile metadata. Target CPU actually loaded own helper, checked source import resolution/SDK stub/native binding/versions/all sources and whole E0b10994float/W35b026102float/gate02718c194tensor113float. Source-only metadata is distinct from actual loaded DLL and full SDK/20k GPU state restoration. Actual per-case resource/OS-lock/source/lease is independent of approvedGPUfalse template.

Own first s5_nominal_s20261002_single_eval_flat_120_v1 actually completed120x80/480callbacks, parentEXIT0/unique45.02816557884216s frozen0PPO/no canonical write, actual parent/launcher/child out/sharedmsvcrtfree and whole twohost rawSHA. Original missing EXIT_NATURAL remains missing beside independent data/cleared/EXIT0/actualPID closure. First coordinator34592 naturally stopped on CPU-reader TypeError: the original physical flat main legitimately saves optional mild_initial/mild_final as None in nominal; it did not fail physics. V1 reader and coordinator ORIGINAL_ERROR remain. Independent V2 reader uses actual final chassis_PD nominal audit and complete initial/final witness readback, does not fabricate initial audit or rewrite None, rejects eight wrong actual-saved metadata negatives; unchanged full query1e-6/contact integration/COM frame1e-5/hardware/raw-finite/history/reset/source rules pass. Source9/STD initial-final exact/every saved CPU mean max5.340576171875e-5 nonbitexact/normal35/shared cached feedback/previous actual clipped6/selected reset/whole6 passed ordinary0/trunc0. Original GPU/native/Task/lease/raw collection not replayed. This is native admission, not15s behavior/fullskill or20k training DR restore.

New continuation executes only29 actualunused frozen cases (11newnative+18full), retaining already complete/admitted native1; original fixed30 coordinator/lease/once not relaunched. Actual coordinator70456/create1792060426.803 argv run_nominal_ABC_unused_remainder29_after_reader_fix_once.py --execute-root-remainder29-unused-only exclusively owns210/249 while actual creation/argv alive. Root/agents localreports+CIM only, actual CURRENT/COMPLETE/ORIGINAL_ERROR and OS-lock/PID boundaries take priority; no permanent-alive assumption. Every owncase EXIT0/PIDout/sharedlockfree/full physical-sourceCPU/twohostSHA before next; full same-seed-kind A/B/C initialrootq30/allparams/staticrecipes-RNGqueues-DLL exact pair before credit. Future full/otherkinds are not inferred passed. Static prelaunch transport-import alias and unused launcher logname mismatch were corrected before execution, originals kept. No extra watcher, retry/signal, duplicateGPU, extra PPO or budget transaction.

Source experts/gate/STD frozen, shared normal35 once/tick, previous actual action22:28/normalmode28:35/whole6 then originalclip6/selectedreset remain exact. No envID/terraintruth/futurecontact/teacher/headingposition correction/action averaging/hysteresis. Firstgate148 training already finalized/unique2668.750717s settled; no second gate window. Existing white_v2/v3 bothdevseed world A250/B256/C252 out of256 descriptive, B observed reference/fallback, C frozen, not a new mechanical promotion threshold or architecture global winner. Old straight/spin/legacyfalse and every failed validprefix preserved. SingleA is existing W35 ancestry scope comparator, not equal mixed-training ancestry or highspeed/pure registered qualification. Nominal remaining comparisons/original35 secondseed/profile/combinationDR/within-episode transitions/matchedsingle training ancestry/hardware remain unfinished. S3overall/S5overall/50or70/hardware qualification not claimed; f51650mm26/26 and all ancestor sources protected, no third blind BODY/left block or automatic70.

Human video42168288822-1-192.mp4 actualpath-size-SHA index preserved. About42/50s visually inspected approach/body lowering, extension, full airborne edge clearance and wheel landing/leg compression. Reference target is airborne wheel-leg step hopping; earlier12-24h low-step preparation estimate cannot be applied to its training start. Torque/spring energy/height/contact-force internals unknown from video. Asking for video understanding or earlier y is not E5/S8/newPPO approval; executable takeoff/reset/airborne/landing plan still separate, no reliable startdate. No change to sole005 canonical1188000s330h/sevenextensions or localWindows pending historic accounting. CPU/native/frozen0PPO uncharged, no ledgercopy/clearactive/refund/tail/recharge/automaticbudget. LaptopGPUpaused/Linux4090normalrepairtrainingauthorized/3060evalonly/Creadonly-Ddurable, no installed SDK/driver hotpatch/kill-delete/otherAI-WASDGUI/dualGPUworker. All saved success/failure/false/unused/source/schema/readers/lookupmisses/rawindexes/cost/deployment/workorders/monitor/Gitreceipts captured. Unique annotatedtrial once, later ordinary supplements; pushfailure resumes existing objects only; large originals indexed and retained, credentials excluded, Git is not runtime dependency.
'''


def main():
    assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list','*'+ID)
    assert json.loads((R/'NOMINAL_FIRST_NATIVE_REMAINDER29_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').read_bytes())['passed']
    assert json.loads((R/'NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL.json').read_bytes())['passed']
    old={}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
        v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
    assert len(old)==1346
    put('NOMINAL_ISOLATED_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,base=BASE,oldtags=len(old),
         no_runtime_dependency_or_GPU_replay=True,first_native_CPU_admitted_and_unused_remainder29_actual_started=True))
    note=D/'ACTUAL_NOMINAL_SOURCE_TARGET_FIRST_NATIVE_AND_UNUSED_REMAINDER29_STAGE_NOTE.txt'
    with note.open('x',encoding='utf8') as f:f.write(NOTE)
    m.cap.g=git;m.cap.a.gitio.g=git
    rows,files=capture()
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def recgit(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],
                input=b''.join(x.encode()+b'\0' for x in args[2:]),capture_output=True,check=True)
            return p.stdout.decode().strip()
        return git(*args)
    rec.git=recgit
    sys.argv=['record_experiment.py','--id',ID,'--title','Admit isolated nominal audit source on native physics and continue only unused frozen A/B/C cases',
        '--kind','evaluation','--note-file',str(note),'--files',*files,
        '--validation','Seven audit-source inverseAST, N80/88 bothdevseeds60negatives, whitebranch metadata/RNGexact; V1missingos preserved/V2reader fix. New complete isolated ZIP6799d602/518files/476original/477isolated/eightoverlays actualtargetCPU+SDK+whole94/102/113finite, no installed/shared edits. Ownnative120x80/480 closedEXIT0 actualPIDsout-lockfree/twohostSHA/wholephysical-query-contactCOMhardware/source9std-everyCPUmean passed. OriginaloptionalNone V1reader/coordinator34592failure preserved; independentV2 ownfinalaudit+initial-finalwitness fields and8actualsavednegatives, no fakeinitialaudit/no oldGPUreplay. New70456 owns only29unused cases whileactualcreationargv alive, futurefulls not inferred. Original e411objects remote verified after preservedTLS/ordinary-tag-peel reader correction; laterordinary5dc actualremote/all1346tags/tracked488 verified. Originalfalse/prefix/cost/source/video-S8scope/monitor and alloldfailures captured; no PPO/canonical/budget changes.',
        '--push']
    rec.main()
    head=git('rev-parse','HEAD');tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
    obj=git('rev-parse',tag);m.cap.a.verify(rows,old,head,tag,obj)
    value=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,
        actual_remote_main_tag_peeled_all1346oldtags_and_trackedSHA_verified=True,saved_sources=len(rows),
        unique_stage_recorded_once=True,later_results_and_this_receipt_need_ordinary_supplement=True)
    put('NOMINAL_ISOLATED_STAGE_GIT_RECORDED_ACTUAL.json',value);print(json.dumps(value))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('NOMINAL_STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),
            resume_existing_objects_ifrecord_created=True,no_record_tag_commit_replay=True,no_GPU_budget_action=True))
        raise
