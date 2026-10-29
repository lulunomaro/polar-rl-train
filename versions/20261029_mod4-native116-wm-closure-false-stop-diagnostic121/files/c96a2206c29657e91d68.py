"""Archive actual CPU121 once via record_experiment, no binary input reads.
If commit/tag/push partially succeeds, continue those existing objects only.
"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import time
import traceback

T=Path(__file__).resolve().parent
G=T.parent/'polar-rl-train'
S=T/'H1_NATIVE116_WM_CLOSURE_FALSE_STOP_CPU_V121_20261029'
R=S/'reports'
BASE='21c35f2b9120916fc253e190dde3179cd22a2a17'
ID='mod4-native116-wm-closure-false-stop-diagnostic121'
TAG='trial-20261029-'+ID
REL=Path('versions/20261029_'+ID)
DEST=G/REL


def git(*args,binary=False):
    p=subprocess.run(['git',*args],cwd=G,capture_output=True)
    if p.returncode:
        raise RuntimeError('git '+args[0]+' failed: '+p.stderr.decode('utf-8','replace')[-1800:])
    return p.stdout if binary else p.stdout.decode('utf-8').strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put(p,value):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))


def local_tags():
    tags={}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
        p=line.split();tags[p[0]]=dict(object=p[1],peeled=p[2] if len(p)==3 else None)
    return tags


def remote_refs():
    refs=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines())
    tags={name:dict(object=value,peeled=refs.get(name+'^{}')) for name,value in refs.items()
          if name.startswith('refs/tags/') and not name.endswith('^{}')}
    return refs['refs/heads/main'],tags


def main():
    assert git('rev-parse','HEAD')==BASE and git('symbolic-ref','--short','HEAD')=='main'
    assert not git('status','--porcelain=v1'), 'Preserve unrelated existing changes'
    assert not git('tag','--list',TAG) and not DEST.exists(), 'Consumed phase; continue existing objects'
    old_tags=local_tags();assert len(old_tags)==1484
    assert remote_refs()==(BASE,old_tags)
    completed=json.loads((R/'NEW121_WM_CLOSURE_FALSE_STOP_CALIBRATION_COMPLETE_ACTUAL.json').read_bytes())
    assert completed['passed_execution'] and completed['counts']==dict(control_raw_reads=1,checkpoint_decodes=1,checkpoint_integrity_passes=1)
    assert json.loads((R/'AUTOMATION_CURRENT121_PERSISTED_CHECK.json').read_bytes())['passed']
    put(R/'ARCHIVE_ACTUAL121_CONSUMED_BEFORE_CAPTURE.json',dict(epoch=time.time(),phase_ID=ID,
        fixed_tag=TAG,base_HEAD=BASE,protected_old_tag_count=len(old_tags),
        source120_not_selected_as_sufficient_jump_fix=True,
        no_training_model_raw_binary_or_host_GPU_read_for_Git=True,
        failure_policy='If commit/tag/push exists, continue existing objects. Never rerun record_experiment or retag.',
        postGit='Final verification is tool output only, no report chasing HEAD.'))
    extras=[T/'prepare_NEW121_WM_closure_typed_purpose_SOURCE_CPU_once.py',
        T/'freeze121_closure_calibration_and_next_process_requirements_once.py',Path(__file__).resolve()]
    sources=sorted(set(extras+[p for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts]),key=str)
    sys.path.insert(0,str(G/'archive_tools'))
    from capture_history import redact
    DEST.mkdir(parents=True,exist_ok=False);(DEST/'files').mkdir()
    rows=[]
    for p in sources:
        st=p.stat()
        if p.suffix.lower() not in {'.py','.json','.txt','.md','.toml','.ps1'}:
            rows.append(dict(origin=str(p),bytes=st.st_size,SHA='unknown',status='metadata_only_no_content_read'))
            continue
        raw=p.read_bytes();text=raw.decode('utf-8-sig')
        assert st.st_size==len(raw) and p.stat().st_mtime_ns==st.st_mtime_ns
        filtered,n=redact(text)
        archived=filtered.encode('utf-8') if n else raw
        name=sha(str(p).encode())[:20]+p.suffix.lower()
        target=DEST/'files'/name
        assert not target.exists()
        target.write_bytes(archived)
        if p.suffix.lower()=='.py':ast.parse(filtered)
        if p.suffix.lower()=='.json':json.loads(filtered)
        rows.append(dict(origin=str(p),original_name=p.name,bytes=len(raw),original_SHA=sha(raw),
            archive_path=(REL/'files'/name).as_posix(),archived_bytes=len(archived),archived_SHA=sha(archived),
            status='complete_UTF8_redacted' if n else 'complete_UTF8_exact_bytes',redaction_count=n,
            redaction_reason='repository credential detector' if n else None))
    put(DEST/'CAPTURE_INDEX.json',dict(epoch=time.time(),phase_ID=ID,kind='diagnostic_CPU_not_training',
        previous_HEAD=BASE,old_tags=old_tags,entries=rows,
        control_raw_checkpoint_originals_not_read_for_capture=True,
        all_prediction_JSON_are_new_derived_text_not_raw_trace_replay=True,
        external_artifacts_index='See indexed EXTERNAL_INPUTS_METADATA_ONLY_FOR_GIT.json',
        active_MuJoCo_window_not_changed_or_recaptured=True))
    note=(
        'NEW121 is a completed necessary CPU diagnostic of source120 closure-stop readiness, not new training. '
        'The human-observed true MOD4 policy stands tall, charges forward and ends on closure instead of jumping270.\n\n'
        'One qualified116h1 checkpoint decode/integrity pass and one original118431control read were admitted after '
        'synthetic source checks and typed data validation. Only WM was constructed/forwarded; no Pi/Critic/optimizer, '
        'normal86, SDK, GPU, physics, SSH, account, TaskGO or learning. All596 original Python source rows and typed '
        'receipt/manifest pins were guarded. WM/norm/RNG stayed unchanged.\n\n'
        'All431 original31body-anchor and actual-q own-FK classifications agree with the cached real closure flags. '
        'The genuine4.31s terminal is2.23560375mm, above the unchanged original2mm threshold. The actual-q FK gives '
        '2.23564124mm. But all431/424/400 physically contiguous actual-action1/8/32 windows predict no closure stop '
        'anywhere. The three predictions ending at the true failure give1.30721601/1.77261292/1.24487188mm, below2mm. '
        'Thus zero false-stops in this case does not mean successful failure prediction: each final failure forecast '
        'is missed. Source120 detects the supplied true failure state but is not a sufficient repair when used on these '
        'WM-predicted states. It is not selected as a sufficient jump fix and no new H1 learning is launched.\n\n'
        'Actual executed6 and normalized episode-fixedxi31 are used at every offset, with native127/dynamic54, '
        'recorded31body SDKxyzw poses, original time/queue/reset domains and no future actual-state injection. '
        'Request phases/onset crossings are separated. Overlapping windows are not independent trials. This is '
        'one frozen low-flight stand/charge case, not27cm/general counterfactual qualification or a unique causal proof. '
        'CPU Torch2.7 versus producerGPU2.10/TF32 is explicit; the2.98e-8m rootZ agreement is consistency only.\n\n'
        'The valid takeoff/cross/landing process objective remains unresolved. The next requirements document is '
        'source-only and warns that native127 lacks nonwheel-contact/history latches andH32=.32s is shorter than '
        'the required.5s recovery. No blind tuck bonus, missing-signal fabrication, forced motor script, airborne reset, '
        'cold restart, identical learning window or relaxation of the physical2mm guard. Latest qualified method116 remains.\n\n'
        'All source, full new numerical predictions, admission/once/CPU/CIM receipts, next-source requirements and '
        'actual same-hourly-automation update are indexed. No binary/model/raw reads for Git; external originals retain '
        'their path/bytes/existing producer SHA only. Prior ordinary119120 already pushed21c35f2; its consumed entries '
        'and all1484 old tags/peels are preserved. Record this real CPU phase121 once; no separate source-only GPU tag.\n')
    note_path=DEST/'EXPERIMENT_NOTE.md';note_path.write_bytes(note.encode('utf-8'))
    selected=sorted(p.relative_to(G).as_posix() for p in DEST.rglob('*') if p.is_file())
    # A documentary byte archive is checked by UTF8/schema/SHA, not whitespace
    # normalization. Preserve original line endings under existing * -text.
    command=[sys.executable,'-B','-X','utf8',str(G/'archive_tools/record_experiment.py'),
        '--id',ID,'--title','Measure H1 WM closure failure prediction before further learning',
        '--kind','diagnostic','--note-file',str(note_path),'--files',*selected,
        '--validation','CPU121 complete:1 controls read/1 checkpoint decode;431/424/400 action windows;0 false-stops but all three final closure forecasts missed; no GO.',
        '--push']
    child=subprocess.run(command,cwd=G,capture_output=True)
    if child.returncode:
        put(R/('ARCHIVE121_RECORD_OR_PUSH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),returncode=child.returncode,stdout=child.stdout.decode('utf-8','replace'),
                stderr=child.stderr.decode('utf-8','replace'),actual_HEAD=git('rev-parse','HEAD'),
                actual_tag=git('tag','--list',TAG),never_rerecord_or_retag=True))
        raise RuntimeError('record/push refused; inspect actual HEAD/tag and continue existing objects')
    print(child.stdout.decode('utf-8').strip(),flush=True)
    commit=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}')
    assert commit!=BASE and git('rev-parse','HEAD^')==BASE and peel==commit
    expected=dict(old_tags);expected['refs/tags/'+TAG]=dict(object=obj,peeled=commit)
    assert local_tags()==expected
    remote_head,remote_tags=remote_refs();assert remote_head==commit and remote_tags==expected
    for row in rows:
        if row['status'].startswith('complete_UTF8'):
            data=git('show','HEAD:'+row['archive_path'],binary=True)
            assert sha(data)==row['archived_SHA'] and len(data)==row['archived_bytes']
    committed=git('ls-tree','-r','--name-only','HEAD','--',REL.as_posix()).splitlines()
    for name in committed:
        assert git('show','HEAD:'+name,binary=True)==(G/name).read_bytes()
    experiment='history/experiments/20261029-'+ID+'.json'
    record=json.loads(git('show','HEAD:'+experiment,binary=True))
    assert record['tag']==TAG
    for name,digest in record['source_and_evidence_sha256'].items():
        assert sha(git('show','HEAD:'+name,binary=True))==digest
    assert not git('status','--porcelain=v1')
    print(json.dumps(dict(passed=True,commit=commit,remote_main=remote_head,tag=TAG,
        tag_object=obj,peeled=peel,protected_old_tag_objects_and_peels=len(old_tags),
        total_tags=len(expected),verified_new_text_blobs=len(committed),complete_text_entries=len(rows),
        repository_clean=True,no_new_learning_or_binary_read_for_Git=True)),flush=True)
    # Do not write another saved verification file after the above success.


if __name__=='__main__':
    try:
        main()
    except BaseException:
        p=R/('ARCHIVE121_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
        put(p,dict(epoch=time.time(),traceback=traceback.format_exc(),
            rule='Continue existing commit/tag/push if present; no re-record or retag.'))
        raise
