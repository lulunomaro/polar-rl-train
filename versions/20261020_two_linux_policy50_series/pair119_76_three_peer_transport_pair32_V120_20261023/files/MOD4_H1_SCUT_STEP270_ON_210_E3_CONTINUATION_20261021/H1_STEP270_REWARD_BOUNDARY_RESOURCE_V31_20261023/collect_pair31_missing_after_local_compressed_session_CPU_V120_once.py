"""Use once near the actual save/exit boundary; no mid-window model reads."""
from pathlib import Path,PurePosixPath
import hashlib,importlib.util,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;W=N.parent.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ210=r'''
from pathlib import Path
import fcntl,json,os,psutil,subprocess,time
q=v['q'];owner=Path(q['owner_root']);h1=Path(q['roots']['h1']);until=time.monotonic()+850
read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
def own():
 out=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(a.startswith((str(owner)+'/',str(h1)+'/')) for a in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while not (owner/'COHORT_FINAL.json').exists() or not (owner/'OWNER_EXIT_ACTUAL.json').exists() or own():
 assert time.monotonic()<until,'Actual owner/H1 closure not completed; no schedule-based FINAL'
 time.sleep(3)
co=read(owner/'COHORT_FINAL.json');oe=read(owner/'OWNER_EXIT_ACTUAL.json')
assert co['original_cost_settled'] and oe['original_cost_settled']
ne=read(h1/'NODE_EXIT_ACTUAL.json');nt=read(h1/'NODE_TERMINAL_ACTUAL.json')
assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired']
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=read(C)
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8
segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==q['owner_identity']['pid'] and x['started_epoch']>=q['owner_identity']['creation']]
assert len(segments)==1 and set(segments[0]['experts'])==set(co['go'])=={'h1','recovery'}
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))
texts=[]
for key,root in (('owner',owner),('h1',h1)):
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
   raw=p.read_bytes();texts.append(dict(path=str(p),relative=key+'/'+p.relative_to(root).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),cohort=co,owner_exit=oe,H1_node_exit=ne,H1_terminal=nt,original_segment=segments[0],original_canonical_remaining=c['remaining_training_seconds'],original_locks=locks,all_owner_H1_children_actual_out=True,text_files=texts,no_account_write_or_midwindow_model_hash=True)))
'''
READ72=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
q=v['q'];root=Path(q['roots']['recovery']);until=time.monotonic()+180
def own():
 out=[]
 for p in psutil.process_iter(['pid','cmdline']):
  try:
   if p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while not (root/'NODE_EXIT_ACTUAL.json').exists() or own():
 assert time.monotonic()<until,'Actual E3 children still active'
 time.sleep(3)
read=lambda p:json.loads(p.read_bytes());e=read(root/'NODE_EXIT_ACTUAL.json');terminal=read(root/'NODE_TERMINAL_ACTUAL.json')
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'];locks=[]
for p in (Path(q['specs']['recovery']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))
texts=[]
for p in root.rglob('*'):
 if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
  raw=p.read_bytes();texts.append(dict(path=str(p),relative='recovery/'+p.relative_to(root).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),node_exit=e,node_terminal=terminal,locks=locks,all_E3_processes_actual_out=True,text_files=texts,no_account_change=True)))
'''
def capture(c,receipt,models,key):
    sf=c.open_sftp();sf.get_channel().settimeout(90);texts=[];saved=[]
    try:
        for row in receipt['text_files']:
            rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
            p=N/'current_pair_closed_text'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
            texts.append(dict(row,local_path=str(p)))
        for row in models:
            p=N/'current_pair_closed_models'/key/PurePosixPath(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            part=p.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(p)
            saved.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
    finally:sf.close()
    return texts,saved
def main():
    metadata=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert metadata['passed']
    assert max(x['nominal_end_epoch'] for x in metadata['source210']['current']['go'].values())-time.time()<=900,'Only the existing <=900 second closing boundary'
    q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    put('PAIR_MISSING_ONLY_CLOSING_COLLECTOR_STARTED_V120_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_owner=q['owner_identity']))
    s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover();c=None
    try:
        c=d.t.connect();a=d.code(c,d.t.PY,READ210,dict(q=q),timeout=900)
        put('PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json',a)
        row=a['cohort']['rows']['h1'];final=row.get('final') or {}
        texts1,models1=capture(c,a,[final['final']] if final.get('passed') else [],'h1')
        c.close();c=None
        c=d.connect72(secret);secret=None;b=d.code(c,d.PY72,READ72,dict(q=q),timeout=210)
        row=a['cohort']['rows']['recovery'];final=row.get('final') or {}
        texts2,models2=capture(c,b,[final['final']] if final.get('passed') else [],'recovery')
        put('PAIR_CLOSED_TARGET72_ACTUAL.json',b)
        result=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,target72=b,
                    complete_models=dict(h1=models1,recovery=models2),all_texts=texts1+texts2,
                    original_canonical_cost_settled=True,not_skill_qualification=True)
        put('PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',result)
        print(json.dumps(dict(closed=True,models={k:len(v) for k,v in result['complete_models'].items()},original_cost_settled=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('PAIR_MISSING_ONLY_CLOSING_ORIGINAL_ERROR_V120_'+str(time.time_ns())+'.json',
            dict(epoch=time.time(),error=traceback.format_exc(),no_replay_or_refund_or_midwindow_PT=True))
        raise
