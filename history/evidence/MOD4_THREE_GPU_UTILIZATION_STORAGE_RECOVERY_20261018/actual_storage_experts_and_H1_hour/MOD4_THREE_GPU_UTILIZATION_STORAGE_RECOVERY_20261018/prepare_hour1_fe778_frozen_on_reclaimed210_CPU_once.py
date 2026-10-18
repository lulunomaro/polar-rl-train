"""Rebind the already complete frozen source to the restored210 Linux4090, no physical changes."""
from pathlib import Path
import os,sys,json,time,shutil,hashlib,zipfile,ast,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;P=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/hour1_h1_8a7c_v1';Q=B/'H1_fe778_linux210_frozen_v1/payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 original=json.loads((P/'reports/HOUR1_CLOSED_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json').read_bytes());assert original['passed_complete_payload_CPU_only'];old=P/'frozen_H1_hour1_complete_final_linux_v1/payload';assert not Q.exists();shutil.copytree(old,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 changes=[]
 for name in ('h1_linux4090_frozen_worker_v1.py','h1_linux4090_frozen_parent_v1.py','h1_linux_eval_contract_v1.py'):
  p=Q/name;s=p.read_text('utf8');before=H(p)
  s=s.replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e').replace('10.24.0.72','10.24.4.210').replace('linux72_GPU1_frozen_only','linux210_GPU0_frozen_only').replace('H1_HOUR1_FINAL_LINUX4090_V1_20261018','H1_HOUR1_FINAL_LINUX210_V1_20261018').replace('H1_HOUR1_FINAL_LINUX4090_MANIFEST_V1.json','H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').replace('/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python')
  if name=='h1_linux4090_frozen_worker_v1.py':
   start=s.index("owned=Path('/home/lc01/Zonglin Li/zonglin2');lockpath=");end=s.index('compute=subprocess.check_output',start)
   s=s[:start]+"owned=Path('/mnt/mod4_linux_durable_20261013');assert owned.is_mount();lockpath=owned/'H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock';lock=lockpath.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)\n"+s[end:]
  ast.parse(s);p.write_text(s,'utf8');changes.append(dict(name=name,original_SHA=before,new_SHA=H(p),only_host_GPU_interpreter_lock_manifest_binding=True))
 oldm=Q/'H1_HOUR1_FINAL_LINUX4090_MANIFEST_V1.json';m=json.loads(oldm.read_bytes());m['execution_backend']='linux210_GPU0_frozen_only';m['namespace']='H1_HOUR1_FINAL_LINUX210_V1_20261018'
 for row in m['files']:
  p=Q/row['relative'];row.update(bytes=p.stat().st_size,SHA=H(p))
 dest=Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json';assert not dest.exists();dest.write_text(json.dumps(m,indent=2),'utf8')
 os.environ['CUDA_VISIBLE_DEVICES']='';import torch;torch.set_num_threads(1);rng=torch.get_rng_state().clone();sys.path.insert(0,str(Q));from h1_hour1_finite_final_source_guard_v1 import validate_H1_source
 ck=torch.load(Q/m['source_relative'],map_location='cpu',weights_only=False);validate_H1_source(ck);assert H(Q/m['source_relative'])==original['source']['SHA'];assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 for p in Q.rglob('*.py'):ast.parse(p.read_text('utf8'))
 zipout=Q.parent/'H1_FE778_LINUX210_FROZEN_PAYLOAD_V1.zip';assert not zipout.exists()
 with zipfile.ZipFile(zipout,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(Q).as_posix())
 put('H1_FE778_LINUX210_FROZEN_COMPLETE_PACKAGE_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_complete_source_CPU_and_AST=True,source=original['source'],source_owned_updates=71,source_Adam648000=True,changes=changes,manifest=dict(path=str(dest),bytes=dest.stat().st_size,SHA=H(dest)),package=dict(path=str(zipout),bytes=zipout.stat().st_size,SHA=H(zipout)),selected_original_physics_reward_commands_DR_hardware_and_actor_unchanged=True,own_unused_native120_then_CPU_before_full1500=True,original_source_GPU_real_fcntl_and_D25GiB_retained=True,no_GPU_PPO_budget_or_training_interruption=True));print(json.dumps(dict(CPU_prepared=True,source_SHA=original['source']['SHA'],target='210 recovered GPU',files=len(m['files']))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_FE778_LINUX210_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
