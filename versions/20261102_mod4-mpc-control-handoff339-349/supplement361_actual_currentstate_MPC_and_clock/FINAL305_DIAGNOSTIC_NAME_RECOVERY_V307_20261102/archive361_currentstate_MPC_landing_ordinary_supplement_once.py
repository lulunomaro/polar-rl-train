"""Append current-state MPC phase/clock actual evidence without a second trial tag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
BASE=G/'versions/20261102_mod4-mpc-control-handoff339-349';V=BASE/'supplement361_actual_currentstate_MPC_and_clock'
TAG='trial-20261102-mod4-mpc-control-handoff339-349';OBJ='f63c76d9c064a26e6261b544304c7f92a5bbdf76';PEEL='a6c59be6408153875b36ed851d59d3767f8e5709'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(value):return{r.split()[1]:r.split()[0]for r in value.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'SUPPLEMENT361_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert git('rev-parse','refs/tags/'+TAG)==OBJ and git('rev-parse','refs/tags/'+TAG+'^{}')==PEEL
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request=read(R/'AUTOMATION360_UPDATE_REQUEST.json');config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert request['prompt']==config['prompt']and request['rrule']==config['rrule']and request['status']==config['status']=='ACTIVE'and request['targetThreadId']==config['target_thread_id']
for v,n in((355,'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'),(357,'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')):
    assert read(T/n/f'reports/ROOT{v}_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
assert not(T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102/reports/ROOT345_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
put(R/'AUTOMATION360_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(R/'AUTOMATION360_UPDATE_REQUEST.json'),actual_tool_receipt=str(R/'AUTOMATION360_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),hourly_ACTIVE_samechat=True))
put(R/'LOCAL360_DRAFT_SYNTAX_FAILURE_PRESERVED.json',dict(epoch=time.time(),network=0,SDK=0,NN=0,physics=0,stage='local360workorderdraft beforeexecution',error='SyntaxError invalid decimal literal from invalid345GOkeyword',repair='training345GOidentifier; AST/actualscript executed after correction',originalexperiment_results_unchanged=True))
put(R/'SUPPLEMENT361_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),tag=TAG,tagobject=OBJ,peel=PEEL,oldrefs=oldrefs,remote_before=remote,lqr=lqr,mode='ordinarysupplement_no_record_or_retag',push_retry='Resume existingobjects; do not rerun this script or recreate tag.'))
note=R/'SUPPLEMENT361_CURRENT_STATE_MPC_AND_LANDING.md'
note.write_text('''This supplements existing recordedphase mod4-mpc-control-handoff339-349, without a new trial/tag or rewriting its historical failures. Actual source347 MPC and actual349 openloop controltransfer were already recorded. Human asked why their tuned full MPC trajectory did not transfer, so current work tested current-state/event control and timing through the original50Hzaction/100Hzfeedback/400Hzphysics path rather than launch unused345 training.

352 used existing349 recordedmotor/bodyposes,zeroNN/SDK/network/physics: selected targetapplication differs from requested by max~5.4e-6rad/rad_s, not evidence of simple selectedcase scale/permutation/application failure. Sourcejointstate is not inversePDmotortarget; selectedendpointerrors grow inpush/flight. This reads noPT and does notrepeat349once.

353 copied sourcehybridphase equations and nominalMPCgains into a new finitecurrentstatecontroller bridge. Sourcegainextraction blockedmj_step,0physics/SDK/NN;7fixtures approach/push/flight/recover matched originalrequestedtorque exactly. It preserves position+velocitylaunchevent,measuredlaunchpose,sourceflightlaw and measuredtoplandingtransition. It declares privilegedtranslation/vx/yaw and remains a diagnostictraditionalcontroller,not learnedautonomousdepthstudent. Originalsourcegains are sourceplantnominal,not newly identifiedPhysXgains. The originalpredictiondt.01 with currenthold.02 is explicitly acknowledged.

354 independentfiniteattempt built SDK and plannedinitialstates but failedbeforefirstcontrol when actualpolicyterm.scaleTensor was JSONserialized.0NN/optimizer/accountwrites;workerwrapperRC0doesnotmeanpass,resultnull/originalparentfalse/errorlogsretained. Allownchildrenwaited,private/sharedreleased/SSHfinallyclosed/FREE.355 independentrepair converts actualscaletensor toserializableperwidthlist and dividesactualpolicyfeedbackcorrectly; CPUscalar/vector/batchTensorcases checked withoutSDK/model.354consumednotrerun.

Actual355 used80plannedinitialstates/fullDR(originalsame distribution,nonpairedgroups),samefixededge.8/270seed9137/250controls5s,0NNlearningoptimizeraccountwritesGO.0..39openloopprocessedmotor:6/40leadingedgeprogress,37orientation,3full5s,mean1.2705s.40..79current-state/eventMPC:37/40leadingedgeprogress,28orientation,12full5s,mean2.299s.40alllaunchedevent,19recover.0strictstabletopbothgroups.Original50Hzqueue.control_us20000/PD/CADprojection/DCenvelope/fullDR/2.5msTGS32-4retained. CurrentMPCrequestevery20msusingoriginal100Hzfeedback,sourceprediction10ms;thisisnotfaithful100Hzsourceexecution. Realrequested/appliedmotortorque,initialstateandcontrolphasewerecaptured; fullreturned12.7MBtextretained. Safeclosedreplaybodyposesrendered0NN/physicsandnativelyviewed.

356 saved355diagnosis foundcase41full5sreturnsuprighttothegroundbeforetheplatform(finalrootz.2625/x.530),notstableontop. Sourcecriteria.3m/s/.5rad_s differsfromcurrentstrict.03m/s,originalcriteriaunchanged; do notrelaxforgraduation. FullDRunpairedgroupscannotestablishsolecausalbenefit,currentstatefeedbackneverthelessproducesmuchmorefrontedgeprogressinthismeasurement.

357 independentlyre-discretizedsamecontinuoussourceA/B/Q/Ratactual20mscommandperiod(H8=.16sversussourceH15=.15s),CPU0stepAdchangechecked. Actual80fullDRnewfirstepisodescomparisonbothcurrentstateeventMPC:source10msmodel+20msholdgroup0..39,33/40leadingedgeprogress33orientation7full5smean1.8495;actual20msmodel+20msholdgroup40..79,32/40leadingedgeprogress27orientation13full5smean2.471; strict0both,stablemax0.13and20casesenteredrecover.0NNtrainingoptimizeraccount/GO,originalphysics/PD/50Hztargetqueueunchanged. Safeclose/release/SSHFREE;fullreturned17.98MBandactualreplayrendernativelyviewed. Timingadaptationaloneisnotafix,nopolicygraduation,DRnotexactpaired.

358 corrects importantcrossinglanguagewhilepreservingrawflags: existingfirst_flight_both_cross measures eachwheel LEADING authoredcollisionbound crossingedge duringfirstflight,NOT wholefootprintclearance. Thus prior13/40andnew37/40or32/40arefrontedgeprogress,notcompletejumporstabletop. SourceMPCcrossusesrearwheelcenter-minusradiusmargin. Fullcollisionfootprint/topcontact/.5sstableplusactualcontactmanifoldremainrequired. Selected357fourcasebodyposeimagesstilltipnearedge; recordedwheelcenter/radiusproxy(fullboundnotreplaced)shows somefullclearancebutnostablelanding. Allraworiginalclassificationsunchanged,correctiveinterpretationparallel.

359 comparedsourceoriginalsuccessfulposture:minRzz.993447,neverbelowcurrentcos(.75)termination. Currentselected355/357firstRzz<.95about.7-1.0s,push/flighttransfer; orientationguardisnotfalsekillingthesourcesuccess. Preserve.75radactualthreshold,no looseningto source.45Rzz.359offlineappliedtorquecomparisonhadrightcrank/hippermutationwrong[1,0,4,2,3,5]; original359reportpreserved.360correctionuses[1,0,4,3,2,5]frompolicycrankhipcrankhipwheels tosourcehipcrankwheelhipcrankwheel,0newphysics/NN. Actual355/357physicalcontrollerorderswerenotchangedandresultsremainvalid.

Currentdecision360: no blind345training,no identical355/357repeat. Remainingfailureisflightposture/fullfootprint/landingrecovery; nextfinitecomparisonmustinspectactualnominalplant/perenvDR/firstdeviationandrequested/appliedmotortarget/torque/phasebeforechoosingtargetedcontroller/residualtrackingtraining. No nextstage is falselyclaimedpreparedorstarted. Originalsinglecanonical3900/save3600/exit300strictreserve/400Nengineeringk2000/50policy100feedback400physics2.5msTGS32-4/fullD0whitev3D1-D7/10mmepisodeclosure/.01mimic/assetstay. No grantcopyrefundclearactive/secondwriter/unrestrictedtorquecloning/oraclePhysXteacher. Source100Hzscheduleisnotfullyported; do notsilentlyalterqueue100Hz.345unused,324alreadyclosed/339independentevaluated.

Resourceevidence: otherchatNINEfirst/V2failedbeforecommonstartandownchildwaited/private/sharedreleased; thosefailuresnotattributedtoourtask. FreshbroadlocalCIMbeforeeach354/355/357andparentoriginalCNone/private/sharedadmissionrequired. No GPU-PIDscan/unknownkill/secondwatcher/interference. EachfiniteSSHfinallyclosed/SESSIONrestored/FREE. Current360workorder/hourlyexistingmod4-10ACTIVEsamechatupdatedthroughappautomationtool;noGoal/newautomation. Allsource/rawfalse/reports/controltext/automation/draftSyntaxErrorcaptured,indexed; PT/NPZ/mediaonlyactualpathbytesexistingSHA,noarchivemodelread. Preservealloldtags/peelsandlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad. PostGitverificationtooloutputavoidsrecursiveHEADreports.
''',encoding='utf8')
roots=[(P.name,P)]+[(n,T/n)for n in('MPC_CURRENT_STATE_EVENT_BRIDGE_V353_20261102','MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V354_20261102','MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102','MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')]
ext=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for n in('NINE_SINGLE_GPU_STATUS_20261102_090951.json','NINE_SINGLE_GPU_V2_LATEST_CLOSED_RESULT_PATH.json','NINE_SINGLE_GPU_V2_CLOSED_20261102_091553/CLOSED_RESULT.json'):
    if(ext/n).is_file():roots.append(('resource_evidence',ext/n))
known={}
for base in(BASE,G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
    for idx in base.rglob('*CAPTURE_INDEX*.json'):
        for row in read(idx).get('files',[]):
            sha,gp=row.get('SHA'),row.get('Git_path')
            if sha and gp and(G/gp).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):known.setdefault(sha,gp)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
identities={}
def collect(v,receipt):
    if isinstance(v,dict):
        sha=v.get('SHA')or v.get('sha256');size=v.get('bytes')
        if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
            for key in('path','local_path','source','remote_path'):
                path=v.get(key)
                if isinstance(path,str):identities.setdefault((path.replace('\\','/'),size),(sha,receipt))
        for a in v.values():collect(a,receipt)
    elif isinstance(v,list):
        for a in v:collect(a,receipt)
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*.json'))):
        if p.suffix!='.json':continue
        try:collect(read(p),str(p))
        except(ValueError,UnicodeDecodeError):pass
V.mkdir();rows=[];heavy=[]
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*'))):
        if not p.is_file()or'__pycache__'in p.parts:continue
        size=p.stat().st_size
        if p.suffix.lower()in binary:
            identity=identities.get((str(p).replace('\\','/'),size));heavy.append(dict(path=str(p),bytes=size,SHA=identity[0]if identity else'unknown:noarchiveonlybinaryhash',SHA_receipt=identity[1]if identity else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
        assert p.suffix.lower()in texts,str(p)
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8')
        dest=V/label/(p.name if root.is_file()else p.relative_to(root));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
        if count==0:known[sha]=gp
put(V/'CAPTURE_INDEX_SUPPLEMENT361.json',dict(epoch=time.time(),existing_tag=TAG,tagobject=OBJ,peel=PEEL,ordinary_supplement=True,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,actual355357safeclosed=True,training345GO=False,noarchiveonlymodelreads=True))
files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
assert not git('diff','--cached','--name-only')
for i in range(0,len(files),24):git('add','--',*files[i:i+24])
git('commit','-m','Record current-state MPC transfer and 20ms timing comparison; diagnose unstable landing')
head=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/main')
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())and all(remote_after.get(k)==v for k,v in remote.items())
assert remote_after['refs/tags/'+TAG]==OBJ and remote_after['refs/tags/'+TAG+'^{}']==PEEL
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,ordinary_supplement=True,HEAD=head,remote_main=head,tag=TAG,unchanged_tagobject=OBJ,unchanged_peel=PEEL,alloldtagsprotected=True,lqr=lqr,files=len(files),indexed=len(rows),heavy_metadata=len(heavy),clean=True)),flush=True)
