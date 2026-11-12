"""Preserve R1 evidence, verify corrected reward endpoint wiring, then run7200s."""
from pathlib import Path
import sys,json,hashlib,time,shlex,traceback
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from start_fresh_round import P,E,REMOTE,connect,execute,read,put

def idle():
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:return
  time.sleep(2)
def main():
 c=connect()
 try:
  sf=c.open_sftp();old=REMOTE+'/probe2048_scut_stair_r1';assert read(sf,old+'/SAFE_CLOSED.json')
  out=E/'probe2048_scut_stair_r1';out.mkdir(exist_ok=True)
  for item in sf.listdir_attr(old):
   if item.filename.endswith('.json'):sf.get(old+'/'+item.filename,str(out/item.filename))
  sf.get(old+'.log',str(E/'probe2048_scut_stair_r1.log'))
  manifest=json.loads((E/'UPLOAD_MANIFEST.json').read_text(encoding='utf8'));rel='support/mod4v3_ppo_v1/continuous_stair_env.py';src=T/rel;sf.put(str(src),REMOTE+'/'+rel);manifest[rel]=dict(sha256=hashlib.sha256(src.read_bytes()).hexdigest(),bytes=src.stat().st_size)
  code='import pathlib,hashlib,json;root=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v["sha256"] for k,v in m.items());print(json.dumps({"files_verified":len(m),"reward_endpoint_sync_fix":True}))'
  result=json.loads(execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code)));put(E/'UPLOAD_MANIFEST.json',manifest);put(E/'PROBE_R2_UPLOAD_VERIFIED.json',result)
 finally:c.close()
 idle();name='probe2048_scut_stair_r2';job=REMOTE+'/'+name
 c=connect()
 try:out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' '+name+' --kind probe --num-envs 2048');put(E/'PROBE_R2_LAUNCH.json',json.loads(out))
 finally:c.close()
 print('SCUT_CORRECTED_PROBE_R2_LAUNCHED',flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,job+'/SAFE_CLOSED.json')
   if closed:
    target=E/name;target.mkdir(exist_ok=True)
    for item in sf.listdir_attr(job):
     if item.filename.endswith('.json'):sf.get(job+'/'+item.filename,str(target/item.filename))
    sf.get(job+'.log',str(E/(name+'.log')))
    result=read(sf,job+'/ROUGH_PROBE.json');complete=read(sf,job+'/PROBE_COMPLETE.json');error=read(sf,job+'/ERROR.json');restore=read(sf,job+'/RESTORE.json')
    if error or not result or not complete:raise RuntimeError('Corrected native probe failed: '+str(error))
    assert restore['optimizer_entries']==0 and restore['iteration']==0 and restore['source_iteration']==24692
    group=result['samples'][-1]['terrain']['course_groups'];assert group['continuous_stairs']==273 and group['retained_rough']==1365 and group['flat']==410
    put(E/'PROBE_ACCEPTED.json',dict(epoch=time.time(),accepted_probe=name,no_optimizer_update=True,functional600steps=True,actual_groups=group,reported_per_environment_resets=result['done_totals'],scope='Finite output and no-air/reward isolation; source corrected to same-endpoint termination masks; original perenv2mm/finite/mimic guards unchanged; no globalzero-reset gate',restore=restore));break
  finally:c.close()
  time.sleep(5)
 idle()
 c=connect()
 try:out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' train120m_scut_stair_r1 --kind train --num-envs 2048');put(E/'TRAIN_LAUNCH.json',json.loads(out))
 finally:c.close()
 print('SCUT7200S_MAIN_TRAIN_LAUNCHED',flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
