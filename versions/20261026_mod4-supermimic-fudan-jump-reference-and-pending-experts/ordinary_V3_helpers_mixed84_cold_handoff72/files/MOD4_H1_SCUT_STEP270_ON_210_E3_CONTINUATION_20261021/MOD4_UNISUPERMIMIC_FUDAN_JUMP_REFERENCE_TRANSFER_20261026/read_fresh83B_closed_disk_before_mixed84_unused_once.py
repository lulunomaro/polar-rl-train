from pathlib import Path
import importlib.util,json,sys,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('FRESH83B_CLOSED_DISK_BEFORE84_STARTED_ACTUAL.json',dict(epoch=time.time(),read_only=True,no_GPU_or_model_or_raw_read=True))
 p=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py';s=importlib.util.spec_from_file_location('defs_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);d=m.d
 q=json.loads((T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None;result={}
 try:
  c=d.connect72(secret)
  result['72']=d.code(c,d.PY72,"import shutil,json,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/tasks').free)))",{},timeout=30);c.close();c=None
  c=d.t.connect()
  source="from pathlib import Path;import json,psutil,shutil,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=C.read_bytes();c=json.loads(b);assert c['active_segment'] is None and c['remaining_training_seconds']==595256.8240613937;B=Path(v['owner_root']);assert json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=v['owner_identity'];alive=False\ntry:\n p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01\nexcept psutil.NoSuchProcess:pass\nassert not alive;assert C.read_bytes()==b;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,canonicalNone=True,remaining=c['remaining_training_seconds'],previous_owner_actual_out=True)))"
  result['210']=d.code(c,d.t.PY,source,dict(owner_root=q['owner_root'],owner_identity=q['owner_identity']),timeout=30);c.close();c=None
  put('FRESH83B_CLOSED_DISK_BEFORE84_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,hosts=result));print(json.dumps(result))
 except BaseException:
  put('FRESH83B_CLOSED_DISK_BEFORE84_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial=result));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
