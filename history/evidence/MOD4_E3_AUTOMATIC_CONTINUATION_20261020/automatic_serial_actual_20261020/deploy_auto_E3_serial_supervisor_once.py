"""Deploy one explicitly authorized serial E3 parent, with fresh guards and exact reviewed source bytes."""
from pathlib import Path
import getpass,hashlib,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019'));import deploy_available_E2_E3_original_writer_V2_once as d
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
INSTALL=r'''
from pathlib import Path
import sys,json,os,shutil,socket,time,psutil,fcntl,subprocess,hashlib
cfg=json.loads(sys.argv[1]);B=Path('/home/lc01/Zonglin Li/zonglin2');root=Path(cfg['remote_root']);base=root.parent;lease=B/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json';assert root==B/'tasks/E3auto_2010v26/controller' and base.resolve().is_relative_to(B.resolve()) and not base.exists() and not lease.exists();assert shutil.which('ssh-keyscan');assert (B/'state/MOD4_SINGLE_E3_OFFLINE_COST_PENDING_20261020.json').is_file();owner=Path(cfg['initial_owner']);node=Path(cfg['initial_node']);read=lambda p:json.loads(p.read_bytes());co=read(owner/'COHORT_FINAL.json');oe=read(owner/'OWNER_EXIT_ACTUAL.json');ne=read(node/'NODE_EXIT_ACTUAL.json');nr=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];assert oe['pending_cost_record_complete'] and oe['original_cost_settled'] is False and co['pending_cost']['cost']['actual_production_seconds']==cfg['prior_single_E3_pending_seconds'];assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and nr['returncode']==0 and not nr['errors'] and nr['final']['passed'] and nr['final']['final']['SHA']==cfg['initial_source']['SHA'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(r)+'/') for r in (owner,node) for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));locks=[]
for path in [Path(cfg['initial_spec']['private_lock']),B/'state/finite_environment_validation.lock']:
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_fcntl_free=True))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();uuid=cfg['initial_spec']['GPU_UUID'];gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if uuid in x);disk=shutil.disk_usage(B);ram=psutil.virtual_memory().available;assert not any(uuid in x for x in compute.splitlines()) and int(gpu.split(',')[-1])>7000 and disk.free>25*1024**3 and ram>8*1024**3
with socket.socket() as s:s.bind(('127.0.0.1',29754))
p=subprocess.run(['ssh-keyscan','-T','5','-t','ed25519',cfg['original_account_host']],capture_output=True,text=True,timeout=20);keys={x.split()[2] for x in p.stdout.splitlines() if len(x.split())>=3 and x.split()[1]=='ssh-ed25519'};assert keys=={cfg['known_Windows_host_key']};base.mkdir();root.mkdir();print(json.dumps(dict(epoch=time.time(),root=str(root),fresh_unused_root_created=True,previous_owner_node_all_children_actual_out=True,old_pending_reservation_retained=True,series_lease_not_yet_created=True,known_Windows_original_canonical_offline=True,GPU_line=gpu,compute_snapshot=compute,RAM_available=ram,disk_free=disk.free,locks=locks,no_original_canonical_or_two_locks_opened=True,no_GO_yet=True)))
'''
def main():
 review=json.loads((R/'AUTO_E3_SERIAL_CONTROLLER_AND_DYNAMIC_SOURCE_CPU_ACTUAL.json').read_bytes());assert review['passed'];expected=review['reviewed_files'];assert all(H(B/n)==sha for n,sha in expected.items());cfg=json.loads((B/'SERIES_CONFIG_NO_SECRET.json').read_bytes());assert 'token' not in cfg;put('AUTO_E3_SERIAL_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_training_transport=True,reviewed_files=expected));pw=getpass.getpass('72 automatic E3 serial deploy (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);install=d.a.code(c,d.a.PY,INSTALL,json.dumps(cfg),timeout=90);put('AUTO_E3_FRESH_INSTALL_RESOURCES_AND_UNUSED_ROOT_ACTUAL.json',install);root=cfg['remote_root'];sf=c.open_sftp()
  try:
   for name in expected:sf.put(str(B/name),root+'/'+name)
  finally:sf.close()
  verify=d.a.code(c,d.a.PY,"from pathlib import Path;import sys,json,hashlib,ast;B=Path(sys.argv[1]);expected=json.loads(sys.argv[2]);actual={n:hashlib.sha256((B/n).read_bytes()).hexdigest() for n in expected};assert actual==expected;[ast.parse((B/n).read_text('utf8')) for n in expected if n.endswith('.py')];print(json.dumps(dict(actual_SHA=actual,exact_reviewed_bytes=True,no_GO_yet=True)))",root,json.dumps(expected),timeout=60);put('AUTO_E3_REMOTE_CONTROLLER_EXACT_SHA_ACTUAL.json',verify);runtime=dict(cfg,role='supervisor');parent=d.old.launch(d.a.code,c,d.a.PY,root,'auto_E3_serial_supervisor_v1.py',runtime);runtime.clear();result=dict(epoch=time.time(),supervisor=parent,root=root,series_id=cfg['series_id'],authority=cfg['authority'],source=cfg['initial_source'],reviewed_files=expected,pending_cost_not_canonical_settled=True,original_canonical_not_opened=True,no_H1_E2_GO=True,not_actual_PPO_claim_before_metadata=True);put('AUTO_E3_SERIAL_SUPERVISOR_DEPLOYED_ACTUAL.json',result);print(json.dumps(dict(serial_parent_detached=parent,initial_source_SHA=cfg['initial_source']['SHA'])),flush=True)
 finally:
  pw=None
  if c:c.close()
 put('AUTO_E3_SERIAL_DEPLOY_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,no_current_transport_hold=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('AUTO_E3_SERIAL_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_partial_do_not_replay=True));raise
