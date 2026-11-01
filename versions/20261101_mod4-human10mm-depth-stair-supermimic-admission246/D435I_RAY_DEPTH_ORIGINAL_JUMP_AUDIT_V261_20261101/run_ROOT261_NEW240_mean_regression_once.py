"""ROOT model-free ray depth admission; bind current actual Robot/links/chassis."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';S=N/'source'
J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_D435I_FORWARD_RAY_DEPTH261_20261101/case'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import hashlib,json,time
raw=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]and c['active_segment']is None
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_writes=0)))"""
EXEC="""from pathlib import Path
import contextlib,hashlib,io,json,runpy,sys,time,traceback
B=Path(v['job'])
for r in v['files']:
 b=(B/r['relative']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA']
capture=io.StringIO();error=None
try:
 sys.argv=[str(B/'target261_single_N1_parent_UNUSED.py'),'--task',str(B/'TASK261.json')]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
if error:
 with(B/'ROOT261_REMOTE_WRAPPER_ORIGINAL_ERROR.json').open('x',encoding='utf8')as f:json.dump(dict(error=error,no_auto_retry=True),f,indent=2)
p=B/'ACTUAL261_ORIGINAL_PARENT_RETURNED.json';value=json.loads(p.read_bytes())if p.is_file()else None
texts=[]
for folder in(B,B/'actual_capture'):
 for p in sorted(folder.iterdir())if folder.is_dir()else[]:
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed_execution=bool(not error and value and value['passed_execution']),original_parent=value,wrapper_error=error,
 original_parent_stdout=capture.getvalue(),full_UTF8=texts,model_copies=0,artifact_transfers=0,GUI=False)))"""
def main():
 assert sys.version_info[:2]==(3,14)
 p=argparse.ArgumentParser();p.add_argument('--source-index-SHA',required=True);a=p.parse_args()
 idx=N/'INDEX261_NEW240_MEAN_REGRESSION_FROZEN.json';assert H(idx)==a.source_index_SHA
 for r in read(idx)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and H(f)==r['SHA']
 assert read(R/'ROOT261_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json')['passed']
 C=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101'
 close=read(C/'reports/ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu=read(C/'reports/ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
 contract=module('root261_qualified_contract',S/'contract261.py');q=contract.qualified240(close,cpu)
 assert read(C/'reports/ROOT240V2_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 pattern='run_ROOT261_|run_ROOT260_|run_ROOT258_|run_ROOT257_|run_ROOT256_|run_ROOT254_|read253_|read252_|read251_|run_ROOT250_|read248_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_ROOT240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 r=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(r.stdout)if r.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT261_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 task=dict(kind=contract.KIND,model_path=q['path'],model_SHA=q['SHA'],model_bytes=q['bytes'],model_iteration=q['iteration'],actual_17Adam_step=q['Adam17'],source_parent_SHA=contract.PARENT_SHA,
  closure_threshold_m=.01,mimic_threshold_rad=.01,human_requested_closure_change=True,actual_closed240_qualification=q,source240_formal_CPU_actual_passed=True,qualified240_package_root=read(C/'reports/INSTALL240_SOURCE_ASSET_MANIFEST.json')['job_root'],
  GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',num_envs=1,controls_per_case_max=12,controls_max=12,physics_callbacks_max=96,feedback_samples_max=24,
  policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],worker_seconds=720,parent_wait_seconds=900,
  current_authority_binding=dict(kind='FRESH_CNONE',authority_generation='MOD4_SINGLE_WRITER72_20261026'),model_byte_reads=0,model_decodes=0,model_copies=0,
  no_optimizer_or_training_or_budget_write=True,training_reward_changed=False,actual_parent_private_EX_and_authority_admitted=False,
  sdk_python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',worker_SHA=H(S/'evaluate261_front_depth_zero_PT_UNUSED_once.py'),
  cases=[dict(name='sensor_zero_action',env=0)],
  scope='Sensor-only1env/12controls96physics24feedback, no PT/actor/optimizer. D435i front-fixed provisional virtual mount and real84x48 image-plane depth, physical270mm static stair fixture. Not learned navigation or training.')
 assert contract.validate_task(task)
 files=[dict(relative=f.name,local_path=str(f),bytes=f.stat().st_size,SHA=H(f))for f in sorted(S.glob('*.py'))]
 taskbytes=json.dumps(task,indent=2,allow_nan=False).encode();files.append(dict(relative='TASK261.json',bytes=len(taskbytes),SHA=hashlib.sha256(taskbytes).hexdigest()))
 put('ROOT261_FROZEN_NEW_PURPOSE_AND_ACTUAL_MODEL_COUNT_ADMISSION.json',dict(epoch=time.time(),Task=task,source_model_CPU_qualification_only_JSON_join=True,
  GPU_model_byte_read_decode_max=0,input2050_E0_native_model_reads=0,source_model_uploads=0,original_constructor_RESET_NPZ=1,
  controls_max=12,physics_max=96,feedback_max=24,extra_PhysX_getters=0,loaded_geometry_queries=0,NPZ_raw_download_or_reads=0,neural_learner_or_optimizer_steps=0,GUI=False))
 wrapper=module('root261_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root261_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  put('ROOT261_FRESH72_CNONE_BEFORE_NEW_CASE_ACTUAL.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  create="from pathlib import Path\nimport json\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False)\nprint(json.dumps(dict(passed=True,new_root=str(p),model_stat_hash_copy=0)))"
  put('ROOT261_NEW_UNUSED_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for f in files:
    data=taskbytes if f['relative']=='TASK261.json'else Path(f['local_path']).read_bytes()
    with sf.file(J+'/'+f['relative'],'wx')as stream:stream.write(data);stream.flush()
   pack=json.dumps(dict(files=[{k:r[k]for k in('relative','bytes','SHA')}for r in files]),indent=2).encode()
   with sf.file(J+'/PACKAGE261_SOURCE_AND_TASK.json','wx')as stream:stream.write(pack);stream.flush()
  finally:sf.close()
  actual=d.code(client,d.PY72,EXEC,dict(job=J,files=files),timeout=1140)
  put('ROOT261_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',actual)
  case=(actual.get('original_parent')or{}).get('result')or{}
  print(json.dumps(dict(passed_execution=actual['passed_execution'],wrapper_error=actual['wrapper_error'],controls=case.get('controls'),cases=[dict(name=r['name'],controls=r['controls'],flags=r['first_episode_original_terminal_flags'],BODY_vx_MAE=r['BODY_vx_MAE'],yaw_delta_rad=r['yaw_delta_rad'],endpoint_flight=r['endpoint_flight'])for r in case.get('cases',[])])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT261_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT261_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
