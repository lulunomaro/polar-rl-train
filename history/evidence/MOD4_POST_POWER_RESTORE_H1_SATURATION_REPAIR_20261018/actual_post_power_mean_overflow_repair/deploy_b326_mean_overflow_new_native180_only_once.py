"""New H1 source native-only GPU parent; no owner, learning GO or canonical operation."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';sys.path.insert(0,str(O));import deploy_H1_closed24_target72_new_native_original_handoff_once as old
a=old.a;TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1mb_1810n1'
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 proof=json.loads((R/'B326_MEAN_OVERFLOW_NATIVE_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());assert proof['passed_CPU_static_source_and_actual_mock_parent_flow'];spec=proof['spec'];assert spec['role']=='native_only';save('LATEST_H1_NATIVE_ONLY_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,new_unused_source_native_only_no_production_or_account=True));pw=getpass.getpass('Host72 latest closed H1 native-only validation (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None;save('LATEST_H1_NATIVE_ONLY_ACTUAL_OLD_FINAL_RESOURCE_FCNTL_NEW_ROOT_ADMISSION.json',a.code(c,a.PY,old.CREATE,TARGET,spec['previous_runtime_root'],spec['GPU_UUID'],timeout=60));Q=B/'payload_h1_native';sf=c.open_sftp();sf.get_channel().settimeout(120);made={TARGET,TARGET+'/job0'}
  try:
   for p in sorted(Q.rglob('*')):
    if '__pycache__' in p.parts:continue
    remote=TARGET+'/'+p.relative_to(Q).as_posix()
    if p.is_dir():
     if remote not in made:sf.mkdir(remote);made.add(remote)
    elif p.is_file():sf.put(str(p),remote)
  finally:sf.close()
  save('LATEST_H1_NATIVE_ONLY_FULL_TARGET_SOURCE_RSL_SDK_CPU_ADMITTED_ACTUAL.json',a.code(c,a.PY,old.d.CPU,TARGET,timeout=180));verify="from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);sys.path.insert(0,str(B/'job0/runtime/isaac/mod4'));import torch,rsl_rl.algorithms.ppo as original;assert hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest()=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c';import owned_h1_mean_overflow_ppo_v1 as owned;from h1_action_mean_overflow_loss_v1 import mean_overflow_loss;x=torch.tensor([[-100.,0.,0.,0.,0.,9.]],requires_grad=True);loss=mean_overflow_loss(x);loss.backward();assert x.grad[0,0]<0 and x.grad[0,5]>0 and not torch.cuda.is_initialized();print(json.dumps(dict(actual_installed_owned_PPO_CPU_import=True,owned_class=owned.PPO.__module__,loss_fixture=float(loss.detach()),no_optimizer_or_CUDA=True)))";save('ACTUAL_TARGET_OWNED_MEAN_OVERFLOW_PPO_IMPORT_GRADIENT_CPU.json',a.code(c,a.PY,verify,TARGET,timeout=90));parent=old.launch(a.code,c,a.PY,TARGET,'H1_closed_target72_native_only_parent_v1.py',spec);save('LATEST_H1_NEW_SOURCE_NATIVE180_ONLY_FINITE_PARENT_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=TARGET,source_SHA=spec['source_SHA'],source_Adamstep=spec['source_Adamstep'],native180_720_allrowCPU_required_not_yet_passed=True,native_only_no_production_GO_or_PPO_or_canonical_charge=True,no_new_budget_or_writer=True,old_O_final_actual_allout_original_account_settled_before_launch=True,original_all_guards_and_reward_physics_bytes_unchanged=True,stdin_only_config_not_saved_or_argv=True));print(json.dumps(dict(parent=parent,actual_new_native_only=True,source_Adam=spec['source_Adamstep'],zero_PPO_zero_charge=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('LATEST_H1_NATIVE_ONLY_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_before_any_new_retry=True));raise
