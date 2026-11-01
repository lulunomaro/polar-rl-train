"""Archive all actual evaluation failures, replay, causal comparison, repair292."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
ID='mod4-student286-replay-retention-repair292';TAG='trial-20261101-'+ID
V=G/('versions/20261101_'+ID)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return {x.split()[1]:x.split()[0] for x in s.splitlines()}
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert git('status','--porcelain').strip()=='M AGENTS.md'
assert not git('diff','--cached','--name-only') and not git('tag','--list',TAG) and not V.exists()
assert not (R/'RECORD292_PHASE_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in old.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
assert git('rev-parse','HEAD')=='dfbc66a949c6c3be3ca6b3c8e305ba4567310b60'
request=R/'AUTOMATION292_HOURLY_AFTER_ROUND_UPDATE_REQUEST.json';q=json.loads(request.read_bytes())
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==q['prompt'] and app['rrule']==q['rrule']=='RRULE:FREQ=HOURLY;INTERVAL=1'
assert app['status']=='ACTIVE' and app['target_thread_id']==q['targetThreadId']
put(R/'AUTOMATION292_HOURLY_AFTER_ROUND_APP_RECEIPT.json',dict(epoch=time.time(),tool_return='Updated automation in the app.',automationId='mod4-10',mode='update',status='ACTIVE',request_SHA=H(request),saved_prompt_schedule_target_exact=True,postround_action_workflow=True))
put(R/'RECORD292_PHASE_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,unique_trial=TAG,old_tagobjects_and_peels=old,lqr=lqr,push_failure_continue_existing_objects_no_retag=True))
put(R/'LOCAL287_292_FAILURE_AND_CORRECTION_LEDGER.json',dict(epoch=time.time(),failures=[
 dict(id='287-task-binding',result='Rejected before SDK/model: current_authority_binding missing; independent288 fixed'),
 dict(id='local287-patch',result='Large initial apply_patch repo AGENTS context verification rejected, applied none; separate patches succeeded'),
 dict(id='288-skill',result='Execution pass but strict2700/72 and ground0/8;80orientation,max.28s, widespread action saturation'),
 dict(id='288-terminal-reader-off-by-one',result='Raw episode_terminal.seconds adds extra.02s. Canonical results.controls*.02 correct. Preserve oldraw; independent289+ fixes only new source.'),
 dict(id='289-source-byte-hash',result='CRLF written bytes differ from text.encode hash;0model/SDK, complete logs; repaired independent290 actual bytes'),
 dict(id='290-missing-terrain-dependency',result='ModuleNotFoundError terrain290 after app,0model; all own wait/free; independent291 explicit dependency'),
 dict(id='291-counterfactual',result='Same9137source2135 drives,final286 shadows.0/72strict;3/8ground8s.55orientation2basecontact0closure/mimic;23firstepisodes complete. Source not graduated.'),
 dict(id='default-angle-hypothesis-false',result='Assistant initially called relative versus absolute default-joint ABI causal.291 actual defaultq/dq allzero; false inference corrected publicly and preserved. No functional default-angle fix claimed.'),
 dict(id='local-rg-windows-glob',result='Two exploratory rg paths containing literal wildcard yielded Windows invalidfilename; next reads used concrete paths. No model/SDK changes.'),
 dict(id='292-CPU-source-test-v1',result='Test shallow optimizer state_dict aliased live tensors and failed equality after correct restoration. Original preserved; independentv2 uses deepcopy and passes proposal cap/no-step/reject rollback.'),
 dict(id='293-unused-parent-CIM-template',result='Unused eval template initially matched its local waiting parent, which would reject legitimate sequential child. Original unused source retained; new staging excludes localtimer while retaining remotecontroller patterns.')],all_prior_raw_preserved=True))
note=R/'REPLAY_EVALUATION_AND_RETENTION292_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The user explicitly requires each saved round to be replayed, independently evaluated and followed by an active continuation/repair decision, permanently. Root and repository AGENTS now preserve this workflow. Existing mod4-10 remains ACTIVE hourly on this chat and includes it; unchanged state stays quiet.

Final286 (4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d,Pi2336/Critic2336/WM7087) was evaluated in independent288 seed9137,80first episodes with72held-out270mm layouts and8ground standing/forward/reverse cases.0/72crossed or stable,0/8ground completed8s,80bad_orientation, no closure/mimic/basecontact. Maximum14controls=.28s. All actual original logs and pose transfers preserved. The real PhysX pose recording was opened visibly in277-mesh MuJoCo display-only viewer, no NN/physics rerun; native model vision inspected screenshot showing pre-edge flip. First viewer was launched20:05:59Beijing for1800s and later exited naturally; displayed image remains external.288raw terminal seconds has extra.02, while controls and canonical results.seconds are correct; correction is append-only.

287 omitted authority binding and failed before SDK/model;288 added explicit freshCNone binding.289 causal probe failed preSDK/model on Windows CRLF workerSHA,290 failed missing renamed terrain after app but0model.291 independent repaired source drove the frozen2135 source from the same complete286 carrier and shadowed final286. Source0/72strict but3/8ground survived8s versus0/8final; source still not a stable expert.55orientation/2basecontact,0closure/mimic. First paired actions and shadow drift retained. Exactly one necessary model decode in291. The assistant's default-angle ABI hypothesis was disproved by actual allzero defaultq/dq and corrected publicly; it is not presented as a causal repair. All these consumed attempts, errors, complete stdout and frees are retained, never replayed.

Source286 selected only valid stair anchors for actor updates; disjoint ground transitions supplied no policy-retention objective. Shared policy drift and deployed saturation are measured; not all model-bias causes are resolved. Independent292 rolls actor/critic/full17Adam back to original frozen2135 migration and retains latest ownWM7087/optimizer/norm/RNG from complete286 carrier. Failed student remains unchanged in original artifact. Fresh physical/DR/queue/replay scope is declared; this is not exact PhysX resume. ActorLR1e-5 versus critic1e-4; separate old-policy ground distillation coefficient1, raw-action overflow.001, measured-start action-drift cap.05 and groundreference cap.5 on sampled observations. Parameter interpolation/Adam rejection rollback is tested synthetically onCPU without model reads; v1 reader alias failure and independentv2deepcopy pass are preserved. No claim of global trust region or retained ground skill follows until evaluation. Original Fudan19methods/16weights and LQR/MPC state-supervision coefficient unchanged; no foreign MuJoCo WM transitions or torqueaction cloning.

Actual292 sole original72 ownerPID1407231/create1793537933.49, node1407240/create1793537933.92; GO2026-11-01T20:58:57.447205+08, SAVE21:58:57.447205, NOMINAL22:03:57.447205. Original3900/save3600/exit300 and sole canonical remaining budget, no grant/refund/accountcopy.400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0white_v3D1-D7/closure10mm perenv/mimic.01rad unchanged.80env72training270platformsseed286+8originalground; actual provisional84x48camera not calibratedD435i. Native24 beforeWM and realH32 reward2.9744/terminal7.7539/teacher.2272/combined10.14195 gradients pass. FIRST64controls/5120ownpairs/Pi1critic1/newWM33total7120, full32408047B SHAfe45582a60e76c3e1e5f2ed965d92d481aa2de857f94df9f19db5ec3f26a3b9a. Subsequent72controls/Pi9/Critic9/WM7128,6orientation. This is training/update evidence, not270success.

Local dedicated postroundPID48920 waits without SSH until original normal900, then invokes the original own-waits/free-locks/CNone/rawfeeSUMONCE collector once, qualified final transfer and fullCPU check once, new293evaluation and actual replay. It saves a concrete result-dependent continuation/repair decision for hourly chat to act on; it creates no GO. Unused template known-parentCIM issue was fixed before execution, with v1 retained. New293first-flight tracking requires prior observed support; no manifold graduation claim. Actual next decisions and results are pending and must enter an ordinary supplemental commit; no duplicate consumed normal/CPU/eval. Waiting process alive does not mean its future actions have run.

Every saved report/source/handoff/automation receipt through this capture is archived. BinaryPT/NPZ/media remain actual producerpath/bytes/SHA metadata only. Full old annotated tagobjects/peels and lqr5848 are protected. Existing286phase tag is unchanged. New unique annotated292repairphase uses record_experiment once; push failure resumes objects. PostGit verification remains tool output rather than generating endless follow-up receipts. The working training owner is never stopped/hotpatched forGit.
''')
names=['TEACHER286_REPLAY_EVAL_V287_20261101','TEACHER286_REPLAY_EVAL_V288_20261101','FROZEN_SOURCE_COUNTERFACTUAL_V289_20261101','FROZEN_SOURCE_COUNTERFACTUAL_V290_20261101','FROZEN_SOURCE_COUNTERFACTUAL_V291_20261101',N.name]
roots=[(name,T/name)for name in names]+[('workspace_policy',W/'AGENTS.md')]
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in (G/'versions/20261101_mod4-lqr-mpc-teacher-assisted-depth-student286').rglob('CAPTURE_INDEX*.json'):
    for row in json.loads(p.read_bytes()).get('files',[]):
        sha=row.get('SHA');gp=row.get('Git_path')
        if sha and gp and row.get('capture')=='full_UTF8_byte_exact' and (G/gp).is_file():known.setdefault(sha,gp)
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usdc','.stl','.obj','.zip','.pyc'}
texttypes={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir();rows=[];selected=['AGENTS.md']
for label,root in roots:
    for p in ([root]if root.is_file()else sorted(root.rglob('*'))):
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
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,protected_old_refs=old,lqr=lqr,postround_results_pending=True,binary_metadata_only=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batch(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original_git('add','--',*args[i:i+24])
        return ''
    return original_git(*args)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Replay failed student286, retain causal failures, and start bounded ground-retaining repair292', '--kind','repair','--note-file',str(G/note_gp),'--validation','288final0/72stairs0/8groundmax.28s;realposeGUIviewed;287/289/290failurespreserved;291source3/8ground8s0/72stairs;defaultanglehypothesisdisproved;CPU292v2boundedproposal/reject/no-stepPASS;actual292native24/H32Pi1critic1WM7120/fullsave32408047B;hourly+localpostroundenabled;originalbudget/physics/Fudanunchanged','--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,peeled=head,indexed_files=len(rows),new_files=len(selected),all_old_refs_protected=True,lqr_protected=True,clean=True)))
