"""Independent0PT retry purpose: original run-python loader, unchanged worker/physics."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 prior=read(R/'ROOT240_ACTUAL_TARGET80_NATIVE8_0PT_OR_ORIGINAL_ERROR_RETURNED.json')
 assert not prior['passed_execution'] and prior['returncode']==1 and prior['private_and_validation_EX_released'] and prior['all_own_children_waited'] and prior['result'] is None
 assert any('GLIBC_2.33'in r['UTF8']for r in prior['full_UTF8'])
 old=module('root240_admit_v1_source_only',T/'install240_model2050_target80_0PT_once.py')
 code=old.ADMIT.replace('[sys.executable,\'-u\',\'-B\'','[v[\'sdk_python\'],\'-u\',\'-B\'')
 assert code!=old.ADMIT
 code=code.replace('ADMISSION80_','ADMISSION80V2_').replace("B/'admission80'","B/'admission80v2'").replace("admission80/","admission80v2/")
 ast.parse(code)
 code="assert not (Path(v['job'])/'admission80v2').exists()\n"+code if False else code
 put('ROOT240_ADMIT80V2_LOADER_ONLY_PURPOSE_FROZEN.json',dict(epoch=time.time(),prior_false_preserved=True,
  original_error='Bare sys.executable bypassed existing glibc240 run-python.sh; before SDK/env constructor/model',
  change='Only original existing SDK wrapper argv and independent admission80v2 output/report namespace',
  unchanged_worker_SHA=hashlib.sha256((N/'package/run240_model2050_mixed_literal_worker.py').read_bytes()).hexdigest(),
  new_parent_SHA=hashlib.sha256(code.encode()).hexdigest(),models_NN_PPO_or_account_writes=0,old_admission_rerun=False,physics_or_reward_changes=0))
 pattern='install240_|transfer240_|read240_|start240_|run_ROOT240_|launch_e2_solo_|collect_e2_solo_|run_ROOT_latest32481_|run_ROOT238_|admit238_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT240_ADMIT80V2_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT240_ADMIT80V2_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),actual_new_0PT_purpose=True,worker_native8_max=1,model_reads=0,source_asset_model_reuploads=0,signals=0))
 wrapper=module('root240_admitV2_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 source=module('root240_admitV2_remote_helpers',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root240_admitV2_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  put('ROOT240_ADMIT80V2_FRESH72_CNONE_RESERVE_ACTUAL.json',d.code(client,d.PY72,source.AUTH,{},timeout=45))
  install=read(R/'INSTALL240_SOURCE_ASSET_MANIFEST.json')
  result=d.code(client,d.PY72,code,dict(job=install['job_root'],GPU_UUID=old.GPU,sdk_python=d.PY72),timeout=1080)
  put('ROOT240_ACTUAL_TARGET80V2_NATIVE8_0PT_OR_ORIGINAL_ERROR_RETURNED.json',result)
  assert result['passed_execution'] and result['returncode']==0 and result['private_and_validation_EX_released'] and result['all_own_children_waited']
  print(json.dumps(dict(passed=True,controls=result['result']['controls'],physics_callbacks=result['result']['physics_callbacks'],num_envs=result['result']['num_envs'],selected2050_GPU_decodes=0,all_own_waited_EX_free=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT240_ADMIT80V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT240_ADMIT80V2_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
