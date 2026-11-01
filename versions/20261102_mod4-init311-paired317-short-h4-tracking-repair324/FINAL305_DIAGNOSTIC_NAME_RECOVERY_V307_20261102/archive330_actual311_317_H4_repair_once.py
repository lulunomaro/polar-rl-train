"""Archive all new actual311/317 trials and H4 repair evidence exactly once."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
ID='mod4-init311-paired317-short-h4-tracking-repair324';TAG='trial-20261102-'+ID;V=G/('versions/20261102_'+ID)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(value):return{line.split()[1]:line.split()[0]for line in value.splitlines()}
def H(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not git('status','--porcelain')and not V.exists()and not git('tag','--list',TAG)
assert not(R/'RECORD330_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
oldrefs=refs(git('show-ref','--tags','-d'));remote_before=refs(git('ls-remote','--tags','origin'))
assert all(remote_before.get(k)==v for k,v in oldrefs.items())
assert git('symbolic-ref','--short','HEAD')=='main'
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));request=json.loads((R/'AUTOMATION330_UPDATE_REQUEST.json').read_bytes())
assert config['prompt']==request['prompt']and config['status']==request['status']=='ACTIVE'and config['rrule']==request['rrule']and config['target_thread_id']==request['targetThreadId']
put(R/'AUTOMATION330_APP_UPDATE_RECEIPT.json',dict(epoch=time.time(),automationId='mod4-10',mode='update',status='ACTIVE',hourly=True,savedprompt_schedule_targetexact=True,requestSHA=H(R/'AUTOMATION330_UPDATE_REQUEST.json'),tool_return='Updated automation in the app.'))
put(R/'RECORD330_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,tag=TAG,oldrefs=oldrefs,remote_before=remote_before,lqr=lqr,pushfailure='Resumeexistingcommit/tagobjects,neverrerecordorretag'))
note=R/'EXPERIMENT330_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The human authorized reference tracking and repeated complete-save/safe-exit -> independent evaluation/native real-pose replay -> active targeted repair. This phase executes the previously unused311 physical comparison after actual other-job release, measures final305 world-model prediction error with real paired transitions, and prepares a complete short-horizon tracking repair. No new H1 training GO has been issued because a separate W35 original owner currently holds the single canonical writer.

305 remains completely saved/recovered, final32695597B SHA02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958. Pi2724/Critic2724/WM12468; full609finite CPU/Adam48257/5317/WM12468/teacher17Adam42940/STD/EMA/norm/RNG preserved. Prior308 independent samefixed270 eval0/80cross/strict,70orientation/10full8s and native replay already reviewed. Original305 falseclassification and307 recovery remain parallel,never rewritten. All old once receipts remain consumed.

Initialresource status: local W35 metadatawatcher PID43232/create2026-11-02T01:26:47.951594+08 heldSSH;no concurrentH1SSH whilelive. W35 completed32s evaluation/RC0/fullsaveexit by01:56:52; local01:58snapshot PARENT_EXIT_SCOPE confirms allownchildrenwaited/private/sharedreleased. E0 attempt2 then completedfresh80/24controls in22.44s and released ownprivate/sharedlocks;its collector finished. Fresh exactLOCALCIM before311 foundonlyowncontrolPID48116. This resource succession is actualevidence,not a lowGPUutilization assumption.

311 exact unused plannedjointq/dq physicalcomparison ran80environments,64controls/512physics/128feedback,0models/optimizers/accountwrites.40originalresetgroup:37orientation,3full1.28s,mean.6485s.40plannedfullreference0resetgroup:40orientation,0full,mean.8225s.0cross/strict/closure/mimic/basecontact/lowbase. Originalrawkind defaultzero_init is an inaccurate label:actualoriginalreset q is nonzero,while default_joint_pos nominal remainszero;do not claim this is a newold35obsABI default-angle error. Groups draw separately from sameDRdistribution,not identicalpairedDR. Full actualinitialroot/q/dq saved. Thus referenceinit+directplannedjointtargets didnot suffice forstabletracking; no claim this alone causally isolates initialization. Actual311recordedpose replay rendered4casesx3times and currentmodeldirectlyviewed:env1tiltsfarbeforestep;env0andref40/41progressnearstepthenpitchbeforecross. Platformvisible,noNN/physicsrerun. Ownparentwaited/locksreleased/SSHclosedSESSIONrestoredserialFREE.

314 necessary labeldiagnosis readexactreferenceNPZ/producertrajectory (no checkpoint,SDK,physics,network).250point20ms timebase,plannedlegposition/wheelspeed targets allinsideclip6,sourcejointlimits within1e-4 tolerance,posechannelselfcost0/goal59finite. Sourceendpose is heldbutlinear/angular/jointvelocity labelsremainnonzero;315 independentfix makesphase>249velocitieszero whilealloriginal250endpointlabels/pose/supportremainexact. CPU315passed. This is a late-label inconsistency,not an assertedcauseof.3s falls.

316 independentactualpairedWMdiagnostic failedstaticTaskkey completeness beforeSSH/SDK/models:teacherSHA/wholeCPUreceipt missing. Source/Task/rejectionpreserved. Independent317metadatafix thenran64controls/5120actualownpairs/512physics/128feedback on frozenfinal305actor/WM. Sourceonebyteopen/decode;WMparameters,norms,allAdam/updatesfrozen. Realcontiguous measureds224/s1before-reset masks/firstactualsameepisodeanchoronly,NO futuredepthorGTmap.1024sampledstarts/18384validpoints. Single-steppositionRMSE.00604888m/RzzMAE.0140022;step4position.0218681m/Rzz.0532855;step8position.0501583m;step16.149151m;step32.340485m(valid383).WholemaskedpositionRMSE.1647766m/RzzMAE.0654231/motorqRMSE.138251rad. Normalizer/optimizer/accountwrites0;sourceWM12468unchanged. This isactualpredictionerror,not reconstructed304contextorgradientfidelityproof.317summarystrict/cross0are placeholdersforthe commonrunner,NOT a newskilltest. Diagnostic131orientation countsrepeatdifferentepisodes;not80firstepisodes. Safeclose/finallyFREEreceipts retained.

318 shortpolicyH4 candidate leavesWMtrainingH32 andactualTD/EMAcritic unchanged. CPU319 necessary newfinal305read restored allactorcriticSTDthreeAdam/EMA and ran synthetic no-step fixture:trackinggradient.5309107,terminal29.86993,combined30.12886. H4alone still dominatedbyterminalgradient (~56x) in thisfixture;notactualruntimegradientproof,notselectedas solved.320 independentcandidate disablesactorlearnedterminalbootstrap explicitly,keepssameexp(-weightedtrackingcost/5)trackingweights/discount.99,actualTD/HubercriticandEMAforfullsave/diagnostics. CPU320 one necessarynewsource read restoredallstateexact;syntheticH4track/combinedgradient.5309107finite,terminal0;doneTD=.6.0optimizersteps/SDK/network. Itisadmission,notphysicalskill. Do not pretendshorteningH makes allmodel/valuegradients reliable.

321 independentproductionpackage completedstaticassembly but was rejectedbeforedeployment because generatedworker/launcher expectedreference321.npz whilecopiedfilewasreference305.npz. OldfrozenINDEX/source retained.322/323unusedpostround sourcesalso retained.324 independentnamingfix nowfreezes117source/task/callers withreference324.npz path/bytes/SHAchecked,actor103critic106/goal59/H4puretracking/WMH32/actualTDcriticEMA,315terminalrestholdand312finalreportclassifier sourceintegrated. INDEX324SHA b56674585d4dd26d53ac68ff5fefb637e1ecbb6e78c0ce6065eeac6352a46c2a;workerSHA6ba8e4add14d2d0d866e8cec5b8945ec934dc190cd6e792fe640730dcbb6d90b;runREFERENCE_TRACKING324_1793557830531817900. Sourcefinal305allAdam/norm/RNG/EMA/teacherSTD preserved;freshphysicalDR/queue/replay/episodes explicit. Noactorrollback/optimizerreset. NoGO/deployment/actualupdateyet.

327staticfullpackagevalidator caught an inherited unusedpostround325parent literal .replace(246,308) inconsistentwith325worker/contract. Originalrejection/source/INDEXpreserved.328 independent correctedpostround usesactualgeneratedparentASTcontract328/evaluate328/RESULT328. Old325/326mustnotexecute.329bindingonlyafteractual324FIRSTwritesexactGO/owner andlaunchesone328localtimer.330staticvalidatorchecksall117frozenbytes,referencehash,allpyAST,CPU320behaviorASTsameexceptnames/reportstrings,andcorrectactual328parent. Noadditionalmodelread. CorrectedINDEX328SHA567eef627db7182e794f9f85e2db66ce6ad25a1225c942f9d3e8ab8553476459.328afterroundwaitsnormal900,normal324fullsave-close/formaltransfer/newfullCPU/independent328samefixededge.8/270new9137DR80firstepisodes400controls/nativeactualposeframes. Human/currentmodelmustnativelyviewrenderanddecidecontinuation,notjust reportend. No timerlaunchedbeforeactualFIRST.

SeparateW35 originalwriter nowactive:MOD4V1_W35_FULLDR_ADAPT_V2_20261102_021542,owner1421790/create1793556950.73,worker1421800/create1793556951.86. GO02:15:51.626201+08/SAVE03:15:51.626201/NOMINAL03:20:51.626201.02:28localactualwatchhas7newPPO/3360000pairs/firstfullsave. HistoricalW35v1pathfailurehandledbyotherchat;notinterfered. EvenGPU1idle,noH1secondwriter/clearactive/newbudget. ReadlatestlocalW35/E0/E2finitecontrollerrelease andexactCIMbeforefiniteSSH. AftercompleteW35saveclose/canonicalNone/serialFREE/originalparentresourceadmission,launchunused324once,collectFIRST_UPDATED,validateactualH4gradient/terminal0/native24/fullfirstsave,bind329andsolepostround328. No extra watcher or new goal/automation.

Originalphysicalcontract retained400Nengineeringk2000,50policy100feedback400physics2.5msTGS32/4,fullD0whitev3D1-D7,10mmclosureperenv/mimic.01rad.Originalsolecanonical3900/save3600/exit300/strictreserve,nogrant/copy/refund/clearactive/secondwriter. HistoricalH1newMOD4v1producerjoinremainspending;324doesnot silentlyswitchassetsorclaimnewexpertadaptation.84x48provisionalcamera isnotrealD435icalibration/FPS. Plannedreference tracker,notautonomousdepth-onlystudent;MPCstateplanisnotqueryablePhysXactionteacher/no torquecloning. Firstobservedanchor+predictedposeonly,no futureactualdepth/GTmap. Skillsuccessrequiresfirstflightcross/fullwheelfootprint/topmanifoldcontact/.5sstability.

mod4-10existingACTIVEhourlycurrentchatupdatedtoactual330workorder/new324+corrected328workflow/activeW35wait. This capture includes307newbuilders/readers/toolerrorsandhandoff/automation plus311newactualresult/replaymetadata/nativeview,314diagnosis/315CPUfix,316staticfalse/317actualpairedWM,318/319CPUdominance/320CPUtrackingonly,321false/322/323unused,324frozenproduction,327false/328repair/329bind/330validation. Allactualfalse/raw/once retained;knownsameSHAtextreferencesoldGitpaths. HeavyPT/NPZ/USD/media only actualpathbytesexistingproducerSHAmetadata;noarchive-onlybinaryread/modelorphysicsrerun. Preservealloldlocal/remotetagobjects/peelsandlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad. Newphaseoneannotatedtrial;laterordinarysupplement,norecord/retag;postGitverificationtooloutputonly.
''')
names=['FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102','REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102','REFERENCE_LABEL_FEASIBILITY_DIAGNOSIS_V314_20261102','REFERENCE_TERMINAL_HOLD_LABEL_REPAIR_V315_20261102','FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V316_20261102','FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V317_20261102','REFERENCE_SHORT_POLICY_H4_REPAIR_V318_20261102','REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102','REFERENCE_H4_TRACKING_REPAIR_V321_20261102','REFERENCE_H4_TRACKING_REPAIR_V324_20261102','REFERENCE324_POSTROUND_CORRECTION_V328_20261102']
roots=[(name,T/name)for name in names]
external=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for name in('W35_eval_terminal_watch_20261102_015652.json','W35_eval_snapshot_20261102_015848.json','E0_attempt2_final_collect_20261102_015756/COLLECTION.json','W35_adaptation_dispatch_20261102_021542.json','W35_adaptation_snapshot_20261102_021807.json','W35_actual_update_watch_20261102_022834.json'):
    roots.append(('resource_evidence',external/name))
known={}
for version in('20261101_mod4-lqr-mpc-teacher-assisted-depth-student286','20261101_mod4-student286-replay-retention-repair292','20261101_mod4-supermimic-bptt-task-tracking-objective294','20261101_mod4-reference-tracking-bptt-save-repair300','20261101_mod4-tracking-actual-termination-real-td-repair305','20261102_mod4-final305-recovery-eval308-targeted-repair307'):
    for index in sorted((G/'versions'/version).rglob('CAPTURE_INDEX*.json')):
        for row in json.loads(index.read_bytes()).get('files',[]):
            s,p=row.get('SHA'),row.get('Git_path')
            if s and p and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference')and(G/p).is_file():known.setdefault(s,p)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.pyc'};texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
artifact_sha={}
def collect(value,receipt):
    if isinstance(value,dict):
        sha=value.get('SHA');size=value.get('bytes')
        if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
            for key in('path','local_path','source','remote_path'):
                path=value.get(key)
                if isinstance(path,str):artifact_sha.setdefault((path.replace('\\','/'),size),(sha,receipt))
        for child in value.values():collect(child,receipt)
    elif isinstance(value,list):
        for child in value:collect(child,receipt)
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*.json'))):
        try:collect(json.loads(p.read_bytes()),str(p))
        except(ValueError,UnicodeDecodeError):pass
V.mkdir();rows=[];heavy=[];selected=[]
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*'))):
        if not p.is_file()or'__pycache__'in p.parts:continue
        if p.suffix.lower()in binary:
            size=p.stat().st_size;identity=artifact_sha.get((str(p).replace('\\','/'),size))
            if identity is None and p.name in('reference305.npz','reference324.npz'):identity=artifact_sha.get((p.name,size))or artifact_sha.get(('reference305.npz',size))
            heavy.append(dict(path=str(p),bytes=size,SHA=identity[0]if identity else'unknown:notmeasured;noarchiveonlybinaryread',SHA_receipt=identity[1]if identity else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
        assert p.suffix.lower()in texts,str(p)
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        suffix=p.name if root.is_file()else p.relative_to(root)
        if root.is_file()and label=='resource_evidence'and p.name=='COLLECTION.json':suffix='E0_attempt2_COLLECTION.json'
        out=V/label/suffix;out.parent.mkdir(parents=True,exist_ok=True)
        try:text=raw.decode('utf8')
        except UnicodeDecodeError:
            safe,count=redact(raw.decode('latin1'));value=safe.encode('latin1');out=out.with_name(out.name+'.bytes.b64.txt');out.write_text(base64.b64encode(value).decode()+'\n',encoding='ascii');gp=out.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,capture='base64_nonUTF8',redactions=count,archive_decoded_SHA=hashlib.sha256(value).hexdigest()));continue
        safe,count=redact(text);value=raw if not count else safe.encode();out.write_bytes(value);gp=out.relative_to(G).as_posix();selected.append(gp)
        rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
        if not count:known[sha]=gp
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,alloldrefs=oldrefs,allremote_before=remote_before,lqr=lqr,no_H1_new_GO=True,actual311_completed=True,actual317_completed=True,unused324=True,correctpostround328=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original=recorder.git
def batched(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original('add','--',*args[i:i+24])
        return''
    return original(*args)
recorder.git=batched
note_git=next(row['Git_path']for row in rows if row['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Measure failed init311 and final WM317 drift; prepare complete H4 tracking repair324','--kind','repair','--note-file',str(G/note_git),'--validation','3110cross77orientation/referenceinitnotfix/nativeview;317actualH32position.340mH4.0219m/frozennorms;314labels315resthold;CPU319terminal56x/CPU320H4trackinggrad.5309terminal0/exactAdamEMA;324frozen117files/328parentAST;W35solewriteractive/noH1GO;hourlyupdated','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in oldrefs.items())and all(remote.get(k)==v for k,v in remote_before.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tagobject=obj,peeled=head,indexed=len(rows),large_metadata=len(heavy),newfiles=len(selected),alloldrefs_remoteobjects_lqr_protected=True,clean=True)))
