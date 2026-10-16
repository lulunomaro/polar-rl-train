"""Unused ownGPU1 scope after old native natural exit; bounded calibration, no PPO."""
from pathlib import Path
import hashlib,json,getpass,paramiko,shlex,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'h1_calibration_payload_v1';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;ROOT=T+'/h1_flat_fullphysics_calibration_v1';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def code(c,text,*args):
 si,so,se=c.exec_command(shlex.quote(PY)+' -B - '+' '.join(shlex.quote(a) for a in args),timeout=90);si.write(text);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,dict(error=err.decode(errors='replace'),output=raw.decode(errors='replace')[-2000:]);return json.loads(raw)
def main():
 assert not (R/'H1_CALIBRATION_ACTUAL_UNUSED_SCOPE_DISPATCH.json').exists();assert json.loads((R/'H1_EXTERNAL_REQUEST_SELECTED_RESET_ACTUAL_AST_CPU_PASSED.json').read_bytes())['passed_CPU_only'];m=json.loads((P/'H1_CALIBRATION_OVERLAY_MANIFEST.json').read_bytes());pw=getpass.getpass('Host72 H1 no-learning calibration password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  created=code(c,r'''
from pathlib import Path
import json,sys,shutil,psutil,subprocess,time
B=Path(sys.argv[1]);old=Path(sys.argv[2])/'job1';owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.resolve().is_relative_to(owned) and not B.exists();cpu=json.loads((old/'native/NATIVE_ALL_ROWS_CPU_ADMITTED.json').read_bytes());ex=json.loads((old/'native_WORKER_EXIT_ACTUAL.json').read_bytes());assert cpu['passed'] and ex['returncode']==0
if psutil.pid_exists(ex['pid']):assert str(old.parent/'e2_h1_phase_worker_v1.py') not in psutil.Process(ex['pid']).cmdline()
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>2000
B.mkdir();j=B/'job1';j.mkdir()
for name in ('runtime','source','assets'):shutil.copytree(old/name,j/name)
for name in ('original_run_manifest.json','TASK.json'):shutil.copy2(old/name,j/name)
(B/'lib').mkdir();shutil.copy2(old.parent/'lib/zonglin2_app_launcher.py',B/'lib/zonglin2_app_launcher.py')
print(json.dumps(dict(epoch=time.time(),new_root=str(B),oldnative_actualclosed=True,actual_GPU1_resource_snapshot=line,static_owned_copy_only=True,new_native80_calibration_no_PPO=True)))
''',ROOT,T);put('H1_CALIBRATION_ACTUAL_NEW_ROOT_AND_GPU_RESOURCE.json',created)
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  for row in m['files']:sf.put(str(P/row['relative']),ROOT+'/'+row['relative'])
  sf.put(str(P/'H1_CALIBRATION_OVERLAY_MANIFEST.json'),ROOT+'/H1_CALIBRATION_OVERLAY_MANIFEST.json');sf.close();sf=None
  checked=code(c,"from pathlib import Path;import json,hashlib,sys,time;B=Path(sys.argv[1]);m=json.loads((B/'H1_CALIBRATION_OVERLAY_MANIFEST.json').read_bytes());rows=m['files']\nfor r in rows:\n p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']\nprint(json.dumps(dict(epoch=time.time(),new_overlays=len(rows),all_SHA_exact=True,source_SHA=hashlib.sha256((B/'job1/source/E0_full_source.pt').read_bytes()).hexdigest(),no_GPU_probe_repeated=True)))",ROOT);put('H1_CALIBRATION_TARGET_OVERLAY_SOURCE_SHA_ACTUAL.json',checked)
  si,so,se=c.exec_command(shlex.quote(PY)+' -u -B '+shlex.quote(ROOT+'/h1_calibration_finite_parent_v1.py'),timeout=35);si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();dispatch=json.loads(raw)
  actual=code(c,"import psutil,json,sys,time;pid=int(sys.argv[1]);p=psutil.Process(pid);print(json.dumps(dict(epoch=time.time(),pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(dispatch['detached_pid']));put('H1_CALIBRATION_ACTUAL_UNUSED_SCOPE_DISPATCH.json',dict(epoch=time.time(),dispatch=dispatch,actual_parent=actual,source_SHA=checked['source_SHA'],scripted_motor_calibration_only_not_actor_or_PPO=True,optimizer_updates=0,canonical_write=False,actual_flight_not_yet_observed=True));print(json.dumps(dict(dispatch=dispatch,actual_parent=actual,no_jump_PPO_or_skill_credit=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_CALIBRATION_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_actual_before_any_continuation_no_oldlaunch_replay=True));raise
