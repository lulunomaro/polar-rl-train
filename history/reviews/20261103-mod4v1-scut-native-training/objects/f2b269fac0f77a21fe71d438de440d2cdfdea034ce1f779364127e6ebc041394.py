"""Human-requested80->20000 switch at the original complete-save boundary."""
from pathlib import Path
import importlib.util,json,time
N=Path(__file__).resolve().parent;A=N/'attempt04'
spec=importlib.util.spec_from_file_location('scut_serial_switch',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.R=N/'reports'
plan=json.loads((A/'PLAN.json').read_bytes());job=plan['remote_root']
with m.connection('HUMAN_CHANGE20000_CLOSE80')as(client,d):
    m.put('HUMAN_CHANGE20000_ONCE.json',dict(epoch=time.time(),human='20000环境一个小时来搞',
        old_root=job,new_envs=20000,new_train_seconds=3600,full_save_safe_exit_then_independent_eval=True))
    code='''from pathlib import Path
import json,time,psutil
j=Path(v['job']);o=json.loads((j/'OWNER_STARTED.json').read_bytes());p=psutil.Process(o['identity']['pid'])
assert abs(p.create_time()-o['identity']['creation'])<.05 and str(j/'owner.py') in p.cmdline()
marker=j/'STOP_AFTER_SAVE.json'
assert not marker.exists()
marker.write_text(json.dumps(dict(epoch=time.time(),reason='Human20000envs1hour supersedes80env2hours; complete update/fullsave/safeexit',fullsave_required=True)))
print(json.dumps(dict(epoch=time.time(),request=str(marker),owner=o,kill=False,source_changed=False)))'''
    value=d.code(client,d.PY72,code,dict(job=job),timeout=40)
    m.put('HUMAN_CHANGE20000_STOP_RECEIPT.json',value)
    print(json.dumps(value),flush=True)
    for tick in range(60):
        code='''from pathlib import Path
import json,time
j=Path(v['job']);files={}
for rel in ['OWNER_STARTED.json','OWNER_EXIT.json','OWNER_ERROR.json','GO_PRODUCTION.json','OWNER_CURRENT.json','TRAIN_CLOSED.json','EVAL_WAITED.json','production/FINAL.json','production/FIRST_UPDATED.json','production/STARTUP.json','production/FINETUNE_INITIALIZATION.json','production/ERROR.json','production/APP_CLOSE_INTENT.json','production/LATEST_PROGRESS.json','evaluation/RESULT.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json']:
 p=j/rel
 if p.is_file():
  try:files[rel]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
for rel in ['WORKER.log','EVAL.log']:
 p=j/rel
 if p.is_file():
  with p.open('rb')as f:f.seek(max(0,p.stat().st_size-8000));files[rel]=f.read().decode('utf-8','replace')
print(json.dumps(dict(epoch=time.time(),files=files)))'''
        row=d.code(client,d.PY72,code,dict(job=job),timeout=30)
        if 'OWNER_EXIT.json'in row['files']:
            m.put('HUMAN_CHANGE20000_80_CLOSED_RETURNED.json',row)
            print(json.dumps(dict(closed=True,files=list(row['files']),
                final=row['files'].get('production/FINAL.json'),eval=row['files'].get('evaluation/RESULT.json'),
                error=row['files'].get('evaluation/ERROR.json'))),flush=True)
            break
        if tick%3==0:print(json.dumps(dict(wait=tick,files=list(row['files']))),flush=True)
        time.sleep(10)
    else:
        m.put('HUMAN_CHANGE20000_CLOSE_PENDING.json',row)
        raise RuntimeError('Original owner not released; no new launch')
