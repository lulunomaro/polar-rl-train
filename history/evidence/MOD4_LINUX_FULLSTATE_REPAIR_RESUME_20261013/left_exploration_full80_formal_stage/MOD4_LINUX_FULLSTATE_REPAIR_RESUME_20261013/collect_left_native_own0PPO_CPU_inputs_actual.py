"""Readonly successful native boundary and exact saved source collection."""
from pathlib import Path
import json,time,os,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
def main():
 c=connect_linux_only();sf=None
 try:
  sf=c.open_sftp();data=sf.open(ROOT+'/LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json').read();v=json.loads(data);assert v['passed'] and v['PPO_updates']==0
  E=json.loads(sf.open(ROOT+'/left_native0PPO_v1/EXIT_RECEIPT.json').read());assert E['returncode']==0 and E['child_actually_absent'] and not E['physics_capacity_error'] and E['canonical_bytes_unchanged']
  dest=D/'left_native_own0PPO_actual';assert not dest.exists();dest.mkdir()
  names=[ROOT+'/LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json',ROOT+'/LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json',ROOT+'/left_native0PPO_v1/EXIT_RECEIPT.json',ROOT+'/left_native0PPO_v1/worker_stdout.log',v['checkpoint']]
  folder=str(Path(v['checkpoint']).parent).replace('\\','/')
  names.extend(folder+'/'+n for n in sf.listdir(folder) if n.endswith('.json') and ('STARTUP' in n or n in ('CLOCK_TRAINING_HEALTH.json','NATIVE_REPAIRED0PPO_COMPLETE.json','run_manifest.json')))
  rows=[]
  for i,name in enumerate(names):
   p=dest/(str(i)+'_'+name.rsplit('/',1)[-1]);sf.get(name,str(p));b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
   with sf.open(name,'rb') as f:rh=hashlib.file_digest(f,'sha256').hexdigest()
   assert h==rh and p.stat().st_size==sf.stat(name).st_size
   rows.append(dict(remote_path=name,local_path=str(p),bytes=len(b),sha256=h))
  own=next(x for x in rows if x['remote_path']==v['checkpoint']);assert own['sha256']==v['sha256'] and own['bytes']==v['bytes']
  q=D/'reports/LEFT_NATIVE_OWN0PPO_ACTUAL_COLLECTION.json';q.write_text(json.dumps(dict(epoch=time.time(),native_pass=v,exit=E,two_host_byteSHA_exact=rows,no_GPU_PPO_or_signal=True),indent=2),encoding='utf8')
  print(json.dumps(dict(collection=str(q),own_source_SHA=v['sha256'],own_source_bytes=v['bytes'],controls=v['health']['control_steps'],callbacks=v['health']['actual_physics_callbacks'],ordinary=v['health']['ordinary_episode_reset_events'],integrity=v['health']['integrity_task_reset_events'],PPO_updates=0)))
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
