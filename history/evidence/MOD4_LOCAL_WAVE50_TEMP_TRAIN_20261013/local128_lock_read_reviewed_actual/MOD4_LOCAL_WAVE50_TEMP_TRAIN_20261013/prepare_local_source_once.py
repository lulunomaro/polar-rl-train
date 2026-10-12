from pathlib import Path
import sys,json,time,hashlib,shutil,traceback,ast,importlib.metadata as metadata,subprocess
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
RUN=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
SOURCE=RUN/'model_32264.pt';SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert not (D/'runtime').exists();assert h(SOURCE)==SHA
 import torch
 torch.set_num_threads(1);ck=torch.load(SOURCE,map_location='cpu',weights_only=False);shape=[]
 def walk(x,path=''):
  if isinstance(x,torch.Tensor):shape.append(dict(path=path,shape=list(x.shape),dtype=str(x.dtype),finite=bool(torch.isfinite(x).all()) if x.is_floating_point() else True))
  elif isinstance(x,dict):
   for k,v in x.items():walk(v,path+'/'+str(k))
  elif isinstance(x,(tuple,list)):
   for k,v in enumerate(x):walk(v,path+'/'+str(k))
 walk(ck);assert all(x['finite'] for x in shape)
 save('SOURCE_FULL_STATE_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,path=str(SOURCE),bytes=SOURCE.stat().st_size,sha256=SHA,iteration=ck['iter'],keys=list(ck),tensors=shape,floating_count=sum('float' in v['dtype'] for v in shape),source_environments=20000,local_projection_not_yet_admitted=True))
 mf=json.loads((RUN/'run_manifest.json').read_bytes());freeze=json.loads((RUN/'rolling_source_freeze.json').read_bytes())['sha256'];assert len(freeze)==459
 for name,sha in freeze.items():assert h(RUN/'e1_source_snapshot'/name)==sha
 runtime=D/'runtime';shutil.copytree(RUN/'e1_source_snapshot',runtime)
 asset=runtime/'assets';asset.mkdir();code=runtime/'isaac/mod4'
 for p in (RUN/'src_snapshot').iterdir():
  if p.suffix in ('.usd','.npz','.json') and p.name not in ('env.json',):shutil.copy2(p,asset/p.name)
 for name in ('robot.usd','import_contract.json','reset_bank.json'):assert (asset/name).exists()
 candidates=list(W.rglob('MOD4_RESET_COLLISION_BANK.npz'))
 assert candidates,'Collision bank original required'
 expected=json.loads((code/'MOD4_RESET_COLLISION_BANK.json').read_bytes())
 bank=next(p for p in candidates if h(p)==expected.get('sha256',expected.get('npz_sha256','')) ) if expected.get('sha256',expected.get('npz_sha256')) else candidates[0]
 shutil.copy2(bank,code/bank.name)
 # This file and field-builder data are original shared task inputs, copied independently.
 deploy=runtime/'train/deploy';deploy.mkdir(parents=True,exist_ok=True)
 contract=W/'train/deploy/contract_rm2025_later.json';assert contract.exists();shutil.copy2(contract,deploy/contract.name)
 originalTask=(code/'mod4_task.py').read_text(encoding='utf8')
 adapted=originalTask.replace('from isaaclab_physx.physics import PhysxCfg','from isaaclab.sim import PhysxCfg').replace('self.sim.physics = PhysxCfg(','self.sim.physx = PhysxCfg(')
 assert adapted!=originalTask;ast.parse(adapted)
 (code/'mod4_task.py').write_text(adapted,encoding='utf8')
 save('LOCAL_SOURCE_PREPARED.json',dict(epoch=time.time(),passed=True,original_source_count=459,original_source_root=str(RUN/'e1_source_snapshot'),runtime_root=str(runtime),source_checkpoint=str(SOURCE),source_SHA=SHA,source_preserved=True,changed=dict(mod4_task=dict(original_sha=hashlib.sha256(originalTask.encode()).hexdigest(),adapted_sha=h(code/'mod4_task.py'),changes=['PhysxCfg public2.x import','SimulationCfg.physx field'])),collisionbank=dict(original=str(bank),bytes=bank.stat().st_size,sha256=h(bank)),source_snapshot_104_actual=True,projection_and_GPU_validation_pending=True,remote_training_and_monitor_not_resumed=True))
 save('LOCAL_HOST_ACTUAL.json',dict(epoch=time.time(),python=sys.version,torch=torch.__version__,CUDA=torch.version.cuda,GPU=torch.cuda.get_device_name(0),GPU_memory_bytes=torch.cuda.get_device_properties(0).total_memory,packages={k:metadata.version(k) for k in ('isaacsim','isaaclab','rsl-rl-lib')},GPU_csv=subprocess.check_output(['nvidia-smi','--query-gpu=memory.total,memory.free','--format=csv,noheader,nounits']).decode(),old_reads_refusals=[dict(id='inspection-powershell-bash-brace-list',classification='preGPU shell ParserError missingargument',retained='Original tool output in this conversation'),dict(id='inspection-guessed-retention_full_checkpoint',classification='readonly guessedfilename absent',retained='Original tool output in this conversation')],no_physics_or_PPO_started=True))
 print(json.dumps(dict(passed=True,root=str(D),source_CPU_floating_count=sum('float' in v['dtype'] for v in shape),tensor_count=len(shape),source_sha=SHA,projection_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_physics_or_PPO=True));raise
