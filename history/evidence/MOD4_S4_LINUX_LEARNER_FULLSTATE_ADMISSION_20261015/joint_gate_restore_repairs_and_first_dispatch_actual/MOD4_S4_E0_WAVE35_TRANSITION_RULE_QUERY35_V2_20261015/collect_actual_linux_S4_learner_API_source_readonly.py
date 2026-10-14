"""One bounded root-owned Linux source audit, not a training launcher."""
from pathlib import Path
import sys,json,time,hashlib,traceback
W=Path(__file__).resolve().parent.parent;D=W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015';R=D/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import sys,sysconfig,json,time,hashlib,importlib.metadata as metadata,fcntl,shutil,subprocess,psutil
sources=[]
def add(p,kind):
 p=Path(p)
 if p.is_file() and p.stat().st_size<2000000:
  sources.append(dict(path=str(p),kind=kind,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
dist=metadata.distribution('rsl-rl-lib')
wanted={'rsl_rl/algorithms/ppo.py','rsl_rl/models/mlp_model.py','rsl_rl/runners/on_policy_runner.py','rsl_rl/storage/rollout_storage.py','rsl_rl/modules/distribution.py','rsl_rl/modules/distribution/gaussian.py','rsl_rl/modules/distribution/gaussian_distribution.py'}
for f in dist.files:
 if str(f).replace('\\','/') in wanted:add(dist.locate_file(f),'installed_rsl_API')
base=Path('/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013')
root=base/'original_Linux20k_d05_continuation_runtime_assets_complete_v3'
names={'g3_terrain_checkpoint.py','e1_terrain_checkpoint.py','g3_cad_wave_geometry.py','train_e1_g3_reviewed_resume_ppo.py','train_e1_terrain_resume_ppo.py','train_mod4_ppo.py','history_actor_label_ppo.py','physical_dr_checkpoint.py','history_frozen_std_guard.py','rescue_training.py','sensor_sdk_checkpoint.py','sensor_mild_dr_checkpoint.py','directional_spin_training_env.py','e1_scene_query_resource.py'}
for p in root.rglob('*.py'):
 if p.name in names and len(p.relative_to(root).parts)<=5:add(p,'completed_original_runtime_API')
budget=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(budget.read_bytes());locks=[]
for p in [budget.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:locks.append(dict(path=str(p),held=True))
  else:fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),held=False))
print(json.dumps(dict(epoch=time.time(),python=sys.version,versions={n:metadata.version(n) for n in ('torch','tensordict','rsl-rl-lib','isaacsim','isaaclab','isaaclab-rl')},sources=sources,original_completed_runtime_root=str(root),original_root_exists=root.exists(),locks=locks,canonical_readonly_snapshot=dict(path=str(budget),sha256=hashlib.sha256(budget.read_bytes()).hexdigest(),active=b['active_segment'],remaining=b['remaining_training_seconds'],authorized=b['authorized_total_seconds']),resource=dict(available_RAM=psutil.virtual_memory().available,durable_free=shutil.disk_usage(base).free,GPU=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.free','--format=csv,noheader,nounits'],text=True).strip(),GPU_apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()),no_torch_or_Isaac_import_no_GPU_PPO_or_budgetwrite=True)))
'''
def main():
 D.mkdir(exist_ok=True);R.mkdir(exist_ok=True);c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+t.PY+' -',timeout=60);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();error=se.read();rc=so.channel.recv_exit_status()
  p=R/('LINUX_S4_API_SOURCE_READONLY_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(code=rc,stdout=raw.decode('utf8','replace'),stderr=error.decode('utf8','replace'),readonly=True,no_automatic_retry=True),indent=2),encoding='utf8');assert rc==0,str(p)
  v=json.loads(raw);dest=D/'actual_original_API_sources'/stamp;dest.mkdir(parents=True);rows=[];sf=c.open_sftp();sf.get_channel().settimeout(60)
  for i,row in enumerate(v['sources']):
   p=dest/(str(i)+'_'+Path(row['path']).name);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];rows.append(dict(**row,local_path=str(p),twohost_SHA_exact=True))
  v['actual_collected_sources']=rows;report=R/('LINUX_ORIGINAL_S4_LEARNER_API_SOURCE_ACTUAL_'+stamp+'.json');report.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(report),source_files=len(rows),versions=v['versions'],locks=v['locks'],canonical=v['canonical_readonly_snapshot'],resource=v['resource'],no_GPU_PPO=True)))
 except BaseException:
  (R/('LINUX_S4_SOURCE_COLLECT_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
