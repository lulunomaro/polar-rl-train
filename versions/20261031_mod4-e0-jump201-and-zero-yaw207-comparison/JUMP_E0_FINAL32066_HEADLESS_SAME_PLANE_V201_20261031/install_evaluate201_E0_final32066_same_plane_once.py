"""Root's finite serial lease: fresh72 readonly, close72, strict forwarded210.
Frozen evaluation only. No continuation, learner, optimizer or ledger writer.
"""
from pathlib import Path
import hashlib, importlib.util, json, os, posixpath, subprocess, sys, time, traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 source=N.parent/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
 closed=json.loads((source/'reports/ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
 cpu=json.loads((source/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
 task=json.loads((N/'TASK201.json').read_bytes())
 assert closed['passed_collection'] and closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
 assert closed['roles']['e0_72']['qualified_formal'] and cpu['passed'] and cpu['roles']['e0_72']['passed']
 assert closed['formals']['e0_72']['SHA']==cpu['roles']['e0_72']['SHA']==task['model_SHA']
 assert cpu['roles']['e0_72']['saved_iteration']==32066
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'install_evaluate201_E0_final32066_same_plane_once|collect197_original_two_role_formals|launch197_unified_194_remaining|human199_main197_one_saved_status|install198_E0_72_source_CPU|request197_original194_saved|collect194_original|start195_literal|collect195_original|install195_literal' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 cim=dict(epoch=time.time(),self_PID=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,actual_exact_CIM=rows,other_known_control_finites=others)
 put('ROOT201V2_FRESH_LOCAL_EXACT_CIM.json',cim)
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 assert own[0]['CreationDate'] and not others and time.time()-cim['epoch']<30
 frozen=json.loads((N/'FROZEN_EVAL201_COMPLETE_MANIFEST.json').read_bytes())
 for row in frozen['files']:
  local=N/row['local_relative'];assert local.stat().st_size==row['bytes']
 put('ROOT201V2_FROZEN_MODEL_TARGET_PLAN_PURPOSE_CONSUMED.json',dict(epoch=time.time(),human_request='Assess trained E0 branch32066 in one same-condition original-JUMP plane first episode; no GUI switch',new_GPU_model_decodes=1,CPU_checkpoint_decodes=0,old_H1_models=0,raw_old_cases=0,maximum_local_seconds=1100,worker_wait_seconds=900,source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),serial_lease='EXCLUSIVE_ROOT201',no_learning_or_budget_write=True))
 wrapper=module('root201V2_authorized_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install()
  sec=module('root201V2_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
  secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import json,time,hashlib,subprocess,psutil,shutil
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');b=p.read_bytes();c=json.loads(b)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),readonly=True)))"""
  try:put('ROOT201V2_FRESH72_CNONE_READONLY.json',d.code(client,d.PY72,auth,{},timeout=45))
  finally:client.close();client=None
  client=route.connect()
  pre="""from pathlib import Path
import json,subprocess
b=Path(v['root']);assert str(b)=='/mnt/mod4_linux_durable_20261013/MOD4_E0_FINAL32066_SAME_PLANE_HEADLESS_20261031v201'
m=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','-o','UUID,OPTIONS'],text=True))['filesystems'][0]
assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
b.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,root=str(b),UUID_rw_actual=m)))"""
  put('ROOT201V2_DURABLE_UUID_RW_FRESH_NAMESPACE.json',d.code(client,route.PY,pre,dict(root=ROOT),timeout=30))
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
  result=d.code(client,route.PY,(N/'remote201_postcopy_and_frozen_capture.txt').read_text(encoding='utf8'),dict(root=ROOT,files=frozen['files']),timeout=1030)
  put('ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json',result)
  if result['passed_execution']:
   artifact=result['result']['artifact'];dest=N/'captured'/Path(artifact['path']).name;dest.parent.mkdir(exist_ok=False)
   sf=client.open_sftp()
   try:sf.get(artifact['path'],str(dest))
   finally:sf.close()
   with dest.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
   assert dest.stat().st_size==artifact['bytes'] and sha==artifact['SHA']
   put('ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json',dict(passed=True,source=artifact,path=str(dest),bytes=artifact['bytes'],SHA=sha,transfers=1,two_host_SHA_equal=True,visual_content_not_yet_decoded=True))

  value=result.get('result') or {}
  print(json.dumps(dict(passed_execution=result['passed_execution'],returncode=result['returncode'],worker=result['actual_worker_identity'],controls=value.get('policy_controls'),true270_successful_cases=value.get('strict_successful_cases'),true270_cross_cases=value.get('strict_same_flight_cross_cases'),both_wheel_peak_m=value.get('maximum_common_both_wheel_peak_400Hz_m'),errors=result['worker_errors'],parent_error=result['parent_error'],full_UTF8_files=len(result['full_UTF8']))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT201V2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT201V2_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True));raise
