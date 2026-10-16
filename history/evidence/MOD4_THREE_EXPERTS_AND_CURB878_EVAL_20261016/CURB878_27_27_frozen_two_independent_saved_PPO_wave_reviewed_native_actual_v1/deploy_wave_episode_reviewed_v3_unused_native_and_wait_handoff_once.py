"""Reuse existing exact bytes on72, upload only new overlay; old runtime never modified."""
from pathlib import Path
import getpass,hashlib,importlib.util,json,paramiko,secrets,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'wave_episode_reviewed_payload_v3';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
S='/mnt/mod4_linux_durable_20261013/'+D.name+'/wave_episode_reviewed_v3';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/wave_episode_reviewed_v3';OLD='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/train/job2'
def code(c,py,text,*args):
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+' '.join(shlex.quote(x) for x in args),timeout=75);si.write(text);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,(rc,err.decode(errors='replace'),raw.decode(errors='replace')[-3000:]);return json.loads(raw)
def launch(c,py,root,role,config):
 si,so,se=c.exec_command(shlex.quote(py)+' -u -B '+shlex.quote(root+'/wave_episode_reviewed_finite_owner_node_v3.py')+' --role '+role,timeout=30);si.write(json.dumps(config)+'\n');si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def put(c,root,files):
 sf=c.open_sftp()
 try:
  for rel in files:
   src=P/rel;dst=root+'/'+rel
   try:sf.stat(dst);raise AssertionError('New overlay destination must be unused: '+dst)
   except FileNotFoundError:pass
   sf.put(str(src),dst)
 finally:sf.close()
def main():
 receipt=R/'WAVE_V3_UNUSED_CONTINUATION_DISPATCH_ACTUAL.json';assert not receipt.exists();assert (R/'WAVE_OLD_EPISODE_AUDIT_CPU_REPRODUCED_AND_EXISTING_REVIEWED_REPAIR_ACTUAL.json').exists();manifest=json.loads((D/'WAVE_EPISODE_REVIEWED_UNUSED_V3_PAYLOAD_MANIFEST.json').read_bytes());newfiles=['expert_independent_worker_v3.py','independent_expert_axis_v1.py','verify_independent_native_cpu_gate_v1.py','wave_episode_reviewed_finite_owner_node_v3.py','lib/zonglin2_app_launcher.py','job3/TASK.json','job3/runtime/isaac/mod4/train_independent_wave_episode_reviewed_v3.py'];c=None;rows=[]
 try:
  c=t.connect();v=code(c,t.PY,"from pathlib import Path;import json,sys;B=Path(sys.argv[1]);assert not B.exists();B.mkdir();print(json.dumps(dict(root=str(B),new_unused=True)))",S);rows.append(v);put(c,S,['wave_episode_reviewed_finite_owner_node_v3.py'])
 finally:t.close(c)
 pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v=code(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',r'''
from pathlib import Path
import json,sys,shutil,psutil,subprocess
B=Path(sys.argv[1]);old=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.resolve().is_relative_to(owned) and not B.exists();assert not psutil.pid_exists(3097639);assert not (old/'run/NATIVE120_COMPLETE.json').exists();assert json.loads((old/'WORKER_EXIT_ACTUAL.json').read_bytes())['returncode']==0
g=subprocess.run(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout;line=next(x for x in g.splitlines() if '16828f91-2b45-b646-8dc0-9481138e2842' in x);assert int(line.split(',')[1])>9000
B.mkdir();j=B/'job3';j.mkdir()
for name in ('runtime','source','assets'):shutil.copytree(old/name,j/name)
shutil.copy2(old/'original_run_manifest.json',j/'original_run_manifest.json');(B/'lib').mkdir();print(json.dumps(dict(root=str(B),old_job2_actual_absent_native_not_passed=True,old_payload_reused_by_copy_not_reupload=True,GPU_actual=g,no_delete_or_other_process_action=True)))
''',T,OLD);rows.append(v);put(c,T,newfiles)
  verify="from pathlib import Path;import json,hashlib,sys;B=Path(sys.argv[1]);m=json.loads(sys.argv[2]);rows=m['files'];actual=[]\nfor r in rows:\n p=B/r['path'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['path']\nprint(json.dumps(dict(root=str(B),files=len(rows),all_manifest_size_SHA_exact=True,only_original_copied_payload_and_explicit_new_overlay=True)))"
  v=code(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',verify,T,json.dumps(manifest));rows.append(v)
 finally:pw=None;c.close()
 # Capabilities are delivered only through inherited stdin memory; never persisted or printed.
 config=dict(token=secrets.token_hex(32),run_id='wave_episode_reviewed_v3_'+str(time.time_ns()));c=None
 try:c=t.connect();rows.append(launch(c,t.PY,S,'owner',config))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password for detached own node (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';rows.append(launch(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',T,'node72',config))
 finally:pw=None;config.clear();c.close()
 receipt.write_text(json.dumps(dict(epoch=time.time(),rows=rows,new_unused_wave_scope=True,native_then_allrow_CPU_required=True,learning_waits_existing_original_owner_exit_and_two_fcntl_release=True,no_old_worker_restart_or_runtime_hotpatch=True,no_PPO_positive_inferred=True),indent=2),encoding='utf8');print(json.dumps(dict(receipt=str(receipt),rows=rows)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('WAVE_V3_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),do_not_blindly_repeat_newroot_or_launch=True),indent=2),encoding='utf8');raise
