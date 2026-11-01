"""Bounded ROOT source-only target lookup for selectedD435i front-fixed integration."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True);T=N.parent;W=T.parent
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
CODE="""from pathlib import Path
import hashlib,importlib.util,importlib.metadata,json,sys,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
spec=importlib.util.find_spec('isaaclab');assert spec and spec.origin
root=Path(spec.origin).resolve().parent;rows=[]
for rel in v['source_files']:
 p=(root/rel).resolve();assert p.is_relative_to(root);b=p.read_bytes();assert len(b)<250000
 rows.append(dict(relative=rel,path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),physical_source_byte_reads=1))
assert 'torch'not in sys.modules
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,isaaclab_version=importlib.metadata.version('isaaclab'),isaaclab_root=str(root),source_files=rows,model_assets_raw_GPU_SDK_App_or_account_calls=0)))"""
def main():
 assert sys.version_info[:2]==(3,14)
 pattern='read248_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|run_actual'
 q="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 a=subprocess.run(['pwsh.exe','-NoProfile','-Command',q],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(a.stdout)if a.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[r for r in rows if r['ProcessId']==os.getpid()];assert len(own)==len(rows)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT248_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 files=['sensors/camera/camera_cfg.py','sensors/camera/tiled_camera.py','sensors/camera/camera.py','app/app_launcher.py']
 put('FROZEN248_D435I_FRONT_FIXED_SOURCE_LOOKUP_ONCE_BEFORE_NETWORK.json',dict(epoch=time.time(),user_camera='D435i',user_mount='fixed at chassis front',source_files=files,reads_each_max=1,model_raw_assets_SDK_App_GPU_or_account=0,purpose='Read actual installed camera config/launcher/data API before creating sensor-only0PT caller. No camera construction or data claimed.'))
 wrapper=mod('root248_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();s=mod('root248_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=s.recover();client=d.connect72(secret);secret=None
  actual=d.code(client,d.PY72,CODE,dict(source_files=files),timeout=60);put('ROOT248_ACTUAL_CURRENT_CAMERA_SDK_SOURCE_OR_ORIGINAL_ERROR.json',actual)
  print(json.dumps(dict(passed=actual['passed'],version=actual['isaaclab_version'],files=[dict(path=r['path'],bytes=r['bytes'],SHA=r['SHA'])for r in actual['source_files']],model_or_App_GPU=0)))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT248_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT248_ORIGINAL_SOURCE_LOOKUP_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
