"""One bounded CPU-only actual read; never imports an old once worker or starts GPU."""
from pathlib import Path
import json,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as base
ROOT=base.BASE+'/bodyframe20k_second_formal3600_same_profile_v1_20261014'
CODE=r'''
from pathlib import Path
import json,time,hashlib,psutil,fcntl
R=Path(CONTEXT['root'])
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def index(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
top={n:read(R/n) for n in ('ROOT_UNIQUE_DISPATCH_ACTUAL.json','PARENT_IDENTITY.json','CURRENT_STAGE.json','PIPELINE_COMPLETE_REVIEW_READY.json','PIPELINE_ORIGINAL_ERROR.json','ACTUAL_NATIVE_STARTUP_CRASH_ALERT.json','GUARDIAN_EXIT.json')}
stage=R/'formal3600';A=stage/'attempt';logfiles=list((A/'learning_logs').glob('*/latest_complete.json'));folders=list((A/'learning_logs').glob('*'))
records={};marker={};files=[]
if folders:
 folder=folders[0]
 for name in ('CLOCK_TRAINING_HEALTH.json','BODYFRAME_FORMAL_FINAL_ACTUAL.json','FORMAL_FINAL_ACTUAL.json','BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json'):
  records[name]=read(folder/name)
 for p in folder.glob('*STARTUP_VERIFIED.json'):marker[p.name]=read(p)
 for p in folder.glob('*FINAL*.json'):records[p.name]=read(p)
if logfiles:
 latest=read(logfiles[0]);records['latest_complete']=latest;target=Path(latest['checkpoint'])
 if target.exists():files.append(index(target))
states={n:read(A/n) for n in ('DISPATCH_RECEIPT.json','GUARDIAN_CURRENT.json','EXIT_RECEIPT.json')}
identities=[]
for row in (top['ROOT_UNIQUE_DISPATCH_ACTUAL.json'],top['PARENT_IDENTITY.json'],states['DISPATCH_RECEIPT.json']['child'] if states['DISPATCH_RECEIPT.json'] else None):
 if not row:continue
 try:
  p=psutil.Process(row['pid']);identities.append(dict(pid=p.pid,created=p.create_time(),expected=row.get('created'),argv=p.cmdline(),cwd=p.cwd(),matches_creation=p.create_time()==row.get('created'),actual_alive=True))
 except psutil.NoSuchProcess:identities.append(dict(pid=row['pid'],actual_alive=False))
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget=read(B);locks=[]
for path in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 held=True
 with path.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:pass
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_fcntl_held=held))
stdout=A/'worker_stdout.log';tail=stdout.read_bytes()[-5000:].decode('utf8','replace') if stdout.exists() else ''
parentlog=R/'pipeline_parent.log'
print(json.dumps(dict(epoch=time.time(),root=str(R),top=top,states=states,records=records,startup_marker_count=len(marker),startup_markers=marker,actual_PID_identities=identities,locks=locks,actual_budget=dict(active_segment=budget['active_segment'],remaining=budget['remaining_training_seconds'],charged=budget['charged_training_seconds'],sha256=hashlib.sha256(B.read_bytes()).hexdigest()),own_complete_saved_files=files,worker_tail=tail,parent_tail=parentlog.read_bytes()[-2000:].decode('utf8','replace') if parentlog.exists() else '',readonly_CPU_only=True)))
'''
def main():
 c=None;stamp=str(time.time_ns())
 try:
  c=base.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+base.PY+' -',timeout=60);si.write('CONTEXT='+repr(dict(root=ROOT))+'\n'+CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,(rc,err.decode('utf8','replace')[-2000:]);v=json.loads(out)
  path=R/('SECOND_BODY_FORMAL_CURRENT_ACTUAL_'+stamp+'.json');path.write_bytes(out)
  health=v['records'].get('CLOCK_TRAINING_HEALTH.json');proof=v['records'].get('BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json')
  print(json.dumps(dict(report=str(path),own_final=v['top']['PIPELINE_COMPLETE_REVIEW_READY.json'] is not None,own_error=v['top']['PIPELINE_ORIGINAL_ERROR.json'],own_startup_markers=v['startup_marker_count'],body14_passed=proof.get('actual_GPU_fullrestore_passed') if proof else None,own_saved=v['own_complete_saved_files'],health={k:health.get(k) for k in ('control_steps','actual_physics_callbacks','ordinary_termination_count','integrity_failure_count','unknown_termination_count','stop_reason','max_loop_closure_error_mm')} if health else None,actual_PID=v['actual_PID_identities'],locks=v['locks'],worker_tail=v['worker_tail'][-2000:],parent_tail=v['parent_tail'])))
 except BaseException:
  (R/('SECOND_BODY_FORMAL_READER_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True,no_retry=True),indent=2),encoding='utf8');raise
 finally:base.close(c)
if __name__=='__main__':main()
