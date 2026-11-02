"""Exact localstat and independent72 CPUcap; no original210 retry/modelbytes."""
from pathlib import Path
import datetime,importlib.util,json,shlex,sys,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');sys.path.insert(0,str(T));from project_connector import connect72
paths=[('SLOPE135',W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job1/source/source.pt','24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'),('CURB141',W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/all_saved_actual/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/1791721755284426300/learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629/model_32114.pt','7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43')]
r=dict(kind='E1_EXACT_LOCAL_SOURCE_STAT_AND_72CPU_CAPABILITY_V2',source_byte_reads_hashes_decodes=0,original210_prior='CONNECT_TIMEOUT_BEFORE_SFTP_STAT; not claimed missing',local_Torch_module_available=importlib.util.find_spec('torch') is not None,sources=[]);client=None
try:
 for name,p,sha in paths:
  x=dict(canonical=name,path=str(p),expected_SHA=sha)
  try:s=p.stat();x.update(exists=True,bytes=s.st_size,mtime_ns=s.st_mtime_ns)
  except FileNotFoundError:x.update(exists=False,errno=2)
  r['sources'].append(x)
 client=connect72();code="import os;os.environ['CUDA_VISIBLE_DEVICES']='';import torch,json;print(json.dumps({'Torch':torch.__version__,'CUDA_initialized':torch.cuda.is_initialized(),'scope':'CPU capability only, no checkpoint/SDK/GPUquery'}))"
 i,o,e=client.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();r.update(CPU72_rc=rc,CPU72_stdout=stdout,CPU72_stderr=stderr);assert rc==0;r['status']='SLOPE_EXACT_LOCAL_EXISTS_CPU72_READY_CUrb_UNLOCATED'
except BaseException:r.update(status='METADATA_CAPABILITY_ERROR',error=traceback.format_exc());raise
finally:
 if client:client.close()
 out=T/'reports'/('E1_exact_sources_metadata_v2_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'EXACT_SOURCE_LOCATION_METADATA_V2.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(out),data=r),ensure_ascii=False,indent=2))
