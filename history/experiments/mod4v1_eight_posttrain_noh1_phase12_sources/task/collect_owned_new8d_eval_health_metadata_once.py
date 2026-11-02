"""Ownedroot/workerPID-creation+cmdline/read-onlylogfile stat. No live telemetry, weights, GPU driver or budget."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;B='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_AFTER_RESUME89ACA_EVAL_20261102_070117_1793574077925312000';code="""from pathlib import Path
import json,time,psutil
B=Path(%r);v={'kind':'OWN8D_EVAL_HEALTH_SMALL_METADATA_NOT_METRICS','epoch':time.time(),'job':str(B),'processes':{},'closed_files':{},'model_live_raw_GPUdriver_canonical_access':False}
for name,file in [('parent','PARENT_STARTED.json'),('worker','WORKER_IDENTITY.json')]:
 identity=json.loads((B/file).read_bytes());pid=identity['pid']
 try:
  p=psutil.Process(pid);cmd=p.cmdline();assert str(B) in ' '.join(cmd)
  if 'creation'in identity:assert abs(p.create_time()-identity['creation'])<.02
  v['processes'][name]={'pid':pid,'creation':p.create_time(),'status':p.status(),'elapsed_seconds':time.time()-p.create_time(),'CPU_user_seconds':p.cpu_times().user,'CPU_system_seconds':p.cpu_times().system,'ownedcmdline_rootmatched':True}
 except psutil.NoSuchProcess:v['processes'][name]={'pid':pid,'not_running':True}
for name in('ACTUAL_ORIGINAL_WAIT.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','FINAL.json'):
 p=B/name
 if p.exists():v['closed_files'][name]=json.loads(p.read_bytes())
p=B/'FULL_EVAL_STDOUT_STDERR.log';st=p.stat();v['ownedstdout_log_stat_only']={'bytes':st.st_size,'mtime':st.st_mtime,'content_reads':0};print(json.dumps(v))
"""%B
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('W35_NEW8D_OWN_HEALTH_METADATA_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({k:x for k,x in v.items()if k!='closed_files'},indent=2));print('TERMINAL_FILES',list(v['closed_files']))
