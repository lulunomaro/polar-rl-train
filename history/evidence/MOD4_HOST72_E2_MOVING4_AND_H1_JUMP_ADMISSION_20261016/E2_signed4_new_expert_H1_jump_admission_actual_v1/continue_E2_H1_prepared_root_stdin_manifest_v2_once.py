"""One human-authorized E2 learning chain and H1 native-only chain; owned72 root only."""
from pathlib import Path
import hashlib,json,getpass,paramiko,sys,shlex,secrets,time,traceback,shutil,os,subprocess
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload';S='/mnt/mod4_linux_durable_20261013/'+D.name;T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train/job1';PY72='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def code(c,py,text,*args):
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+' '.join(shlex.quote(x) for x in args),timeout=120);si.write(text);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,dict(returncode=rc,stderr=err.decode(errors='replace'),stdout=raw.decode(errors='replace')[-4000:]);return json.loads(raw)
def launch(c,py,root,script,config):
 si,so,se=c.exec_command(shlex.quote(py)+' -u -B '+shlex.quote(root+'/'+script),timeout=35);si.write(json.dumps(config)+'\n');si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def connect72(password):
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());c.connect('10.24.0.72',username='lc01',password=password,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';return c
def main():
 assert not (R/'E2_H1_ACTUAL_DURABLE_DISPATCH.json').exists();assert json.loads((R/'E2_EXACT_COMMAND_DRAW_AXIS_AND_NATIVE_IMPULSE_NODE_BOUNDARY_CPU_V5_ACTUAL.json').read_bytes())['passed_CPU_only']
 for name in ('e2_h1_phase_worker_v1.py','verify_e2_h1_native_CPU_v1.py','e2_h1_node72_finite_v1.py','e2_source_original_canonical_owner_v1.py'):shutil.copyfile(D/name,Q/name)
 m=dict(epoch=time.time(),files=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='PAYLOAD_MANIFEST.json' and '__pycache__' not in p.parts]);(Q/'PAYLOAD_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 put('E2_H1_FINITE_DISPATCH_STARTED_ACTUAL_V2.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),one_sequential_transport_owner=True,new_scope_only=True,no_other_process_or_system_changes=True))
 pw=getpass.getpass('Host72 password (hidden, not saved): ');c=sf=None
 try:
  c=connect72(pw)
  v=code(c,PY72,"from pathlib import Path;import json,sys,psutil,time;B=Path(sys.argv[1]);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.exists() and B.resolve().is_relative_to(owned);assert not (B/'NODE_IDENTITY.json').exists();print(json.dumps(dict(epoch=time.time(),existing_prepared_root_reused=True,root=str(B),no_executor_or_GPU_dispatched_by_V1=True)))",T);put('TARGET72_EXISTING_PREPARED_ROOT_NO_EXECUTOR_ACTUAL_V2.json',v)
  sf=c.open_sftp();assert not any(x.filename=='PAYLOAD_MANIFEST.json' for x in sf.listdir_attr(T));sf.put(str(Q/'PAYLOAD_MANIFEST.json'),T+'/PAYLOAD_MANIFEST.json');sf.close();sf=None
  expected=m['files'];inventory=code(c,PY72,"from pathlib import Path;import json,hashlib,sys;B=Path(sys.argv[1]);rows=json.loads((B/'PAYLOAD_MANIFEST.json').read_bytes())['files'];need=[]\nfor r in rows:\n p=B/r['relative']\n if not p.exists() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:need.append(r['relative'])\nprint(json.dumps(dict(need_upload=need)))",T)
  need=inventory['need_upload'];assert all(Q/x!=Q/'PAYLOAD_MANIFEST.json' for x in need);sf=c.open_sftp();sf.get_channel().settimeout(120)
  for rel in need:
   src=Q/rel;assert src.is_file();sf.put(str(src),T+'/'+rel)
  sf.put(str(Q/'PAYLOAD_MANIFEST.json'),T+'/PAYLOAD_MANIFEST.json');sf.close();sf=None
  result=code(c,PY72,r'''
from pathlib import Path
import hashlib,json,sys,time,os
B=Path(sys.argv[1]);m=json.loads((B/'PAYLOAD_MANIFEST.json').read_bytes())
for r in m['files']:
 p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['relative']
print(json.dumps(dict(epoch=time.time(),files=len(m['files']),all_target_bytes_SHA_exact=True,source_E0_SHA=hashlib.sha256((B/'job0/source/E0_full_source.pt').read_bytes()).hexdigest(),GPU_or_PPO_not_yet_passed=True)))
''',T);put('TARGET72_ALL845_SOURCE_AND_OVERLAY_SHA_ACTUAL.json',result)
 finally:
  if sf:sf.close()
  if c:c.close()
 c=sf=None
 try:
  c=t.connect();v=code(c,t.PY,"from pathlib import Path;import json,time,sys;B=Path(sys.argv[1]);assert not B.exists();B.mkdir();print(json.dumps(dict(epoch=time.time(),new_source_root=str(B),canonical_not_modified=True)))",S);put('SOURCE210_NEW_FINITE_OWNER_ROOT_ACTUAL.json',v);sf=c.open_sftp();sf.put(str(Q/'e2_source_original_canonical_owner_v1.py'),S+'/e2_source_original_canonical_owner_v1.py');sf.close();sf=None
  config=dict(token=secrets.token_hex(32),run_id='E2_H1_'+str(time.time_ns()),target_root=T);a=launch(c,t.PY,S,'e2_source_original_canonical_owner_v1.py',config);put('SOURCE210_FINITE_OWNER_LAUNCH_ACTUAL.json',a)
 finally:
  if sf:sf.close()
  t.close(c)
 c=None
 try:
  c=connect72(pw);pw=None;b=launch(c,PY72,T,'e2_h1_node72_finite_v1.py',config);put('TARGET72_FINITE_NODE_LAUNCH_ACTUAL.json',b)
  actual=code(c,PY72,"from pathlib import Path;import json,time,sys,psutil;B=Path(sys.argv[1]);rows=[]\nfor p in psutil.process_iter(['pid','create_time','cmdline','cwd']):\n try:\n  if any(str(B) in z for z in p.info['cmdline'] or []) and any('e2_h1_node72_finite_v1.py' in z or 'e2_h1_phase_worker_v1.py' in z for z in p.info['cmdline'] or []):rows.append(p.info)\n except psutil.Error:pass\nprint(json.dumps(dict(epoch=time.time(),actual_processes=rows,root=str(B))))",T)
 finally:pw=None;config.clear();c.close()
 put('E2_H1_ACTUAL_DURABLE_DISPATCH.json',dict(epoch=time.time(),source_owner=a,node72=b,actual_target=actual,E2_native_then_CPU_then_original_CURB_natural_lock_handoff_then128x2_20kx4_fresh_production=True,H1_GPU1_native80_only_no_PPO_or_airborne_reset=True,original_E0_source_and_budget_protected=True,no_PPO_positive_inferred=True));print(json.dumps(dict(source_owner=a,node72=b,actual_target=actual,notyet_E2_or_jump_PPO_pass=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('E2_H1_DEPLOY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_mutation_read_actual_before_any_continuation=True,no_blind_rerun=True));raise
