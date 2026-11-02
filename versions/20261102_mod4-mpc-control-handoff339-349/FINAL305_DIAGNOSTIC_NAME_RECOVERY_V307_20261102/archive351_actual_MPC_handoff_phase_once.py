"""Archive actual335-350 evidence as one new motor-handoff diagnostic phase."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-mpc-control-handoff339-349';TAG='trial-20261102-'+ID
V=G/('versions/20261102_'+ID)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(text):return{line.split()[1]:line.split()[0]for line in text.splitlines()}
assert git('branch','--show-current')=='main' and not git('status','--porcelain')
assert not V.exists()and not(R/'RECORD351_ONCE_CONSUMED_BEFORE_GIT.json').exists()and not git('tag','--list',TAG)
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
oldtag='refs/tags/trial-20261102-mod4-init311-paired317-short-h4-tracking-repair324'
assert oldrefs[oldtag]=='d2e4c479f7ecd7a2974f022a0571c826746fe225'and oldrefs[oldtag+'^{}']=='b4412bafb86d7f7e4f350feafc7a6bed6c45591e'
request=read(R/'AUTOMATION350_UPDATE_REQUEST.json')
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert config['prompt']==request['prompt']and config['status']==request['status']=='ACTIVE'and config['rrule']==request['rrule']and config['target_thread_id']==request['targetThreadId']
assert read(T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102/reports/ROOT349_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
assert not(T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102/reports/ROOT345_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
put(R/'AUTOMATION350_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(R/'AUTOMATION350_UPDATE_REQUEST.json'),actual_tool_receipt=str(R/'AUTOMATION350_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),hourly=True,status='ACTIVE',samechat=True,old336prompt_replaced=True))
put(R/'LOCAL350_READER_AND_DRAFT_FAILURES_PRESERVED.json',dict(epoch=time.time(),network=0,SDK=0,model_reads=0,physics=0,
    reader_errors=['Guessed source/code/explicit_motor_pd_core_v2.py absent; actual runtime explicit_pd_component.py and SDK adapter were then found.','Guessed source/kernel/measured_state224_v268.py absent; actual file source/code/measured_state224_v268.py found.','Broad inherited-source rg output was truncated; subsequently narrowed to exact source files.'],
    draft350_errors=[dict(type='SyntaxError invalid decimal literal',cause='dict keyword 345GO invalid identifier',repair='training345GO'),dict(type='SyntaxError keyword argument repeated actual349',repair='first path key changed to actual349root')],
    prior_summary_reader_errors='Prior context reported several guessed source paths during335-345; precise unavailable outputs not fabricated. Existing static/runtime failures are retained in original reports.',
    original_error_classification_unmodified=True))
put(R/'RECORD351_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase=ID,expected_tag=TAG,mode='one_new_diagnostic_phase_record_experiment',oldrefs=oldrefs,remote_before=remote,lqr=lqr,retry='If commit/tag exists or push fails, continue existingobjects; do not rerun this script or record/retag.',large_artifacts_metadata_only=True))
note=R/'EXPERIMENT351_MPC_CONTROL_HANDOFF_DIAGNOSTIC.md'
note.write_text('''The tuned MPC succeeds in its own source plant, but the learning pipeline has not faithfully executed that controller. After final324 was completely saved and closed, independent339 evaluation and native recorded-pose review found 0/80 crossing or strict270,56 orientation terminations,24 full8s,mean3.35625s. Prior305/308 was0/80,70orientation10full8s,mean1.45675s. Improved survival is not the target skill. Actor spins/drifts or tips before the step; actual343 saved replay analysis has large lateral/backward travel. Costs span different survival distributions and are not a controlled causal comparison.

335 attempted the first final324 evaluation after328 resource refusal; exact resource/authority admission succeeded but worker root contract import failed before SDK/model/physics.338 independent import repair passed its stdlib/contract prefix test but localCIM regex backslashR was invalid, rejected before network.339 independent plainRMPOLAR regex repair executed actual fixededge.8/270 independentDR/episode seed9137,80firstepisodes/400controls,one actor decode,no learning/account writes; safe closed/released. Real recorded-pose rendering was natively inspected. Original335/338false and all consumed attempts remain immutable;328 was not rerun.

340 diagnostic builder failed staticTask kind,0network/model;341 fixed kind but rejected a known local archive controller before network.342 independent actual frozenfinal324 pairedWM diagnostic64controls/5120ownpairs had one necessary model decode,0updates/accountwrites:1step positionRMSE.004578864m,H4.011496116m,H8.018896786m,H32endpoint.110839635m/allmasked.054908916m; predicted yaw tracks existing spinning. LocalH4 action sensitivity used earlyphase0..3 and does not prove physical derivatives or later exponential attenuation. It is not an additional skill evaluation.

344H8directweightedtrackingcost candidate reused exactfinal324 fullactor103critic106STD/threeAdam/EMA/normRNG/WM16879,actorAdam52636/critic9696; unique new necessaryCPU decode,nooptimizerstep. Syntheticfixture trackinggradient5.28002548 finite,terminal0; not physical repair proof.345 production package was frozen with exact344behavior and original3900/save3600/exit300, but remains unused,noSTARTconsumed/deployment/GO/postround. Human then challenged why the already tuned complete MPC/motor trajectory was not transferring. This steering led to halting new objective/horizon training and examining the missing control handoff instead. Existing frozen345 is preserved.

346 source audit found reference prepare consumes qpos/qvel/wheelposes/support from500x10ms successful MPC trajectory, subsampling rows[1::2] to250x20ms. It discards desiredtau and appliedtorque and does not invoke the closed-loop controller. SourceMPC issues100Hz desiredtorque, converts through nominal inversePD to processed position/velocitytargets, retains D4/explicitPD/signedDCclip/motorgain/signedDCclip, and uses measuredstate launch/landing events. Currentactor issues50Hz fourlegposition/twowheelvelocity normalizedtargets. Previous311 copied plannedjointstate into PDtargets, which is not sourceinversePD or faithfulMPCreplay. Sourcephysics500us,currentPhysX2500us, different initial/DR/asset/contact and feedback/event handling remain material; no single causalclaim. Nominal cleanendpoint inversePD arithmetic is explicitly an illustration,not exactoriginalnoisycommand.

347 is a new localCPU control-trace extraction,not an archive-only repeat. Frozen successful sourcecontroller code runs once with instrumentation that leaves its originaltorque_control/physics calls in place and captures previously missing pre-controlstate/processedtargets and everyphysical application. It produced500x100Hzcommands and10000x500usphysicssteps;MPCsuccess andstable3.02s,0NN/Isaac/GPU/SSH/optimizer/account/GO. LocalMuJoCo3.15 vsoriginal3.12,NumPy2.4.5vs2.5.2,so not claimed bitwiseorendpointidentical(oldendpointmaxpositiondifference.09654m). Originalsuccess2.69s/sourceimmutable. Actuallegtarget-stateRMSE.134-.157rad andwheeltarget-dq2.92/2.94rad/s quantify nonzero drive targets distinct from kinematic reference. Full100HzcommandJSON andactualapplicationNPZ preserved,indexedNPZexistingproducerSHA.

348 new noNN probe package prepared but copiedactorimmutability assertion was found statically beforedeployment;0network/model/SDK/physics,unusedfrozenretained. Independent349 removes it and records actual initialstate,motortargets/q/dq with actualbodyposes. Sameplannedt0 initialstate all80,sourceprocessedtargets versus sourcejointstate-as-target; source100Hzcommands deliberately sampled every20ms and held20ms using unchanged50Hz policyinterface and originalD4/PD/CADprojection/DCenvelope. FullD0whitev3D1-D7 draws from same distribution,not pairedexactly. This is an openloop feedforward/controlhandoff comparison,not source100Hzclosed-loopMPCor an actor evaluation.0NNdecode/learning/optimizer/accountwrites/newGO; originalCNone/private/sharedadmission and ownwait/release/SSHfinallyclose restoredFREE.

Actual349 results: state-as-target40cases,0cross0strict,40orientation0full5s,mean1.0855s; processedMPCtarget40cases,13cross0strict,33orientation7full5s,mean1.706s.13/40 crossing is a measured geometry/flight criterion,not stablelanding or actualcontactmanifoldconfirmed graduation. All four selected actualreplaycases0/1/40/41 were natively viewed with platformvisible; they approach/tipnearstep,not stable. Aggregatecross13comesfromall80measurement,not these four images. UnequalDR and sourceclockresampling preclude a solecausalclaim, but evidence supports fixing motorhandoff before more blindstate-onlylearning. This is the first progress toward crossing under transferred plannedmotorcontrols; not a learned policy pass.

Next: establish originalMPCclosedloop or clearly boundedfeedforward+feedback execution at declaredsource/currentclocks, actualrequest/appliedmotortargets/torque/state/phase and firstdivergence, before anothertraininghour. Do not silentlychange50Hzactor100Hzfeedback400Hzphysics/2.5msTGS32-4/fullDR/400Nengineeringk2000/10mmclosure/.01mimic/originalcanonicalbudgetreserve. Do not bypassactuatorlimits, directlycloneunrestrictedtorque, inferone-wayPhysXactionoracle,changehistoricalH1assetorclaimnewMOD4v1graduation. All oldonce,qualifiedfalse,raw/source/errors retained. Everyactualroundsafeclose->independentfacts->nativeactualposes->decision persists.

Current350workorder and existingmod4-10updated viaappautomationtool toACTIVE/hourly/samechat,with old336status replaced. No newautomation orGoal. Freshknownlocalcontrollers/serialFREE and authoritativeCNone/private/sharedadmission required before any newfiniteSSH; neversecondwatcher/unknownPIDscan/kill/clearactive. Credentials useexistingmemory only,neveroutput/Git. Alltextsource/reports/false/raw/automation/reader/draftfailures capturefullorcredentialredacted; heavyweightPT/NPZ/USD/media onlyactualpathbytesexistingSHA. Existingtags/peels andlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad protected. Newphase uses one record_experiment annotatedtrial;pushfailure resumeobjects,notretag. PostGitverification stays tooloutput to avoidrecursiveHEADreports.
''',encoding='utf8')

names=['FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102','FINAL324_IMPORT_REPAIR_EVAL_V338_20261102','FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102','FINAL324_ACTUAL_PAIRED_DIRECTION_DIAGNOSTIC_V340_20261102','FINAL324_ACTUAL_PAIRED_DIRECTION_DIAGNOSTIC_V341_20261102','FINAL324_ACTUAL_PAIRED_DIRECTION_DIAGNOSTIC_V342_20261102','REFERENCE_H8_DIRECT_TRACKING_REPAIR_V344_20261102','REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102','MPC_TIMED_CONTROL_EXTRACTION_V347_20261102','MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V348_20261102','MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102']
roots=[(P.name,P)]+[(n,T/n)for n in names]
external=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for name in ('W35_after_resume89aca_eval_terminal_watch_20261102_080039.json','W35_AFTER_RESUME_EVAL_AND_OWN_CPU_ONCE_RESULT_V1.json','SLOPE_INDEPENDENT50_own_terminal_watch_20261102_070111.json','NINE_N80_SINGLE_GPU_RESOURCE_20261102_084030.json'):
    p=external/name
    if p.is_file():roots.append(('resource_evidence',p))
mpc=Path('F:/RMPOLAR-RL/traditional_control_20261101')
for name in ('model/mod4_400N.xml','MODEL_PROVENANCE.json','results/FINAL_EVIDENCE_V2/control_core.py','results/FINAL_EVIDENCE_V2/hybrid_trial.py','results/FINAL_EVIDENCE_V2/dr_components.py','results/FINAL_EVIDENCE_V2/linear_mpc.py','results/FINAL_EVIDENCE_V2/fullDR_mpc/trajectory.json','results/FINAL_EVIDENCE_V2/fullDR_mpc/result.json','results/FINAL_EVIDENCE_V2/fullDR_mpc/config.json','results/FINAL_EVIDENCE_V2/manifest.json'):
    roots.append(('mpc_source_evidence',mpc/name))
known={};prior_versions=[G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307']
for base in prior_versions:
    for index in base.rglob('*CAPTURE_INDEX*.json'):
        for row in read(index).get('files',[]):
            sha,gp=row.get('SHA'),row.get('Git_path')
            if sha and gp and (G/gp).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):known.setdefault(sha,gp)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
identities={}
def collect(value,receipt):
    if isinstance(value,dict):
        sha=value.get('SHA')or value.get('sha256');size=value.get('bytes')
        if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
            for key in('path','local_path','source','remote_path','image'):
                path=value.get(key)
                if isinstance(path,str):identities.setdefault((path.replace('\\','/'),size),(sha,receipt))
        for child in value.values():collect(child,receipt)
    elif isinstance(value,list):
        for child in value:collect(child,receipt)
for label,root in roots:
    for path in([root]if root.is_file()else sorted(root.rglob('*.json'))):
        if path.suffix!='.json':continue
        try:collect(read(path),str(path))
        except(ValueError,UnicodeDecodeError):pass
V.mkdir();rows=[];heavy=[]
for label,root in roots:
    assert root.exists(),str(root)
    for path in([root]if root.is_file()else sorted(root.rglob('*'))):
        if not path.is_file()or'__pycache__'in path.parts:continue
        suffix=path.suffix.lower();size=path.stat().st_size
        if suffix in binary:
            identity=identities.get((str(path).replace('\\','/'),size))
            heavy.append(dict(path=str(path),bytes=size,SHA=identity[0]if identity else'unknown:noarchiveonlybinaryhash',SHA_receipt=identity[1]if identity else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
        assert suffix in texts,str(path)
        raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        safe,count=redact(raw.decode('utf8'));value=raw if count==0 else safe.encode('utf8')
        leaf=(Path(*path.relative_to(mpc).parts)if label=='mpc_source_evidence'else Path(path.name))if root.is_file()else path.relative_to(root)
        dest=V/label/leaf;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
        gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
        if count==0:known[sha]=gp
index=V/'CAPTURE_INDEX.json';put(index,dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,actual339_and342_and347_and349_completed=True,production345GO=False,all_own_SSH_closed=True,noarchiveonlymodelreads=True))
selected=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
args=[sys.executable,'-B','-X','utf8',str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Diagnose MPC control handoff: source commands cross in PhysX; retain failed state-only tracking','--kind','diagnostic','--note-file',str(V/P.name/'reports'/note.name),'--validation','Actual3390/80; actual347sourceMPCsuccess3.02s; actual349state0/40cross versus processedtargets13/40cross, both0strict; noNNtraining345GO; allsafeclosed.','--files',*selected,'--push']
done=subprocess.run(args,capture_output=True,text=True,encoding='utf8')
if done.returncode:
    print(json.dumps(dict(passed=False,returncode=done.returncode,stdout=done.stdout,stderr=done.stderr,do_not_rerun_record=True,existing_head=git('rev-parse','HEAD'),existing_tag=git('tag','--list',TAG))),flush=True);raise SystemExit(done.returncode)
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}')
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())
assert all(remote_after.get(k)==v for k,v in remote.items())
assert remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==peel==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,phase=ID,HEAD=head,tag=TAG,tagobject=obj,peeled=peel,remote_main=head,oldtags_and_peels_protected=True,lqr=lqr,files=len(selected),indexed=len(rows),heavy_metadata=len(heavy),clean=True,record_stdout=done.stdout),ensure_ascii=False),flush=True)
