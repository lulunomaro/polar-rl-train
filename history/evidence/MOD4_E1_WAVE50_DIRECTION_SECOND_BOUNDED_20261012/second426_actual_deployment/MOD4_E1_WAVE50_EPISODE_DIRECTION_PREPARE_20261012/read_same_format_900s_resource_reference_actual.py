"""Read an existing900s full output as a capacity reference only, never GPU admission."""
from wave_direction_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,hashlib,shutil,time,numpy as np
current=Path(ROOT_TOKEN);old=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011')
j=lambda p:json.loads(p.read_bytes());receipts=list((old/'reports').glob('e1_*_PASSED.json'));assert len(receipts)==1;passed=j(receipts[0]);assert not passed['discarded_preflight'] and passed['actual_updates']==46 and passed['health']['control_steps']==1104
run=Path(passed['run']);m=j(run/'run_manifest.json');assert m['num_envs']==20000 and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32';trace=j(run/'RETENTION_COMMAND_ACTUAL.json');assert trace['actual_controls']==1104
with np.load(run/trace['trace_files'][0]) as z:
 assert z['rows'].shape[1:]==(20000,16) and z['rows'].dtype==np.float32
 assert z['columns'].tolist()==['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
size=sum(p.stat().st_size for p in old.rglob('*') if p.is_file());required=2*size+2*1024**3;free=shutil.disk_usage(current).free
print(json.dumps(dict(epoch=time.time(),actual_completed900s_reference_root=str(old),actual_completed900s_wholeoutput_bytes=size,required_double_actual_wholeoutput_plus2GiB_bytes=required,current_disk_free_bytes=free,resource900_reference_guard_passed=free>required,matching_output_format_20k_float32_16columns_dt2p5ms_PPO24_step_verified=True,reference_only_not_Wave_physics_or_fullstate_admission=True,no_GPU_PPO_RNG_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('NEXT_DIRECTION_900S_RESOURCE_REFERENCE_ACTUAL.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('900S_RESOURCE_REFERENCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
