from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';B=N/'payload'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90b/h1'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

PRE=r'''from pathlib import Path,PurePosixPath
import json,hashlib,fcntl,psutil,subprocess,shutil,time
B=Path(v['root']);old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90/h1')
owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert str(B)==v['root'] and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==558110.3183145523 and c['remaining_training_seconds']>86412.86069250107
locks=[C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock']
for path in locks:
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
e0=owned/'MOD4_E0_PPO50_GAS400_2610v89d';final=json.loads((e0/'owner/COHORT_FINAL.json').read_bytes());node=json.loads((e0/'node_e0/NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert final['original_cost_settled'] and node['terminal_all_own_children_waited'] and node['original_error'] is False and node['returncode']==0 and node['final']['passed']
go=final['go']['e0'];assert go['original_owner_pid']==544164 and go['original_owner_creation']==1793101424.86
segments=[x for x in c['completed_segments'] if x['owner_parent_pid']==544164 and x['experts']['e0']['started_epoch']==go['learning_started_epoch']];assert len(segments)==1 and segments[0]['charged_expert_seconds']==3664.132122516632
own=[]
for row in v['known_own']:
 try:
  p=psutil.Process(row['pid']);creation=p.create_time()
  if creation==row['creation']:assert p.status()==psutil.STATUS_ZOMBIE,'known original own process still executing'
  own.append(dict(pid=row['pid'],out_or_nonexecuting=True,no_foreign_identity_read=True))
 except psutil.NoSuchProcess:own.append(dict(pid=row['pid'],out=True))
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;prior=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if prior and prior['bytes']==row['bytes'] and prior['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:
  shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=dict(GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),C_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],own=own,no_account_write=True,no_GO=True)))'''

CPU=r'''from pathlib import Path
import sys,json,hashlib,time,importlib.util,importlib.metadata
B=Path(v['root']);old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90/h1')
sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps')]
from native_flat90_source_guard_v1 import check_payload,H
base=old/'job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json';proof=old/'job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json'
assert H(base)=='ff20606386aefd53d53e81599d24e020c97e375be453d30263832a46e25734f8' and H(proof)=='85ba6639d3106a9e689cb96a362831bad296b6aea8ccaf1b54625569e5d97a68'
oldmf=json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());newmf=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());a={r['relative']:r for r in oldmf['files']};b={r['relative']:r for r in newmf['files']};assert set(a)==set(b)
changed={rel for rel in a if a[rel]!=b[rel]};assert changed=={'native_flat90_source_guard_v1.py','job0/TASK.json','FLAT90_SOURCE_CONTRACT_ACTUAL.json'}
assert (old/'native_flat90_source_guard_v1.py').read_text().replace("go['manifest_SHA']==manifest_SHA","go['payload_manifest_SHA']==manifest_SHA")== (B/'native_flat90_source_guard_v1.py').read_text()
c0=json.loads((old/'FLAT90_SOURCE_CONTRACT_ACTUAL.json').read_bytes());c1=json.loads((B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json').read_bytes());c0['approved_python']['native_flat90_source_guard_v1.py']=H(B/'native_flat90_source_guard_v1.py');assert c0==c1
checked=check_payload(B);assert checked['manifest_SHA']==v['manifest_SHA']
oldc=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes());sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
for r in oldc['expected_actual_RSL_sources']:assert H(rsl/r['relative'])==r['SHA']
for rel,key in [('utils/math.py','expected_actual_SDK_math_SHA'),('managers/observation_manager.py','expected_actual_SDK_observation_manager_SHA'),('assets/articulation/base_articulation_data.py','expected_actual_SDK_base_articulation_data_SHA')]:assert H(sdk/rel)==oldc[key]
assert {k:importlib.metadata.version(k) for k in ('isaaclab','rsl-rl-lib','torch')}==oldc['expected_installed_versions']
value=json.loads(base.read_bytes());value.update(payload_manifest_SHA=v['manifest_SHA'],source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),initial_loads=dict(native88C=0,normal86=0),actual_source_SDK_CPU_passed=True,actual_source_extension_of_passed90=True,base_actual_CPU_SHA=H(base),base_actual_wait_SHA=H(proof),no_input_model_reread_decode=True,new_source_only_exact_GO_guard_key_and_namespace=True)
report=B/'job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json'
with report.open('x') as f:json.dump(value,f,indent=2)
import psutil
p=psutil.Process();identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
print(json.dumps(dict(passed=True,value=value,extension_current_identity=identity,report_SHA=H(report),base_actual_CPU_SHA=H(base),base_actual_wait_SHA=H(proof),actual_source_extension_not_new_model_CPU=True)))'''

def main():
 put('FLAT90B_INSTALL_SOURCE_EXTENSION_CONSUMED_ACTUAL.json',dict(epoch=time.time(),new_actual_source_CPU_purpose=True,no_GO=True))
 prep=json.loads((R/'FLAT90B_PAYLOAD_SOURCE_PREPARED_ACTUAL.json').read_bytes());manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 first=json.loads((T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_FIRST_ACTUAL_4090_PPO_V5_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json').read_bytes())
 known=[dict(pid=x['pid'],creation=x['creation']) for x in first['snapshot']['known_own_processes']]
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  resource=d.code(c,d.PY72,PRE,dict(root=REMOTE,manifest=manifest,known_own=known),timeout=120);put('FLAT90B_ACTUAL_PRECOPY_RESOURCE_RETURNED.json',resource)
  sf=c.open_sftp();sf.get_channel().settimeout(300)
  try:
   for row in resource['need_upload']:sf.put(str(B/row['relative']),REMOTE+'/'+row['relative'])
   sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),REMOTE+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  result=d.code(c,d.PY72,CPU,dict(root=REMOTE,manifest_SHA=prep['manifest_SHA']),timeout=180)
  put('FLAT90B_ACTUAL_SOURCE_SDK_EXTENSION_RETURNED_ACTUAL.json',dict(**result,resource=resource,actual_finite_returned=True))
  assert result['passed'],result
  print(json.dumps(dict(actual_CPU_passed=True,CPU_SHA=result['report_SHA'],source_extension_only=True,no_GO=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90B_INSTALL_SOURCE_EXTENSION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_GO=True));raise
