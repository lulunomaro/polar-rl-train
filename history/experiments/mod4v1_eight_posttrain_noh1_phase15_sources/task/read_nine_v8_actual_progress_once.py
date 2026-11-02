"""OneownV8publishedrolesnapshot; no repeatedworkerpoll/raw/model/SDK/driver/canonical."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;root=json.loads((R/'NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V8.json').read_bytes())['root'];code="""from pathlib import Path
import json,time
B=Path(%r);p=json.loads((B/'GROUP_PLAN.json').read_bytes());rows=[]
for r in p['roles']:
 d=B/'cases'/r['role'];v={'role':r['role'],'ready':(d/'WORKER_SCENE_READY.json').exists(),'started':(d/'WORKER_EVAL_STARTED.json').exists(),'FINAL':(d/'FINAL.json').exists(),'pre_close':(d/'PRE_CLOSE.json').exists()}
 f=d/'FINAL.json'
 if f.exists():
  x=json.loads(f.read_bytes());v.update(controls=x.get('controls'),seconds=x.get('seconds'),passed_execution=x.get('passed_execution'),start=x.get('first_eval_epoch',x.get('wall_start_epoch')),end=x.get('last_eval_epoch',x.get('wall_end_epoch')))
 f=d/'WORKER_ERROR.json'
 if f.exists():
  x=json.loads(f.read_bytes());v['error_tail']=x['error'].splitlines()[-7:];v['controls_before_error']=x.get('controls_completed')
 rows.append(v)
print(json.dumps({'kind':'ACTUAL_OWN_V8_PUBLISHED_PROGRESS_ONLY','epoch':time.time(),'root':str(B),'rows':rows,'parent_exit':(B/'PARENT_EXIT_SCOPE.json').exists(),'PT_raw_SDK_driver_canonical_calls':0}))
"""%root;c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('NINE_V8_ACTUAL_PROGRESS_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,indent=2))
