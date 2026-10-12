from pathlib import Path
import json,time,hashlib,sys,torch,psutil,msvcrt,subprocess
D=Path(__file__).resolve().parent;A=D/'attempts/temporary_train128_v10_sameidentity_saved_source';O=A/'output'
def read(p):
 for _ in range(4):
  try:return json.loads(p.read_bytes())
  except (OSError,json.JSONDecodeError):time.sleep(.1)
 raise RuntimeError('Actual local report unavailable: '+str(p))
def main():
 dispatch=read(A/'DISPATCH_RECEIPT.json');pid=dispatch['child_pid'];actual=None
 if psutil.pid_exists(pid):
  proc=psutil.Process(pid)
  if abs(proc.create_time()-dispatch['child_create_time'])<.001:actual=dict(pid=pid,create_time=proc.create_time(),argv=proc.cmdline(),cwd=proc.cwd())
 latest=read(O/'LOCAL_LATEST_COMPLETE.json') if (O/'LOCAL_LATEST_COMPLETE.json').exists() else None
 cpu=None
 if latest:
  p=Path(latest['path']);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==latest['sha256'] and latest['pid']==pid
  ck=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(O/'LOCAL_PROJECTED_FULLSTATE_SOURCE.pt',map_location='cpu',weights_only=False)
  items=[]
  def walk(v):
   if isinstance(v,torch.Tensor) and v.is_floating_point():assert torch.isfinite(v).all();items.append(v)
   elif isinstance(v,dict):
    for x in v.values():walk(x)
   elif isinstance(v,(tuple,list)):
    for x in v:walk(x)
  walk(ck);assert len(items)==107 and ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==128
  changed=sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items());delta=[float(v['step'])-float(source['optimizer_state_dict']['state'][k]['step']) for k,v in ck['optimizer_state_dict']['state'].items()]
  assert changed>0 and min(delta)>0 and ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
  cpu=dict(passed=True,path=str(p),sha256=sha,bytes=p.stat().st_size,finite_floating_count=107,actor_changed=changed,optimizer_step_delta_min=min(delta),actual_updates=latest['actual_updates'],actual_controls=latest['actual_controls'],all_private_DR_RNG_and_geometry_command_state_saved=True)
 health=read(O/'CLOCK_TRAINING_HEALTH.json') if (O/'CLOCK_TRAINING_HEALTH.json').exists() else None
 error=read(O/'ORIGINAL_ERROR.json') if (O/'ORIGINAL_ERROR.json').exists() else None
 final=read(O/'LOCAL_PPO_FORMAL_FINAL_ACTUAL.json') if (O/'LOCAL_PPO_FORMAL_FINAL_ACTUAL.json').exists() else None
 lock_free=False
 with (D/'LOCAL_GPU_EXCLUSIVE.lock').open('r+b') as f:
  try:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
  except OSError:pass
  else:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);lock_free=True
 v=dict(epoch=time.time(),root=str(D),actual_process=actual,dispatch=dispatch,own_saved_positive_PPO_CPU=cpu,health=health,error=error,formal_final=final,exclusive_OS_lock_free=lock_free,original_remote_training_still_paused=True,source_original_checkpoint_intact=True,temporary_local_not_qualified50_or70_or_MoE=True,canonical_reconciliation_pending=True,no_GPU_or_PPO_launch_or_budgetwrite_by_reader=True)
 p=D/'reports'/('LOCAL_TRAINING_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(p),actual_active=actual is not None,own_positive_PPO_cpu=cpu,health_controls=health.get('control_steps') if health else None,error=bool(error),final=final is not None,exclusive_lock_free=lock_free)))
if __name__=='__main__':main()

