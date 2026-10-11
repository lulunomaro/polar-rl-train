"""New genuine CPU diagnosis stage; do not replay previous386 trial."""
from second50_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name/'complete147_independent_entry_CPU_diagnosed'
ID='wave50-full147-failure-preserved-entry-cpu-diagnosed'
def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 decision=json.loads((R/'WAVE50_147_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes());assert decision['decision_complete'] and not decision['qualified_observed50mm']
 component=json.loads(max(R.glob('WAVE50_ENTRY_V1_SAVED20K_CPU_COMPONENT_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert component['passed'] and component['stage']=='CPU_component_only_not_target_GPU_or_learning_admission'
 assert json.loads((R/'FINAL_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed'] and json.loads((R/'FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED.json').read_bytes())['passed']
 previous=gitio.refs();save('ENTRY_CPU_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
 note=R/'ENTRY_CPU_DIAGNOSTIC_STAGE_REPORT.md'
 with note.open('x',encoding='utf8') as f:f.write('''# Complete147 valid50mm failure preserved; stop blind duration-only training and test independent reset-entry CPU component

The second50mm1800s training naturally fullysaved andexited: source386 ownmodel32357 a67b955f680dd101cc4480f19c2e95dd86c34423148302fad1d8e925e206d4df/17615730B/CPU102/81module snapshots+386fullfreeze/PID3010588.94updates2256controls45.12Menvironmentsteps9024callbacks,9actor tensors changed/optimizerdelta1880. Sevenstrictsame50 actorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA roundtrip/sourceepisode+1 passed. Unique1825.9359953403473s loadlearnsaveexit originalparent once settled; parentguardianchildgone/twofcntl-free/active-Sactiveempty. Ordinary1control1412env18887base_contact/closure1.221559010mm/mimic.001691456rad retained, integrityunknown0/nonfinitefalse/STOPnone. timeout15963+route17091 with8overlap/unique33046/two reasoncoverageexact, counts notsummed. Legalreviewready, notwholecoursefinished. AllfiveNPZ2256controls22.56s/env/maxphysicalepisode20s actualSHA/fulltrace independentlyaudited, dynamiccurrentrootcell family4/commands-beforephysics vsafterupdatehist/prereset-beforeteleportexclusion preserved. Rootcommandproxy isnotcontact/fullroute orcausalproof.

147allfour cases actualcomplete/errorfree andindependentfullraw audit/direct146 matched. 50mmpeak-valley tenwaves2.406422727m/9mmirror/.4approach/fulltwowheels200mmafter/80env1500control15s20260928white3: forward5/27 versus1467/27, reverse25/27unchanged. Ordinary0/truncation0/closure.654120871mm. Fullraw182624801B SHA778f301d9e1e9785efaee9583cef84ada35c712a56b47736169b6ec40985c3b8, twohost8JSONbyteSHA/queryNPZ/actualworldfloat32triangle independentground1e-6/allinitialroot30qparamsrecipesassignments/6000callbacks/groundcontactintegralCOMlinkhardware oldtolerances verified. Alloriginal1N support matchespositioncompleteepisodes. Sixforwardcomplete-to-incomplete21/33/42/51/60/63 andfourimprovements6/18/30/78 preserved; all22forward andreverse19/64 incompleteprefixes/xyzwheading/prereset-before retained. Standing26 neednotcross, nowindowextension/approachshortening/teleportprogress/relabeling. Legacynegative4pi0/8 positive3/8/world64/64/maxcross.043386544/straight±1.5 errors.062802039/.042432778 andalloriginalstrictfalse/spinphysicalsmokefalse remain. Validphysicalcontract isnot50mmgraduation. Two duration-only blocksinitial300+1800completed; thissame50duration-onlyPPOended, nothirdblindblock/no70/RM/MoE/permanentantiforgettingclaim. E0 frozen/gateuntrained, noexpert overwritten.

IndependentCPUreadactualownsaved20korigins/firsttrace/exactbank/50profile found620Wave initialrootcenters inside theten-wave span,940fullaxisalignedfootprints before/940after; bothleftandright signedinward/outward andstanding commands present. Thisis actualcoveragefact, not failurecausality. Newwave50_entry_v1_math.py reset-position-only component has actuallyexecuted on saved20korigins, exactoriginalnative20kresetroots/full1600generatedassignmentSHA and25200fullcollisionpoints. All2820Waveorigins changed,17180otherenvironments byteexact. Positions halfspan+.8/.85rank onbothX sides, Yboundedcompletefootprint+.004, minimumflatfrontsupport.517000000335m, separatedlanes/nooverlap/no duplicateXY; mapSHAf42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d. Wrongfootprint/duplicateassignment/wrongspan rejected, sameinputcacheexact andactualoriginmutationcache invalidation passed. No RNGdraws/newstreams/command/geometry/reward/LR/DR/hardware/health changes, noGPU/restore/PPO/budgetwrite. CPUcomponentonly, nottargetfullstate/CUDA/SDK/native/learningexecutoradmission. Original2mtrainingroutefromspawn stillholds; fulltestdistance3.006m cannotfitit, soentry/onset exposure isnotwholetenwavetrainingcertificate. Nocausalclaim/commandaxisrepair slippedin.

Newexplicitworkorder advancesisolatedentryfullstate/sourcefreeze/CPU andgenuinelymissingSDK/native, preservingactualcacheoriginchanges/selectedreset/full30q/rootnormals/zero velocity/clearance. Futureinitiallearningwarmstart acceptsobserved35mm own369b026/CPU102/ancestor1293c97, fulloldidentitystrict thenexplicit35to50actualassignment+entrymapidentity/newdictownedstate/CUDA diskroundtrip/episode+1. Noautomaticdegraded219f/a67b/discard warmstart. Strictoldnamed/privateassignment schemas stay. Subsequentsame50+entry exact, notPhysXexactresume. Onlygenuinelymissingnew-entry SDK10/native20k andnewfullstatePPOpreflights/fresh scopeonce, unchangedclock/geometry/DRhardware exactSHAreuse/no45minclock. First300s formal onlyafterownscopeallpassed/15sguardian/uniqueoriginalcanonicalaccounting thennewfourcasesfullraw+trace. Newjobnumberactualtwohostunusedcheck, noblind148claim. Commandaxisremainsold±.3/yaw0/standing.2/RNGconsumption/route2m, no truthteacher/liveheadingcorrection/actor-gateinputs/rewardchange. Completecandidateauditbeforecontinuation; atmosttwojustifiedscopeblocks≤2h thenfullaudit/systematicfailurediagnosis.

Ownfinal/complete147/directpair/trace/newCPUdiagnosis/component/workorder centrallyCASsynced; masterapprovaltracksRM004 andcanonicalbyteprotected. Sameexistingmod4-10ACTIVEhourly targetnativeupdatedandactualtomlverified, quiethealthy/meaningfulnotification only. OldfullpromptpreservedSHA. Localguessedsourcepaths/invalidWindowswildcard/sourceabsence/Gitarchivefilename lookup andapply_patch multiope ration prewrite rejection preservedasreader/preparationerrors; no GPUfault/replay. Rejectedpatch didnotmodifytargetfile, originalpreparedsync preserved andsingleUpdate onlyunexecutedmetadata prepcompleted. Allsavedsource/results/partialreports/errors/sync/monitor/workorders capturedor exactexistingGitSHAreferenced, largePTNPZUSDZIPrawJSON onlyactualpathsizeSHA/originalskept, credentials excluded. Thisuniqueannotateddiagnostictrial is anewrealCPUrepairattempt, not replay old386trainingtrial. Later stageGitreceipt ordinarysupplement, failedpushoriginalobjectsonly/no recordtagcommitreplay.

005canonical1188000s330h/sevenextensions seventh100h alreadyonce, noextension/copy/clear/tail/recharge. Actualactiveaccountedtail overridesidle668407.7181019783snapshot. CPU/SDK/native/frozen/fresh0PPOnocharge; PPOloadlearnsaveexit originalparentunique. Locksactualfcntlnotfileexistence/nokillhotpatchdual20k/otherAI/WASD. E0/CURB20/SLOPE5-8-10/WAVE35 ONLYacceptedobserved scopesfrozen; gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused. OriginalfixedclockDRrewardLRhardware/fivefamilies/commands/healthv3/ground1e-6/contact1N/COM/fullsignedcirclethresholds/otherexpertgateplanning remain.
'''.replace('multiope ration','multioperation'))
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
    clean,count=redact(txt);data=clean.encode('utf8') if count else raw
    out=DEST/folder.name/p.relative_to(folder);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
    row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
   rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_complete147_and_new_entry_CPU_evidence_captured=True,large_originals_retained=True,credentials_excluded=True,later_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Preserve complete147 Wave50 failure and verify independent reset-entry CPU repair','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Own386 completefinal/uniqueaccounting/exit/free verified; all147fourcase fullraw physics/query/contact/legacy anddirect146exact audited,5forward25reverse notqualified. NewentryCPU actual20k map2820changed17180exact/collisioncontainment/cacheoriginmutation/strictrejections passed,noGPU orlearning claim. Allsavedfailures andfalse retained,metadataCASprotected/hourlymonitoractualverified.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('ENTRY_CPU_DIAGNOSTIC_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_complete147_entry_CPU_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_CPU_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_repeat_record_tag_commit=True));raise
