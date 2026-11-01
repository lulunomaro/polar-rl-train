"""Archive authorized reference tracking launch, prior failed attempts and292postround."""
from pathlib import Path
import ast,base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
ID='mod4-reference-tracking-bptt-save-repair300';TAG='trial-20261101-'+ID;V=G/('versions/20261101_'+ID)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()}
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not git('status','--porcelain')and not V.exists()and not git('tag','--list',TAG)
assert not(R/'RECORD300_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in old.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request=json.loads((R/'AUTOMATION300_REFERENCE_TRACKING_UPDATE_REQUEST.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['prompt']==request['prompt']and actual['status']=='ACTIVE'and actual['rrule']==request['rrule']and actual['target_thread_id']==request['targetThreadId']
put(R/'AUTOMATION300_REFERENCE_TRACKING_APP_RECEIPT.json',dict(epoch=time.time(),automationId='mod4-10',mode='update',status='ACTIVE',tool_return='Updated automation in the app.',request_SHA=H(R/'AUTOMATION300_REFERENCE_TRACKING_UPDATE_REQUEST.json'),hourly=True,prompt_target_schedule_exact=True))
snap=json.loads((R/'ROOT300_STATUS_AFTER_HANDOFF.json').read_bytes());selected={Path(x['path']).name:json.loads(x['UTF8'])for x in snap['full_selected_UTF8']}
assert not any(k in selected for k in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
first=selected['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT300_UPDATE.json'];progress=selected['LATEST_PROGRESS.json']
assert first['passed']and first['actual_new_Pi_updates']==first['actual_new_critic_updates']==1
assert progress['actual_new_Pi_updates']==progress['actual_new_critic_updates']==668
put(R/'LAUNCH300_VERIFIED_ACTUAL_PROGRESS_AND_LIMITS.json',dict(epoch=time.time(),passed=True,source_snapshot=str(R/'ROOT300_STATUS_AFTER_HANDOFF.json'),progress=progress,first_full=first['first_complete'],latest_complete=selected['latest_complete.json'],errors=0,training_started=True,planned_reference_tracker=True,not_autonomous_depth_student=True,skill_evaluation_pending=True,observed_flight_environment_controls=0,latest_actual_tracking_cost_mean=progress['tracking_cost_mean_last32'],interpretation='Real updates/full saves prove loop runs, not skill improvement;83orientation resets/no flight at731controls retained. Final fresh evaluation/replay decides continuation. Healthy frozen job retains original save boundary; no hotpatch/restart.'))
# Check exact future303 parent and all frozen postround bytes without model/SDK.
index=json.loads((N/'INDEX303_POSTROUND_FOR300_FROZEN.json').read_bytes())
for row in index['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
runner=ast.parse((N/'postround303/run303_eval_once_template.py').read_text('utf8'));main=next(n for n in runner.body if isinstance(n,ast.FunctionDef)and n.name=='main');env={'T':T}
for stmt in main.body:
 if isinstance(stmt,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='parent'for x in stmt.targets):exec(compile(ast.Module(body=[stmt],type_ignores=[]),'<parent303>','exec'),env)
parent=env['parent'];ast.parse(parent);assert 'from contract303 import' in parent and "str(P/'source/evaluate303.py')"in parent and 'RESULT303.json'in parent
put(R/'POSTROUND303_FROZEN_SOURCE_BINDING_VALIDATED.json',dict(epoch=time.time(),passed=True,index_SHA=H(N/'INDEX303_POSTROUND_FOR300_FROZEN.json'),allfiles=True,generatedparent303=True,localtimer_pid=53348,normal300_and_CPU300_UNCONSUMED=True,eval303_UNCONSUMED=True,model_reads=0))
put(R/'RECORD300_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,tag=TAG,old_refs=old,lqr=lqr,push_failure_resume_existing_objects=True))
note=R/'EXPERIMENT300_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The human explicitly authorized "新跟踪启动" after rejecting old Fudan velocity/flight reward plus decaying teacher auxiliary and requesting SuperMimic BPTT task tracking. This phase implements and actually starts a declared planned-reference tracker. It is not an autonomous depth-only stair student and no270mm skill is inferred.

Old292 completed its original full save/safe exit: Pi211/critic211/newWM2491,total9578,32408111B SHAfb01f5d5cc3bf9e6d2b0bce3e26a777aea93ceb587b1e7de3180f750dd68f38c; fullCPU600finite tensors/three optimizers/teacher preserved; originalfee3603.630714893341seconds.293 failed missingwheel_geometry220 after scene but before model read. Independent299 retained that failure, added dependency, evaluated exactfinal once:0/72strict/crossed,6/8ground completed8s,57orientation/1basecontact/2lowbase,0closure/mimic. Actual recorded pose viewer opened and screenshot was natively reviewed in the preceding context; old mixed objective retired. No replay of consumed293/299.

295 local source producer assumed support0or2; actual reference includes1, so failed before model/SDK/GO.296 corrected aggregate supported-wheel count without inventing contact identity. Necessary actual sourceCPU model read/migration/H32 no-step passed: actor103,critic106,goal59; original outputs/STD preserved with zero new input columns; originalactorAdam42940,NEW trackingcriticAdam0; WM7087/optimizer/RNG retained.296 source review found1-cost termination shortcut and endpoint phaseoffset; independent297 usesexp(-cost/5), positive return, same actor/critic reward and correctendpointphase.297local chainedcomparison/source failure and repair retained. Source-only positivegradient/phase test passed.297 first caller wrongindexSHA refused before network; preserved. Actual297run loaded source, completednative24 and firstWM update, then periodic save before firstPi usedmin(empty newcriticAdam), failed before anyactor/criticstep. Partial/error saves and full stdout retained, originalowner/node/children waited, private/sharedlocksfree, CNone; originalfee32.7745041847229seconds. No fee refund or rerun.

Independent300 preserves297 bytes/once/INDEX. Save helper explicitly supports fresh emptycriticAdam0 and validates8slots/stepcount afterupdates. Periodic latest saves begin only afterfirstPi; emergency complete save beforePi remains supported. Source-only zero/one/invalidmetadata tests passed without model reread. It inherits296actual migration/H32 evidence and297positive reward/phase test, then requires actual ownH32 gradients beforestep. Literal hashes/seed/networkport were not blindly version-substituted.

New task:80fixed270mm platforms, edge.8m, fullDR, reference fullDR_mpc500states100Hz resampled250states50Hz, continuous episodephase0..249 plus finalhold. Labels are MuJoCo planned state trajectories, not callable arbitraryPhysX normalized-action teacher; no torquecloning/foreignWM transitions.103actor=35proprio+9currentdepth+59referencegoals(current+10control lookahead andphase);106critic predicts matchingexp(-weightedtrackingcost/5). Trackbaseposition/orientation/velocities/legq,dq/virtualleglengthangle/aggregatewheel support with smallactionrate/overflowregularization. Actual/imagined phase aligned. Ownobserved episodeanchor reused when edge leavescamera, neverfuturedepth orGT fallback. The resulting policy needs plannedreference and currentpose; autonomy goalgeneration is separate.

Original2135actor/fullAdam42940 andSTD restored,59goal columns/moments appendedzero; new106trackingcritic with zerooutput/freshAdam0,oldcritic remains in carrier. OwnWM7087/optimizer/norm/dedicatedRNG from complete286SHA4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d retained. Fresh physicalepisode/DR/queue/replay scope, not exactPhysXresume. Actor/criticLR1e-4,perupdate real sampledstart actiondelta<=.05.400Nengineeringk2000,50policy100feedback400physics2.5msTGS32/4,fullD0whitev3D1-D7,closure10mm perenv,mimic.01rad unchanged. Originalsolecanonical3900/save3600/exit300, no grant/clear/copy/refund/secondwriter.

Actual300runREFERENCE_TRACKING300_1793542482471737300, original72owner1411085/create1793542524.8,node1411094/create1793542525.26. Fresh exactCIM/CNone/privateEX/resourceadmission then oneGO2026-11-01T22:15:28.756283+08, SAVE23:15:28.756283,NOMINAL23:20:28.756283. Native24passed. Actual ownH32 tracking andcombinedgrad6.79213 finite/nonzero; terminalgrad0 because newcriticoutputzero, explicitly not misrepresented. FIRST64controls/5120ownpairs/512physics/128feedback,Pi1/critic1/newWM33total7120;complete32593725B SHA4c30982ac5a47a8955af3c9aa753d2cbeeb8cf4aa3089c8c5bf22db2be04a38a,teacher/STD/threeoptimizers/norm/RNG/DR/phase state preserved. Subsequent731controls/Pi668/critic668/newWM700total7787,83orientationresets,0closure/mimic; finiteWM. Actualtrackingcostmean24.9433 and0flight controls retained as limitations, not improvement claims. FIRST/latest are notFINAL or skillsuccess. AllSSHclosed/SESSIONrestored/serialFREE.

Unused301postroundsource had label-vx/cue/parent-version issues; unused302 fixed parent303equivalentgeneration, removedgroundcue, matchedtrackingcost and actionclip, but usedrawaction for measuredregularization unlike300's frameactionABI. Bothunusedsource preserved; independent303 matchesactual300frameinverseorder, retains rawoverflowdiagnostic, correctreferencevelocitymetric and newseed9137freshDRfirstepisodes400controls. Fixedcourse geometry is same, not heldoutnewterrain. Strict270candidate still requires physicalfirstflightcross,wholewheel top footprint,stable.5s and contactmanifold confirmation before graduation.

Dedicatedlocal postround303 PID53348/Start2026-11-01T22:25:50.032056+08 waits withoutSSH untiloriginalnormal900 then invokes uniqueoriginal300close/formaltransfer/fullCPU and303independenteval/actualposereplay. It has no newGO/accountwrite; heartbeat nativelyreviews replay+result and executes within-scopecontinuation/targetedrepair, never merely saysended. Caller/index validation passed. mod4-10ACTIVE/hourly/currentchat updated to300workorder; oldstale292continuation removed, fullrequest/actualappreceipt preserved. Priorunusednormal297/CPU297/postround297 are notexecuted. Consumedonce never replayed, no livehotpatch or healthrestart.

All saved source/failures/fullstdout/reports/automation/verification through capture enterGit. Earlier exploratorywrongcwd/missingINDEXreads and broadfilequery noise are tool-output issues only, no experimentrerun. TextSHA dedupe references priorGit; binaryPT/NPZ/USD/media remain externaltruepath/bytes/associatedproducerSHAmetadata, no hash/modelread forarchive. Newunique300phase usesrecord_experiment once; lateractualfinal/eval/replay/results use ordinarysupplements withoutretag. Alloldtagobjects/peels andlqr5848protected; postGitverification stays tooloutput rather thanendlessreports.
''')
names=['DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101','RETENTION292_POSTROUND_REPLAY_EVAL_V293_20261101','REFERENCE_TRACKING_BPTT_V295_20261101','REFERENCE_TRACKING_BPTT_V296_20261101','REFERENCE_TRACKING_BPTT_V297_20261101','RETENTION292_DEPENDENCY_REPLAY_EVAL_V299_20261101',N.name]
roots=[(name,T/name)for name in names]+[('stage_builder',T/'prepare300_tracking_save_repair.py')]
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for name in('20261101_mod4-lqr-mpc-teacher-assisted-depth-student286','20261101_mod4-student286-replay-retention-repair292','20261101_mod4-supermimic-bptt-task-tracking-objective294'):
 for p in (G/'versions'/name).rglob('CAPTURE_INDEX*.json'):
  for row in json.loads(p.read_bytes()).get('files',[]):
   sha=row.get('SHA');gp=row.get('Git_path')
   if sha and gp and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference')and(G/gp).is_file():known.setdefault(sha,gp)
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usdc','.stl','.obj','.zip','.pyc'}
texttypes={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir();rows=[];selected=[]
for label,root in roots:
 assert root.exists(),str(root)
 for p in([root]if root.is_file()else sorted(root.rglob('*'))):
  if not p.is_file()or'__pycache__'in p.parts:continue
  if p.suffix.lower()in binary:
   rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA='See associated producer/transfer receipt, otherwise unknown; no binary read forGit',capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texttypes,str(p)
  b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  dest=V/label/(p.name if root.is_file()else p.relative_to(root));dest.parent.mkdir(parents=True,exist_ok=True)
  try:text=b.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(b.decode('latin1'));value=safe.encode('latin1');dest=dest.with_name(dest.name+'.bytes.b64.txt');dest.write_text(base64.b64encode(value).decode()+'\n',encoding='ascii');gp=dest.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,redactions=count,capture='base64_nonUTF8',archive_decoded_SHA=hashlib.sha256(value).hexdigest()));continue
  safe,count=redact(text);value=b if not count else safe.encode('utf8');dest.write_bytes(value);gp=dest.relative_to(G).as_posix();selected.append(gp)
  rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
  if not count:known[sha]=gp
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,alloldrefs=old,lqr=lqr,running300=True,final_eval303_pending=True,binary_metadata_only=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original=recorder.git
def batch(*args):
 if args[:2]==('add','--'):
  for i in range(2,len(args),24):original('add','--',*args[i:i+24])
  return''
 return original(*args)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Launch reference tracking BPTT300 after preserving297 zero-step save failure and292 evaluation','--kind','training','--note-file',str(G/note_gp),'--validation','292fullsaveCPU;2990/72stairs6/8groundreplayed;295/296/297failuresretained;296actual103/106H32;300zeroAdamrepair;actual300Pi668critic668WM7787/FIRSTcomplete32593725B;noFudanPPO0;originalbudgetphysics;hourlyandlocalpostround303;skillpending','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,peeled=head,indexed_files=len(rows),new_files=len(selected),alloldrefsprotected=True,lqrprotected=True,clean=True)))
