"""Single finite shared4090 comparison, no training or canonical access."""
from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,sys,time,traceback,zipfile
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
REMOTE=r'''
from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,os,psutil,shutil,signal,subprocess,time,zipfile
base=Path(v['root']);assert base.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve()) and not base.exists();uuid=v['uuid'];line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if uuid in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(base.parent).free>25*1024**3
lock=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_MOE_MATCHED_FROZEN_EVAL_20261024.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);base.mkdir();print(json.dumps(dict(new_root=str(base),GPU_line=line,only_own_eval_lease=True)))
'''
RUN=r'''
from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,os,psutil,signal,subprocess,time,zipfile
base=Path(v['root']);archive=base/'payload.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['SHA'];lock=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_MOE_MATCHED_FROZEN_EVAL_20261024.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():
  p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and (base/name).resolve().is_relative_to(base.resolve())
 z.extractall(base)
env=dict(os.environ,CUDA_VISIBLE_DEVICES=v['uuid'],CUDA_DEVICE_ORDER='PCI_BUS_ID',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='1');start=time.time()
with (base/'FULL_WORKER.log').open('xb') as f:
 p=subprocess.Popen([v['python'],'-u','-B',str(base/'worker.py')],cwd=base,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);identity=dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=psutil.Process(p.pid).cmdline());(base/'OWN_STARTED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),identity=identity,explicit_4090_human_test=True)))
 try:rc=p.wait(timeout=720)
 except subprocess.TimeoutExpired:
  process=psutil.Process(p.pid);assert abs(process.create_time()-identity['creation'])<.01 and any(str(base/'worker.py')==a for a in process.cmdline());p.send_signal(signal.SIGINT);rc=p.wait(timeout=60)
final=json.loads((base/'out/FINAL.json').read_bytes()) if (base/'out/FINAL.json').exists() else None;fcntl.flock(lock,fcntl.LOCK_UN);lock.close();receipt=dict(epoch=time.time(),root=str(base),identity=identity,actual_child_waited=True,actual_returncode=rc,elapsed=time.time()-start,final=final,own_eval_lock_released=True,no_PPO_or_budget_or_training_mutation=True)
(base/'OWN_RETURNED_ACTUAL.json').write_text(json.dumps(receipt,indent=2));receipt['artifacts']=[dict(path=str(p),relative=p.relative_to(base).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in base.rglob('*') if p.is_file() and (p.suffix in ('.json','.log') or p.parent==base/'out' and p.suffix=='.npz')];print(json.dumps(receipt))
'''
def main():
 assert not (R/'4090_SERIES_BASELINE_DEPLOY_STARTED_ACTUAL.json').exists();probe=json.loads((R/'4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json').read_bytes());assert probe['packages']['mujoco'] and probe['packages']['torch']
 worker=D/'series_baseline_matched_cuda_worker_v1.py';tree=ast.parse(worker.read_text('utf8'));assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('PPO','Adam','OnPolicyRunner') for n in ast.walk(tree))
 manifest=json.loads((PLAYER/'policy/manifest.json').read_bytes());cfg=dict(GPU_UUID=probe['GPU_UUID'],variants=['auto','E0','W35'],speeds_m_s=[.6,1.5],controls=500,public_mode=0,normal_MoE_equivalent_to_original_gate148=True,physics='Exact copied player MuJoCo XML/assets/adapter; CPU physics runs on remote host, torch CUDA policy on4090.',human_request='可以在4090上测试不在本机测试',checkpoints={role:dict(relative='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1/checkpoints/'+role+'.pt',**manifest['sources'][role]) for role in ('E0','W35','gate148')},human_baseline=dict(environment='本机 MuJoCo 播放器',entry='平地／起伏／小陀螺系列播放器（可切 E0、W35）',source=str(W/'MOD4_LOCAL_WASD_SERIES_20261011'),exact_E0_checkpoint=True,old_terrain_registry_not_current_W35=True))
 (D/'SERIES_BASELINE_CONFIG.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8');archive=D/'SERIES_BASELINE_4090_PAYLOAD.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  z.write(worker,'worker.py');z.write(D/'SERIES_BASELINE_CONFIG.json','SERIES_BASELINE_CONFIG.json')
  source=W/'MOD4_LOCAL_WASD_SERIES_20261011'
  for name in ('sim_runtime.py','series_sim.py','runtime_config.json','SERIES.json','DOWNLOAD_RECEIPT.json','terrain.npz'):
   z.write(source/name,'player/'+name)
  for name in ('reset_bank.json','import_contract.json'):
   z.write(source/'src_snapshot'/name,'player/src_snapshot/'+name)
  import xml.etree.ElementTree as ET
  root=ET.fromstring((source/'scenes/flat.xml').read_bytes());root.find('compiler').set('meshdir','assets')
  z.writestr('player/flat.xml',ET.tostring(root,encoding='utf-8',xml_declaration=True))
  for mesh in root.findall('asset/mesh'):
   name=mesh.get('file');z.write(W/'chassis_mod4/assets'/name,'player/assets/'+name)
 put('4090_SERIES_BASELINE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),worker_SHA=H(worker),payload=dict(path=str(archive),bytes=archive.stat().st_size,SHA=H(archive)),no_local_policy_inference_or_simulation=True,protocol=cfg))
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None;root='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_confirmed_series_baseline_4090_2410v1'
 try:
  put('4090_SERIES_BASELINE_FRESH_ADMISSION_NEW_ROOT_ACTUAL.json',d.code(c,d.PY72,REMOTE,dict(root=root,uuid=cfg['GPU_UUID']),timeout=45))
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:sf.put(str(archive),root+'/payload.zip')
  finally:sf.close()
  result=d.code(c,d.PY72,RUN,dict(root=root,SHA=H(archive),uuid=cfg['GPU_UUID'],python='/home/lc01/Zonglin Li/zonglin2/run-python.sh'),timeout=840)
  put('4090_SERIES_BASELINE_FROZEN_FINITE_RETURNED_ACTUAL.json',result);local=D/'actual_series_4090';local.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in result['artifacts']:
    p=local/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
  finally:sf.close()
 finally:c.close()
 print(json.dumps(dict(actual_returned=True,rc=result['actual_returncode'],has_complete_FINAL=result['final'] is not None,final=result['final'])))
if __name__=='__main__':
 try:main()
 except BaseException:put('4090_SERIES_BASELINE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_old_root_or_once=True));raise
