from second50_io import *

def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_second_bounded_once as wrapper
own=wrapper.prior;j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(R/'E1_STATE.json');runs=[p for p in (D/'learning_logs').glob('*e1_WAVE50_second_bounded_observation_*') if (p/'run_manifest.json').exists()]
if not runs:print(json.dumps(dict(epoch=time.time(),pending=True,manifest_not_generated=True,no_mutation=True)));raise SystemExit(0)
assert len(runs)==1;root=runs[0];names=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')
missing=[name for name in names if not (root/name).exists()]
if missing:print(json.dumps(dict(epoch=time.time(),pending=True,startup_markers_not_generated=missing,no_mutation=True)));raise SystemExit(0)
m=j(root/'run_manifest.json');freeze=j(R/'SOURCE_FREEZE.json')['sha256'];assert len(freeze)==386 and m['source_map']==freeze and m['init_checkpoint_sha256']==wrapper.INIT_SHA
for name,sha in m['src_sha256'].items():assert h(root/'src_snapshot'/name)==sha
markers={}
for name in names:
 p=root/name;a=j(p);assert a['source_sha256']==wrapper.INIT_SHA;markers[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),receipt=a)
t=markers['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']['receipt'];c=markers['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']['receipt']
assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']
assert h(own.source())==wrapper.INIT_SHA and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,source_SHA=wrapper.INIT_SHA,source_count=386,actual_same50_CUDA_fullstate_roundtrip_and_episode_plus_one=True,seven_own_startup_receipts=markers,own_run=str(root),actual_owner=own.identity(st['owner']['pid']),actual_child=own.identity(st['child']['pid']) if st.get('child') else None,source_fullsave=own.fullsave(own.source()),activity_not_final_or_graduation=True,saved_PPO_positive_proof_separate=True,no_GPU_PPO_controller_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('SECOND50_OWN_STARTUP_CONTRACT_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=v.get('passed'),pending=v.get('pending'),same50_CUDA_restore=v.get('actual_same50_CUDA_fullstate_roundtrip_and_episode_plus_one'))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STARTUP_CONTRACT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_replay=True));raise
