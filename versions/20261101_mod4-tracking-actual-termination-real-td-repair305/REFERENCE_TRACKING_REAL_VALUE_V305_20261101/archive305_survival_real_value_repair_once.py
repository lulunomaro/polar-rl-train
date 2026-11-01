"""Archive actual305 repair plus completed300/303 and native304 diagnosis."""
from pathlib import Path
import ast,base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';O=T/'REFERENCE_TRACKING_BPTT_V300_20261101';E=T/'REFERENCE_TRACKING300_POSTROUND_EVAL_V303_20261101';D=T/'TRACKING300_FAILURE_DIAGNOSIS_V304_20261101'
ID='mod4-tracking-actual-termination-real-td-repair305';TAG='trial-20261101-'+ID;V=G/('versions/20261101_'+ID)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()}
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not git('status','--porcelain')and not V.exists()and not git('tag','--list',TAG)
assert not(R/'RECORD305_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in old.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));request=json.loads((R/'AUTOMATION305_UPDATE_REQUEST.json').read_bytes());assert config['prompt']==request['prompt']and config['status']=='ACTIVE'and config['rrule']==request['rrule']and config['target_thread_id']==request['targetThreadId']
put(R/'AUTOMATION305_APP_UPDATE_RECEIPT.json',dict(epoch=time.time(),automationId='mod4-10',mode='update',status='ACTIVE',hourly=True,saved_prompt_target_schedule_exact=True,request_SHA=H(R/'AUTOMATION305_UPDATE_REQUEST.json'),tool_return='Updated automation in the app.'))
result=json.loads((E/'reports/ROOT303_EVALUATION_FULL_RETURNED.json').read_bytes())['result'];assert result['passed']and result['strict_successes']==result['crossed_cases']==0
cases=result['results'];times=sorted(x['seconds']for x in cases);terms=result['terminations']
put(D/'reports/ACTUAL304_REPLAY_EVAL300_REPAIR_DECISION.json',dict(epoch=time.time(),status='COMPLETE300_REPLAY_EVAL_DIAGNOSE_AND305_REPAIR_STARTED',source_final_SHA=result['model_SHA'],strict_success=0,crossed=0,cases=80,finished8s=sum(x['full_window']for x in cases),terminations=terms,lifetime_min=times[0],lifetime_median=(times[39]+times[40])/2,lifetime_max=times[-1],actual_native_vision_image=str(D/'RECORDED303_NATIVE_FRAMES/ACTUAL303_FINAL300_BODY_POSE_SEQUENCE.png'),native_vision_review='Currentmodel directly viewed4casesx3actualrecordedposes withvisible270platform:env0/env1approachthenpitchandstaybeforeedge;env10/env20pitchfailureby.2s;nojumponto/overedge. No model inference/physicsrerun.',originalviewer='303viewerlaunchedthenclosed~24s before finalshot; originalreference270kind hidplatform, failurepreserved.304separaterenderonly fixesdisplay.',source_defects='actualorientation.75rad versusoldimaginationRzz.45;criticfittedonlyimaginedreturns;rawheelactionsaturationobserved',causal_scope='Theseare measured/source-backed defects and symptoms, not proof eachissolecause.304reconstructedcontextWMrolloutnotclaimedactualpredictionerror.',decision='Independent305resumesall300optimizer/modelstate, matchesactualterminationandtrainscriticonactualownTDwithEMA, thenindependenteval/replay. No unchanged300continuation.',old_sources_once_preserved=True))
put(R/'RECORD305_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,tag=TAG,old_refs=old,lqr=lqr,resume_existing_objects_on_push_failure=True))
note=R/'EXPERIMENT305_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The human requested "继续看收尾然后修复". Completed the already authorized300 full-save/safe-exit -> independent303 evaluation -> native actual recorded-body-pose review -> source-backed diagnosis -> independent305 repair and real training start. No consumed once replay, hotpatch, grant, accountcopy/refund/secondwriter or physical changes.

300 savednormally2026-11-01T23:15:29.41719+08,final32593725B SHAe700e546e3cada81dee7cdd6ed1aa59d51eb0d0d1932f0dfda928799de7812a8;Pi2593/critic2593/newWM2625,total9712/2656controls/212480owntransitions. FullCPU601finite tensors,teacherSTD/full17Adam/threeoptimizers/norm/RNG/DR/phase passed. Original owner/node/allownchildren waited/private/sharedlocksfree/CNone;fee3603.3367319107056seconds,closingbalancesnapshot386875.29836797714seconds. Alloriginalcost/fullstdout/transfer/saveandCPUreceipts now archived as same300phase supplements in this independentrepaircapture; original300tagunchanged.

303 independentnewseed9137 freshDR firstepisodes80/samefixed270course/400controls completed:0strict/0cross,66bad_orientation,14full8s;0closure/mimic/basecontact/lowbase. No270skill. Actualvieweropenedthenclosedafter~24s beforeterminalshot; missingimagequery retained as a tool-outputerror. Codekindcondition mistakenly hidreference270platform. Preserveoriginal303viewer/rawreports; independent304finite native renderer reads only alreadyrecorded303bodyposes/NPZ,showsplatform and4casesx3times,noNN/physicssimulation. Current model directly viewedoutput:two examples approach/staybeforeedgewithpitch,twoterminatepitchwithin.2s. Actualviewisnotinventedfrommetrics.

304 one necessary newfinal300CPUread for causaldiagnostics, notGit. Restoredcleanobservation reconstructionhasrawheelactionsmax9.27/9.84 andcriticmean39.33; it is notactualdelayedpolicyobservation. Diagnostic WMrollout uses reconstructedcontext, notadmittedobservedpacket and notactualpredictionerror. The referenceinitialposeafteredgeoffset isnearx0,z.253,endsx1.38,z.536; actualrecordedexamplesremainlow/beforeedge. Clear source mismatch:actualbad_orientationlimit.75rad=>Rzzcos(.75)=.7316889,imaginationsurvivalsigmoidthresholdRzz.45=>~63deg. Thus realfailedpostures can retain imaginedreturn. Critic300fitonlyimaginedrewards,withdirectbootstrapgradients. Wheel saturation/source mismatch/self-consistentmodelvalueare evidence-backed problems, notproofoneistheonlycause.

Independent305 source/Task/INDEX/control/once from preserved300final. Restoreactor103,critic106,teacherSTD,allthreeAdam/moments,norms,WM9712/dedicatedRNG;actoroffset45533/criticoffset2593,teacher17Adam42940 staysfrozen. Noactorrollbackoroptimizerreset. Physicalepisodes/DR/queue/replayarefresh,notexactPhysXresume. Mainreferenceexp(-trackingcost/5)weightsandgoals unchanged,actorH32BPTTcontinues;Fudanfalse/PPO0. Correctimaginationsurvivaltosigmoid((Rzz-cos(.75))/.025),sameactualphysicaltermination. Critic nowusesactualowntransitionr/done/nextcritic/currentdepth,one-stepTD+Huber,donezerobootstrap;EMA.01targetcritic,actorbootstrapclamp0..100,completeEMAweightsaved. CPU305one newnecessarysourcefullread verifiedexactactorcriticSTD/Adamrestore,syntheticH32no-step,actualterminalflagtestTDtarget=.6withnonzerocritic,survival(.5,.75,1rad)=[.997087,.5,.000473]. Notanindependentskilltest.

Actual305 runREFERENCE_TRACKING305_1793547655904296600,original72owner1414841/create1793547867.41,node1414850/create1793547867.83. FreshlocalexactCIM/selectedprivateEX/CNone/resourceadmission,GO2026-11-01T23:44:31.365921+08,SAVE2026-11-02T00:44:31.365921,NOMINAL00:49:31.365921,normalearliest00:34:31.365921. Originalsolecanonical3900/save3600/exit300noextension. Physical400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/closure10mm perenv/mimic.01rad unchanged.84x48RayCaster/temporarystandoffnotmeasuredD435icalibration.103/106plannedreferencegoal59tracker,notautonomousdepth-onlystudent;futureactualdepth/GTterrainnotactor/H32,ownstartobservedanchorpluspredictedposeonly;noMuJoCotorquecloning.

Native24passed. Real305FIRST64controls/5120ownpairs/512physics128feedback,Pi1critic1/newWM33total9745;actualtracking20.48794/terminal70.17518/combined74.9077finitegradients. Complete32695597B SHA296e267af8d8809a5a8caa3b93efbf8a319f906e1693ddfbde3b673ee4af4a47,actorAdam45534/critic2594,teacher42940,allthreeoptimizersandEMA/fullmemories. Subsequent73controls/Pi10critic10WM9754/28orientation;FIRSTisnotFINAL/skillsuccess.

ActualpairedWMdiagnosticbeforefirstPi uses owncontiguousrealtransitions/fixedstartobservedanchor/maskbeforereset,30313validsamplepoints,WM9744. Single-steppositionRMSE.008502956m/RzzMAE.01050248,H32positionRMSE.064150415m/RzzMAE.031208405. This isnewrealpredictionerrorontrainingreplay,notheldoutevaluation;source304reconstructedrolloutisexplicitlydistinct. ItprovidesdiagnosticforlaterWMrepairwithoutaddingarbitraryphysicsaudits.

Localsolepostround306PID20404/Start2026-11-01T23:48:11.040444+08 waitswithoutSSHuntiloriginalnormal900;thenoriginal305close/formaltransfer/newfullCPUcheck/independent306newseed9137samecourse80firstepisodes400controls/actualposereplay+finiteframecapture. NoGO/accountwritebywaiter. ItsfrozenINDEX306SHA4ff36b74f075eeaacb81933f80742dac9bd6d4c22bf11bda067600c6f1ce6020validated;viewerreference270platformnowvisibleandearlierscreenshot,capturecontinuesifGUIclosed. Final/evaluation/replaynativereview/continuationdecisionremainpending;activehourlymod4-10updatedto305andmustactonresultswithoutuserprompt. No duplicateconsumednormal/CPU/evalorsecondwatcher,sourceunchangedwhilehealthy.

Allnewsource/failures/originalreports/closed300results/303eval/304diagnosticandnativevisualreview/305CPUadmission/actualfirstupdatefullsave/automationhandoffcaptured. Rootbuildersand304diagnosticcalleroutsidephasetreesalsoincluded. Missingviewimageandexploratorywrongpathsaretoolerrors,noexperimentrerun. HeavyPT/NPZ/mediaactualpathbytesproducerSHAmetadataonly;noarchive-onlymodelhash/read. Unique305annotatedrepairtrialrecordonce;futurephase305reportsordinarysupplementnoretag. Protectalloldtagobjects/peelsandlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad. PostGitverificationtooloutputavoidsinfiniteverificationfiles.
''')
names=[O.name,E.name,D.name,N.name]
roots=[(name,T/name)for name in names]+[('stage_builders',T/'diagnose304_tracking_final_once.py'),('stage_builders',T/'prepare305_tracking_real_value_repair.py')]
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for version in('20261101_mod4-lqr-mpc-teacher-assisted-depth-student286','20261101_mod4-student286-replay-retention-repair292','20261101_mod4-supermimic-bptt-task-tracking-objective294','20261101_mod4-reference-tracking-bptt-save-repair300'):
 for p in(G/'versions'/version).rglob('CAPTURE_INDEX*.json'):
  for row in json.loads(p.read_bytes()).get('files',[]):
   sha=row.get('SHA');gp=row.get('Git_path')
   if sha and gp and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference')and(G/gp).is_file():known.setdefault(sha,gp)
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usdc','.stl','.obj','.zip','.pyc'};texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir();rows=[];selected=[]
for label,root in roots:
 for p in([root]if root.is_file()else sorted(root.rglob('*'))):
  if not p.is_file()or'__pycache__'in p.parts:continue
  if p.suffix.lower()in binary:
   rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA='Associatedproducer/transferreceipt elseunknown;no binaryreadforGit',capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texts,str(p)
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  out=V/label/(p.name if root.is_file()else p.relative_to(root));out.parent.mkdir(parents=True,exist_ok=True)
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(raw.decode('latin1'));value=safe.encode('latin1');out=out.with_name(out.name+'.bytes.b64.txt');out.write_text(base64.b64encode(value).decode()+'\n',encoding='ascii');gp=out.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,capture='base64_nonUTF8',redactions=count,archive_decoded_SHA=hashlib.sha256(value).hexdigest()));continue
  safe,count=redact(text);value=raw if not count else safe.encode();out.write_bytes(value);gp=out.relative_to(G).as_posix();selected.append(gp)
  rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
  if not count:known[sha]=gp
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,alloldrefs=old,lqr=lqr,running305=True,final_eval306_pending=True,binary_metadata_only=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original=recorder.git
def batch(*a):
 if a[:2]==('add','--'):
  for i in range(2,len(a),24):original('add','--',*a[i:i+24])
  return''
 return original(*a)
recorder.git=batch
note_gp=next(x['Git_path']for x in rows if x['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Evaluate failed tracker300 and start305 with matched termination and actual TD critic','--kind','repair','--note-file',str(G/note_gp),'--validation','300fullsavePi2593WM9712;303eval0/80cross66orientation14full8s;304nativeposesreview;305CPUfullAdamresume/survival/actualTD;actualPi1critic1WM9745/fullsave32695597B;realH32RMSE.06415m;originalphysicsbudget;hourlyandpostround306;skillpending','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,peeled=head,indexed=len(rows),newfiles=len(selected),oldrefsandlqrprotected=True,clean=True)))
