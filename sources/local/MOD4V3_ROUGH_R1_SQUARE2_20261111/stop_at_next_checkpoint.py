from pathlib import Path
import json,hashlib,time,os,signal
b=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/rough_r1_square2_20261111_r1');j=b/'train_remaining_rough_r1_square2_r1';pid=json.loads((b/'train_remaining_rough_r1_square2_r1_LAUNCH.json').read_text())['pid']
request=dict(reason='User nextcheckpoint cubic stronger speedpenalty; retain square+absolute cubic to avoid signed reward and weak smallerrors',target='PERIODIC_015M.json',requested_epoch=time.time(),pid=pid)
(b/'SWITCH_CUBIC_REQUEST.json').write_text(json.dumps(request,indent=2))
while not (j/request['target']).exists():
 if (j/'ERROR.json').exists() or (j/'FINAL.json').exists():raise RuntimeError('ended before nextcheckpoint')
 time.sleep(1)
x=json.loads((j/request['target']).read_text());f=Path(x['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==x['SHA'] and f.stat().st_size==x['bytes']
cmd=Path('/proc/'+str(pid)+'/cmdline').read_bytes().decode().replace('\0',' ');assert str(j) in cmd and 'scut_flat_train' in cmd
p=json.loads((j/'LATEST_PROGRESS.json').read_text());now=time.time();start=p['epoch']-p['training_elapsed_seconds']
r=dict(request=request,checkpoint=x,verified_sha=True,signal='SIGINT',signal_epoch=now,actual_segment_consumed_seconds=now-start,last_progress=p)
(b/'SWITCH_CUBIC_CHECKPOINT_SAVED.json').write_text(json.dumps(r,indent=2));os.kill(pid,signal.SIGINT)
for _ in range(20):
 if not Path('/proc/'+str(pid)).exists():break
 time.sleep(.5)
r['process_exited']=not Path('/proc/'+str(pid)).exists();r['FINAL']=(j/'FINAL.json').exists();r['SAFE_CLOSED']=(j/'SAFE_CLOSED.json').exists();(b/'SWITCH_CUBIC_STOPPED.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='last_progress'}))
