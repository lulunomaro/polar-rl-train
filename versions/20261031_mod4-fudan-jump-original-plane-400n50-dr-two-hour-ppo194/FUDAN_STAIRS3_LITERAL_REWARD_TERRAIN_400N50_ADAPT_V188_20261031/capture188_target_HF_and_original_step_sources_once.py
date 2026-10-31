"""Human requested existing other-AI jump model on original forwarded4090.
Read-only filename/stat inventory. No checkpoint bytes/hash/load, SDK/GPU or training.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/"reports";R.mkdir(exist_ok=True)
def put(name,v):
 with (R/name).open("x",encoding="utf8") as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import json,time,hashlib
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');b=p.read_bytes();c=json.loads(b)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
a=c['active_segment']
active=None if a is None else {k:a.get(k) for k in ('owner_parent_pid','kind','started_epoch','accounted_through_epoch')}
if active is not None:active['expert_keys']=list(a.get('experts',{}))
print(json.dumps(dict(epoch=time.time(),canonical_None=a is None,actual_active_owner_summary=active,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),no_account_write=True)))"""
REMOTE="from pathlib import Path\nimport importlib.util,json,time,hashlib\nroot=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))\npaths=[root/'terrains/height_field/hf_terrains.py',root/'terrains/height_field/hf_terrains_cfg.py',root/'terrains/height_field/utils.py',Path('/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/repo/isaac/mod4/mod4_env.py'),Path('/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/repo/isaac/mod4/mild_dr.py')]\nrows=[]\nfor p in paths:\n if not p.is_file():rows.append(dict(path=str(p),exists=False));continue\n b=p.read_bytes();rows.append(dict(path=str(p),exists=True,bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),byte_reads=1))\nprint(json.dumps(dict(epoch=time.time(),purpose='Bind unchanged original STAIRS3 general reward and terrain to existing400N50 Lab runtime; source-only installed API metadata',files=rows,source_files_read=sum(x['exists'] for x in rows),SDK_Torch_imports=0,model_reads=0,physics_GPU_or_learning_calls=0,no_remote_writes=True)))\n"
def main():
 q=r"""Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'capture188_target_HF_and_original_step_sources_once|install_evaluate187_totalplan_frozen_once|inspect_forward210_|install_and_probe_A_original_fudan|fudan184|find_existing_forwarded210_jump|collect_E3_source210|run_ONE178_selected|collect_ONE178_original' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"""
 p=subprocess.run(["pwsh.exe","-NoProfile","-Command",q],capture_output=True,text=True,encoding="utf8",check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 other=[x for x in rows if x["ProcessId"]!=os.getpid()]
 cim=dict(epoch=time.time(),self_PID=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,actual_exact_CIM=rows,other_known_finites=other)
 put("ROOT188API_FRESH_LOCAL_EXACT_CIM.json",cim);assert not other and time.time()-cim["epoch"]<30
 put("ROOT188API_EXISTING_JUMP_FILENAME_METADATA_PURPOSE_CONSUMED.json",dict(epoch=time.time(),
  human_instruction="Latest human selects original 上台阶3 general reward byte-literal and original Fudan stairs terrain, then continuation under400N50 total-plan DR",
  route="10.24.5.27:4090 -> original210 inner22",checkpoint_content_reads=0,checkpoint_decode_limit=0,maximum_s=200,
  no_GPU_or_learning_or_account_write=True,source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
 wrapper=module("root185_session",T/"H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py")
 sys.path.insert(0,str(W/"MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021"));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/"MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025"));import strict_user_forwarded_original210_transport_v1 as route
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install()
  sec=module("root185_memory_auth",W/"MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py")
  secret=sec.recover();client=d.connect72(secret);secret=None
  try:put("ROOT188API_FRESH72_CURRENT_AUTHORITY_READONLY.json",d.code(client,d.PY72,AUTH,{},timeout=45))
  finally:client.close();client=None
  client=route.connect();result=d.code(client,route.PY,REMOTE,{},timeout=140)
  put("ROOT188API_ORIGINAL_FORWARD210_MODEL_FILENAME_INVENTORY_ACTUAL.json",result)
  print(json.dumps(dict(source_files=result['source_files_read'],model_reads=result['model_reads'],SDK_Torch_imports=result['SDK_Torch_imports'])),flush=True)
 finally:
  secret=None
  if client:client.close();client=None
  if transport:transport.SESSION=previous
  put("ROOT188API_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json",dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_lease="FREE"))
if __name__=="__main__":
 try:main()
 except BaseException:
  put("ROOT188API_ORIGINAL_ERROR_"+str(time.time_ns())+".json",dict(error=traceback.format_exc(),no_automatic_retry=True));raise

