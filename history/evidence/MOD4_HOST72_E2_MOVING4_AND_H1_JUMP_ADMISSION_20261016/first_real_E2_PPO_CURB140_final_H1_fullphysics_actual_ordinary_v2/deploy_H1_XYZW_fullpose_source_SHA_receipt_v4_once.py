"""New observer-correction scope, original raw and dynamics never replaced."""
from pathlib import Path
import importlib.util,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'h1_calibration_XYZW_fullpose_payload_v4';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;OLD=T+'/h1_flat_fullphysics_calibration_v1_launcher_environment_v2';ROOT=T+'/h1_flat_XYZW_fullpose_calibration_v3'
s=importlib.util.spec_from_file_location('closed_scope_pure_helpers',D/'deploy_H1_fullphysics_calibration_unused_scope_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'H1_XYZW_FULLPOSE_V4_DISPATCH_ACTUAL.json').exists();manifest=json.loads((P/'NEW_H1_XYZW_OBSERVER_MANIFEST.json').read_bytes());pw=m.getpass.getpass('Host72 new XYZW fullpose diagnostic password (hidden): ');c=m.paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(m.paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v=m.code(c,r'''
from pathlib import Path
import sys,time,json,shutil,psutil,hashlib,subprocess
A=Path(sys.argv[1]);B=Path(sys.argv[2]);assert not B.exists() and B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2').resolve());assert json.loads((A/'PARENT_FINAL.json').read_bytes())['passed'] and json.loads((A/'PARENT_EXIT_ACTUAL.json').read_bytes())['own_child_actual_out']
for name in ('PARENT_IDENTITY.json','WORKER_STARTED_ACTUAL.json'):
 v=json.loads((A/name).read_bytes())
 if psutil.pid_exists(v['pid']):
  p=psutil.Process(v['pid']);assert abs(p.create_time()-v['creation'])>.01 or p.cmdline()!=v['argv']
math=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/math.py');assert hashlib.sha256(math.read_bytes()).hexdigest()=='4ae6fe19d9b18c2747bf6546dc72f75cfe497ee2ba6046e95fabbeb33d958d33'
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>2000
B.mkdir();shutil.copytree(A/'job1',B/'job1');shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'h1_flat_jump_evidence_reward_cpu_v1.py',B/'h1_flat_jump_evidence_reward_cpu_v1.py')
print(json.dumps(dict(epoch=time.time(),original_calibration_parent_child_actual_out=True,new_root=str(B),actual_GPU1_resource=line,SDK_math_actual_SHA_exact=True,source_E0_SHA=hashlib.sha256((B/'job1/source/E0_full_source.pt').read_bytes()).hexdigest(),no_old_data_or_runtime_mutated=True)))
''',OLD,ROOT);put('H1_XYZW_V4_NEW_SOURCE_RESOURCE_OLD_EXIT_ACTUAL.json',v)
  sf=c.open_sftp()
  for row in manifest['files']:sf.put(str(P/row['relative']),ROOT+'/'+row['relative'])
  sf.put(str(P/'NEW_H1_XYZW_OBSERVER_MANIFEST.json'),ROOT+'/NEW_H1_XYZW_OBSERVER_MANIFEST.json');sf.close();sf=None
  verified=m.code(c,"from pathlib import Path;import json,hashlib,sys;B=Path(sys.argv[1]);m=json.loads((B/'NEW_H1_XYZW_OBSERVER_MANIFEST.json').read_bytes())\nfor r in m['files']:\n p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']\nprint(json.dumps(dict(new_files=len(m['files']),all_target_SHA_exact=True)))",ROOT);put('H1_XYZW_V4_TARGET_OVERLAY_SHA_ACTUAL.json',verified)
  si,so,se=c.exec_command(shlex.quote(m.PY)+' -u -B '+shlex.quote(ROOT+'/h1_calibration_parent_launcher_environment_v3.py'),timeout=35);si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();dispatch=json.loads(raw)
  actual=m.code(c,"import psutil,sys,time,json;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(dispatch['detached_pid']));put('H1_XYZW_FULLPOSE_V4_DISPATCH_ACTUAL.json',dict(epoch=time.time(),dispatch=dispatch,actual_parent=actual,source_SHA=v['source_E0_SHA'],new_callback_bodypose_and_XYZW_observer_not_original_physics_change=True,controls=224,callbacks=896,no_PPO_or_budget=True));print(json.dumps(dict(dispatch=dispatch,actual_parent=actual,no_learning=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_XYZW_V4_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_scope_replay=True));raise
