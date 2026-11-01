"""Read-only live GPU/project discovery through the existing pinned project SSH connector."""
from pathlib import Path
import sys,json,datetime,hashlib,stat,re,traceback
sys.path.insert(0,r'F:\RMPOLAR-RL\traditional_control_20261101')
from ssh_task import connect
ROOT=Path(__file__).resolve().parent;BASE='/home/lc01/Zonglin Li/zonglin2'
report={'captured_local':datetime.datetime.now().astimezone().isoformat(),'mode':'read_only','training_started':False,'commands':{},'listings':[]}
commands={
 'gpus':'nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits',
 'compute_apps':'nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory,name --format=csv,noheader,nounits',
 'ram':'free -m',
 'disk':"df -Pm '/home/lc01/Zonglin Li/zonglin2'",
 'project_gpu_process_users':"ps -eo pid,user,comm,etime | awk '$3 ~ /python|kit|isaac|ld-linux/ {print}' | head -60"
}
try:
 c=connect();report['peer']=list(c.get_transport().getpeername());s=c.open_sftp()
 try:
  for label,cmd in commands.items():
   si,so,se=c.exec_command(cmd,timeout=30);si.close();out=so.read().decode('utf-8','replace');err=se.read().decode('utf-8','replace');code=so.channel.recv_exit_status();report['commands'][label]={'exit':code,'stdout':out,'stderr':err};print(json.dumps({'label':label,'exit':code,'stdout':out,'stderr':err},ensure_ascii=False),flush=True)
  for rel in ('','tasks','state','control','runtime_exports'):
   path=BASE+('/'+rel if rel else '')
   try:
    entries=s.listdir_attr(path)
    if rel=='tasks':entries=[e for e in entries if re.search(r'W25|W35|RM70|EXPERT|FROZEN|V29[0-9]|292|293|294|SINGLE_WRITER|FULLDR|FULL_DR',e.filename,re.I)]
    entries=sorted(entries,key=lambda e:e.st_mtime,reverse=True)
    report['listings'].append({'path':path,'entries':[{'name':e.filename,'directory':stat.S_ISDIR(e.st_mode),'bytes':e.st_size,'mtime':e.st_mtime} for e in entries[:50]]})
   except OSError as e:report['listings'].append({'path':path,'error_type':type(e).__name__})
  report['status']='LIVE_READ_COMPLETE'
 finally:s.close();c.close()
except Exception as e:
 report['status']='LIVE_READ_FAILED';report['error_type']=type(e).__name__;report['error_message']=str(e)
out=ROOT/'reports'/('resource72_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',str(out));print(json.dumps({'status':report['status'],'error_type':report.get('error_type'),'error_message':report.get('error_message'),'peer':report.get('peer'),'listings':report['listings']},ensure_ascii=False,indent=2))
if report['status']!='LIVE_READ_COMPLETE':raise SystemExit(2)
