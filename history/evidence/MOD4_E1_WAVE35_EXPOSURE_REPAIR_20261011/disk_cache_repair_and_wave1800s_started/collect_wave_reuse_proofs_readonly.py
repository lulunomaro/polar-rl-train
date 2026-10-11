from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_wave_isolated_revision004_once as old
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=j(D/'reports/SOURCE_SELECTED.json');p=Path(source['path']);assert h(p)==old.SOURCE_SHA
row=j(D/'reports/e1_wave_G3_isolated_observation_PASSED.json');run=Path(row['run']);startup={}
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','FEEDBACK_DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
 path=run/name
 if path.exists():startup[name]=dict(path=str(path),bytes=path.stat().st_size,sha256=h(path),value=j(path))
base=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010');reuse=j(base/'reports/REUSED_NATIVE_SMALL_ACTUAL.json');pre=j(base/'reports/E1_COMPLETE_PPO_PREFLIGHT_PASSED.json')
runtime=old.m.runtime();assert float(runtime.get('RM_EPISODE_S','20'))==20.
print(json.dumps(dict(epoch=time.time(),source=old.fullsave(p),runtime_scope={k:v for k,v in runtime.items() if k.startswith('RM_')},old366_own=row,all_saved_old366_startup=startup,original_native_small=reuse,original_complete_preflight=pre,CPU_only=True,no_CUDA_initialized=not torch.cuda.is_initialized())))
''')
  save('WAVE_REUSE_PROOF_SOURCE_READONLY.json',v)
  with n.open_sftp() as f:
   for name in ('SOURCE_SELECTED.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json','G3_BEHAVIOR_PACKAGE_READY.json','REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','REUSED_CONTRACTS.json'):
    raw=f.open(OLD+'/reports/'+name,'rb').read();dest=D/'old_scope_reports'/name;dest.parent.mkdir(exist_ok=True);assert not dest.exists();dest.write_bytes(raw)
  print(json.dumps(dict(source_SHA=v['source']['sha256'],old_startup_files=list(v['all_saved_old366_startup']),reuse_keys=list(v['original_native_small']),complete_keys=list(v['original_complete_preflight']),runtime_episode_s=v['runtime_scope'].get('RM_EPISODE_S','20 default'),no_GPU=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
