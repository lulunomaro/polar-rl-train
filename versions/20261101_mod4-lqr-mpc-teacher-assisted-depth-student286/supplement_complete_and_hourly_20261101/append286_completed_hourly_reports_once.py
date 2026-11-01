"""Ordinary phase supplement: completed final/fees/CPU and user hourly monitor."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;R=N/'reports';W=N.parent.parent;G=W/'polar-rl-train'
V=G/'versions/20261101_mod4-lqr-mpc-teacher-assisted-depth-student286'
DEST=V/'supplement_complete_and_hourly_20261101'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not DEST.exists() and not git('status','--porcelain')
assert git('rev-parse','HEAD')=='8efa6a7422286a5d3a4aee6d26b0f9177786e57a'
tag='trial-20261101-mod4-lqr-mpc-teacher-assisted-depth-student286'
tag_object=git('rev-parse','refs/tags/'+tag);assert tag_object=='a16478f0982dca42cd05c7fd7f510b41d48676bc'
work=json.loads((R/'CURRENT_ACTUAL286_COMPLETED_HOURLY_WORK_ORDER_V4.json').read_bytes())
assert work['status']=='ACTUAL286_COMPLETE_QUALIFIED_FORMAL_CPU_PASS_HOURLY_MONITOR'
assert work['whole_CPU']['passed'] and work['actual_updates']['Pi']==work['actual_updates']['critic']==2336
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
request=R/'AUTOMATION286_COMPLETED_HOURLY_UPDATE_REQUEST.json';q=json.loads(request.read_bytes())
assert app['prompt']==q['prompt'].rstrip('\n') and app['rrule']==q['rrule']=='RRULE:FREQ=HOURLY;INTERVAL=1'
assert app['status']=='ACTIVE' and app['target_thread_id']==q['targetThreadId']
put(R/'AUTOMATION286_COMPLETED_HOURLY_APP_RECEIPT.json',dict(epoch=time.time(),tool_return='Updated automation in the app.',
 automationId='mod4-10',mode='update',status='ACTIVE',human_requested_frequency='every hour',
 request_SHA=H(request),saved_prompt_schedule_target_exact=True,completed286_consumed_entries_marked=True))
note=R/'COMPLETE286_AND_HOURLY_NOTE_20261101.md'
with note.open('x',encoding='utf8')as f:f.write('''The user asked to set a timer and inspect current progress, then explicitly corrected the patrol interval to once per hour. Existing mod4-10 was updated in place, ACTIVE on the current continuation chat, with an actual hourly schedule. No new automation, training window, grant or account writer was created. Original schedule metadata and the first hourly update request/receipt are preserved; the completed-state prompt supersedes its older active/unused wording without changing the earlier reports.

The status snapshot taken around2026-11-01 19:29+08 found that actual286 had just completed its original one-hour learning window. Final save occurred2026-11-01T19:29:01.895679+08:00, after original19:29:00.362623 deadline. Original worker returned0, no original worker/node/owner errors, node and owner terminal/exit receipts were present. The authorized unique normal286_v2 collector then ran for the first and only time. It verified original owner/node identities and nonexecuting state, all own child waits, private and shared lock release, canonicalNone and a single matching original fee segment. Original fee3602.823357820511seconds was summed once, closing remaining-budget snapshot394115.0403189659seconds. No refund, budget copy, ledger clear, extra GO, healthy worker interruption or experiment rerun.

Final real policy2336/value2336/newWM2368(total7087),2399controls/191920own transitions/19192physics callbacks/4798feedback samples. PPO/STD/frozen-teacher updates remain0. Full final32407215bytes SHA4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d was transferred once to current_closed286_models/jump_72/formal/model_final.pt, with source and local SHA equal. The distinct unused finalCPUv2 purpose then decoded that new formal once on CPU and passed600finite tensors, actor44/Critic47, original frozen teacher2135/full17Adam42940/learnedSTD, actor9/Critic8/WM optimizer trees, counters/norm/RNG/DR/queues/reward memory and completed save scope. CUDA was not initialized; all old models/raw remained unread. Both the collector and CPU purpose are now CONSUMED.

Training completion is not stair-skill acceptance. Final7754episode terminations include7731orientation and23basecontact,0closure/0mimic. No held-out strict270mm first-air/fullwheel-footprint/top-support/.5s stable landing evaluation has been run. The existing supervision/reference/physical and original reward boundaries remain as documented. Next independent strict270 and small ground-retention evaluation needs separate source/Task/admission; the hourly patrol cannot replay consumed entries or automatically grant another training window.

This ordinary supplemental commit preserves all new saved status reports, complete original owner/node/stdout receipts, formal metadata, unique normal collection, CPU whole-tree result, hourly automation requests/app receipts, handoff and source scripts. PT/raw/NPZ/USD/media stay metadata-only forGit. The original phase annotated trial object and peel remain unchanged; no second record_experiment call or tag is made. PostGit checks remain tool outputs.
''')
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in sorted(V.rglob('CAPTURE_INDEX*.json')):
    data=json.loads(p.read_bytes())
    for row in data.get('files',[]):known[row['path']]=row['SHA']
DEST.mkdir();selected=[];rows=[]
texttypes={'.py','.json','.md','.txt','.log','.toml','.xml','.csv','.tsv','.yaml','.yml','.sh','.ps1'}
for p in sorted(N.rglob('*')):
    if not p.is_file()or'__pycache__'in p.parts or p.suffix not in texttypes:continue
    b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
    if known.get(str(p))==sha:continue
    safe,count=redact(b.decode('utf8'));value=b if not count else safe.encode('utf8')
    out=DEST/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
    gp=out.relative_to(G).as_posix();selected.append(gp)
    rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),
      redactions=count,capture='full_UTF8_byte_exact'if not count else'credential_pattern_redacted'))
index=DEST/'CAPTURE_INDEX_SUPPLEMENT_COMPLETE_HOURLY.json'
index.write_text(json.dumps(dict(epoch=time.time(),files=rows,parent_phase_tag=tag,
 parent_phase_tag_object=tag_object,parent_commit=git('rev-parse','HEAD'),current_workorder=work,
 new_formal_metadata_only=work['new_final_formal'],no_model_raw_GPU_reads_for_Git=True,
 ordinary_append_only=True),indent=2,ensure_ascii=False),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Complete teacher286 final model validation and set human-requested hourly patrol')
head=git('rev-parse','HEAD');git('push','origin','HEAD')
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
refs={x.split()[1]:x.split()[0] for x in git('ls-remote','--tags','origin').splitlines()}
assert refs['refs/tags/'+tag]==tag_object and refs['refs/tags/'+tag+'^{}']=='18571a95decc557b82d0afeda3ab8ee9c856d0e7'
assert git('ls-remote','origin','refs/heads/lqr').split()[0]=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,original_phase_tag_unchanged=tag_object,
 saved_new_files=len(rows),hourly=True,completed_final_CPU_PASS=True,clean=True)))
