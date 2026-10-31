"""One necessary cross-effect check of the shared material code, savedJSON only.
No new watcher/model/physics/GPU resource query or E0 intervention.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);sys.modules[name]=m;q.loader.exec_module(m);return m
def main():
 assert read(T/'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101/reports/ROOT216_EXIT_COLLECTION_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 launch=read(S/'reports/ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json');state=read(S/'reports/ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
 e0=S/'package/payload/job0/runtime/isaac/mod4/mild_dr.py'
 w35=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/mild_dr.py'
 source_compare=dict(E0=str(e0),W35=str(w35),E0_SHA=H(e0),W35_SHA=H(w35),byte_identical=H(e0)==H(w35))
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'ROOT_compare214_E0_saved_updates_after_W35_material_failure_once|collect216_|terminate216_|stop215_|launch210_|collect210_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT214_E0_COMPARE_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,others=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT214_E0_MATERIAL_CROSS_EFFECT_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),scope='Actual peer material-limit failure; check saved E0 counters and source equality, no generic healthy polling',
  source_comparison=source_compare,saved_small_JSON_opens=2,models_raw_SDK_GPU_queries=0,owner_fresh_exact_binding=True,E0_writes_or_signals=0))
 wrapper=module('material214_compare_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 transport=None;prior=None;client=None;secret=None
 try:
  transport,prior=wrapper.install();sec=module('material214_compare_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import json,hashlib,time
O=Path(v['owner']['root']);J=Path(v['job']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());cur=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert c['active_segment']['owner_parent_pid']==v['owner']['pid'] and cur['go']==v['go']
reports={}
for name in ['LATEST_PROGRESS.json','latest_complete.json']:
 p=J/'production'/name;raw=p.read_bytes();reports[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),value=json.loads(raw))
print(json.dumps(dict(epoch=time.time(),passed_binding=True,source_model_reads=0,GPU_queries=0,E0_not_modified=True,reports=reports,original_owner_rows=cur['rows'])))"""
  result=d.code(client,d.PY72,code,dict(owner=launch['owner'],job=launch['specs']['e0_72']['job_root'],go=state['current']['go']),timeout=45)
  put('ROOT214_E0_SAVED_UPDATES_SOURCE_COMPARISON_ACTUAL.json',dict(source_compare=source_compare,result=result))
  print(json.dumps(dict(source_mild_DR_identical=source_compare['byte_identical'],progress=result['reports']['LATEST_PROGRESS.json']['value'],latest_complete=result['reports']['latest_complete.json']['value'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=prior
  put('ROOT214_E0_COMPARE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is prior,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT214_E0_COMPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
