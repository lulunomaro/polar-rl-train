"""Record the real second426 deployment and full150/SCUT source review exactly once."""
from wave_direction_second_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';ID='wave50-full150-reviewed-same-direction426-second900-started';DEST=REPO/'history/evidence'/D.name/'second426_actual_deployment'

def main():
    assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
    assert json.loads((R/'DIRECTION_SECOND_TARGET_CPU_PASSED.json').read_bytes())['passed']
    assert json.loads((R/'DISPATCH_ACTUAL_RECEIPT.json').read_bytes())['actual_Popen_argv_cwd_start_verified']
    assert json.loads((R/'COMPLETE150_SECOND426_METADATA_SYNCED.json').read_bytes())['passed']
    assert json.loads((R/'SECOND_DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
    assert json.loads((R/'SECOND_DIRECTION_OWN_STARTUP_CONTRACT_VERIFIED.json').read_bytes())['passed']
    previous=gitio.refs();save('SECOND_DIRECTION_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
    note=D/'SECOND426_REAL_STAGE_REPORT.md'
    with note.open('x',encoding='utf8') as f:f.write('''# Full150 reviewed; same50 entry-direction second426 bounded900s deployed

Complete150 allfour errorfree/fullraw182821946B SHA2452d4c4c36a2cfc0d32aa3f14c17ded7ba2477b3d3ccfd2c9a8fed2e2aaffc7/query/twohost8JSON/allinitialization/6000callbacks/ground1e-6/contactintegralCOMhardware strictreview passed as data-validity. Forward12/27 reverse25/27, ordinary0/route4, original1N before-aftercontact equalsposition perenv/episode, all15forward+2reverse validfailedprefixes/rawfalse/cost preserved. Direct149 paired original1→12forward/25→25reverse but different initialsource/no causaltrainingclaim. Unqualified50, no70/fullRM-MoE/permanentantiforgetting.

Actualnewimmutable root /home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012/source426=all424oldbytesexact+truthfulsame50entrydirectionmanifestworker anduniquecontroller. Explicitown424095f/18038795B/CPU104 continuation onlysame-scope; accepted35b026/1293c97 ancestor retained, nodiscard/otherexpert default. Own424fullsave/PASSED/PID/unique325.21194553375244s/actualparentguardianchildexit/twofcntl-free/noactive verified. New426targetCPUfull104/independentstorage/privatecommanddiskfixture/strictwrongassignment-map-origin-profile-boundepisode/import-main-Popen-guardian/0051188000sevenextensions passed. Unique actualcontrollerPID3165050-start92072197/child3165148-start92072342, actualargv/cwd/source identity; nine actualownstartup strictsame50entrydirection CPUCUDA diskroundtrip/sourceepisode+1 passed, allnewflagsfalse/terrain-entry-direction-commandexacttrue. Activity is notformal final orpositivePPO proof withoutownsavedCPU changedactor/optimizerdelta.

Original1800s durable-save resourceguard refused: actualfree~4.75GB, 2*actualold1800wholeoutput1536678072B+2GiB=5220839792B. Refusal preserved; no raw/weights/source/environment/cache/otherAI deletion ortmpfs durability bypass. Independent900s chosen withinoriginal005max1800/max2; actualcompleted900s same20k/24control/16columnfloat32 trace wholeoutput795686159B resourceformat reference, same2x+2GiB+sourceassetdelta guard passed. CURB900 reference is storageformat evidence only, notWavegeometry/fullstate admission. Current900s loadlearnsaveexit/save25/15sguardian uniquelycharged byoriginalparent, no newbudget/preflightSDKnativefreshclockDR replay. Output/sourcefreeze426 independent; sameactualgeometry/reset-command-DR-reward-LR-hardware-clock/fivefamilies unchanged. Newactualcandidate151 unusedbothhostschecked, actualpublication governs; futureownfullsave/CPU104/PID/snapshots/PASSED/uniquecloseout/exitlocksidle beforefourcase/fulltrace/direct150, max2thenfullaudit/noautomaticthird/70. Missingfuture ispending, notfailure.

PreservedpreGPU/source-reader errors: oldfeedbackhelper selected149raw fromincorrectnamespace andstrictSHArejected full150; independentnamespace-only reader recovered originalstrictfeedbackformula/age/ready/rawlastreset. Originalbuildertwo malformedquote SyntaxErrors beforeexecution; independentonlyunfinishedbuild continued. SCUTreview dictkeyword startedwith15s preexecSyntaxError retained, independentkeyword continuation onlyunexecutedread. Read-only rg/Get-Content/git cwd lookups had missing-path errors; no physicalfault or GPU replay. No originalfailed source overwritten.

PinnedSCUT1a26356 train/V14/parentdones/July30savedenv actualpriorauditpath-size-SHA reverified plusofficialwebprimaryreads. Continuouslearn/ordinaryperenvreset, July30ordinary20*20ms=.4s duration/nonfiniteimmediate; heightcoursecode available butJuly30enabledfalse. Publicpathsdo notspecifyMOD427+27/15s/tenwave/200mm1Ngraduation; privateauthoracceptance unknown. RM003approved explicitlyno90/95/100gate: previousassistant27each hardgatewording corrected, allcomplete isstrongobservedscope evidence notuniversal mechanicalprogressionline. Current150 majorforwardresidual remains/contact-positionexact; no alternatepercentage invented, no false relabel/protocol/health/reward/DR/geometry mutation. Before-aftertwo-wheel support noteverytickdoublecontact. Full3.006m test vsoriginal2mtrainingroute exposure mismatch retained/rootproxy notcontact orcausalcertificate.

CentralCAS complete150/actual426/source/reuse/startup/resource/sourcecomparison synced, master-approval-tracks-RM004 bytesprotected/canonicalnotwritten. Same mod4-10ACTIVEhourlysametarget nativeupdateexact verified, healthypendingquiet/meaningfulonly.005solecanonical1188000s330h/7extensions seventh100h alreadyonce, actualaccountedtail priority/no extension-copy-clearactive-tail-recharge. No deletefcntl locks/kill/hotpatch/dual20k/otherAI/WASDGUIresetstoprestart. E0/CURB20/WAVE35/SLOPEONLYacceptedobservedfrozen/gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused; fixed004005/master/RM/clockDRrewardhardwarehealth/fullsignedcircle/fivefamilies/otherexpertgate min(18h,.13B) protected.

Allsavedsource/successfailurefalse/raw/cost/preparedunused/errors/monitor/sync/workorders captured, largePTNPZrawJSONUSDZIP actualpath-size-SHA indexonly originalsretained/credentials excluded. Uniqueannotatedrecord_experiment actualremote main/tag/peeled/alloldtags; pushfailurecontinueoriginalobjects withoutrecord-tag-commit replay. LaterstageGitreceipt/newreports ordinarysupplement. Gitnottrainingdependency. NewhumanSCUT3060physicalcomparison request isfuture independenttest, notclaimedcomplete bythis source review.
''')
    prior={}
    for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
        for row in json.loads(p.read_bytes()).get('entries',[]):
            if row.get('sha256') and row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
    sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    DEST.mkdir(parents=True);rows=[];files=[]
    for folder in (D,PRIOR):
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
            if sha in prior:
                ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
            elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
            else:
                try:txt=raw.decode('utf8');encoding='utf8'
                except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
                clean,count=redact(txt);data=clean.encode('utf8') if count else raw;out=DEST/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
            rows.append(row)
    p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_sources_reports_errors_captured=True,large_originals_retained=True,credentials_excluded=True,later_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
    rec=importlib.import_module('record_experiment');original=rec.git
    def short_git(*args):
        if args[:2]==('add','--'):
            q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
        return original(*args)
    rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Review full150 and deploy resource-verified second Wave50 direction900s','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Own426 fulltargetCPU104/actualdispatch/nine strictsame50entrydirection startupCPUCUDA receipts; complete150 fullraw direct149 with allfailedprefixes. Resource1800refusal/independent900sameguard retained. SCUTpinnedsource comparison corrects perfect-batch wording only, no activegate/GPU/budget replay. CentralCAS andnativehourly monitor verified.','--push']
    rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
    remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
    for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
    tracked=set(gitio.g('ls-files').splitlines())
    for row in rows:
        if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
    save('SECOND_DIRECTION_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_sources_reports_tracked_exact=True))
    print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))

if __name__=='__main__':
    try:main()
    except BaseException:save('SECOND_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_repeat_record_tag_commit=True));raise
