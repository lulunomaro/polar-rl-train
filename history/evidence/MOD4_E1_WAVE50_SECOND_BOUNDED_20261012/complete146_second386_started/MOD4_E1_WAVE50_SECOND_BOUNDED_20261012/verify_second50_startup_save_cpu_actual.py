from second50_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_second_bounded_once as wrapper
own=wrapper.prior
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();st=j(R/'E1_STATE.json');names=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')
runs=[p for p in (D/'learning_logs').glob('*e1_WAVE50_second_bounded_observation_*') if (p/'run_manifest.json').exists() and (p/'latest_complete.json').exists()]
if not runs:print(json.dumps(dict(epoch=time.time(),pending=True,own_formal_manifest_or_save_not_generated=True,state=st,no_mutation=True)));raise SystemExit(0)
assert len(runs)==1;root=runs[0];missing=[x for x in names if not (root/x).exists()]
if missing:print(json.dumps(dict(epoch=time.time(),pending=True,own_formal_startup_pending=missing,state=st,no_mutation=True)));raise SystemExit(0)
rec=j(root/'latest_complete.json');manifest=j(root/'run_manifest.json');freeze=j(R/'SOURCE_FREEZE.json')['sha256'];pid=rec['pid'];assert manifest['init_checkpoint_sha256']==wrapper.INIT_SHA and manifest['source_map']==freeze and len(freeze)==386 and rec['checkpoint'].startswith(str(root)+'/')
for name,sha in manifest['src_sha256'].items():assert h(root/'src_snapshot'/name)==sha
markers={}
for name in names:
 p=root/name;a=j(p);assert a['source_sha256']==wrapper.INIT_SHA;markers[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p))
t=j(root/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');c=j(root/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']
ckpath=Path(rec['checkpoint']);info=own.fullsave(ckpath);ck=torch.load(ckpath,map_location='cpu',weights_only=False);source=own.source();before=torch.load(source,map_location='cpu',weights_only=False)
changed=sum(not torch.equal(x,before['actor_state_dict'][k]) for k,x in ck['actor_state_dict'].items());step=lambda s:float(s['step'].item()) if hasattr(s['step'],'item') else float(s['step']);deltas=[step(x)-step(before['optimizer_state_dict']['state'][k]) for k,x in ck['optimizer_state_dict']['state'].items()]
assert h(source)==wrapper.INIT_SHA and not torch.cuda.is_initialized();audit=j(root/'RETENTION_COMMAND_ACTUAL.json') if (root/'RETENTION_COMMAND_ACTUAL.json').exists() else None
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,own_PID=pid,own_actual_process=own.identity(pid),own_manifest_PID_receipt_exact=True,own_run=str(root),own_checkpoint=info,actual_finite_tensor_count=info['finite_tensors'],actual_source_count=386,own_source_SHA=wrapper.INIT_SHA,startup_markers=markers,actual_same50_CUDA_fullstate_roundtrip_and_episode_plus_one=True,actor_tensors_changed=changed,optimizer_step_delta_min=min(deltas),optimizer_step_delta_max=max(deltas),actual_saved_PPO_updates_positive=changed>0 and min(deltas)>0,actual_saved_trace_controls=audit['actual_controls'] if audit else None,own_formal_final_not_claimed_from_activity=True,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('SECOND50_OWN_STARTUP_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=v.get('passed'),pending=v.get('pending'),actual_PPO_updates_positive=v.get('actual_saved_PPO_updates_positive'),actor_tensors_changed=v.get('actor_tensors_changed'),optimizer_step_delta=v.get('optimizer_step_delta_min'),checkpoint=v.get('own_checkpoint'))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN_STARTUP_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_budget_replay=True));raise
