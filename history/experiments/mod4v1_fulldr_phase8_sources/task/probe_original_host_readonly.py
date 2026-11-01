"""Read-only hardware probe on the other already-authorized project Linux node."""
from pathlib import Path
import json,datetime
from project_connector import connect_original
ROOT=Path(__file__).resolve().parent
r={'captured_local':datetime.datetime.now().astimezone().isoformat(),'mode':'read_only','commands':{},'training_started':False}
try:
 c=connect_original();r['peer']=list(c.get_transport().getpeername())
 try:
  for label,cmd in {'gpus':'nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits','compute_apps':'nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory,name --format=csv,noheader,nounits','ram':'free -m','disk':'df -Pm /home/egde/fangzhen_linux'}.items():
   i,o,e=c.exec_command(cmd,timeout=30);i.close();r['commands'][label]={'exit':None,'stdout':o.read().decode('utf-8','replace'),'stderr':e.read().decode('utf-8','replace')};r['commands'][label]['exit']=o.channel.recv_exit_status()
  r['status']='LIVE_READ_COMPLETE'
 finally:c.close()
except Exception as e:r.update(status='LIVE_READ_FAILED',error_type=type(e).__name__,error_message=str(e))
p=ROOT/'reports'/('resource_original_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(r,ensure_ascii=False,indent=2))
if r['status']!='LIVE_READ_COMPLETE':raise SystemExit(2)
