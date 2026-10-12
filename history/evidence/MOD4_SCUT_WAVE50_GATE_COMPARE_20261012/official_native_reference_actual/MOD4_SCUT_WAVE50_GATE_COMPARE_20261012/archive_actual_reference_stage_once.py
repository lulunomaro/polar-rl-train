"""One unique actual SCUT reference stage; every retained trial/report and later supplement."""
from scut_wave_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';ID='scut3060-wave50-official-models-fullraw-and151-route-diagnosed';DEST=REPO/'history/evidence'/D.name/'official_native_reference_actual';FOLDERS=(D,W/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012',W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012')

def prior_index():
    prior={}
    for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
        for row in json.loads(p.read_bytes()).get('entries',[]):
            if row.get('sha256') and row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
    return prior

def capture(dest):
    prior=prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    assert not dest.exists();dest.mkdir(parents=True);rows=[];files=[]
    for folder in FOLDERS:
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
            if sha in prior:
                ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
            elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
            else:
                try:txt=raw.decode('utf8');enc='utf8'
                except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1_byte_preserving'
                clean,n=redact(txt);data=clean.encode('utf8') if n else raw;out=dest/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=enc,redactions=n)
            rows.append(row)
    p=dest/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_source_reports_rejections_errors_cost_false_and_prepared_unused_captured=True,large_originals_retained_index_only=True,credentials_excluded=True,later_Git_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix());return rows,files

def verify(rows,old,head,tag=None,obj=None):
    remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
    if tag:assert remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
    for name,(o,c) in old.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
    tracked=set(gitio.g('ls-files').splitlines())
    for row in rows:
        if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']

