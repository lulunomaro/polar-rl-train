"""Record this genuine386 stage once; include complete146 and every saved error."""
from second50_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name;DEST=BASE/'complete146_second386_started'
ID='wave50-full146-reviewed-second1800s-started'

def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'SECOND_TARGET_CPU_PASSED.json').read_bytes())['passed'] and json.loads((R/'MONITOR_PPO_ACTUAL_VERIFIED.json').read_bytes())['passed']
 positive=json.loads(max(R.glob('SECOND50_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert positive['passed'] and positive['actual_saved_PPO_updates_positive'] and positive['actual_source_count']==386
 decision=json.loads((PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['full_four_cases_complete_errorfree_and_raw_reviewed'] and decision['not_qualified50mm_scope']
 previous=gitio.refs();save('SECOND_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
 note=R/'SECOND_STAGE_REPORT.md'
 with note.open('x',encoding='utf8') as f:f.write('''# Complete146 remains nonqualified50mm; one independent same50 second1800s training block actually started

Own384 initial300s formal saved219faeadcceaa3e015b6a50ccdbf7614cd0f7e0b1cafe2cea04fad0d59b0c550/17615730B/CPU102, actual6updates144controls2.88Menvsteps576callbacks, unique335.2139837741852s originalparent once settled and exited. 146 allfour actualcomplete/errorfree and independent fullraw/oldskill audit now complete. Same50 peak-valley tenwaves2.406422727m/.4m approach/bothwheels200mm after/80env1500controls15s/20260928white3: forward7/27 reverse25/27, ordinary0/route7/closure1.325404970mm. Full183035056B raw SHA6669ff5659662b387f7c38fe8a6c4bd8c9b06c98dc58f5d45210fee0f5be1f45, twohost8JSON byteSHA andqueryNPZ actualworldfloat32 independentexpected1e-6 exact. Allroot30q parameters/recipes/assignment/6000callbacks/groundcontactintegralCOMlinkhardware originaltolerances passed. Independently everyposition-completeepisode equals bothwheel original1N pre/postsupport. All validincompleteprefixes, xyzwheading/sameepisode prereset-before excludesresetteleport, standing26 no crossing; source145 frozen50 forward11 reverse23 kept. No shortenedapproach/extendedwindow/relabeling. Oldskills exact115/129 pair: negative4pi0/8 positive4pi4/8, world63/64/maxcross.052828551, straight±1.5 errors.066670597/.048466872; strictfalse and physicalsmokefalse preserved. E0 remainsfrozen/gateuntrained; source219f notqualified50 or otherexperts' defaultwarmstart.

Initial50 fulltrainingtrace144controls=1.44s/env/.3 nominalmaxintegral.432m is short versus tenwavesplusapproach/aftersupport. Inadequate route exposure is a testable inference, not causalablation or wheelcontactcertificate. 005 authorizes one genuinely new same50 secondbounded1800s window, nowactuallyrunning. Root MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012 source386 preserves all384 bytes exact and adds only unique same-scope controller plus worker whose three manifest disclosures truthfully mark same50 rather than initial35to50 transition. Physics/learningloop/geometry/DR/reset/commands/reward/LR/hardware unchanged. Own384 source219f CPU102 with original35 b026 and ancestor1293c97 strict identity. Allactual new50 SDK10/native20k/small128x2/big20kx4/freshsame50/clock/DR passed originalpath-size-SHA reused; no GPU preflight/clock replay.

ActualnewtargetCPU/noCUDA/source386/originalallD0D7/named/privatecommand/storage/strictwrongsourceassignment fixture anddiskroundtrip passed. Originalstage wrote newrootfreeze and localreceipt duplication rejected before CPU/GPU action; independent remainingCPU finisher Path+str TypeError likewise preCPU. Both originalsource/errors retained, onlyunexecutedCPU completed independently with compiled dynamiccontroller worker/guardian code identity. Unique dispatch parent3010516-start89921988, child3010588-start89922117, argv/cwd/source/20k24controls/seed20260928 verified; no oldonce/main/resume replay. Sevenownstartup receipts actually strictsame50 terrainexacttrue/newG3false, commandpredecessorexacttrue/newscopefalse, fullCPUCUDA diskroundtrip/savedsourceepisode+1 passed. Own savedmodel32275 SHAa1fa6e1b1a02d86e4c0609de6d07f6d8cc16e4064daf4b6b859ce561048c094e CPU102 with9actor tensors changed andoptimizerdelta240/288actualsavedtracecontrols proves positivePPOupdates; this is activecheckpoint, not formalfinal/graduation. Allsevenstartup rawbytesSHA collected. 1800s includesloadlearnsaveexit/save25/local15sownsaveguardian, canonicaloriginalparentuniqueaccounting; source andE0/CURB/SLOPE/WAVE35 not optimizer/outputtargets.

Original146 legacyspin reset reader assumed absentcountzero and failed; independentreaderusespreviousstrictactual reset schema/firstfailure evidence andunchangedphysics auditors. Original reader/source/traceback andcorrectedschema review retained, no GPUreplay. Additional missinglocalfilename lookups, stagewbx/Path errors andallolderfalse/raw/cost retained, not physicalfailures or rewrittenpasses.

Complete146+new386 actualCPU/dispatch/startup andpositiveCPU proof CAS synced centrally; masterapprovaltracksRM004 andcanonicalbytes preserved during each metadataaction, no metadata budgetwrite. Sameexisting mod4-10 ACTIVE hourly target/nativeautomationprompt andtoml actuallyverified; quiethealth intent/noextramonitor. Oldfullprompt savedrawSHA, oldstage/partialpending text onlyhistory. Futureownfinal/fullsave/CPU/snapshots/PID/PASSED/uniquesettlement/actualexit/twofcntl/noactive mustbe independentlyread beforeparentpublishednewfourcase. Candidate147 bothhostqueue/results/jobs unused actuallychecked; no blindclaim/republication. Prepared future readonlyfinal/collector/fullraw/reset-correctedreview/dynamicfamilytrace readers are not futurepass. Fullcandidate mustsame145 query/contact/COMhardware and115/129skill protocols, direct146 pairing andwholeowntrainingtrace before decision. Max2same50 blocks(initial300+this1800), noautomaticthird or70mm; systematicresidual aftersecond demands independentjustified axisdiagnosis rather than blindPPO or indefinitehold.

005solecanonical1188000s330h/sevenextensions seventh100h alreadyonce, actualactive/accounted/tail wins snapshots, noextension/copy/clearactive/retail/recharge. OriginalclockDRrewardLRhardware/fivefamily proportions/commands/healthv3/ground1e-6/contact1N/fullsignedcircle thresholds stay. E0/CURB20/SLOPE5-8-10/WAVE35 ONLYacceptedobservedscopes frozen; gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused/WASDplayer untouched. Otherexpert/gate/min(18h,.13B) planningprotected withoutledgerreserve. Capture allsavednew386 andcomplete146 source/errors/results/metadata/monitor/workorders orreferenceexistingexactSHA; largePTNPZrawJSONUSDZIP onlyactualpathsizeSHA originalsretained, credentialsexcluded. Thisuniqueannotatedtrial coversactualnewtrainingstage; laterreports/Gitreceipt ordinarysupplement. Gitnottrainingdependency, pushfailurecontinueonlyoriginalobjects/no recordtagcommit replay.
''')
 prior={}
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
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
    clean,count=redact(txt);data=clean.encode('utf8') if count else raw
    out=DEST/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
    row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
   rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_complete146_and_second386_evidence_captured=True,large_originals_retained=True,credentials_excluded=True,later_saved_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete146 nonqualified50mm and start isolated same50 second1800s training','--kind','training','--note-file',str(note),'--files',*files,'--validation','Actualcomplete146 twohost fullraw originalphysics/contact/query/oldskill schema audited, forward7 reverse25 nonqualified andallfalse retained. New386 CPUstrict passed, actualunique20kPPO dispatch andsevenCUDArestore receipts, own9actor/optimizerdelta240 savedpositive proof. OriginalpreflightSHAreuse, metadataCAS protected andsamehourlymonitor actualverified. No thirdblock/70/futurefinalclaim. Allsaved source/errors/evidence indexed, largeoriginals retained.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('SECOND_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_complete146_second386_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_original_objects_only_no_repeat_record_tag_commit=True));raise
