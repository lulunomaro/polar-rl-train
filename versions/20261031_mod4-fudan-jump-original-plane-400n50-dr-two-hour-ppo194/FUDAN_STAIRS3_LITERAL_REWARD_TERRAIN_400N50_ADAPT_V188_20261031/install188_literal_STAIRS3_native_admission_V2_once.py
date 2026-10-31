"""Root's finite serial lease: fresh72 readonly, close72, strict forwarded210.
Frozen evaluation only. No continuation, learner, optimizer or ledger writer.
"""
from pathlib import Path
import hashlib, importlib.util, json, os, posixpath, subprocess, sys, time, traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'install188_literal_STAIRS3_native_admission_V2_once|admit_delivered185|capture_delivered185|inspect_user_delivered_forward|find_existing_forwarded210_jump|inspect_forward210_|install_and_probe_A_original_fudan|collect_E3_source210|run_ROOT180_latest|run_ONE178_selected|collect_ONE178_original|install_NATIVE178|run_ROOT171_secure' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 cim=dict(epoch=time.time(),self_PID=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,actual_exact_CIM=rows,other_known_control_finites=others)
 put('ROOT188ADMITV2_FRESH_LOCAL_EXACT_CIM.json',cim)
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 assert own[0]['CreationDate'] and not others and time.time()-cim['epoch']<30
 frozen=json.loads((N/'TRAIN188_COMPLETE_MANIFEST.json').read_bytes())
 for row in frozen['files']:
  local=N/row['local_relative'];assert local.stat().st_size==row['bytes']
 put('ROOT188ADMITV2_FROZEN_MODEL_TARGET_PLAN_PURPOSE_CONSUMED.json',dict(epoch=time.time(),human_request='Latest: resume selected4999 with byte-literal 上台阶3 general reward and original Fudan trimesh stairs, own400N50/DR retained; this entry is necessary0PT admission only',new_GPU_model_decodes=0,CPU_checkpoint_decodes=0,old_H1_models=0,raw_old_cases=0,maximum_local_seconds=1100,worker_wait_seconds=900,source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),serial_lease='EXCLUSIVE_ROOT187',no_learning_or_budget_write=True))
 wrapper=module('root187V2_authorized_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install()
  sec=module('root187V2_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
  secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import json,time,hashlib
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');b=p.read_bytes();c=json.loads(b)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),readonly=True)))"""
  try:put('ROOT188ADMITV2_FRESH72_CNONE_READONLY.json',d.code(client,d.PY72,auth,{},timeout=45))
  finally:client.close();client=None
  client=route.connect()
  pre="""from pathlib import Path
import json,subprocess
b=Path(v['root']);assert str(b)=='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27'
m=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','-o','UUID,OPTIONS'],text=True))['filesystems'][0]
assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
b.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,root=str(b),UUID_rw_actual=m)))"""
  put('ROOT188ADMITV2_DURABLE_UUID_RW_FRESH_NAMESPACE.json',d.code(client,route.PY,pre,dict(root=ROOT),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in frozen['files']:
    rel=row['relative'];cur=ROOT
    for bit in posixpath.dirname(rel).split('/'):
     if not bit:continue
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(str(N/row['local_relative']),ROOT+'/'+rel)
  finally:sf.close()
  result=d.code(client,route.PY,(N/'remote188V2_postcopy_CPU_and_native_admission.txt').read_text(encoding='utf8'),dict(root=ROOT,files=frozen['files']),timeout=1030)
  put('ROOT188ADMITV2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json',result)
  value=result.get('result') or {}
  print(json.dumps(dict(passed_execution=result['passed_execution'],returncode=result['returncode'],controls=value.get('policy_controls'),true270_successful_cases=value.get('strict_successful_cases'),true270_cross_cases=value.get('strict_same_flight_cross_cases'),both_wheel_peak_m=value.get('maximum_common_both_wheel_peak_400Hz_m'),errors=result['worker_errors'],parent_error=result['parent_error'],full_UTF8_files=len(result['full_UTF8']))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT188ADMITV2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT188ADMITV2_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True));raise
