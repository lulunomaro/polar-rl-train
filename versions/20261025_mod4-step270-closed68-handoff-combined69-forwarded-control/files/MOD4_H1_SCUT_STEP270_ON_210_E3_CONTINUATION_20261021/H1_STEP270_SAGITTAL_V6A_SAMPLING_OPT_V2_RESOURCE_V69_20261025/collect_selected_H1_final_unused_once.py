"""Use once near the actual save/exit boundary; no mid-window model reads."""
from pathlib import Path,PurePosixPath
import base64,hashlib,importlib.util,json,os,sys,time,traceback
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
assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==q['owner_identity']['pid'] and x['started_epoch']>=q['owner_identity']['creation']]
assert len(segments)==1 and set(segments[0]['experts'])==set(co['go'])=={'h1'}
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
def capture(c,receipt,models,key):
    sf=c.open_sftp();sf.get_channel().settimeout(90);texts=[];saved=[]
    try:
        for row in receipt['text_files']:
            rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
            p=N/'current_pair_closed_text'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            sf.get(row['path'],str(p))
            if p.stat().st_size==row['bytes'] and H(p)==row['SHA']:
                texts.append(dict(row,local_path=str(p)))
            else:
                assert rel.as_posix()=='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log','Unexpected text mismatch; preserve original and stop'
                original=dict(row,local_path=str(p),transferred_bytes=p.stat().st_size,transferred_SHA=H(p),manifest_time_bytes_not_captured=True)
                code="from pathlib import Path;import base64,hashlib,json; p=Path(v['path']); a=p.stat(); raw=p.read_bytes(); b=p.stat(); assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns); print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),mtime_ns=b.st_mtime_ns,base64=base64.b64encode(raw).decode())))"
                fresh=d.code(c,d.t.PY,code,dict(path=row['path']),timeout=45);raw=base64.b64decode(fresh.pop('base64'));assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
                fp=p.with_name('omni.processlifetime.fresh_after_manifest_mismatch.log')
                with fp.open('xb') as f:f.write(raw)
                put('H1_ONLY_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),original=original,fresh=dict(fresh,local_path=str(fp)),cause_unknown=True,original_manifest_time_bytes_unavailable=True,no_training_failure_or_refund_inferred=True))
                texts.append(dict(row,bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(fp),original_manifest_and_transferred_log_preserved=original,one_fresh_snapshot_only=True))
        for row in models:
            p=N/'current_pair_closed_models'/key/PurePosixPath(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
            part=p.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(p)
            saved.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
    finally:sf.close()
    return texts,saved
def main():
 metadata=json.loads((R/'H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json').read_bytes());assert metadata['passed'] and metadata['source210']['H1_actual_GO']['nominal_end_epoch']-time.time()<=900
 q=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('H1_ONLY_CLOSING_STARTED_ACTUAL.json',dict(epoch=time.time(),actual_owner=q['owner_identity']));c=d.t.connect()
 try:
  a=d.code(c,d.t.PY,READ210,dict(q=q),timeout=900);put('H1_ONLY_CLOSED_CANONICAL_COST_ACTUAL.json',a);final=a['cohort']['rows']['h1'].get('final') or {};texts,models=capture(c,a,[final['final']] if final.get('passed') else [],'h1')
 finally:c.close()
 result=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,complete_models=dict(h1=models),all_texts=texts,original_canonical_cost_settled=True,E3_no_GO_or_cost_interval=True,not_skill_qualification=True)
 put('H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json',result);print(json.dumps(dict(closed=True,H1_complete_models=len(models),original_cost_settled=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('H1_ONLY_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_or_refund=True));raise
