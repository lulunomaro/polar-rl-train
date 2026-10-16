"""Read-only existing WAVE final boundary; no signals, jobs, leases or budget writes."""
from pathlib import Path
import getpass,hashlib,importlib.util,json,paramiko,shlex,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';N=D.name+'/wave_episode_reviewed_v3'
s=importlib.util.spec_from_file_location('own_original_read_helpers',D/'read_independent_cohort_actual_bounded.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def code(c,py,s):
 si,so,se=c.exec_command(shlex.quote(py)+' -B -',timeout=35);si.write(s);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 report=R/'WAVE_FIRST_FINITE_FINAL_AND_ACTUAL_CANONICAL_EXIT_HANDOFF_COLLECTION.json';assert not report.exists();c=None
 try:
  c=m.t.connect();root='/mnt/mod4_linux_durable_20261013/'+N;start=time.monotonic()
  while True:
   state=code(c,m.t.PY,"from pathlib import Path;import json,psutil;R=Path("+repr(root)+");p=R/'OWNER_EXIT_ACTUAL.json';print(json.dumps(dict(exit=json.loads(p.read_bytes()) if p.exists() else None,owner_alive=psutil.pid_exists(466300))))")
   if state['exit'] and not state['owner_alive']:break
   assert time.monotonic()-start<240,'Only own final wait240s; no forced stop/retry'
   time.sleep(15)
  source=m.read(c,m.t.PY,root)
  budget=code(c,m.t.PY,"from pathlib import Path;import json,fcntl;B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(B.read_bytes());v=dict(active=b['active_segment'],authorized=b['authorized_training_seconds'],charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],segments=[x for x in b['completed_segments'] if x.get('owner_parent_pid')==466300]);v['locks']=[]\nfor p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):\n f=p.open('rb+');free=False\n try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)\n except BlockingIOError:pass\n f.close();v['locks'].append(dict(path=str(p),actual_fcntl_free=free))\nprint(json.dumps(v))")
  assert budget['active'] is None and len(budget['segments'])==1 and all(x['actual_fcntl_free'] for x in budget['locks'])
 finally:m.t.close(c)
 pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  target=m.read(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+N)
  assert not [x for x in target['actual_own_processes'] if any('expert_independent_worker_v3.py' in s or 'wave_episode_reviewed_finite_owner_node_v3.py' in s for s in x['cmdline'])]
  final=next(x['data'] for x in target['files'] if x['path'].endswith('/job3/run/FINAL.json'))
  out=D/'first_closed_expert_models/job3'/Path(final['path']).name;assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);part=out.with_suffix('.pt.partial');sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:sf.get(final['path'],str(part))
  finally:sf.close()
  assert part.stat().st_size==final['bytes'] and H(part)==final['SHA'];part.replace(out)
  report.write_text(json.dumps(dict(epoch=time.time(),source=source,target=target,actual_original_canonical=budget,final=final,local_model=str(out.resolve()),complete_twohost_SHA=True,no_new_training_window_or_budget_write=True),indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(report),final=final,budget=budget)),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('WAVE_FINAL_BOUND_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),read_only_no_restart=True),indent=2),encoding='utf8');raise
