"""Exact producer PTstat only, no sourcebyte/hash/decode; CPUruntime metadata only."""
from pathlib import Path
import datetime,importlib.util,json,shlex,sys,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');sys.path.insert(0,str(T));from project_connector import connect72,connect_original
SOURCES=[dict(canonical='CURB141',SHA='7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43',original_remote='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629/model_32114.pt',local=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/all_saved_actual/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/1791721755284426300/learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629/model_32114.pt'),dict(canonical='SLOPE135',SHA='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411',original_remote='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011/learning_logs/2026-10-11_09-26-50_e1_SLOPE5_independent_observation_1791681817786379719/model_32069.pt',local=W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011/snapshot_actual_remote/learning_logs/2026-10-11_09-26-50_e1_SLOPE5_independent_observation_1791681817786379719/model_32069.pt')]
report=dict(kind='E1_EXACT_CANONICAL_SOURCE_STAT_LOCATOR_NO_BYTES',source_byte_reads_hashes_decodes=0,local_Torch_module_available=importlib.util.find_spec('torch') is not None,sources=[]);client=sf=cpu=None
try:
 client=connect_original();sf=client.open_sftp()
 for x in SOURCES:
  row=dict(canonical=x['canonical'],expected_SHA=x['SHA'],original_remote_path=x['original_remote'],exact_local_path=str(x['local']))
  try:st=x['local'].stat();row['local_stat']=dict(exists=True,bytes=st.st_size,mtime_ns=st.st_mtime_ns)
  except FileNotFoundError:row['local_stat']=dict(exists=False,original_errno=2)
  try:st=sf.stat(x['original_remote']);row['original_remote_stat']=dict(exists=True,bytes=st.st_size,mtime=st.st_mtime)
  except OSError as e:
   if getattr(e,'errno',None)!=2:raise
   row['original_remote_stat']=dict(exists=False,original_errno=2)
  report['sources'].append(row)
 cpu=connect72();code="import os;os.environ['CUDA_VISIBLE_DEVICES']='';import torch,json;print(json.dumps({'Torch':torch.__version__,'CUDA_initialized':torch.cuda.is_initialized(),'scope':'CPUonly runtime capability; no source load, GPUquery, SDK'}))"
 i,o,e=cpu.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(CPU72_runtime_rc=rc,CPU72_runtime_stdout=stdout,CPU72_runtime_stderr=stderr);assert rc==0,'CPUonly runtime metadata failed'
 report['status']='EXACT_STAT_COMPLETE_SOURCE_CONTENT_UNREAD'
except BaseException:report.update(status='LOCATOR_ERROR',error=traceback.format_exc());raise
finally:
 if sf:sf.close()
 if client:client.close()
 if cpu:cpu.close()
 dest=T/'reports'/('E1_exact_sources_stat_locator_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'EXACT_SOURCE_LOCATION_METADATA.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(dest),data=report),ensure_ascii=False,indent=2))
