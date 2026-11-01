"""Explicit parent-authorized ONE72direct-tcpip sameoriginal210project STAT ONLY.
Existing project_connector memoryauth+systemhostkey pin unchanged; never log
credentials/kwargs, never remote credential write/cmdline, no PTbyte/hash/load.
"""
from pathlib import Path
import datetime,json,sys,traceback
import paramiko
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72,connect_original
TARGET='10.24.4.210';PORT=22;SOURCE='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629/model_32114.pt'
report=dict(kind='PARENT_AUTHORIZED_SAME_PROJECT_210_EXACT_PT_STAT_VIA72_ONCE',source_path=SOURCE,expected_SHA='7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43',fixed_target=TARGET,fixed_port=PORT,source_byte_reads_hashes_decodes=0,credential_implementation='Unchanged project_connector.connect_original RAMprovider; originalsystemhostkey pin; no values/logs/files/cmdline',new_scan_or_other_user_scope=False);jump=original=channel=sf=None;saved=paramiko.SSHClient.connect
try:
 assert not (B/'CURB141_TUNNEL_STAT_ONCE_CONSUMED.json').exists()
 with (B/'CURB141_TUNNEL_STAT_ONCE_CONSUMED.json').open('x',encoding='utf-8') as f:json.dump(dict(target=TARGET,port=PORT,purpose='Exact knownproducerstat only no content'),f,indent=2)
 jump=connect72()
 def routed(self,*args,**kwargs):
  host=kwargs.get('hostname',args[0] if args else None);port=kwargs.get('port',PORT)
  if host!=TARGET or port!=PORT or kwargs.get('sock') is not None:raise ValueError('Only exact bound originalproject target permitted')
  nonlocal_channel=jump.get_transport().open_channel('direct-tcpip',(TARGET,PORT),('127.0.0.1',0),timeout=20)
  kwargs['sock']=nonlocal_channel
  return saved(self,*args,**kwargs)
 paramiko.SSHClient.connect=routed
 try:original=connect_original()
 finally:paramiko.SSHClient.connect=saved
 sf=original.open_sftp()
 try:s=sf.stat(SOURCE);report.update(status='EXACT_ORIGINAL_PT_STAT_EXISTS_VIA72_NO_CONTENT',exists=True,bytes=s.st_size,mtime=s.st_mtime)
 except OSError as e:
  if getattr(e,'errno',None)!=2:raise
  report.update(status='EXACT_ORIGINAL_PT_STAT_MISSING_VIA72',exists=False,errno=2)
except BaseException:
 report.update(status='SAME_PROJECT_TUNNEL_STAT_NOT_OBTAINED_NOT_MODEL_MISSING',error=traceback.format_exc());raise
finally:
 paramiko.SSHClient.connect=saved
 if sf:sf.close()
 if original:original.close()
 if jump:jump.close()
 dest=T/'reports'/('CURB141_same_project72_tunnel_stat_v4_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'CURB141_EXACT_TUNNEL_STAT_V4.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(dest),data=report),ensure_ascii=False,indent=2))
