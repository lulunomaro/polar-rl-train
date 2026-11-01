from pathlib import Path
import ast,hashlib,importlib.util,io,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 source=T/'D435I_RAY_DEPTH_ORIGINAL_JUMP_AUDIT_V261_20261101/reports/ROOT261_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'
 result=json.loads(source.read_bytes());assert result['passed_execution'];producer=result['original_parent']['result']['producer']
 put('FROZEN262_NEW261_NECESSARY_GEOMETRY_READ_PURPOSE_BEFORE_IO.json',dict(epoch=time.time(),purpose='Diagnose incorrect platform height using only NEW261 actual depth/K/T; fit surface normals and bind SDK pixel centers.',producer=producer,NPZ_transfer_max=1,NPZ_stream_byte_pass_max=1,hash_from_same_bytes=True,np_load_max=1,each_member_reads=1,primary_current_pattern_source_max=1,models_ONNX_PT_GPU_App_inference_optimizer_GO_account=0,no_GUI=True))
 pattern='read262_|run_ROOT261_|run_ROOT260_|run_ROOT258_|run_ROOT257_|run_ROOT256_|run_ROOT254_|run_ROOT250_|read253_|read252_|read251_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_ROOT240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 x=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(x.stdout)if x.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT262_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,PID=os.getpid(),exe=sys.executable,argv=sys.argv))
 transport=previous=client=secret=None
 try:
  wrapper=module('root262_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
  sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root262_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import ast,hashlib,json,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
p=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/sensors/ray_caster/patterns/patterns.py');b=p.read_bytes();s=b.decode();f=[x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef)and x.name=='pinhole_camera_pattern'];assert len(f)==1
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),function=ast.get_source_segment(s,f[0]),source_byte_reads=1,account_writes=0)))"""
  meta=d.code(client,d.PY72,code,{},timeout=45);put('ROOT262_PRIMARY_CURRENT_PINHOLE_PATTERN_ACTUAL.json',meta);assert meta['passed']
  sf=client.open_sftp()
  try:
   with sf.file(producer['path'],'rb')as stream:raw=stream.read()
  finally:sf.close()
  assert len(raw)==producer['bytes']and hashlib.sha256(raw).hexdigest()==producer['SHA']
  with(N/'NEW261_DEPTH_K_T_FOR262_NUMERICAL_PURPOSE.npz').open('xb')as f:f.write(raw)
  put('ROOT262_ONE_NEW261_TRANSFER_AND_SAME_BYTES_SHA_ACTUAL.json',dict(epoch=time.time(),producer=producer,stream_byte_passes=1,local_write=1,model_reads=0))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT262_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
 import numpy as np
 z=np.load(io.BytesIO(raw),allow_pickle=False);assert set(z.files)=={'depth_image_plane_m','K','T_heading_optical'}
 depth=z['depth_image_plane_m'];K=z['K'];T_=z['T_heading_optical'];z.close();rows=[]
 for i in range(len(depth)):
  frame=[]
  for center in(0.,.5):
   v,u=np.indices(depth[i].shape,dtype=np.float32);u+=center;v+=center
   p=np.stack(((u-K[i,0,2])*depth[i]/K[i,0,0],(v-K[i,1,2])*depth[i]/K[i,1,1],depth[i]),-1)@T_[i,:3,:3].T+T_[i,:3,3]
   with np.errstate(invalid='ignore'):
    a=p[:,1:]-p[:,:-1];b=p[1:]-p[:-1];normal=np.cross(a[:-1],b[:,:-1]);norm=np.linalg.norm(normal,axis=-1);horizontal=np.abs(normal[...,2])/(norm+1e-12)>.95
   finite=np.isfinite(p).all(-1)&(depth[i]>0)&(depth[i]<4);q=p[:-1,:-1][horizontal&finite[:-1,:-1]&finite[:-1,1:]&finite[1:,:-1]]
   hist=[]
   if len(q):
    levels,counts=np.unique(np.rint(q[:,2]/.01).astype(np.int32),return_counts=True)
    hist=[dict(z_m=float(k*.01),pixels=int(c))for k,c in zip(levels,counts)if c>10]
   frame.append(dict(pixel_center=center,horizontal_pixels=len(q),horizontal_z_histogram=hist,K=K[i].tolist(),T_heading_optical=T_[i].tolist()))
  rows.append(dict(frame=i,variants=frame))
 put('ROOT262_NEW261_SINGLE_PASS_SURFACE_GEOMETRY_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),NPZ_byte_passes=1,np_loads=1,each_three_members_reads=1,models_SDK_GPU_optimizers=0,rows=rows,old_detector_false_scope='Height bins alone did not establish horizontal support; prior261 found flags are candidates, not correct270mm localization or trained navigation.'))
 print(json.dumps(dict(passed=True,rows=rows),allow_nan=False))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT262_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
