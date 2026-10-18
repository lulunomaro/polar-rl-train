"""Use fresh roots only after failed V1 parents and children actually exited."""
import deploy_two_idle_4090_linux_reward_frame_observations_once as old
from inventory_current_owned210_storage_readonly_once import *
import getpass
def main():
 prep=json.loads((R/'TWO_EXPERT_LINUX_V2_CALLABLE_LAUNCHER_CPU_REPAIR_ACTUAL.json').read_bytes());assert prep['callable_class_fixture_actual_passed'];by={x['expert']:x for x in prep['payloads']};prior=json.loads((R/'TWO_EXPERT_FIRST_LINUX_CURRENT_ACTUAL.json').read_bytes())
 for kind in ('E2','E3'):assert prior[kind]['rows']['OBSERVATION_PARENT_EXIT_ACTUAL.json']['actual_child_waited'] and not prior[kind]['own_processes'] and 'native120_observation/COMPLETE_ACTUAL.json' not in prior[kind]['rows']
 save('TWO_EXPERT_CORRECTED_LINUX_V2_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True,original_failures_kept_new_unused_roots=True));pw=getpass.getpass('72 GPU1 corrected finite observation V2 (hidden): ');results=[]
 try:
  for kind in ('E2','E3'):
   cfg=dict(old.S[kind],expert=kind,steps=120,no_PPO=True,case_id=kind+'_FIRST_LINUX_ACTUAL_REWARD_FRAME_NATIVE120_1810V2',source_SHA=by[kind]['source_SHA'],manifest_SHA=by[kind]['manifest_SHA'],worker_SHA=by[kind]['worker_SHA'],package_SHA=by[kind]['package']['SHA']);cfg['previous_failed_root']=cfg['root'];cfg['root']=cfg['root'][:-1]+'2';c=None
   try:
    c=a.t.connect() if cfg['host']=='210' else a.connect72(pw);py=cfg['python'];check=r'''
from pathlib import Path
import json,psutil,os
cfg=json.loads(CFG);B=Path(cfg['previous_failed_root']);v=json.loads((B/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());assert v['actual_child_waited'] and not (B/'native120_observation/COMPLETE_ACTUAL.json').exists();alive=[]
for p in psutil.process_iter(['pid','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):alive.append(p.pid)
 except psutil.Error:pass
assert not alive;print(json.dumps(dict(old_failed_root=str(B),actual_parent_child_all_out=True,old_error_retained=True)))
''';save(kind+'_LINUX_V1_ACTUAL_ERROR_EXIT_HANDOFF_BEFORE_V2.json',a.code(c,py,old.codefmt(check,cfg),timeout=60));save(kind+'_LINUX_V2_CURRENT_RESOURCE_REAL_LOCK_ADMISSION.json',a.code(c,py,old.codefmt(old.ADMIT,cfg),timeout=90));sf=c.open_sftp()
    try:sf.get_channel().settimeout(120);sf.put(by[kind]['package']['path'],cfg['root']+'/payload.zip')
    finally:sf.close()
    save(kind+'_LINUX_V2_TARGET_COMPLETE_SOURCE_RUNTIME_CPU_ACTUAL.json',a.code(c,py,old.codefmt(old.INSTALL,cfg),timeout=180));v=a.code(c,py,old.codefmt(old.LAUNCH,cfg),timeout=60);save(kind+'_LINUX_V2_REWARD_FRAME_DETACHED_ACTUAL.json',v);results.append(v)
   finally:
    if c:c.close()
 finally:pw=None
 save('TWO_EXPERT_LINUX_V2_CORRECTED_FINITE_DETACHED_ACTUAL.json',dict(epoch=time.time(),results=results,actual_transport_returned=True,no_H1_or_budget_or_original_error_mutation=True,no_E2_E3_paid_GO=True));print(json.dumps(dict(results=results,actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('TWO_EXPERT_LINUX_V2_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_rerun_or_live_patch=True));raise
