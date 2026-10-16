"""Use the free sourceGPU for a new source/backend H1 admission, never PPO or accounting."""
from pathlib import Path
import sys,os,time,json,traceback
N=Path(__file__).resolve().parent;P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';R=N/'reports';Q=N/'h1_closed25_source210_nativeonly_payload';ROOT='/mnt/mod4_linux_durable_20261013/H125_1710n1'
sys.path.insert(0,str(P));from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import code,H,t
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 audit=json.loads((R/'H1_ALL25_V2_CORRECTED_CPU_ACTUAL_COMPLETE_OR_ERROR.json').read_bytes());assert audit['actual_CPU_waited_returncode']==0;proof=next(r['value'] for r in audit['files'] if r['path'].endswith('/ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json'));assert proof['passed_integrity_CPU'] and proof['all_policy_rows']==12000000 and proof['candidate_takeoff_landing_recovery_events']==[0,0,0];prep=json.loads((R/'H1_CLOSED25_SOURCE210_NATIVE_ONLY_FULL_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());tar=Path(prep['tar']['path']);assert H(tar)==prep['tar']['SHA'];put('H1_SOURCE210_NATIVE_ONLY_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,no_PPO_canonical_write_or_new_owner=True));c=sf=None
 try:
  c=t.connect();v=code(c,t.PY,r'''
from pathlib import Path
import sys,os,json,time,psutil,shutil,subprocess,fcntl
B=Path(sys.argv[1]);owned=Path('/mnt/mod4_linux_durable_20261013').resolve();assert B.parent.resolve()==owned and not B.exists();old=owned/'C275_1610v2';assert json.loads((old/'PARENT_FINAL.json').read_bytes())['passed'] and json.loads((old/'PARENT_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];identity=json.loads((old/'PARENT_IDENTITY.json').read_bytes())
if psutil.pid_exists(identity['pid']):
 p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
computes=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not computes.strip(),computes;gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if '937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=json.loads(C.read_bytes());a=canonical['active_segment'];assert canonical['authorized_training_seconds']==1188000 and len(canonical['budget_extensions'])==7
if a is not None:
 assert a['owner_parent_pid']==594718;p=psutil.Process(a['owner_parent_pid']);assert any(x=='/mnt/mod4_linux_durable_20261013/N72_1710v2/two72_native_then_original_owner_handoff_v2.py' for x in p.cmdline())
B.mkdir();print(json.dumps(dict(epoch=time.time(),new_owned_root=str(B),old_CURB275_actual_FINAL_all_children_out=True,actual_empty_source_GPU_compute=computes,actual_GPU_resource=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,known_original_canonical_owner=None if a is None else a['owner_parent_pid'],native0PPO_no_original_locks_or_ledger_write=True)))
''',ROOT);put('H1_SOURCE210_OLD_CURB_OUT_GPU_FREE_ORIGINAL_OWNER_READONLY_ADMITTED.json',v);sf=c.open_sftp();sf.get_channel().settimeout(120);sf.put(str(tar),ROOT+'/payload_original.tar');sf.close();sf=None
  v=code(c,t.PY,r'''
from pathlib import Path,PurePosixPath
import sys,os,json,hashlib,tarfile,ast,time
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(sys.argv[1]);p=B/'payload_original.tar';assert p.stat().st_size==int(sys.argv[2]) and hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[3]
with tarfile.open(p,'r:') as tf:
 members=tf.getmembers();assert len({q.name for q in members})==len(members)
 for q in members:
  n=PurePosixPath(q.name);assert q.isfile() and not n.is_absolute() and '..' not in n.parts and '\\' not in q.name;dest=B.joinpath(*n.parts);assert dest.resolve().is_relative_to(B.resolve()) and not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
  with tf.extractfile(q) as src,dest.open('xb') as out:
   while block:=src.read(1024*1024):out.write(block)
mfile=B/'H1_SOURCE210_NATIVE_ONLY_COMPLETE_MANIFEST.json';assert hashlib.sha256(mfile.read_bytes()).hexdigest()==sys.argv[4];m=json.loads(mfile.read_bytes())
for row in m['files']:
 f=B/row['relative'];assert f.resolve().is_relative_to(B.resolve()) and f.stat().st_size==row['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==row['SHA'],row['relative']
 if f.suffix=='.py':ast.parse(f.read_text('utf8'))
import torch;torch.set_num_threads(2);s=torch.load(B/'job0/source/H1_final10_protected.pt',map_location='cpu',weights_only=False);assert {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={640260} and s['owned_H1_completed_updates']==25 and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8;count=[0,0]
def finite(x):
 if torch.is_tensor(x):
  count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v)
finite(s);assert not torch.cuda.is_initialized();v=dict(epoch=time.time(),all449_manifest_bytes_SHA_AST_passed=True,source_SHA=m['source_SHA'],whole_model_counts=count,all17Adam640260_finite=True,source_H1_phase_version2_original_restore_then_new_episode_required=True,source210_backend_actual_native_not_inferred=True,no_PPO_or_canonical_mutation=True);(B/'TARGET_SOURCE_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',ROOT,str(prep['tar']['bytes']),prep['tar']['SHA'],prep['manifest_SHA'],timeout=180);put('H1_SOURCE210_ALL449_TARGET_SHA_AST_FULLSOURCE_CPU_ADMITTED_ACTUAL.json',v)
  # No credential or capability configuration is passed in argv or persisted.
  v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,subprocess,time,psutil
B=Path(sys.argv[1]);assert (B/'TARGET_SOURCE_CPU_ADMITTED_ACTUAL.json').is_file() and not (B/'parent.log').exists();p=subprocess.run([sys.argv[2],'-u','-B',str(B/'h1_source210_native_CPU_only_parent_v1.py')],cwd=B,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr;v=json.loads(p.stdout);q=psutil.Process(v['detached_pid']);v['actual_identity']=dict(pid=q.pid,creation=q.create_time(),argv=q.cmdline(),root=q.cwd());v['epoch']=time.time();print(json.dumps(v))
''',ROOT,t.PY);put('H1_SOURCE210_NATIVE180_CPU_ONLY_ACTUALLY_DETACHED_DISPATCH.json',v);print(json.dumps(v),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_SOURCE210_NATIVE_ONLY_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_no_blind_retry_or_task_replay=True,no_PPO_or_budget_authorization_from_files=True));raise
