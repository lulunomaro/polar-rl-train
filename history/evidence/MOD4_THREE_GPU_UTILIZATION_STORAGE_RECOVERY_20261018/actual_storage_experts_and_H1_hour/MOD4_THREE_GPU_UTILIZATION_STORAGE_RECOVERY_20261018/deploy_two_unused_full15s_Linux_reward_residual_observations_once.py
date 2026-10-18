"""Start two unused full diagnostics after native recorded-CPU and actual resource handback."""
import deploy_two_idle_4090_linux_reward_frame_observations_once as base
from inventory_current_owned210_storage_readonly_once import *
import getpass
def main():
 prep=json.loads((R/'TWO_FULL15S_NEW_LINUX_REWARD_FRAME_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['native_recorded_source_and_physics_CPU_passed'];by={x['expert']:x for x in prep['payloads']};save('TWO_FULL15S_LINUX_DIAGNOSTIC_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_transport=True,no_H1_stop_or_paid_E2_E3_GO=True));pw=getpass.getpass('72 GPU1 full residual diagnostic (hidden): ');results=[]
 try:
  for kind in ('E2','E3'):
   cfg=dict(base.S[kind],expert=kind,steps=1500,no_PPO=True,case_id=kind+'_NEW_LINUX_FULL15S_REWARD_RESIDUAL_1810V1',source_SHA=by[kind]['source_SHA'],manifest_SHA=by[kind]['manifest_SHA'],worker_SHA=by[kind]['worker_SHA'],package_SHA=by[kind]['package']['SHA'],recorded_native_CPU_SHA=by[kind]['native_CPU_SHA']);cfg['previous_native_root']=cfg['root'][:-1]+'4';cfg['root']=cfg['root'][:-1]+'4f';c=None
   try:
    c=a.t.connect() if cfg['host']=='210' else a.connect72(pw);py=cfg['python'];check=r'''
from pathlib import Path
import json,psutil,os,time
cfg=json.loads(CFG);B=Path(cfg['previous_native_root']);e=json.loads((B/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());v=json.loads((B/'native120_observation/COMPLETE_ACTUAL.json').read_bytes());assert e['actual_child_waited'] and e['returncode']==0 and v['passed_data_contract'] and v['steps']==120 and v['checkpoint_sha256']==cfg['source_SHA'];assert not (B/'native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists();alive=[]
for p in psutil.process_iter(['pid','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):alive.append(p.pid)
 except psutil.Error:pass
assert not alive;print(json.dumps(dict(epoch=time.time(),actual_native_parent_children_out=True,same_source_native_completed=True,native_recorded_source_physics_CPU_SHA=cfg['recorded_native_CPU_SHA'],missing_native_E3_internal_fields_not_claimed_observed=True)))
''';save(kind+'_FULL15S_ACTUAL_NATIVE_CPU_SOURCE_EXIT_HANDOFF.json',a.code(c,py,base.codefmt(check,cfg),timeout=60));save(kind+'_FULL15S_CURRENT_RESOURCE_REAL_LOCK_ADMISSION.json',a.code(c,py,base.codefmt(base.ADMIT,cfg),timeout=90));sf=c.open_sftp()
    try:sf.get_channel().settimeout(120);sf.put(by[kind]['package']['path'],cfg['root']+'/payload.zip')
    finally:sf.close()
    install=base.INSTALL.replace("validate(ck);assert not torch.cuda.is_initialized();versions={}","validate(ck);assert not torch.cuda.is_initialized();proof=json.loads((B/'EXPECTED_ACTUAL_LINUX_DIAGNOSTIC_BACKEND_V1.json').read_bytes())['native_binding'];assert H(proof['path'])==proof['SHA'];versions={}")
    save(kind+'_FULL15S_TARGET_SOURCE_INSTALLED_LINUX_BACKEND_CPU_ACTUAL.json',a.code(c,py,base.codefmt(install,cfg),timeout=180));v=a.code(c,py,base.codefmt(base.LAUNCH,cfg),timeout=60);save(kind+'_LINUX_NEW_FULL15S_REWARD_RESIDUAL_DETACHED_ACTUAL.json',v);results.append(v)
   finally:
    if c:c.close()
 finally:pw=None
 save('TWO_EXPERT_NEW_LINUX_FULL15S_DIAGNOSTICS_DETACHED_ACTUAL.json',dict(epoch=time.time(),results=results,actual_transport_returned=True,not_full_data_PASS_or_three_PPO=True,H1_not_stopped_or_modified=True,E2_E3_no_paid_GO_zero_charge=True));print(json.dumps(dict(results=results,actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('TWO_FULL15S_DIAGNOSTIC_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_rerun_or_live_patch=True));raise
