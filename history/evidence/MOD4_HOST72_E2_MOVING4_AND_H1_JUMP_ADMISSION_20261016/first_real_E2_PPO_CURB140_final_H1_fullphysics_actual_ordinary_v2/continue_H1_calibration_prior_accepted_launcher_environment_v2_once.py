"""New isolated no-learning calibration after pre-physics launcher rejection.

Reuse the already used task launcher environment; never edit the failed scope.
"""
from pathlib import Path
import json,time,hashlib,importlib.util,shlex,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
s=importlib.util.spec_from_file_location('old_h1_transport',D/'deploy_H1_fullphysics_calibration_unused_scope_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
OLD=m.ROOT;NEW=OLD+'_launcher_environment_v2'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'H1_CALIBRATION_V2_NEW_UNUSED_SCOPE_DISPATCH_ACTUAL.json').exists()
 c0=json.loads((R/'H1_FULLPHYSICS_CALIBRATION_ACTUAL_BOUND_COLLECTION.json').read_bytes());assert not c0['actual_processes'] and not c0.get('complete_local_raw')
 assert any('EOF when reading a line' in x['value'].get('error','') for x in c0['errors'])
 old=(D/'h1_calibration_payload_v1/h1_calibration_finite_parent_v1.py').read_text()
 needle="XDG_DATA_HOME=str(B/'data'))";assert old.count(needle)==1
 new=old.replace(needle,"XDG_DATA_HOME=str(B/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')")
 p=D/'h1_calibration_parent_launcher_environment_v2.py';p.write_text(new,encoding='utf8');compile(new,str(p),'exec')
 put('H1_CALIBRATION_PREPHYSICS_LAUNCH_ENVIRONMENT_REJECTION_AND_V2_FIX_ACTUAL.json',dict(epoch=time.time(),old_scope=OLD,new_scope=NEW,old_error=c0['errors'],old_parent_final=next(x['value'] for x in c0['files'] if x['path'].endswith('/PARENT_FINAL.json')),old_physics_callbacks=0,old_raw_files=0,no_old_runtime_or_shared_source_modified=True,new_parent_change='Reuse OMNI_KIT_ACCEPT_EULA and ISAACSIM_ACCEPT_EULA values already used by actual successful job1 native launcher; isolated HOME previously lost those environment settings.',new_parent_SHA=m.hashlib.sha256(p.read_bytes()).hexdigest(),no_new_license_terms_or_system_configuration=True,worker_physics_actions_source_identical=True,no_PPO_or_canonical_write=True))
 pw=m.getpass.getpass('Host72 new H1 launcher-environment continuation password (hidden): ');c=m.paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(m.paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  receipt=m.code(c,r'''
from pathlib import Path
import json,sys,time,hashlib,shutil,psutil,subprocess
A=Path(sys.argv[1]);B=Path(sys.argv[2]);assert not B.exists() and B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2').resolve());ex=json.loads((A/'PARENT_EXIT_ACTUAL.json').read_bytes());assert ex['own_child_actual_out'];assert not json.loads((A/'PARENT_FINAL.json').read_bytes())['passed'];assert not (A/'output/VALID_PREFIX_INDEX_ACTUAL.json').exists()
for p in psutil.process_iter(['pid','cmdline']):
 if any(str(A) in z for z in p.info['cmdline'] or []):raise AssertionError(p.info)
g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>2000
B.mkdir();shutil.copytree(A/'job1',B/'job1');shutil.copytree(A/'lib',B/'lib')
manifest=json.loads((A/'H1_CALIBRATION_OVERLAY_MANIFEST.json').read_bytes())
for row in manifest['files']:
 rel=row['relative'];src=A/rel;assert src.stat().st_size==row['bytes'] and hashlib.sha256(src.read_bytes()).hexdigest()==row['SHA']
 if rel=='h1_calibration_finite_parent_v1.py':continue
 dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
print(json.dumps(dict(epoch=time.time(),old_parent_child_actual_out=True,new_root=str(B),actual_GPU1_resource=line,old_all_manifest_SHA_exact=True,new_reused_worker_source_SHA=hashlib.sha256((B/'h1_fullphysics_calibration_worker_v1.py').read_bytes()).hexdigest(),new_scope_physics_not_yet_run=True)))
''',OLD,NEW);put('H1_CALIBRATION_V2_SOURCE_RESOURCE_AND_OLD_EXIT_ACTUAL.json',receipt)
  sf=c.open_sftp();sf.put(str(p),NEW+'/h1_calibration_parent_launcher_environment_v2.py');sf.close();sf=None
  verified=m.code(c,"from pathlib import Path;import hashlib,json,sys; p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[2];print(json.dumps(dict(parent_SHA=sys.argv[2],actual_twohost_SHA_exact=True)))",NEW+'/h1_calibration_parent_launcher_environment_v2.py',hashlib.sha256(p.read_bytes()).hexdigest());put('H1_CALIBRATION_V2_PARENT_TARGET_SHA_ACTUAL.json',verified)
  si,so,se=c.exec_command(shlex.quote(m.PY)+' -u -B '+shlex.quote(NEW+'/h1_calibration_parent_launcher_environment_v2.py'),timeout=35);si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();dispatch=json.loads(raw)
  actual=m.code(c,"import psutil,json,sys,time;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(dispatch['detached_pid']));put('H1_CALIBRATION_V2_NEW_UNUSED_SCOPE_DISPATCH_ACTUAL.json',dict(epoch=time.time(),dispatch=dispatch,actual_parent=actual,calibration_only_not_actor_or_PPO=True,original_failure_retained=True));print(json.dumps(dict(dispatch=dispatch,actual_parent=actual)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_CALIBRATION_V2_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_launch_replay=True));raise
