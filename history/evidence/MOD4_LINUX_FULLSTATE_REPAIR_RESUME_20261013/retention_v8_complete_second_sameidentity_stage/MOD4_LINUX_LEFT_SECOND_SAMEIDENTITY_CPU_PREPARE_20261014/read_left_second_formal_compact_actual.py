"""Future compact readonly actual observer; this source preparation does not connect."""
import json,os
import second_root_owned_transport_common_v1 as t
CODE=r'''
from pathlib import Path
import json,time,fcntl,hashlib,sys,psutil
R=Path(CONTEXT['proposed_root']);a=R/'left_second_formal3600_v1'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
m=read(R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json')
assert m and m['source']['sha256']==CONTEXT['source_SHA'] and m['num_envs']==20000 and m['no_initializer_repeat'] is True
dispatch=read(R/'LEFT_SECOND_FORMAL_DISPATCH_ACTUAL.json')
assert dispatch and dispatch['pid']==CONTEXT['expected_parent_pid'] and dispatch['start_ticks']==CONTEXT['expected_parent_start_ticks']
files={n:read(R/n) for n in ('PARENT_IDENTITY.json','CURRENT_STAGE.json','LEFT_SECOND_FORMAL_PARENT_ERROR.json','LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json','GUARDIAN_EXIT.json')}
files.update({n:read(a/n) for n in ('DISPATCH_RECEIPT.json','EXIT_RECEIPT.json','GUARDIAN_CURRENT.json')})
folders=[p for p in (a/'learning_logs').glob('*') if p.is_dir()] if (a/'learning_logs').is_dir() else []
if folders:
 assert len(folders)==1
 f=folders[0];files['latest_complete']=read(f/'latest_complete.json');health=read(f/'CLOCK_TRAINING_HEALTH.json')
 files['health_compact']={k:v for k,v in (health or {}).items() if isinstance(v,(str,int,float,bool)) or v is None}
 markers=list(f.glob('*STARTUP*VERIFIED.json'));files['startup_count']=len(markers);files['log_dir']=str(f)
 if len(markers)==13:
  sys.path.insert(0,str(R));from left_sameidentity_typed13_receipts import validate_set
  worker=files['DISPATCH_RECEIPT.json'];assert worker and worker['source']['sha256']==CONTEXT['source_SHA']
  files['thirteen_actual_typed_startup']=validate_set(markers,worker['child']['pid'],CONTEXT['source_SHA'])
 else:files['thirteen_actual_typed_startup_pending']=True
actual=[]
for role,row in [('parent',files['PARENT_IDENTITY.json']),('worker',(files['DISPATCH_RECEIPT.json'] or {}).get('child'))]:
 if not row:continue
 try:
  p=psutil.Process(row['pid']);stat=Path('/proc',str(p.pid),'stat').read_text();ticks=int(stat.split(') ',1)[1].split()[19])
  got=dict(role=role,pid=p.pid,created=p.create_time(),start_ticks=ticks,argv=p.cmdline(),cwd=p.cwd())
  assert got['created']==row['created'] and got['argv']==row['argv'] and got['cwd']==row['cwd'],'PID reuse or changed argv/cwd'
  assert got['cwd']==str(R)
  if role=='parent':assert got['pid']==dispatch['pid'] and ticks==dispatch['start_ticks']
  actual.append(got)
 except psutil.NoSuchProcess:actual.append(dict(role=role,pid=row['pid'],actual_absent=True))
log=a/'worker_stdout.log'
if log.is_file():
 with log.open('rb') as f:f.seek(max(0,log.stat().st_size-3000));tail=f.read()
 files['worker_log_compact']=dict(bytes=log.stat().st_size,tail=tail.decode('utf8',errors='replace'),tail_only_not_full_capacity_audit=True)
locks=[]
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held=False;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:held=True
  locks.append(dict(path=str(p),held=held))
print(json.dumps(dict(epoch=time.time(),root=str(R),actual_manifest_SHA=digest(R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json'),source=m['source'],sourcefreeze_count=len(m['sourcefreeze']),files=files,actual_processes=actual,actual_fcntl_locks=locks,readonly_no_PPO_or_signal_or_budget_write=True,active_save_not_formal_final_or_qualified50=True)))
'''
def main():
    local=json.loads((t.REPORTS/'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json').read_bytes())
    assert local['cwd']==t.ROOT and local['source']['sha256']==t.SOURCE_SHA
    c=None
    try:
        c=t.connect();v=t.run(c,CODE,'LEFT_SECOND_FORMAL_COMPACT_CURRENT_ACTUAL',dict(proposed_root=t.ROOT,source_SHA=t.SOURCE_SHA,expected_parent_pid=local['pid'],expected_parent_start_ticks=local['start_ticks']))
        f=v['files'];print(json.dumps(dict(phase=(f['CURRENT_STAGE.json'] or {}).get('phase'),parent_error=f['LEFT_SECOND_FORMAL_PARENT_ERROR.json'],own_parent_saved_review_ready_exists=bool(f['LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json']),latest_complete=f.get('latest_complete'),startup_count=f.get('startup_count',0),health=f.get('health_compact'),actual_processes=v['actual_processes'],locks=v['actual_fcntl_locks'],active_save_not_final_or_qualified50=True)))
    except BaseException:t.original_error('LEFT_SECOND_COMPACT_READER_ORIGINAL_ERROR');raise
    finally:
        if c:c.close()
        os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
