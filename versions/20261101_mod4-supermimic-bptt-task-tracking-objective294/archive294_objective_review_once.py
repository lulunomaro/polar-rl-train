"""Unique diagnostic phase: retain user-led BPTT/task-objective correction."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;W=N.parent.parent;G=W/'polar-rl-train';R=N/'reports'
ID='mod4-supermimic-bptt-task-tracking-objective294';TAG='trial-20261101-'+ID;V=G/('versions/20261101_'+ID)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()}
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not git('status','--porcelain') and not V.exists() and not git('tag','--list',TAG)
assert not(R/'RECORD294_ONCE_CONSUMED_BEFORE_RECORD.json').exists()
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in old.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
q=json.loads((R/'AUTOMATION294_OBJECTIVE_REVIEW_UPDATE_REQUEST.json').read_bytes());a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['prompt']==q['prompt'] and a['rrule']==q['rrule'] and a['target_thread_id']==q['targetThreadId'] and a['status']=='ACTIVE'
put(R/'AUTOMATION294_OBJECTIVE_REVIEW_APP_RECEIPT.json',dict(epoch=time.time(),automationId='mod4-10',mode='update',tool_return='Updated automation in the app.',status='ACTIVE',hourly=True,request_SHA=H(R/'AUTOMATION294_OBJECTIVE_REVIEW_UPDATE_REQUEST.json'),saved_prompt_schedule_target_exact=True,unchanged_mixed_objective_continuation_superseded=True))
put(R/'RECORD294_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),phase=ID,tag=TAG,old_refs=old,lqr=lqr,push_failure_resume_objects_no_retag=True))
note=R/'EXPERIMENT294_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The human challenged why a teacher-guided stair policy still optimizes Fudan velocity/flight rewards and correctly asked whether SuperMimic uses BPTT to replace PPO for task tracking. This diagnostic reviews actual292source and saved successful LQR/MPC JSON trajectories, without new model reads, SDK runs, optimizer steps, GO, account writes or new reward-version training.

Current292already uses H32 BPTT through learned own dynamics; PPO is not its policy updater. Its objective is negative Fudan return plus negative Fudan critic, decaying teacher-state auxiliary averaged overH32, ground retention and overflow. Critic targets explicitly exclude teacher tracking. Stair commands remain fixed1.4m/s across the episode. Successful saved teacher terminal halfsecond meanvx is-.0113352m/s(LQR) and-.00117397m/s(MPC), i.e. stop and stabilize. This proves competing terminal goals; it does not prove the sole cause of all failures. The prior LR/ground-retention patch did not fix the task definition.

Official SuperMimic paperarXiv2610.28480 and authors project were opened. It uses a deterministic goal-conditioned policy, reference-motion tracking reward, BPTT through frozen-within-update WM and critic bootstrap. BPTT replaces the model-free policy-gradient estimate, not the need to define a task objective, and a critic remains compatible. AppendixA reference tracking and AppendixB downstream velocity are distinct goal interfaces. We do not claim paper results or performance transfer to this custom closed-chain robot.

Concrete new design: task/reference-conditioned tracker for approach, takeoff, clearance, landing and stable rest. Train with state/joint/base and actually supported wheel landing targets and small action regularization; declare new reward/loss configuration. Match actor and critic to the same tracking objective. Use per-episode consistent clip and monotonic phase/reference goals, with training/deployment goal inputs aligned. Train ownWM on own actual transitions; no foreign MuJoCo dynamics or future actual depth/GT leak. The two5s successful MuJoCo trajectories are references, not an arbitraryPhysX-state callable normalized-action teacher, so no unfounded torqueaction cloning or DAgger plan.

Existing frozen292completes its original full save and safe exit; original postround48920handles293independent evaluation/replay, without newGO. No healthy training hotpatch/kill or oldonce replay. Hourlymod4-10now explicitly supersedes unchanged-mixed-objective continuation, even if ground3/8is retained. New task-tracking code/Task/admission remains pending; this diagnostic does not claim implementation, skill acceptance or new training started. Physical400N/50policy100feedback400physics2.5msTGS32/4/fullDR/10mmperenvclosure/.01radmimic and solecanonical budget protections remain.

All saved diagnosis, redesign, automationprior/request/receipt and source errors are preserved. Exploratorygitwrongcwd and rgwrongcwd errors are disclosed. Unique294diagnostictrial uses record_experiment once, all old tagobjects/peels/lqrprotected. Later implementation/evaluation requires independent phase or append as appropriate; pushfailure resumes existingobjects.
''')
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
V.mkdir();selected=[];rows=[]
for p in sorted(N.rglob('*')):
    if not p.is_file()or'__pycache__'in p.parts:continue
    assert p.suffix in('.py','.json','.md','.txt','.log')
    b=p.read_bytes();safe,count=redact(b.decode('utf8'));data=b if not count else safe.encode('utf8')
    out=V/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);gp=out.relative_to(G).as_posix();selected.append(gp)
    rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),files=rows,phase=ID,all_old_refs_protected=old,lqr=lqr,model_SDK_GO_budget_writes=0,implementation_pending=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original=recorder.git
def batch(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original('add','--',*args[i:i+24])
        return''
    return original(*args)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Correct SuperMimic tracking objective diagnosis and supersede mixed-reward continuation','--kind','diagnostic','--note-file',str(G/note_gp),'--validation','Actual292BPTTnotPPO;fixed1.4m/sversusteacherterminalnear0;teacherexcludedfromcritic;officialpaperreview;concretereferencetrackingdesign;hourlycontinuationcorrected;0model0SDK0steps0GO0accountwrites;newimplementationpending','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,peeled=head,files=len(rows),all_old_refs_protected=True,clean=True)))
