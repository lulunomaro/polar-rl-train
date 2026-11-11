from pathlib import Path
import json,hashlib,os,signal,time
base=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/flat_square15_20261111_r1');job=base/'train040m_flat_square15_r1';launch=json.loads((base/'train040m_flat_square15_r1_LAUNCH.json').read_text());pid=launch['pid']
request=dict(requested_epoch=time.time(),reason='User: switch to Rough after next complete checkpoint',target='PERIODIC_020M.json',pid=pid,original_seconds=2400)
(base/'SWITCH_TO_ROUGH_REQUEST.json').write_text(json.dumps(request,indent=2))
while not (job/'PERIODIC_020M.json').exists():
 if (job/'ERROR.json').exists() or (job/'FINAL.json').exists():raise RuntimeError('Training ended before requested next checkpoint')
 time.sleep(1)
r=json.loads((job/'PERIODIC_020M.json').read_text());p=Path(r['path']);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==r['SHA'] and p.stat().st_size==r['bytes']
command=Path('/proc/'+str(pid)+'/cmdline').read_bytes().decode().replace('\0',' ');assert str(job) in command and 'scut_flat_train' in command
receipt=dict(request=request,checkpoint=r,sha256_verified=True,signal='SIGINT for Python finally scene close',signal_epoch=time.time())
(base/'SWITCH_CHECKPOINT_SAVED.json').write_text(json.dumps(receipt,indent=2));os.kill(pid,signal.SIGINT)
for _ in range(180):
 if (job/'SAFE_CLOSED.json').exists() and not Path('/proc/'+str(pid)).exists():break
 time.sleep(1)
receipt['process_exited']=not Path('/proc/'+str(pid)).exists();receipt['safe_closed']=json.loads((job/'SAFE_CLOSED.json').read_text()) if (job/'SAFE_CLOSED.json').exists() else None;receipt['completed_epoch']=time.time()
(base/'SWITCH_FLAT_STOPPED.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
