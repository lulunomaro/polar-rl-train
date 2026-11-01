"""Ordinary supplement after recorded286; do not record or tag this phase again."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;W=N.parent.parent;R=N/'reports';G=W/'polar-rl-train'
V=G/'versions/20261101_mod4-lqr-mpc-teacher-assisted-depth-student286'
DEST=V/'supplement_final_CPU_v2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not DEST.exists() and not git('status','--porcelain')
assert git('rev-parse','HEAD')=='18571a95decc557b82d0afeda3ab8ee9c856d0e7'
tag='trial-20261101-mod4-lqr-mpc-teacher-assisted-depth-student286'
tag_object=git('rev-parse','refs/tags/'+tag);assert tag_object=='a16478f0982dca42cd05c7fd7f510b41d48676bc'
req=json.loads((R/'AUTOMATION_ACTUAL286_FINAL_CPU_V2_APPEND_REQUEST.json').read_bytes())
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==req['prompt'].rstrip('\n') and app['target_thread_id']==req['targetThreadId'] and app['rrule']==req['rrule']
put(R/'AUTOMATION_ACTUAL286_FINAL_CPU_V2_APPEND_APP_RECEIPT.json',dict(epoch=time.time(),
 tool_return='Updated automation in the app.',automationId='mod4-10',mode='update',status='ACTIVE',
 request_SHA=H(R/'AUTOMATION_ACTUAL286_FINAL_CPU_V2_APPEND_REQUEST.json'),saved_prompt_schedule_target_exact=True))
work=json.loads((R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER_V2.json').read_bytes())
work['epoch']=time.time();work['status']='ACTUAL286_RUNNING_FINAL_CPU_V2_UNUSED_SELECTED'
work['next']['final_CPU']=json.loads((R/'HANDOFF286_NEW_FINAL_CPU_V2_UNUSED.json').read_bytes())
work['observed_tool_only_latest']=dict(snapshot_epoch=1793530035.613718,Pi_updates=693,critic_updates=693,
 new_WM_updates=725,total_WM_updates=5444,controls=756,own_transitions=60480,
 terminated=3212,bad_orientation=3211,base_contact=1,closure=0,mimic=0,
 worker_original_error=False,statement='single metadata-only snapshot from original node; no continuous-health or skill claim')
work['recorded_phase']=dict(commit='18571a95decc557b82d0afeda3ab8ee9c856d0e7',tag=tag,tag_object=tag_object,
 note='Subsequent reports ordinary supplemental commit; original trial remains on its original commit.')
put(R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER_V3.json',work)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
old=json.loads((V/'CAPTURE_INDEX.json').read_bytes());known={r['path']:r['SHA'] for r in old['files']}
DEST.mkdir();selected=[];rows=[]
texttypes={'.py','.json','.md','.txt','.log','.toml','.xml','.csv','.tsv','.yaml','.yml','.sh','.ps1'}
for p in sorted(N.rglob('*')):
    if not p.is_file()or'__pycache__'in p.parts or p.suffix not in texttypes:continue
    b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
    if known.get(str(p))==sha:continue
    text=b.decode('utf8');safe,count=redact(text);value=b if not count else safe.encode('utf8')
    out=DEST/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
    gp=out.relative_to(G).as_posix();selected.append(gp)
    rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,
      capture='full_UTF8_byte_exact'if not count else'credential_pattern_redacted',reason='new or changed saved text after first phase capture'))
index=DEST/'CAPTURE_INDEX_SUPPLEMENT.json'
index.write_text(json.dumps(dict(epoch=time.time(),files=rows,parent_trial_tag=tag,parent_trial_commit=git('rev-parse','HEAD'),
 status='ordinary append only; selected unused finalCPU v2 typed286 key join and app receipt; no new experiment or model read'),indent=2,ensure_ascii=False),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Append unused286 final CPU reader key repair and verified continuation receipts')
head=git('rev-parse','HEAD');git('push','origin','HEAD')
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','--tags','origin').splitlines()}
assert refs['refs/tags/'+tag]==tag_object and refs['refs/tags/'+tag+'^{}']=='18571a95decc557b82d0afeda3ab8ee9c856d0e7'
assert git('ls-remote','origin','refs/heads/lqr').split()[0]=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,phase_tag_unchanged=tag_object,new_saved_reports=len(rows),clean=True)))
