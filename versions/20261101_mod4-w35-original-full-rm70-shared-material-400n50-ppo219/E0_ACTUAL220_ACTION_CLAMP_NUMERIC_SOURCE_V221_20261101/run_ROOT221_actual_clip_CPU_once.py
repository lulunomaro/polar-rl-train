"""ROOT one new numerical artifact purpose; no evaluation/model/GPU repeat."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
Q=T/'E0_NEW210_FORMAL_MEAN_PLANE_FLIGHT_SOURCE_V220_20261101'
J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_CLIP221_NUMERIC_20261101/review'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EXEC="""from pathlib import Path
import contextlib,hashlib,io,json,runpy,sys,time,traceback
B=Path(v['job']);p=B/'diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()==v['SHA']
out=B/'actual221';capture=io.StringIO();error=None
try:
 sys.argv=[str(p),'--out-new',str(out)]
 with contextlib.redirect_stdout(capture):runpy.run_path(str(p),run_name='__main__')
except BaseException:error=traceback.format_exc()
result=out/'ACTUAL221_ACTION_CLAMP_Q_ROOT_NUMERIC.json';value=json.loads(result.read_bytes())if result.is_file()else None
texts=[]
for p in sorted(out.glob('*.json'))if out.is_dir()else[]:
 raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),passed=bool(not error and value and value['diagnostic_execution_passed']),result=value,error=error,full_UTF8=texts,
 model_GPU_SDK_or_account_calls=0,artifact_transfers=0,GUI=False)))
"""
def main():
 assert H(N/'INDEX221_FROZEN.json')=='fb2859380c0b69cf8dda35e389fd943d92b0f474e437504583f0520628b24d5e'
 p=N/'diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py';assert H(p)=='0f52299636bad2e0a1d90bee17d0ab4a3ef52cb6cd24b89445a2ec75c9dfbd70'
 assert read(Q/'reports/ROOT220V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 case=read(Q/'reports/ROOT220V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json')
 assert case['original_parent']['result']['passed']and case['original_parent']['wait']['returncode']==0
 binding=read(Q/'ROOT220_TASK_ACTUAL_32341_V2/TASK220.json')['current_authority_binding']
 source=ast.parse((Q/'run_ROOT220V2_qualified_actor_case_once.py').read_bytes())
 auth=ast.literal_eval(next(n.value for n in source.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='AUTH'for x in n.targets)))
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run_ROOT221_actual_clip_CPU_once|run_ROOT220V2_|launch219V3_|collect219V3_|collect210_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT221_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,others=others))
 assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT221_NEW_ARTIFACT_NUMERIC_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),contract=read(R/'ROOT221_MINIMAL_UNUSED_CPU_READ_CONTRACT.json'),
  original220_parent_false_preserved=True,original220_rollout_not_replayed=True,source_SHA=H(p),no_new_model_GPU_or_SDK=True))
 wrapper=module('numeric221_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('numeric221_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret)
  put('ROOT221_FRESH72_EXACT_CURRENT219_BEFORE_CPU.json',d.code(client,d.PY72,auth,dict(binding=binding),timeout=45))
  client.close();client=None;client=d.connect72(secret);secret=None
  create="""from pathlib import Path
import json
B=Path(v['job']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,new_root=str(B))))"""
  put('ROOT221_NEW_CPU_NAMESPACE.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
  sf=client.open_sftp()
  try:sf.put(str(p),J+'/'+p.name)
  finally:sf.close()
  actual=d.code(client,d.PY72,EXEC,dict(job=J,SHA=H(p)),timeout=90)
  put('ROOT221_ACTUAL_NEW_NPZ_ACTION_CLAMP_NUMERIC_RETURNED.json',actual)
  a=(actual.get('result')or{}).get('analysis')or{}
  print(json.dumps(dict(passed=actual['passed'],error=actual['error'],channels=a.get('raw_action_channels'),
   clip_residual=a.get('clip6_reordered_global_max_abs_residual'),root_reference=a.get('root_reference'),authored_bottom=a.get('authored_bottom_reference'))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT221_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT221_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
