"""Collect only this new native admission's status/error files, never model weights."""
from pathlib import Path
import json,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent
source=sorted((R/'reports').glob('native_pair_dispatch_*.json'))[-1];dispatch=json.loads(source.read_bytes());job=dispatch['plan']['new_remote_job'];r={'source_dispatch':str(source),'remote_job':job,'captured_local':datetime.datetime.now().astimezone().isoformat(),'files':{}}
c=connect72();s=c.open_sftp()
try:
 for rel in ('PARENT_STARTED.json','CHILDREN.json','TERMINAL_ROWS.json','FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json'):
  try:
   with s.open(job+'/'+rel,'rb')as f:r['files'][rel]=json.loads(f.read())
  except FileNotFoundError:pass
 for label in ('gpu0','gpu1'):
  try:rows=s.listdir_attr(job+'/'+label)
  except FileNotFoundError:continue
  for row in rows:
   rel=label+'/'+row.filename
   if row.filename.endswith('.json') and row.st_size<200000:
    with s.open(job+'/'+rel,'rb')as f:r['files'][rel]=json.loads(f.read())
   if row.filename.endswith('.log'):
    with s.open(job+'/'+rel,'rb')as f:f.seek(max(0,row.st_size-24000));text=f.read().decode('utf-8','replace')
    r['files'][rel]={'bytes_at_snapshot':row.st_size,'tail_only':text}
 for cmd in ('nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader,nounits','nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory --format=csv,noheader,nounits'):
  i,o,e=c.exec_command(cmd,timeout=30);i.close();r.setdefault('gpu_now',[]).append({'stdout':o.read().decode(),'stderr':e.read().decode(),'exit':o.channel.recv_exit_status()})
finally:s.close();c.close()
p=R/'reports'/('native_snapshot_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p)
compact={k:v for k,v in r['files'].items() if not k.endswith('.log') and not k.endswith('NATIVE_DATA_COMPLETE.json')};print(json.dumps({'status_files':compact,'gpu_now':r.get('gpu_now')},ensure_ascii=False,indent=2))
for k,v in r['files'].items():
 if k.endswith('.log'):print('LOG_TAIL',k,v['tail_only'][-3500:])
