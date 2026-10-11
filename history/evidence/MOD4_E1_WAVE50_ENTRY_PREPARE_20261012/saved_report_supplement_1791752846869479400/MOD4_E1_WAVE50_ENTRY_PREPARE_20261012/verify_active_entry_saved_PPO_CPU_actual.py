"""Own activity proof, distinguish discard preflight from formal final."""
from entry_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch
D=Path(NEW_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once_v2 as own
R=D/'reports';j=lambda p:json.loads(p.read_bytes());st=j(R/'E1_STATE.json');receipt=j(R/'E1_CURRENT_SAVE.json') if (R/'E1_CURRENT_SAVE.json').exists() else None
loc=st.get('child');pid=loc['pid'] if loc else None
if receipt is None or receipt['receipt']['pid']!=pid:
 print(json.dumps(dict(epoch=time.time(),passed=False,pending=True,actual_state=st,own_live_child_has_no_matching_save_yet=True,formal_final_not_claimed=True)));sys.exit(0)
run=Path(receipt['own_run']);rec=receipt['receipt'];cp=Path(rec['checkpoint']);count=j(run/'run_manifest.json')['num_envs'];info=own.fullsave(cp,count=count)
ck=torch.load(cp,map_location='cpu',weights_only=False);source=torch.load(own.source(),map_location='cpu',weights_only=False)
changed=[k for k,a in ck['actor_state_dict'].items() if not torch.equal(a,source['actor_state_dict'][k])]
step=lambda ck:max(float(v['step']) for v in ck['optimizer_state_dict']['state'].values());delta=step(ck)-step(source)
assert changed and delta>0 and rec['pid']==pid and info['sha256']==own.s.q.base.sha(cp)
markers={}
if count==20000:
 for name in ('ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json'):
  markers[name]=j(run/name);assert markers[name]['source_sha256']==own.SOURCE_SHA
 terrain=markers['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];entry=markers['E1_WAVE50_ENTRY_STARTUP_VERIFIED.json']
 assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicit_new_entry_reset_scope'] and terrain['saved_source_episode_plus_one_verified']
 assert entry['actual_entry_terrain_command_CUDA_disk_roundtrip_exact'] and entry['explicit_new_entry_scope'] and not entry['same_entry_identity_restored_exact']
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,own_current_checkpoint=info,actual_actor_tensors_changed=changed,actual_optimizer_step_delta=delta,actual_saved_PID=pid,actual_num_envs=count,discarded_preflight=receipt['discarded_preflight'],startup_markers=markers,activity_only_not_formal_final=True,formal_final_not_claimed=True,actual_state=st,CPU_readonly_no_budget_write=True)))
'''.replace('NEW_TOKEN',repr(NEWROOT)))
  p=save('ENTRY_OWN_SAVED_PPO_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=v['passed'],pending=v['pending'],discarded_preflight=v.get('discarded_preflight'),actor_changed=len(v.get('actual_actor_tensors_changed',[])),optimizer_step_delta=v.get('actual_optimizer_step_delta'))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ACTIVE_PPO_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
