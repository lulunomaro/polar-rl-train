"""One authenticated bounded handoff after the requested original complete-save boundary."""
from pathlib import Path
import getpass,hashlib,json,os,shlex,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'controller50'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
INSTALL=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,shutil,subprocess,os
old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/E3auto_2010v26/controller');owned=Path('/home/lc01/Zonglin Li/zonglin2');root=owned/'tasks/E3auto50_2010v27/controller';read=lambda p:json.loads(p.read_bytes());until=time.monotonic()+880
assert (old/'STOP_SERIES_AFTER_CURRENT.json').is_file() and not root.parent.exists() and not (owned/'state/MOD4_E3_AUTO50_PENDING_SERIES_20261020.json').exists()
while not (old/'SERIES_EXIT_ACTUAL.json').is_file():
 assert time.monotonic()<until,'Original series has not actually exited; no installation or GO';time.sleep(3)
exitrow=read(old/'SERIES_EXIT_ACTUAL.json');current=read(old/'SERIES_CURRENT.json');state=read(old/'SERIES_STATE.json');assert exitrow['status']==current['status']=='requested_stop_at_boundary' and current['active'] is None
own=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(old.parent)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own;cfg=read(old/'SERIES_CONFIG_NO_SECRET.json');rows=state['completed'];assert len(rows)==len({x['run_id'] for x in rows});last=rows[-1];node=Path(last['node_root']);owner=Path(last['owner_root']);proof=read(Path(last['whole_CPU_proof']));assert proof['passed'] and proof['final']['SHA']==last['final']['SHA'] and proof['whole_tensor_counts']==[173,96]
assert read(owner/'OWNER_EXIT_ACTUAL.json')['pending_cost_record_complete'] and read(node/'NODE_EXIT_ACTUAL.json')['actual_all_own_children_waited'];locks=[]
for path in [owned/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json',owned/'state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',owned/'state/finite_environment_validation.lock']:
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(path))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();uuid=cfg['initial_spec']['GPU_UUID'];gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if uuid in x);assert not any(uuid in x for x in compute.splitlines()) and int(gpu.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
prior=sum(x['actual_pending_seconds'] for x in rows);available=cfg['last_settled_remaining_seconds']-cfg['legacy_unsettled_reserve_seconds']-cfg['original_safety_reserve_seconds']-cfg['prior_single_E3_pending_seconds']-prior;assert available>=3900
cfg.update(series_id='AUTO_E3_POLICY50_20261020_'+str(time.time_ns()),remote_root=str(root),initial_source=last['final'],initial_node=str(node),initial_owner=str(owner),initial_spec=read(node.parent/'SPEC_NO_TOKEN.json'),previous_100hz_controller=str(old),prior_100hz_series_pending_seconds=prior)
cfg['authority']=dict(cfg['authority'],policy_clock_50Hz_authorized=True,human_policy_clock_instruction='换成50hz继续训吧',policy_clock_only_physics_unchanged=True,temporal_gamma=.9801,temporal_lam=.9025)
root.mkdir(parents=True);(root/'SERIES_CONFIG_NO_SECRET.json').write_text(json.dumps(cfg,indent=2));(root/'INITIAL_SOURCE_WHOLE_CPU_PROOF.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(dict(epoch=time.time(),root=str(root),cfg=cfg,previous_closed_windows=rows,original_series_actual_exit=exitrow,original_all_own_processes_out=True,original_series_and_GPU_shared_locks_free=locks,compute_snapshot=compute,GPU_line=gpu,budget_guard_available_snapshot=available,canonical_not_opened=True,no_GO_yet=True)))
'''
def code(c,script,*args,timeout=60):
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(script)+' '+' '.join(shlex.quote(x) for x in args);_,out,err=c.exec_command(cmd,timeout=timeout);raw=out.read().decode();error=err.read().decode();rc=out.channel.recv_exit_status()
 if rc:raise RuntimeError(json.dumps(dict(returncode=rc,stdout=raw,stderr=error)))
 return json.loads(raw)
def main():
 review=json.loads((R/'POLICY50_SERIAL_V2_SOURCE_PREPARED_CPU_ACTUAL.json').read_bytes());factory=json.loads((R/'POLICY50_REAL_FACTORY_SOURCE_BINDING_CPU_ACTUAL.json').read_bytes());assert review['passed_source_CPU'] and factory['passed'];assert all(H(C/n)==sha for n,sha in review['controller_files'].items())
 put('POLICY50_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,one_finite_transport=True));pw=getpass.getpass('72 saved-boundary 50Hz handoff (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,look_for_keys=False,allow_agent=False,timeout=15,auth_timeout=20,banner_timeout=20);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';c.get_transport().set_keepalive(15)
  install=code(c,INSTALL,timeout=900);put('POLICY50_ORIGINAL_SERIES_CLOSED_RESOURCE_HANDOFF_ACTUAL.json',install);root=install['root'];sf=c.open_sftp();sf.get_channel().settimeout(90);expected={}
  try:
   made={root}
   for p in sorted(C.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(C).as_posix();remote=root+'/'+rel;parts=rel.split('/')[:-1];folder=root
    for part in parts:
     folder+='/'+part
     if folder not in made:sf.mkdir(folder);made.add(folder)
    sf.put(str(p),remote);expected[rel]=H(p)
  finally:sf.close()
  verify=code(c,"from pathlib import Path;import sys,json,hashlib,ast;B=Path(sys.argv[1]);x=json.loads(sys.argv[2]);actual={n:hashlib.sha256((B/n).read_bytes()).hexdigest() for n in x};assert actual==x;[ast.parse((B/n).read_text('utf8')) for n in x if n.endswith('.py')];print(json.dumps(dict(exact_SHA=actual,no_GO_yet=True)))",root,json.dumps(expected));put('POLICY50_REMOTE_CONTROLLER_OVERLAY_EXACT_SHA_ACTUAL.json',verify)
  launch="import subprocess,json,sys;from pathlib import Path;B=Path(sys.argv[1]);cfg=json.loads((B/'SERIES_CONFIG_NO_SECRET.json').read_bytes());p=subprocess.run(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'auto_E3_serial_supervisor_v1.py')],input=json.dumps(cfg)+'\\n',text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)"
  # json stdin must end with a real newline; no token or password is stored.
  launch=launch.replace("+'\\n'","+'\n'") if False else launch
  dispatched=code(c,launch,root,timeout=45);put('POLICY50_SERIAL_PARENT_DEPLOYED_ACTUAL.json',dict(epoch=time.time(),supervisor=dispatched,root=root,series_id=install['cfg']['series_id'],initial_source=install['cfg']['initial_source'],previous_100hz_pending_seconds=install['cfg']['prior_100hz_series_pending_seconds'],not_actual_GO_or_PPO_claim=True));print(json.dumps(dict(parent_detached=dispatched,actual_GO_not_yet_verified=True)),flush=True)
 finally:pw=None;c.close()
 put('POLICY50_DEPLOY_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('POLICY50_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once_or_partial_roots=True));raise
