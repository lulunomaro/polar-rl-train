"""ONE first actual fixed92W35 PPO metadata reader; no PT/GPU/ledger mutation."""
from pathlib import Path
import sys,json,time,os,threading,traceback,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent;R=HERE/'reports'
CODE=r"""from pathlib import Path
import json,time,psutil
v0=v['request'];J=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_RETENTION_2610v92/w35');B=Path(v0['owner_root']);N=Path(v0['node_root']);O=J/'adaptation'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def own(expected):
 try:
  p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'],'own PID recycled'
  q=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert all(q[k]==expected[k] for k in ['exe','argv','root']);return q
 except psutil.NoSuchProcess:return None
start=time.time()
while True:
 owner=own(v['actual']['owner']);node=own(v['actual']['node']);go=read(J/'GO_PRODUCTION.json');full=read(O/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json');native=read(O/'CLOCK_GAS400_NATIVE24_ACTUAL.json');preload=read(O/'GAS400_ORIGINAL_PRELOAD_ACTUAL_FIRST_PREWRITE.json');positive=read(O/'PPO_POSITIVE_CURRENT.json');current=read(B/'OWNER_CURRENT.json') or {}
 errors=[dict(path=str(p),text=p.read_text()) for root in [B,N,O] for p in sorted(root.glob('*ORIGINAL_ERROR*.json'))]
 value=dict(epoch=time.time(),passed_first_W35_real_PPO=False,go=go,fullrestore=full,native24=native,preload=preload,positive_PPO=positive,original_errors=errors,owner=owner,node=node,no_model_read_or_hash_no_GPU_or_accountwrite=True,not_skill_or_WM_dataset=True)
 if go:
  assert go['run_id']==v0['run_id'] and go['source_SHA']=='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393' and go['source_CPU_SHA']=='0bb31d204681f83039e748dee8b317118892f3d6533b6a9417fbdee464dcf9a8' and go['original_owner_pid']==v['actual']['owner']['pid']
  assert go['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and go['num_envs']==20000 and go['policy_hz']==50
 if positive:
  n=positive['new_updates'];assert owner and node and go and n>=1 and positive['Adam_step']==646800+20*n and positive['not_skill_qualified'] is True
  assert full['original_actor9_critic8_STD_17Adam_LR_D1_D7_exact'] is True and full['actual_algorithm_learning_rate']==.00001 and full['W35_retained_command_and_G3_state_restored'] is True
  assert native['passed'] is True and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and native['actual_RewardManager_dt_s']==.02 and native['no_optimizer_update'] is True
  assert preload['actual_original_preload'] is True and preload['nominal_force_N_each']==400 and not errors
  value['passed_first_W35_real_PPO']=True
  value['normal900_earliest_epoch']=go['nominal_end_epoch']-900
  value['startup_receipt_values']=[dict(path=r['path'],value=read(Path(r['path']))) for r in full['receipts']]
  print(json.dumps(value));break
 if errors or not owner or not node or time.time()-start>=780:
  value['node_current']=read(N/'NODE_CURRENT.json');value['owner_current']=current;print(json.dumps(value));break
 time.sleep(3)
"""
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1;save('FIXED92_W35_FIRST_OBSERVER_CONSUMED_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve())))
 A=L/'W35_fixed92_single72_owner_source_v2';request=json.loads((A/'reports/W35_FIXED92_ACTUAL_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((A/'reports/W35_FIXED92_OWNER_NODE_LAUNCHED_ACTUAL.json').read_bytes())
 p=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';sp=importlib.util.spec_from_file_location('same_authorized_zstd_memory_fixed92first',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);t,old=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_fixed92first',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_FIXED92_FIRST_OBSERVER_WAIT',epoch=time.time())),flush=True)
 threading.Thread(target=progress,daemon=True).start()
 try:
  c=d.connect72(secret);secret=None;value=d.code(c,d.PY72,CODE,dict(request=request,actual=actual),timeout=810);save('FIXED92_W35_FIRST_ACTUAL_FULLRESTORE_NATIVE24_PPO_RETURNED_ACTUAL.json',value);print(json.dumps(dict(actual_finite_returned=True,passed_first_W35_real_PPO=value['passed_first_W35_real_PPO'],go=value.get('go'),positive=value.get('positive_PPO'))))
 finally:
  secret=None;stop.set()
  if c:c.close()
  t.SESSION=old
if __name__=='__main__':
 try:main()
 except BaseException:save('FIXED92_W35_FIRST_OBSERVER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_other_watcher=True));raise
