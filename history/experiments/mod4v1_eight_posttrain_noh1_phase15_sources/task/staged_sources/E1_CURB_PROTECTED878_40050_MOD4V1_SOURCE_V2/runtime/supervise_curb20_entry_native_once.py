"""New isolated entry reset SDK/native only. No PPO or canonical writer."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';sys.path.insert(0,str(CODE))
import supervise_e1_command_retention_episode_reviewed_once as inherited
from reviewed_budget005_source_guard import verify_original_records
from budget_authority import validate_budget
s=inherited.s;read=inherited.read;write=inherited.write;identity=inherited.identity
SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'

def verify():
 verify_original_records(s.q,D)
 assert validate_budget(s.q.base.budget_state())==1188000
 c=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json');assert c['terrain_subexpert_revision004']['approved'] and c['budget_retrain_revision005']['approved']
 assert read(R/'ENTRY_V2_COMPONENT_CPU_PASSED.json')['passed']
 for n,h in read(R/'SOURCE_FREEZE.json')['sha256'].items():assert s.q.base.sha(D/n)==h,n

def wait_existing():
 assert not inherited.trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
 old=Path('/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011/reports');st=read(old/'E1_STATE.json');p=read(old/'e1_SLOPE5_independent_observation_PASSED.json')
 assert st['child'] is None and p['checkpoint']['sha256']=='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
 for loc in (st['owner'],read(old/'E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=83699658)):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']

s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'ENTRY_NATIVE_STARTED.json').exists();verify();wait_existing()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 before=s.q.ctl.CANONICAL.read_bytes();source=Path(read(R/'SOURCE_SELECTED.json')['path']);assert s.q.base.sha(source)==SOURCE_SHA and inherited.fullsave(source)['finite_tensors']==102
 write('ENTRY_NATIVE_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),no_PPO_or_budget_transaction=True,first_new_entry_scope=True))
 results={}
 for count,steps,label in ((10,300,'ENTRY_SDK10'),(20000,120,'ENTRY_NATIVE20K')):
  output=D/(label+'.json');log=D/(label+'.log');assert not output.exists() and not log.exists()
  args=[s.q.base.PY,str(D/'native_curb20_entry_v2_probe.py'),'--headless','--dt','.0025','--checkpoint',str(source),'--output',str(output),'--num_envs',str(count),'--warmup','0' if count==10 else '24','--steps',str(steps),'--profile_steps','0']
  with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=inherited.runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  loc=identity(p.pid);write(label+'_PID_RECEIPT.json',dict(epoch=time.time(),child=loc,argv=args,no_PPO=True));write('ENTRY_NATIVE_STATE.json',dict(epoch=time.time(),phase=label,owner=identity(os.getpid()),child=loc,active_log=str(log),no_PPO=True))
  while p.poll() is None:time.sleep(2)
  assert s.q.ctl.CANONICAL.read_bytes()==before
  assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
  v=read(output);assert v['PPO_update_count']==0 and not v['nonfinite'] and v['actual_task_failed_environments']==0
  assert v['physical_callback_count']==steps*4 and v['health']['actual_physics_callbacks']==(steps+(24 if count==20000 else 0))*4
  assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6 and v['actual_solver_readback']['all_position32_velocity4']
  a=v['CURB_entry_map'];assert a['profile']=='CURB20_actual_cell_entry_reset_v2' and a['minimum_front_support_m']>=.4 and a['no_new_random_stream']
  if count==10:assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact']
  if count==20000:
   hist=v['command_retention']['sample_histogram'];assert all(hist[1][i]>0 for i in (2,3,4,5)) and all(sum(row[2:6])==0 for row in hist[:1]+hist[2:])
  results[label]=dict(path=str(output),bytes=output.stat().st_size,sha256=s.q.base.sha(output),passed=True,no_PPO=True,own_child_PID=loc)
  write(label+'_PASSED.json',results[label])
 write('ENTRY_NATIVE_SCOPE_PASSED.json',dict(epoch=time.time(),passed=True,results=results,fullstate_PPO_formal_pending=True,new_budget_seconds=0,no_learning_executor_installed=True))
 write('ENTRY_NATIVE_STATE.json',dict(epoch=time.time(),phase='CURB20_entry_native_complete_review_ready',owner=identity(os.getpid()),child=None,no_PPO=True))
if __name__=='__main__':
 try:main()
 except BaseException:write('ENTRY_NATIVE_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_restart=True,no_PPO=True));raise
