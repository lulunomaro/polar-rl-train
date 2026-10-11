from direction_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name

def main():
    assert not old.g('status','--porcelain') and not old.g('diff','--cached','--name-only')
    previous=old.refs();prior_main=old.g('rev-parse','HEAD')
    assert prior_main=='ec83c93f732781d017f973e94aa76e75e0ad0553'
    assert json.loads((R/'DIRECTION_FINAL_CLOSEOUT_METADATA_SYNCED.json').read_bytes())['metadata_synced']
    save('DIRECTION_FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),prior_main=prior_main,ordinary_supplement_not_new_trial=True,all_saved_results_errors_sources_receipts_to_capture=True))
    sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    prior={}
    for p in BASE.rglob('*CAPTURE_INDEX.json'):
        index=json.loads(p.read_bytes())
        for row in index.get('entries',[]):
            if row.get('Git_path') and row.get('archived_sha256'):
                gitp=REPO/row['Git_path']
                assert gitp.is_file() and H(gitp.read_bytes())==row['archived_sha256']
                prior.setdefault(row['sha256'],row)
    dest=BASE/('final_saved_actual_supplement_'+str(time.time_ns()));assert not dest.exists();dest.mkdir()
    rows=[];selected=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get(h)
        if ref:
            row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'],same_content_source_context_preserved_by_index=True)
        elif p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip') or len(raw)>8000000:
            row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
        else:
            try:text=raw.decode('utf8');encoding='utf8'
            except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
            clean,n=redact(text);data=clean.encode('utf8') if n else raw
            out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            name=out.relative_to(REPO).as_posix();selected.append(name)
            row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=n)
            prior[h]=row
        rows.append(row)
    index=dest/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_errors_fullsave_current_eval_monitors_sync_Git_receipts_captured=True,large_originals_preserved=True,credentials_excluded=True,no_experiment_replay=True),ensure_ascii=False,indent=2),encoding='utf8');selected.append(index.relative_to(REPO).as_posix())
    note=dest/'SUPPLEMENT_REPORT.md';note.write_text('''# CURB20 direction startup repaired formal final and actual closeout evidence

Source423 inherited421 exact native/SDK proofs. Both new completePPO preflight weights discarded; fresh sameCURB-entry-direction newprocess0control0PPO strictfullCPUCUDA restore passed. Formal from1293c97 actually learned7updates168control3.36Menvsteps672callbacks then naturally fullsaved exited, own model32069 e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16/CPU104/source423/91actualsrcsnapshot+ownfreeze/PID2805952/unique originalparent330.21030592918396s. Ordinary/integrity/unknown0/nonfinitefalse/STOPnone, closure.947713444mm/mimic.001691456. Timeout1693 route287 overlap1 unique1979 andtwoexactcoverage. Actualparentguardianchildexited/twofcntl-free/active-Sactiveempty legalreviewready. Candidate140 terrain+flat+spin+world actuallypublished; current completed/errorfree onlycollected/reviewed, remainingpending normal. NoautomaticmorePPO/highercurb/qualification beforecomplete ownbehavior decision.

All original421 failedprelearn binding source/error/0PPO unique21.062857627868652cost retained; oldmonitor21.028 approximation corrected separately, notledgerrewrite. Original Windows argv206 deniedrecord process beforelaunch, capturepreserved andonlyunexecutedrecord completed via inprocess tool andNUL stdin pathspec; annotated repair ec83c93/tag3a322 unchanged andremotelyverified. This ordinarysupplement includes laterbig/fresh/formal/fullsource snapshots/rollingfreeze/CPUfullsave/PIDreceipts/ownuniquehealth/new140readers/countidentity/actualpendingcollection/localpathreadererrors/monitor/currentworkorder/finalcentralsync andpreviousGitreceipts. ExactexistingSHA content references originalGit paths; largeweights/rawNPZ/USD/ZIP indices only. Allsaved false/raw/cost retained, nocredentialoutput/Git.

Same heartbeat hourlyACTIVE quietpending actualverified; historicalmasterapprovaltracksRM andidlecanonical bytes protected duringunique metadataCAS, noledgerwrites/extension/recharge/clear/oldmain replay. E0/SLOPE5-8-10 acceptedranges frozen, Wave/CURB oldunqualified evidence retained, gateuntrained, WASDuntouched. Finaltracked/remote main/all oldtag/peeled verification emitted as tool output rather thancreating anendless receiptfile chain. Future candidate140complete/newreports requireordinarysupplement.
''',encoding='utf8');selected.append(note.relative_to(REPO).as_posix())
    payload=b''.join(name.encode('utf8')+b'\0' for name in selected)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=payload,capture_output=True,check=True)
    old.g('commit','-m','Record CURB20 direction formal fullsave closeout and candidate140 actual review evidence')
    head=old.g('rev-parse','HEAD')
    try:old.g('push','origin','HEAD')
    except Exception:
        save('DIRECTION_FINAL_SUPPLEMENT_PUSH_ERROR.json',dict(epoch=time.time(),commit=head,continue_original_objects_only=True));raise
    remote={x.split()[1]:x.split()[0] for x in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
    tracked=set(old.g('ls-files').splitlines())
    for row in rows:
        if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
    assert not old.g('status','--porcelain')
    print(json.dumps(dict(commit=head,remote_main_verified=True,all_old_tags_and_peeled_verified=len(previous),all_current_saved_source_report_indices_tracked_exact=True,new_files=len(selected),same_SHA_references=sum(row['capture']=='same_SHA_existing_Git_reference' for row in rows),large_indices=sum(row['capture']=='large_actual_path_size_SHA_index_only' for row in rows),total_source_index_entries=len(rows),later_reports_require_supplement=True)))

if __name__=='__main__':main()
