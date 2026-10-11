"""Own formal save inspection only, future missing files are pending. No launch/resume."""
from entry_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path(NEW_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once_v2 as own
R=D/'reports';j=lambda p:json.loads(p.read_bytes());p=R/'e1_WAVE50_entry_observation_PASSED.json'
if not p.exists():
 st=j(R/'E1_STATE.json');print(json.dumps(dict(epoch=time.time(),formal_complete=False,pending=True,actual_state=st,attention=j(R/'E1_ATTENTION.json') if (R/'E1_ATTENTION.json').exists() else None)));sys.exit(0)
row=j(p);run=Path(row['run']);rec=j(run/'latest_complete.json');cp=Path(rec['checkpoint']);info=own.fullsave(cp);ck=torch.load(cp,map_location='cpu',weights_only=False)
assert rec['pid']==row['own_PID_bound_receipt']['pid'] and str(cp).startswith(str(D/'learning_logs')+'/') and info['sha256']==row['checkpoint']['sha256']
assert row['source_sha256']==own.SOURCE_SHA and len(row['unique_completed_segment'])==1 and row['source_count']==410 and not row['discarded_preflight']
f=j(R/'SOURCE_FREEZE.json')['sha256'];m=j(run/'run_manifest.json');assert m['source_map']==f and m['init_checkpoint_sha256']==own.SOURCE_SHA
for name,h in m['src_sha256'].items():assert own.s.q.base.sha(run/'src_snapshot'/name)==h
source=torch.load(own.source(),map_location='cpu',weights_only=False);changed=[k for k,a in ck['actor_state_dict'].items() if not torch.equal(a,source['actor_state_dict'][k])]
def maxstep(x):return max(float(v['step']) for v in x['optimizer_state_dict']['state'].values())
delta=maxstep(ck)-maxstep(source);assert changed and delta>0
markers={}
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','FEEDBACK_DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json'):
 if (run/name).is_file():markers[name]=j(run/name)
assert all(name in markers for name in ('ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json'))
terrain=markers['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];entry=markers['E1_WAVE50_ENTRY_STARTUP_VERIFIED.json']
assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicit_new_entry_reset_scope'] and terrain['saved_source_episode_plus_one_verified']
assert entry['actual_entry_terrain_command_CUDA_disk_roundtrip_exact'] and entry['explicit_new_entry_scope'] and not entry['same_entry_identity_restored_exact']
st=j(R/'E1_STATE.json');pub=j(R/'E1_WAVE50_ASYNC_PUBLISHED.json') if (R/'E1_WAVE50_ASYNC_PUBLISHED.json').exists() else None
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),formal_complete=True,pending=False,own_checkpoint=info,actual_actor_tensors_changed=changed,actual_optimizer_step_delta=delta,own_source_count=410,own_snapshot_count=len(m['src_sha256']),own_PID_bound_receipt=rec,own_stage=row,startup_markers=markers,actual_state=st,actual_publication=pub,CPU_only_no_cuda_or_canonical_write=True)))
'''.replace('NEW_TOKEN',repr(NEWROOT)))
  p=save('ENTRY_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),formal_complete=v['formal_complete'],pending=v['pending'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN_FORMAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
