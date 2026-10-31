"""One ROOT-leased72 staging/0PT admission. No owner/GO/model load/training."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,posixpath,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209/e0_72'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False,ensure_ascii=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args()
 assert args.root_lease_label.startswith('ROOT209_EXCLUSIVE_ADMISSION_')
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'install209_mixed_target80_admission_once|human196_194_one_saved_progress|collect194_original|start194_literal|install194_literal|install195_literal|start195_literal|collect195_original|run197_|start197_|control197_|run189_W35_saved_cycle|install_capture193_|install_evaluate191_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 proc=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(proc.stdout) if proc.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ACTUAL209_ADMIT_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_control_finites=other))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 proof=json.loads((R/'ROOT209_MIXED_SOURCE_AND_TaskGO_CPU_ACTUAL.json').read_bytes());assert proof['passed']
 manifest=json.loads((N/'PACKAGE209_MANIFEST.json').read_bytes());mh=H(N/'PACKAGE209_MANIFEST.json')
 for row in manifest['files']:
  p=N/row['local_relative'];assert p.stat().st_size==row['bytes']
  if p.suffix.lower() not in ('.usd','.usda','.npz','.npy'):assert H(p)==row['SHA']
 binding=None
 task=json.loads((N/'package/TASK209.json').read_bytes())
 put('ACTUAL209_ADMIT_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),root_exclusive_lease_label=args.root_lease_label,
  scope='Only72 current194 authority check, new source stage, sourceCPU and64env0PT admission. No learning or owner creation.',
  local_entry_SHA=H(Path(__file__)),manifest_SHA=mh,maximum_local_seconds=1300,
  maximum_actual_GPU0PT_worker_wait_seconds=900,model_checkpoint_reads=0,raw_case_or_reference_reads=0,
  maximum_source_asset_postcopy_integrity_passes=1,reset_NPZ_constructor_only_paths=['payload/job0/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'],
  no_extra_NPZ_decode_beyond_original_constructor=True,known_E0_input_stat_only=True,
  GPU_resource_queries_without_PID_only=True,global_serial_lease='EXCLUSIVE209_UNTIL_FINALLY'))
 wrapper=module('e0_209_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install();secure=module('e0_209_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=secure.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import hashlib,json,time
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),passed=True,canonical_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],no_canonical_write=True)))"""
  put('ACTUAL209_FRESH72_CURRENT194_BINDING_BEFORE_STAGE.json',d.code(client,d.PY72,auth,dict(binding=binding),timeout=45))
  create="""from pathlib import Path
import json,psutil,shutil,time
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B==owned/'tasks/MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209/e0_72' and B.resolve().is_relative_to(owned)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned/'tasks').free>25*1024**3
B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(epoch=time.time(),passed=True,new_owned_root=str(B),RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(B).free,source_model_bytes=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72/production/model_final_complete.pt').stat().st_size,no_model_or_GPU_read=True)))"""
  put('ACTUAL209_NEW72_TASK_NAMESPACE_CREATED.json',d.code(client,d.PY72,create,dict(root=REMOTE),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in manifest['files']:
    rel=row['relative'];cur=REMOTE
    for bit in posixpath.dirname(rel).split('/'):
     if not bit:continue
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(str(N/row['local_relative']),REMOTE+'/'+rel)
   sf.put(str(N/'PACKAGE209_MANIFEST.json'),REMOTE+'/PACKAGE209_MANIFEST.json')
  finally:sf.close()
  result=d.code(client,d.PY72,(N/'remote209_source_CPU_and_mixed_native80_admission.txt').read_text('utf8'),dict(root=REMOTE,files=manifest['files'],manifest_SHA=mh,
    source_CPU_proof=dict(path=task['source_fullstate_CPU_report'],SHA=task['source_fullstate_CPU_report_SHA'],source_SHA=task['source_SHA'],Adam17=641200,RSL=32094,actual_35_38_6_finite=True)),timeout=1110)
  put('ACTUAL209_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json',result)
  selected=result.get('admission') or {}
  print(json.dumps(dict(passed=result['passed_execution'],selected_GPU=selected.get('selected_GPU'),resource=selected.get('resource'),actual_controls=selected.get('actual_native_controls'),physics=selected.get('actual_physics_callbacks'),feedback=selected.get('actual_feedback_samples'),waited=result['all_own_children_waited'],private_EX_released=result['private_EX_released'],source_model_loads=0),ensure_ascii=False),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ACTUAL209_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE',GPU_resource_release_only_as_proved_by_original_wait_report=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ACTUAL209_ADMIT_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
