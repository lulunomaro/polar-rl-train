"""Unique new50mm scope stage, all saved success/error/source evidence retained."""
from wave50_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name;DEST=BASE/'independent384_missing_scope_started';ID='wave50-isolated384-sdk-passed-fullscope-controller-started'
assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
assert json.loads((R/'WAVE50_TARGET_CPU_PASSED.json').read_bytes())['passed'] and json.loads((R/'MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
actual=json.loads(max(R.glob('WAVE50_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert 'WAVE50_SDK10_PASSED.json' in actual['reports'] and not actual['reports'].get('E1_ATTENTION.json')
previous=gitio.refs();save('STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
note=R/'STAGE_REPORT.md';assert not note.exists()
note.write_text('''# Deploy independent50mm fullscope384 after complete145 proves incomplete passage

Full145 frozen50mm forward11/27 reverse23/27 remains nonqualified, original144 precontrol failed/resultabsent/errorfiles/exit0/cost and alloldfailures retained. Ground queryoriginal1e-6 and fullroute/contact/COMhardware tolerances unchanged. Observed35mm source369b02627/27 bothdirections remains frozen. E0/CURB/SLOPE/gate/WASDplayer not altered.

New isolated MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012 source384 preserves allimmutable377 CPU root bytes, including369alloriginalbytes plus8G4components, and adds7 genuinelynew missingphysical/fullstate scope SDKplacement/native/twoPPOworkers/fresh/controller/005sourceguard files. Sourceown369model32259 b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd/17615538B/CPU102 with1293c97ancestor. ActualtargetCPU authenticated allD0D7/schema/storage/wrongassignment andwrongsource strictrejection/privatecommandCPUfixture/diskrestore/noCUDA, allmodule snapshotfilepaths andimport/main/Popenworker roots matched. Rootguard sourcefreeze copiedfull viaE1source snapshot, separatefrommodule src_snapshot. Original broadfilename list andexternalasset ASTreader rejection retained; independentremainingCPUproof corrected reader only, noGPUreplay or validator relaxation.

Newcontroller actuallydispatched owner2983989-start89534237, ownSDKchild2984036-start89534352, actualargv/cwd/creation receipts preserved. Trulynew SDK10 actual10G4cells/twoflatfrontsupport sides/allcolliderbank footprint rootbeforephysics exact andselectedreset300control1200callbacks PASSED. Native20k24warm120timed480/576callbacks is the currentactive newphysicalscope, not alreadyPPO/formalgraduation. Controller automatically continues onlyownPASSED through128x2/20kx4 fullPPO discardedweights, independentfreshsame50 new20k0control0PPO explicitseed20260928/strictfullCPUCUDA restore andepisode+1, thenfirst300s loadlearnsaveexit/save25/local15s guardian fromb026, notdiscard. Fullold35 actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA geometrycommandidentity exact before explicit35to50 actualassignment migration; subsequent same50 exact, noPhysXexactresume. Existingclock/DR/hardware priorPASSEDpathsizeSHA reused; nooldSDK/native/PPO/preflight/clock/once replay. Reward/LR/clock/DR/commandmath/reset/fivefamilies unchanged except50mm geometry axis.

Actualbothhostqueue/results/jobs candidateunusednumber examined atstageanddispatch, no blindnumberclaim or old144/145 replay. Onlyownfullsave/PID/CPU/sourcefreeze/PASSED/uniqueparentsettlement/actualexit/twolocks/noactive afterformal triggersownfourcases based145 exact50mm protocol and115/129oldskill diagnostic; incompleteprefixes/strictfalse/finalbias schema preserved. Fullraw+actualperenvfulltrainingtrace must be reviewed beforefurtherPPO or70mm; max2boundedblocks<=2h beforefullaudit/noautomaticthird. Thisstage doesnotclaimfuturePPO/fullresume/formal/candidatepass.

005authority1188000/sevenextensions validatesregistration sum+base10h andownsource/ancestor. Native/SDK0PPO nocharge; futurePPOloadlearnsaveexit originalparent uniquecanonicalaccounting, noextension/copy/clearactive/tailreplay. Oldsource369 parentguardianchildactualgone/twofcntl locksfree/noactive/uniquesettled beforelaunch. Metadataactualnewroot/source384 state CAS synced, masterapproval unchanged, no metadata budgetwrite. Samehourlymod4-10 ACTIVE target/prompt actualverified, quiethealth intent. Allsaved source/CPUerrors/rawindices/nativeSDKreceipts/dispatch/sync/monitor captured orsameSHAreference, largeoriginals actualpathsizeSHAonly/credentials excluded. Futureownfinal/fulltrace/newcandidate reports require ordinarysupplement; Git isnottrainingdependency.
''',encoding='utf8')
prior={}
for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
 for row in json.loads(p.read_bytes()).get('entries',[]):
  if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
DEST.mkdir(parents=True);rows=[];files=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts:continue
 raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
 if sha in prior:
  ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
 elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
 else:
  try:txt=raw.decode('utf8');encoding='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
  clean,count=redact(txt);data=clean.encode('utf8') if count else raw
  out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
  row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
 rows.append(row)
p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_evidence_captured=True,large_originals_retained=True,credentials_excluded=True,later_saved_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
rec=importlib.import_module('record_experiment');original=rec.git
def short_git(*args):
 if args[:2]==('add','--'):
  q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
 return original(*args)
rec.git=short_git
sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Deploy independent50mm source384 with actual10-cell SDK and guarded automatic bounded learning','--kind','deployment','--note-file',str(note),'--files',*files,'--validation','Actual4090 source384 CPU/noCUDA/allD0D7/sourceb026/strictmigrationfixture/snapshotfilenames/importargv passed. NewSDK10 actual10G4cells/twofrontsupport sides/allfootprint/selectedreset/1200callbacks passed. Newnative20k active; fullPPO/fresh/formal are guarded futurestages, no falseclaim. Complete14550mm11/23 notqualified/35mm27/27 frozen. Uniqueactualdispatch/PIDargv/cwd, canonicalregistration005/noextension, centralCAS/hourlymonitor verified. Alloriginalfailures/source/errors/rawindices preserved.','--push']
try:rec.main()
except BaseException:save('STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_only=True));raise
tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
tracked=set(gitio.g('ls-files').splitlines())
for row in rows:
 if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_reports_tracked_exact=True))
print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
