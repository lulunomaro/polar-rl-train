"""One bounded read stream, sole transport while live; no launch or retry."""
from pathlib import Path
import json,time,traceback
import transport_bodyframe_pipeline_v6 as t

CODE=r'''
from pathlib import Path
import json,time,os,psutil,fcntl
r=Path(CONTEXT['root']);start=time.time();last=None
def read(p):
 try:return json.loads(p.read_bytes())
 except (FileNotFoundError,json.JSONDecodeError):return None
while time.time()-start<1200:
 current=read(r/'CURRENT_STAGE.json');error=read(r/'PIPELINE_ORIGINAL_ERROR.json');done=read(r/'PIPELINE_COMPLETE_REVIEW_READY.json')
 row=dict(epoch=time.time(),current=current,error=error,complete=bool(done))
 if current and current.get('stage'):
  s=Path(current['stage']);row['stage_passed']=(s/'OWN_STAGE_POSTEXIT_PASSED.json').exists()
  a=s/'attempt';p=a/'DISPATCH_RECEIPT.json';row['dispatch']=read(p);row['exit']=read(a/'EXIT_RECEIPT.json')
  folders=list((a/'learning_logs').glob('*')) if (a/'learning_logs').exists() else []
  for f in folders:
   if not f.is_dir():continue
   row['body14_present']=(f/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').exists()
   h=read(f/'CLOCK_TRAINING_HEALTH.json')
   if h:row['health']={k:h.get(k) for k in ('control_steps','actual_physics_callbacks','ordinary_task_reset_events','integrity_task_reset_events','unknown_task_reset_events','nonfinite_observed','stop_reason','max_closure_error_m')}
   row['latest_complete']=read(f/'latest_complete.json')
  if error:
   p=a/'worker_stdout.log'
   if p.exists():
    with p.open('rb') as f:f.seek(max(0,p.stat().st_size-12000));row['worker_error_tail']=f.read().decode('utf8',errors='replace')
 if error:
  log=r/'pipeline_parent.log'
  if log.exists():row['parent_error_tail']=log.read_text(errors='replace')[-12000:]
 state=json.dumps({k:v for k,v in row.items() if k!='epoch'},sort_keys=True)
 if state!=last:print(json.dumps(row),flush=True);last=state
 if error or done:break
 time.sleep(15)
print(json.dumps(dict(epoch=time.time(),finite_stream_ended=True,complete=(r/'PIPELINE_COMPLETE_REVIEW_READY.json').exists(),original_error=(r/'PIPELINE_ORIGINAL_ERROR.json').exists())),flush=True)
'''

def main():
    c=None;rows=[]
    try:
        c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+t.PY+' -',timeout=1250)
        si.write('CONTEXT='+repr(dict(root=t.ROOT))+'\n'+CODE);si.flush();si.channel.shutdown_write()
        for line in so:
            row=json.loads(line);rows.append(row)
            current=row.get('current') or {}
            print(json.dumps(dict(epoch=row.get('epoch'),phase=current.get('phase'),child_PID=(current.get('child') or {}).get('pid'),
                body14_present=row.get('body14_present'),health=row.get('health'),complete=row.get('complete'),
                original_error=row.get('error'),worker_error_tail=row.get('worker_error_tail'),parent_error_tail=row.get('parent_error_tail'),
                finite_stream_ended=row.get('finite_stream_ended'))),flush=True)
        err=se.read();rc=so.channel.recv_exit_status()
        p=t.save('BODYFRAME_FINITE_PIPELINE_ACTUAL_STREAM',dict(epoch=time.time(),code=rc,stderr=err.decode(errors='replace'),rows=rows,bounded_finite_read_only=True))
        print(json.dumps(dict(collection=str(p),code=rc)));assert rc==0
    except BaseException:
        print(t.save('BODYFRAME_FINITE_COLLECTOR_ORIGINAL_ERROR',dict(epoch=time.time(),error=traceback.format_exc(),rows=rows,no_retry_or_launch=True)),flush=True);raise
    finally:t.close(c)

if __name__=='__main__':main()
