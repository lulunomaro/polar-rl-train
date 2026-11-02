"""DiagnoseownparentpreGOmetadataabsenceonce; ifexactownparentexitedreadownstderr, neverforeignprocess/model/raw/C."""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/FIRST_OWNER_ACTUAL_LIFECYCLE_DIAGNOSIS_ONCE.json';assert not out.exists();m=json.loads((R/'SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json').read_bytes());root=m['root'];code=r'''from pathlib import Path
import json,time,psutil
B=Path(%r);pid=%d;creation=%r;live=False;identity=None
try:
 p=psutil.Process(pid);live=abs(p.create_time()-creation)<.001 and p.status()!=psutil.STATUS_ZOMBIE;identity={'pid':pid,'creation':p.create_time(),'status':p.status(),'cmdline':p.cmdline(),'cpu_times':list(p.cpu_times()),'memory':p.memory_info().rss}
except psutil.NoSuchProcess:pass
v={'root':str(B),'epoch':time.time(),'exact_owner_live':live,'identity':identity,'metadata':{}}
for name in('OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','PREGO_RESOURCE_WAIT.json'):
 p=B/name;v['metadata'][name]=json.loads(p.read_bytes())if p.exists()else None
if not live:
 p=B/'OWNER_FULL_STDOUT_STDERR.log'
 with p.open('rb')as f:f.seek(max(0,p.stat().st_size-24000));v['own_parent_closed_log_tail']=f.read().decode('utf-8','replace')
print(json.dumps(v))
'''%(root,m['parent']['pid'],m['parent']['creation']);c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
finally:c.close()