def main():
    assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
    for name in ('SCUT_REFERENCE_COMPLETE_SCOPE_DECISION.json','ELIGIBLE_SCUT_REFERENCE_FULLRAW_REVIEW.json','UNCHANGED_WORKER_ACTUAL_RESTORED_VERIFIED.json','SCUT_REFERENCE_AND151_METADATA_SYNCED.json','SCUT151_HOURLY_MONITOR_ACTUAL_VERIFIED.json','WAVE_ACTUAL_TRAINING_DURATION_SUMMARY.json'):assert json.loads((R/name).read_bytes())['passed']
    old=gitio.refs();save('SCUT_REFERENCE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=gitio.g('rev-parse','HEAD'),old_tags=len(old)))
    note=D/'ACTUAL_SCUT_REFERENCE_STAGE_REPORT.md';assert not note.exists();note.write_text('''# Official SCUT original-plant3060 Wave50 reference complete; full151/route coverage reviewed

Human explicitly requested originalSCUT policy/strategy on3060 against our wave route, and keeping normal training independent. Pinnedb8ff79f3 114source/model/asset/savedparameter bytes verified; both officialrough_rotation_stair model1000 and originalV14_2 USD/native5msx4-50Hz/TGS12-6/originalDR/inference actorunchanged/no optimizer. ExactactualMOD4saved80cellfloat32 worldtriangles/50mmpeaktrough/fulltenwaves2.406422727m/.4rootapproach/±.3vy-yaw0/15s/bothwheelbefore-to-after200mm/positiveverticalforceintegral>1N: July23forward5/27 reverse0/27, July30forward6/27 reverse0/27. All750controls3000callbacks/sensors actualdownrays/finitehits/scaledactorcommands/no modes/fullraw/query actualSHA independently reviewed. Removing1N orafter200mm addedno completes. Extra2mm closure shadowcontrolendpoint+.1sgraceall0 iscrossplantdiagnostic; nooriginaldones changed/noMOD4threshold lower/no originalauthorengine orcrossrobotDRsolver/hardware equivalence claimed. Publicmodels donot prove authorlackoftraining; fulltrainingexposurelogsunknown. Perfect27/27batchhardgatewording wasoverstated, corrected againstapprovedRM003no90/95/100gate, noalternatenumericthreshold invented.

All attempts retainedindependentID/root: SSHorphan preGPU/borrow; TaskServicetokenSyntaxError preexec; nulltriggerreader receipt-onlycontinuation; network_retry jobsreader beforeborrow/GPU; initialtwo completefullraw scope-ineligible becauseheightRayCaster quaternionABI; subsequentactualdownrays pass butactorcommand assertionstrictcontrol0reject; finalindependentcommandhook scope retains originalhookonce andbindsrequestedfixturebeforeoriginalobs, noaddednoisedraw/changedactorrobotDRclocksolverroute. Nooldscope scoresraw/failure overwritten orqualified. Oldineligible fullGPU traces retainedseparately, noMOD4validcomplete/failureeval replay. Source/nativeAPI diffs/errors/unusedpreparation/logs/actualresult pathsSHA captured.

Original3060demandworker borrowedonlyallcurrentplannedjobscomplete/actualfreshpolling/PIDcreationargv/noGPUchild andownedmsvcrt lock. OriginalsourceSHAs/taskactions/zero triggers/newactualCIM andsharedOSlockheld restored; allownreferencechild/coordinatorexited/fouroneoffszero-triggerReady. No4090trainerstop-hotpatch/no canonicalwrite-charge/oldmainresumeonce replay/WASDGUI. Samehourlymod4-10ACTIVEtarget/quiethealthy nativeupdateactualTOMLexact verified; noadditionalmonitor.

Own426same50entrydirection finalCPU104/830f/PID/fullsave/9startup exactCPUCUDAroundtrip/sourceepisode+1/41updates984controls/positive9actorchangedoptimizerdelta820/PASSED/unique935.4992797374725s parentonce/actualexit-twofcntl-free-noactive reviewed. Fullsavedtrace originaldynamicfamily/two signedstanding/prereset-before/histphase retained. New151fourcases actualcomplete/errorfree/twohost8JSONfullraw-query/6000callbacks-ground1e-6-contactintegralCOMhardware/initial30q-params-staticrecipes-assignments originalprotocol and115129retention audited; forward9/27 reverse26/27/ordinary0/route0, direct15012/25 pairedall perenvimprovement-regression-prefix. Noqualified50/fullRM-MoE/permanentantiforgetting, E0/acceptedCURB20-WAVE35-SLOPEscope freeze/gateuntrained preserved.

ActualCPUpost151 confirms1Npositioncompletionepisodeagreement and35observedcompleted rootpaths2.973834991455078–3.1593399047851562m all>oldtraining2m route; independentexposuregapdiagnosis, notallposturesunreachable oruniquecausalproof. Oldrouteunchanged/newroutelearningexecutornotdeployed; nextindependentfullstate/route-lifecycle scopeworkorder mustactualadmit, notthirdblindcurrentdurationblock/70. SamefixedDRrewardhardwarecommandsclockgeometry/005max2thenfullreview/otherexpertgate protected. CentralCAS actualSCUT/final426/complete151/direct150/routeCPU/nextworkorder withmasterapprovaltracksRM004bytesprotected/canonicalnotwritten. Allnewreports/errors/source/preparedunused/monitor/sync/Gitreceipt captured; laterreceiptordinarysupplement. Gitnottrainingdependency.

Solecanonical actual9Waveformal segments9564.97620677948s≈2h39min includesloadlearnsaveexit (35mm3986.96098780632s≈1h6min/50mm5578.01521897316s≈1h33min); discardedPPOprechecks973.965128660202s≈16min separately. Firstformal2026-10-10 23:42+08, wall~35h isnotcontinuoustraining andexcludesancestor129mixedlessons.0051188000/7extensions seventh100h alreadyonce/noledgercopy-clearactive-tail-recharge-extension; actualaccounted tail priority. NoARMs/S8/hardware/MoE deploymentgrant. Nocredentialoutput/Git; largeweights-rawNPZ-USD-ZIP actualpathsizeSHA indexonlyoriginalskept.

Allrealstage evidence capturedcomplete anduniqueannotatedrecord_experiment remote main-tag-peeled-alloldobjects/trackedSHA verified; pushfailurecontinueexistingobjects no re-record-tag-commit. Workspace lookup missingpath/cwd errors preCPU/sourceinspection retainedasobserver errors, notphysicsfailures.
''',encoding='utf8')
    rows,files=capture(DEST)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
    def short_git(*args):
        if args[:2]==('add','--'):
            r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in args[2:]),capture_output=True,check=True);return r.stdout.decode().strip()
        return original(*args)
    rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Audit official SCUT3060 Wave50 references and complete151 route exposure','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Two native official actors fullraw originalplant/DR/50Hz complete; initial rejected/ineligible source/raw/errors retained. Threshold/contact-margin split, unchangedworker actualrestored. Own426final/full151direct150/routeCPU diagnosis and exactsoleledger durations. ProtectedcentralCAS and nativehourlymonitor verified. NoPPO/budget or productionthreshold mutation.','--push'];rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag);verify(rows,old,head,tag,obj)
    save('SCUT_REFERENCE_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_current_saved_sources_reports_tracked_exact=True,saved_sources=len(rows),old_tags_preserved=len(old),push_pending=False))
    print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,saved_sources=len(rows))))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_record_tag_commit_replay=True));raise
