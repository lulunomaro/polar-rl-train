"""Unique real repair/deployment stage; originals and all preparation failures retained."""
from entry_second_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name/'full148_reviewed_sameentry_second412_scope'
ID='wave50-entry-full148-reviewed-sameentry-second-started'
def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 cpu=json.loads((R/'ENTRY_SECOND_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==412
 dispatch=json.loads((R/'DISPATCH_ACTUAL_RECEIPT.json').read_bytes());assert dispatch['actual_Popen_argv_cwd_start_verified']
 assert json.loads((R/'ENTRY_SECOND_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed'] and json.loads((R/'ENTRY_SECOND_DISPATCH_METADATA_SYNCED.json').read_bytes())['passed']
 actual=json.loads(max(R.glob('ENTRY_SECOND_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
 previous=gitio.refs();save('ENTRY_SECOND_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
 note=R/'ENTRY_INITIALIZATION_REPAIR_STAGE_REPORT.md'
 with note.open('x',encoding='utf8') as f:f.write('# Full148 audit and independent second sameentry1800s training started\n\nComplete148 own410ea9 twohost8JSONbyteSHA/fullraw182748249B ec64d2ab2aed1df9059e562110502ed8e9fb84c9f9b3eb8a208d0184c8fc6b1a, queryNPZ, allroot30q/parameters/recipes/assignments/6000callbacks/actualfloat32worldtriangles ground1e-6/contactintegralCOMhardware oldtolerances passed. Forward16/27 reverse24/27, ordinary0 route4 closure.851099088mm; original1N support and position completion match everyepisode. All validprefixes and legacystrictfalse kept. Direct147 forward5→16 regressions6/30 and13improvements; reverse25→24 regression67, retained alongside differentweights and no causal claim. Notqualified50/70/fullRM/MoE/permanentantiforgetting. Original feedbackreader allwarmuptrue failed at lasttick1499 env30 route reset. Original immutablearchive source readyfalse/currentwarmupsample andactualrawlastreset support strictfinal-feedback schema: readyrows exactrequested0/10ms, only actualfinalreset rows age0/sample1500/warmupfalse. Formula2e-6/100Hz and allphysics tolerances unchanged. Originalreadererror retained. Direct147 genericdecision KeyError retained, independentactual_collection/full_actual_review onlyfixed. Read-onlypathlookup errors kept.\n\nNew immutable source412=410 all410bytesexact +truthful sameentrymanifestworker anduniquecontroller. Source own410 model32264 ea9fd8558079ec690b0a483e3620c27201ed1afc36cfac56ec2a5c74f42c1f5a/17616882B/CPU102, originalaccepted35own369b026/ancestor1293c97 preserved, notdiscard/otherexpertwarmstart/qualified50. Old410 fullsave/PASSED/unique325.21946477890015s andactualparentguardianchildexit/twofcntl-free/active-Sactiveempty verified. NewtargetCPU originalfullD0D7 schema/privatecommand fixture diskroundtrip/strictwrongentrymap-origin-assignment rejection/sourcepin/import-main-Popen/storage passed/noCUDA. All410passed SDK10/native20k/small128x2/big20kx4/freshsameentry andclockDRhardware exactpath-size-SHA reused without GPU replay. Firststage copiedremote allfiles beforeCPU thenlocal duplicate-unusedreceipt save refused; originalerror saved. Independent continuation only admittedunexecutedCPU, no stagecopy/GPUrerun. RAM59.7GB/disk7.35GB > measured2xpreviouscomplete1800swhole1.515GB+2GiB required5.178GB; no deletion of evidence/cache/environments.\n\nActualunique parent3088352-start91013673 dispatch, child3088429-start91013803 onlyhistoricallocator; actual/proc argv/cwd/start/ownreceipt preferred. Actual eightownstartup sourceea9 fullsame50entry CUDAroundtrip/episode+1 PASSED. terrainexacttrue/newG3false/entryexacttrue/newentryfalse/commandpredexacttrue/newcommandfalse, no initial35→50 flag copied, nonPhysXexactresume. Globalnamed/dictprivateCPUCUDA/RNG/assignment/optimizerstd validators unchanged. Sourceworker only truthfulmanifest changed, physics/learn/save loops oldbytes. Target1800s includes loadlearnsaveexit/save25/guardian15s/20kenv24controlupdate. Only durationexposure changed; original2m trainingroute/frontflat.517m andfirst144controls1.44s≤.432m nominal support exposurehypothesis notcausal/fullroute-contact proof. No reset/commands/RNG/reward/LR/DR/geometry/hardware/clock orfivefamilies changed. ActualPPO positive savedproof when emitted, not fromprocess/CPU. At archive strictstartup passed, fullformal andcandidate notyetclaimed.\n\nOwnfullsave/CPU102/source412/module snapshots+ownfreeze/ownPID/PASSED/uniqueoriginalparent settlement/actualall exit/twofcntl-free/noactive beforeparentautomaticnewcandidatefourcase. Actualbothhost unused149 verified stage+dispatch; actualpublicationnumber governs, no blindreissue. Preparedreaders no futurepass: fullownfinal thencompletecandidate/query/raw old145/14750protocol and115/129legacyfullsignedcircle/strictfalse/validprefix/standing26/noresetteleport, direct148 fullpair andfulltrainingtrace dynamiccurrentrootcellfamily4 vsstaticassignment/beforephysicscommands vsafterupdatehist. Secondentryscope is lastduration-only block(first300+this1800); no automaticthird/70. Systematicnoimprovement independentdiagnosis/nextapprovedaxis, not unlimitedhold orblindPPO. Gateuntrained/E0-CURB20-SLOPE5-8-10-WAVE35acceptedONLYobserved frozen, no otherexpertoptimizer/output/WASD intervention.\n\nCentral complete148+source412 CPUdispatch CAS master/approval/tracks/RM004 protected and no canonicalwrites; actualactive budget may account concurrently. Existingmod4-10 ACTIVEhourly same target nativeverified, quietpending andmeaningfulnotification only. 005canonical1188000s330h/sevenextensions seventh100h alreadyonce/no newtime. Originalparentunique PPOloadlearnsaveexit/failedstartup; CPU/SDK/native/frozen/fresh0PPO nocharge; actualactive/accountedtail priority. No extension/copy/clearactive/tail/recharge/oldonce replay. Actualfcntlheld notexists, no deletelocks/kill/hotpatch/dual20k/otherAI. Fullfixed004005/master/RM/clockDRrewardhardware/fivefamilies/healthv3groundcontactCOM/fullsignedcircle remain. Allsavedreports/errors/unusedpreparedsource/monitor/sync/workorders captured orSHA-existingGit references, largePTNPZrawJSONUSDZIP onlyactualpath-size-SHA originalsretained, credentials excluded. Uniqueannotatedtrial actualremote main/tag/peeled; pushfail continueexistingobjects no record/commit/tag replay. Poststage receipts/reports ordinarysupplement, Git nottrainingdependency.\n'+'\nActual phase: '+str(actual['reports'].get('E1_STATE.json',{}).get('phase'))+'\nAttention: '+json.dumps(actual['reports'].get('E1_ATTENTION.json'))+'\n')
 prior={}
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('sha256') and row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted([p for folder in (D,ENTRY_LOCAL) for p in folder.rglob('*')]):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(txt);data=clean.encode('utf8') if count else raw
   folder=D if p.is_relative_to(D) else ENTRY_LOCAL;out=DEST/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_entry_repair_sources_reports_failures_captured=True,large_originals_retained=True,credentials_excluded=True,later_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Audit complete148 and start reviewed second sameentry1800s window','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Complete148/fullraw/direct147/strictfinalresetfeedback passed, originalreader errors andfalse retained. Source412targetCPU/fullsameentrystartupCUDA passed, unique1800s controller actualdispatched, alloriginalpreflights exactSHAreused. CentralCASprotected/hourlymonitor verified, formal/candidate stillawaitownactual.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('ENTRY_SECOND_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_entry_repair_sources_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_SECOND_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_repeat_record_tag_commit=True));raise
