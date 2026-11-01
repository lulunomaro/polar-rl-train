"""Archive final305 recovery, independent308 evaluation and all follow-up attempts.

Only text content is captured. Binary artifacts are metadata/producer-SHA indexes.
"""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
ID='mod4-final305-recovery-eval308-targeted-repair307';TAG='trial-20261102-'+ID;V=G/('versions/20261102_'+ID)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(value):return {line.split()[1]:line.split()[0]for line in value.splitlines()}
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(path):return hashlib.sha256(path.read_bytes()).hexdigest()

assert not git('status','--porcelain')and git('symbolic-ref','--short','HEAD')=='main'
assert not V.exists()and not git('tag','--list',TAG)and not(R/'RECORD307_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request=json.loads((R/'AUTOMATION307_UPDATE_REQUEST.json').read_bytes())
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert config['prompt']==request['prompt']and config['status']==request['status']=='ACTIVE'
assert config['target_thread_id']==request['targetThreadId']and config['rrule']==request['rrule']
put(R/'AUTOMATION307_APP_UPDATE_RECEIPT.json',dict(epoch=time.time(),automationId='mod4-10',mode='update',status='ACTIVE',hourly=True,request_SHA=H(R/'AUTOMATION307_UPDATE_REQUEST.json'),saved_prompt_target_schedule_exact=True,tool_return='Updated automation in the app.'))
put(R/'RECORD307_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,tag=TAG,oldrefs=oldrefs,lqr=lqr,push_failure_action='continue existing commit/tag objects, never rerecord/retag'))
note=R/'EXPERIMENT307_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''305 completed full save and safe exit, but its node/collector classified a normal WM prediction-error metrics filename as fatal. The original failed classification, CPU reader failure, once receipts and cost remain unchanged. This phase independently recovers the exact final, evaluates and visually reviews it, and prepares evidence-based repairs; it does not resume the failed tracking policy unchanged.

Final305:32695597 bytes, SHA02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958,Pi2724/Critic2724/newWM2756/totalWM12468,2787controls/222960ownpairs. OriginalworkerRC0,FINALpassed,save2026-11-02T00:44:31.691783+08. Originalfee3603.144765138626seconds,closingbalancesnapshot383272.1536028385seconds;alloriginalownchildrenwaited/private/sharedfree/canonicalNone. Originalnodeassertionandqualified_formalfalseare preserved because glob(*ERROR*.json) matched ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json,whose passed=true and finiteRMSEmetricsare normaldiagnostics. CPU305lookupfailedbeforemodelreads,postround306exitedbeforeeval;normal305/CPU305/postround306mustneverreplay.

307 independent recovery checked exact original worker/node/owner closure and the sole falsepositive diagnostic, transferred the exact final once, and preserved original classification. CPU307v1 syntax error (else8) occurred before imports/model reads; original source and failure receipt preserved. IndependentCPU307v2 decoded final once onCPU and passed609finite tensor/fullstate checks:actor103/critic106/goal59,threeAdam48257/5317/12468,EMA targetcritic,teacher17Adam42940/STD,fullDR/norm/RNG/referencephase. This validates complete saving, not skill. No accounting or physical changes.

308 independent evaluation used same fixed edge.8/270mm platform and a fresh seed9137 DR/episode distribution,80firstepisodes,400controls/3200physics/800feedback. OneGPU modeldecode,nooptimizer/accountwrites. Execution passed,skillfailed:0strict/0cross,70bad_orientation,10full8s,meanlifetime1.45675s;0closure/mimic/basecontact/lowbase. Previous300/303 had66bad_orientation/14full8s with0cross;305isworse,so no unchanged continuation. Actualvieweropened and finite native rendering replayed only savedbodyposes. Currentmodeldirectlyviewed4casesx3timeswithvisibleplatform:earlytilt/legfolding at.26-.32s farbeforeplatform,noedgecross. No newNN/physicsforrender. Largeimage/NPZ are indexed,notcommitted.

309 independentplannedinitialstatephysicalprobe producer failed IndentationError locally;0network/SDK/model/physics,originalsourcepartial preserved. 310 repairedproducer/sourceparse then attempted zero-model physicalprobe; originalparent was refused at sharedfinitevalidationEX Errno11 before SDK/physics/model/GO. Ownlockcleanup andSSHclosed/SESSIONrestored/FREE receipts retained;310once consumed and never rerun. Shared resource evidence is anotherMOD4v1 W35 evaluation,parent1418833,worker1418842/create1793552711.6,jobMOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800;latestlocal01:15snapshot holdsvalidationEX. No bypassing globalsharedlock or interfering withotherjob. GPU1availability alone doesnotpermitconcurrentvalidation.

311 is a newunusedno-model physicalcomparison prepared after resource refusal:40originalreset vs40fullplannedreference0root/q/dqreset,64controls/512physics,sameplannedjointq/dqtargetsequence. Two groups draw from sameDRdistribution,notidenticalpairedDR. Explicitactualinitialstate logging added; originalresetqueue/PDmemory remainsoriginal,notexactstatefulresume. This tests reference-task physicalinitialdistribution, not the olddefaultqobservationABIhypothesis disprovedin291. It is not yetexecutedandcannotestablishcausation. No newtrainingGO. RespectcurrentrootAGENTS newMOD4v1expertregistration;historicalH1producerjoin remainspending,not silently migratedtoanewasset/contract.

312 fixes the observed final-report classification bug in unused future-version node/collector/worker source. Newclassifier admits only the exact successful305WMdiagnostic with passedtrue,expectedsource,positive samplecount,finite nonnegative metrics and noerror/traceback; other ERRORfiles remainfatal. Actual305saveddiagnostic nowclassifies0fatal/1diagnostic,while realerror/unknownerror/malformed remainfatal in meaningfullocalregressioncases. Newworkeruses METRICSfilename.0models/SDK/network/physics;notdeployed,original305frozen sources/INDEX/falseunchanged. Futureindependenttrainingpackage mustintegratethissourcefixbeforenewfreeze,notrerun305.

Current task remains referenceconditioned103actor=35proprio+9currentdepth+59plannedreference,106critic,H32BPTT/PPO0/exp(-weightedtrackingcost/5),Fudanfalse. MuJoCoMPCsuccessmotionisstateplan,notqueryablePhysXactionteacher;no torque cloning. Futureactualdepth/GTterrainnotactor/H32;startobservedanchor+predictedposeonly. 84x48RayCaster/temporarymountisnothardwareD435icalibration/FPS.400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/10mmperenvclosure/mimic.01unchanged. Originalsinglecanonical/reserve/fullsave boundaries;no grants/copies/refunds/clearactive/secondwriter. Existing training objective retained under human newtracking authorization.

mod4-10 existinghourlyACTIVE/currentchatheartbeatupdatedtoactual307workorder/final305done/eval308done/unused311and312repair/resourcewait. No newgoal/automation/watcher. Nextreadlocalresource release/311consumption;only fresh exactLOCALCIM andserialFREEcanconnectfiniteSSH. Afterresourcesreleaseexecuteunused311onceviaoriginalparentadmission,reviewactualresults/replayandchoosewithin-taskrepair. Do not trainanotherhourunchangedbasedonloss. No inventedskill/convergenceclaim;successfulcandidaterequiresfirstflightcross/fullwheelfootprint/topmanifoldcontact/.5sstability.

This capture includes all305lateclosefalse/raw/cost reports,307transfer/CPUv1failure/v2pass,308source/task/fullresults/replaymetadata/nativevisualreview,309localfailure/310lockrefusal/311unusedsource/312classifierfixandvalidation,builders/rootrecovercaller/currentworkorder/automationprior/request/update-receipt/localtoolerrors. Knownbyte-identicaltext references existingGitpaths. PT/NPZ/USD/media are actualpath/bytes/producerSHAmetadataonly;noarchive-onlybinaryread/modelrerun. Preserve alloldtagobjects/peelsandlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad. Newphase oneannotatedtrial,latephase additionsordinarycommits,postGitvalidationtooloutputwithoutrecursiveHEADreports.
''')
resource=json.loads((R/'ROOT313_EXACT_SHARED_RESOURCE_READONLY_RETURNED.json').read_bytes())
assert resource['read_only']and resource['model_reads']==resource['SDK']==resource['canonical_writes']==0
assert all(p['running_exact']for p in resource['known_processes'])
with note.open('a',encoding='utf8')as f:f.write('\nFinal313exactknownjobread-onlycheck confirmed parent1418833/create1793552711.12 andworker1418842/create1793552711.6 stillalive,fullargv/exe/cwdverified,no terminal/releasereceipts. Didnotcontendsharedlockwhileactive,noGPUorunknownPIDscan/signals. LocalfreshCIMbeforeSSH/SSHfinallyclosed/SESSIONrestored/serialFREE saved.311remainsunusedandnoadditionaltrainingGOissued.\n')
put(R/'CURRENT307_RESOURCE_CONFIRMED313_AND_REPAIR_READY.json',dict(epoch=time.time(),status='WAITING_OTHER_EXACT_SHARED_CONTROLLER_NO_NEW_TRAINING_GO',resource_receipt=str(R/'ROOT313_EXACT_SHARED_RESOURCE_READONLY_RETURNED.json'),resource_epoch=resource['epoch'],known_processes=resource['known_processes'],shared_validation_free=None,probe311='unused,not executed while sharedcontrolleractive',classification312='local validation passed,unused independent repair source,not deployed',no_new_GO=True,no_unchanged305training=True,lastSSH=str(R/'ROOT313_ALL_SSH_CLOSED_FREE.json'),next='Read latest otherjobterminal and consumed311 before any finiteSSH.311only after actual release/originalparentlockadmission. Continue ordinary307Git supplements after unique record.'))

names=['REFERENCE_TRACKING_REAL_VALUE_V305_20261101','FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102','RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102','REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V309_20261102','REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V310_20261102','REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102','FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102']
roots=[(name,T/name)for name in names]+[('stage_builders',T/'recover307_final305_diagnostic_name_once.py')]
# Read only prior indexes. Their SHA-to-Git mapping avoids duplicating frozen text.
known={}
for version in ['20261101_mod4-lqr-mpc-teacher-assisted-depth-student286','20261101_mod4-student286-replay-retention-repair292','20261101_mod4-supermimic-bptt-task-tracking-objective294','20261101_mod4-reference-tracking-bptt-save-repair300','20261101_mod4-tracking-actual-termination-real-td-repair305']:
    for index in sorted((G/'versions'/version).rglob('CAPTURE_INDEX*.json')):
        for row in json.loads(index.read_bytes()).get('files',[]):
            s,p=row.get('SHA'),row.get('Git_path')
            if s and p and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference')and(G/p).is_file():known.setdefault(s,p)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
artifact_sha={}
def collect_artifact_sha(value,receipt):
    if isinstance(value,dict):
        sha=value.get('SHA');size=value.get('bytes')
        if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
            for key in('path','local_path','source','remote_path'):
                path=value.get(key)
                if isinstance(path,str):artifact_sha.setdefault((path.replace('\\','/'),size),(sha,receipt))
        for child in value.values():collect_artifact_sha(child,receipt)
    elif isinstance(value,list):
        for child in value:collect_artifact_sha(child,receipt)
for label,root in roots:
    if root.is_file():continue
    for receipt in sorted(root.rglob('*.json')):
        try:collect_artifact_sha(json.loads(receipt.read_bytes()),str(receipt))
        except(ValueError,UnicodeDecodeError):pass
V.mkdir();selected=[];rows=[];heavy=[]
for label,root in roots:
    assert root.exists(),str(root)
    for path in([root]if root.is_file()else sorted(root.rglob('*'))):
        if not path.is_file()or'__pycache__'in path.parts:continue
        if path.suffix.lower()in binary:
            size=path.stat().st_size;identity=artifact_sha.get((str(path).replace('\\','/'),size))
            if identity is None and path.name=='reference305.npz':identity=artifact_sha.get(('reference305.npz',size))
            heavy.append(dict(path=str(path),bytes=size,SHA=identity[0]if identity else'unknown,not measured by producer; no binaryreadforGit',SHA_receipt=identity[1]if identity else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
        assert path.suffix.lower()in texts,str(path)
        raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        out=V/label/(path.name if root.is_file()else path.relative_to(root));out.parent.mkdir(parents=True,exist_ok=True)
        try:text=raw.decode('utf8')
        except UnicodeDecodeError:
            safe,count=redact(raw.decode('latin1'));value=safe.encode('latin1');out=out.with_name(out.name+'.bytes.b64.txt');out.write_text(base64.b64encode(value).decode()+'\n',encoding='ascii')
            gp=out.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=gp,capture='base64_nonUTF8',redactions=count,archive_decoded_SHA=hashlib.sha256(value).hexdigest()));continue
        safe,count=redact(text);value=raw if not count else safe.encode();out.write_bytes(value);gp=out.relative_to(G).as_posix();selected.append(gp)
        rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
        if not count:known[sha]=gp
index=V/'CAPTURE_INDEX.json'
index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,alloldrefs=oldrefs,lqr=lqr,no_new_training_GO=True,unused311=True,classification312_deployed=False,large_artifact_receipt_sources=[str(N/'reports/ROOT307_NEW_FINAL305_SINGLE_TRANSFER.json'),str(T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/reports/ROOT308_SELECTED_REPLAY_TRANSFERS.json'),str(T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/reports/NATIVE308_RENDER_RETURNED.json')]),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original=recorder.git
def batched(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original('add','--',*args[i:i+24])
        return ''
    return original(*args)
recorder.git=batched
note_git=next(row['Git_path']for row in rows if row['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Recover complete305, evaluate failed308 and prepare targeted initial-state and close-report repairs','--kind','repair','--note-file',str(G/note_git),'--validation','305fullsaveSHA02b6/Pi2724WM12468;originalfalsepreserved;307CPU609finitefullstate;3080of80cross70orientation10full8s/nativeposesviewed;309localfalse310lockrefused;311unused312classifieractualreportregressionpass;nonewGO;hourlyupdated','--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in oldrefs.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,peeled=head,indexed_texts=len(rows),large_metadata=len(heavy),newfiles=len(selected),oldrefs_and_lqr_protected=True,clean=True)))
