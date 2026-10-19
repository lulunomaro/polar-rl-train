"""Plan exact old output files under known owned, closed hourly roots; no deletion."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'))
import deploy_three_next_closed_source_hours_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,re,shutil,stat,sys,time
B=Path('/home/lc01/Zonglin Li/zonglin2');roots=[Path(x) for x in json.loads(sys.argv[1])];rows=[];proofs=[];skipped=[];start=time.monotonic();errors=[]
for root in roots:
 assert root.resolve()==root and root.is_relative_to(B/'tasks') and root.name in ('h1','recovery')
 m=re.fullmatch(r'T3sf(\d*)_1910v\d+',root.parent.name);assert m and (int(m[1]) if m[1] else 1)<16
active=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []):active.append(p.info)
 except psutil.Error:pass
for root in roots:
 if time.monotonic()-start>120:raise TimeoutError('Old raw cleanup plan bound120s')
 if any(any(a.startswith(str(root)+'/') for a in x['cmdline'] or []) for x in active):skipped.append(dict(root=str(root),reason='actual own-root process present'));continue
 try:
  exitp=root/'NODE_EXIT_ACTUAL.json';termp=root/'NODE_TERMINAL_ACTUAL.json';e=json.loads(exitp.read_bytes());t=json.loads(termp.read_bytes())['row']
  if not (e.get('actual_all_own_children_waited') and e.get('validation_fcntl_released_if_acquired') and t.get('terminal_all_own_children_waited')):skipped.append(dict(root=str(root),reason='missing actual closed proof'));continue
  prod=root/'job0/production'
  if not prod.is_dir():skipped.append(dict(root=str(root),reason='no production directory, no binary candidate'));continue
  protected=set()
  for name in ('FINAL.json','latest_complete.json','PPO_POSITIVE_CURRENT.json'):
   q=prod/name
   if q.is_file():
    x=json.loads(q.read_bytes());x=x.get('final',x)
    if isinstance(x,dict) and x.get('path'):protected.add(x['path'])
  proof=dict(root=str(root),exit=dict(path=str(exitp),SHA=hashlib.sha256(exitp.read_bytes()).hexdigest()),terminal=dict(path=str(termp),SHA=hashlib.sha256(termp.read_bytes()).hexdigest()),protected_complete_checkpoint_paths=sorted(protected));proofs.append(proof)
  trace=prod/'control_prefix_raw';indexp=trace/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json';known={}
  if indexp.is_file():
   raw=indexp.read_bytes();index=json.loads(raw);proof['trajectory_producer_index']=dict(path=str(indexp),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
   known={x['path']:x for x in index.get('index',[])}
   for p in sorted(trace.glob('control_prefix_*.npz')):
    if not re.fullmatch(r'control_prefix_\d+\.npz',p.name) or str(p) not in known:continue
    s=p.lstat();k=known[str(p)]
    assert p.resolve()==p and stat.S_ISREG(s.st_mode) and s.st_size==k['bytes'] and re.fullmatch('[0-9a-f]{64}',k['SHA']) and s.st_mtime_ns<=indexp.stat().st_mtime_ns
    rows.append(dict(path=str(p),root=str(root),category='old_control_trajectory_npz',bytes=s.st_size,producer_SHA=k['SHA'],actual_current_file_SHA_not_recomputed=True,device=s.st_dev,inode=s.st_ino,mtime_ns=s.st_mtime_ns,links=s.st_nlink,producer_index=str(indexp)))
  for p in sorted(prod.rglob('*')):
   if not p.is_file() or p.is_symlink() or str(p) in protected:continue
   category=None;sha=None
   if p.name.endswith('.pt.partial'):category='old_incomplete_checkpoint_atomic_partial'
   elif p.name.endswith('.npz.partial') and p.parent==trace:category='old_incomplete_trajectory_atomic_partial'
   elif p.name=='own_failed_valid_prefix.pt' and (prod/'failed_prefix_complete.json').is_file():
    k=json.loads((prod/'failed_prefix_complete.json').read_bytes())
    if k.get('failed_partial_prefix') is True and k.get('path')==str(p):category='old_failed_prefix_checkpoint_not_healthy_final';sha=k.get('SHA')
   elif p.suffix.lower() in ('.mp4','.webm','.avi') and any('replay' in z.lower() or 'video' in z.lower() for z in p.relative_to(prod).parts[:-1]):category='old_production_replay_video'
   if category:
    s=p.lstat();assert p.resolve()==p and stat.S_ISREG(s.st_mode) and s.st_mtime<=e['epoch']+1
    rows.append(dict(path=str(p),root=str(root),category=category,bytes=s.st_size,producer_SHA=sha,actual_current_file_SHA_not_recomputed=True,device=s.st_dev,inode=s.st_ino,mtime_ns=s.st_mtime_ns,links=s.st_nlink,producer_SHA_unknown=sha is None))
 except (OSError,KeyError,json.JSONDecodeError) as err:errors.append(dict(root=str(root),error=type(err).__name__+':'+str(err)))
assert len({x['path'] for x in rows})==len(rows)
print(json.dumps(dict(epoch=time.time(),human_latest_authorization='你去吧老旧的轨迹数据，回放，残缺检查点都给删除释放空间',owned_base=str(B),cutoff='Known own closed SCUT+Fudan hours1through15 only; latest completed16 and reserved17 excluded',roots=proofs,candidates=rows,candidate_count=len(rows),candidate_logical_bytes=sum(x['bytes'] for x in rows),durable=dict(zip(('total','used','free'),shutil.disk_usage(B))),skipped=skipped,errors=errors,protected_latest16_and_all_complete_FINAL_source_runtime_reset_bank_text_reports=True,producer_hashes_retained_not_claimed_newly_rehashed=True,no_delete_GPU_Task_or_account_write=True)))
'''
def main():
 assert not (R/'EXPLICIT_OLD_RAW_PLAN_STARTED_ACTUAL.json').exists()
 inv=json.loads((R/'OWNED_CLOSED_TRAINING_DISK_INVENTORY_ACTUAL.json').read_bytes());roots=[x for x in inv['exact_our_training_roots'] if '/T3sf16_1910v21/' not in x];assert roots
 put('EXPLICIT_OLD_RAW_PLAN_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,latest_human_authorization='你去吧老旧的轨迹数据，回放，残缺检查点都给删除释放空间',installation_backup_V1_actual_out_partial_retained_not_resumed=True,actual_alive_finite_only_exclusive_all_transport=True))
 pw=getpass.getpass('72 explicit old trajectory cleanup plan only (hidden): ');c=None
 try:c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);v=d.a.code(c,d.a.PY,READ,json.dumps(roots),timeout=150)
 finally:
  pw=None
  if c:c.close()
 v['actual_finite_transport_returned']=True;put('EXPLICIT_OLD_TRAJECTORY_AND_PARTIAL_CLEANUP_PLAN_ACTUAL.json',v)
 counts={}
 for x in v['candidates']:counts[x['category']]=counts.get(x['category'],0)+1
 print(json.dumps(dict(candidate_count=v['candidate_count'],candidate_GiB=v['candidate_logical_bytes']/1024**3,categories=counts,errors=v['errors'],latest16_preserved=True,no_delete_yet=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('EXPLICIT_OLD_RAW_PLAN_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete_or_GPU_or_account_change=True));raise
