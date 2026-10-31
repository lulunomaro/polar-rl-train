"""Necessary installed RSL scalar-STD semantics; no model/raw/NN/SDK imports."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert json.loads((R/'ROOT223_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json').read_bytes())['global_serial_control_client_lease']=='FREE'
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'read223_target_scalar_STD_primary_source_once|run_ROOT223_|run_ROOT222_|collect219V3_|launch219V3_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[r for r in rows if r['ProcessId']==os.getpid()];assert len(own)==1 and len(rows)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower()and own[0]['CreationDate']
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT223_STD_SOURCE_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,CIM=rows))
 put('ROOT223_STD_SOURCE_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose='Interpret new223 learned distribution.std_param6 using exact installed primary RSL source',source_file_reads_max=1,metadata_version_calls=1,models_raw_NPZ_SDK_GPU_and_NN_calls=0,no_account_write=True))
 caller=module('std223_caller',N/'run_ROOT223_input_mode_action_flow_once.py')
 wrapper=module('std223_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('std223_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  auth=d.code(client,d.PY72,caller.AUTH,{},timeout=45);put('ROOT223_STD_SOURCE_FRESH72_CNONE_ACTUAL.json',auth)
  code="""from pathlib import Path
from importlib import metadata
import json,hashlib,time
dist=metadata.distribution('rsl-rl-lib');version=dist.version
paths=[x for x in dist.files if str(x).replace('\\\\','/').endswith('rsl_rl/modules/distribution.py')];assert len(paths)==1
p=Path(dist.locate_file(paths[0]));raw=p.read_bytes();text=raw.decode('utf8')
assert 'self.std_param = nn.Parameter(init_std * torch.ones(output_dim))'in text and 'std = self.std_param.expand_as(mean)'in text
print(json.dumps(dict(passed=True,epoch=time.time(),installed_RSL_version=version,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=text,source_file_byte_reads=1,metadata_version_calls=1,no_RSL_Torch_NN_SDK_import=True,account_write=0)))
"""
  result=d.code(client,d.PY72,code,{},timeout=45);put('ROOT223_TARGET_INSTALLED_RSL_SCALAR_STD_PRIMARY_SOURCE_ACTUAL.json',result)
  print(json.dumps(dict(passed=result['passed'],RSL_version=result['installed_RSL_version'],source_reads=1,model_reads=0,scalar_std_param_is_direct=True)))
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT223_STD_SOURCE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT223_STD_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
