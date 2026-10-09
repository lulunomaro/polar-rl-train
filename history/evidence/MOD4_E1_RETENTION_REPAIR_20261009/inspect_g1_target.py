from pathlib import Path
import os,sys,json,hashlib,shlex,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_REVIEWED_STABLE_20261009'
def main():
 assert not (R/'G1_TARGET_INSPECTED.json').exists()
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as sf:
   b=sf.open(ROOT+'/reports/E1_PLANNED_BEHAVIOR_PUBLISHED.json').read();(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json').write_bytes(b)
   row=json.loads(b);asset=row['terrain_package'];p=D/'artifacts'/Path(asset['path']).name;p.parent.mkdir(exist_ok=True)
   if not p.exists():sf.get(asset['path'],str(p))
   assert hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256']
  code="""from pathlib import Path
import json,hashlib,time
root=Path('/home/egde/IsaacLab/source/isaaclab/isaaclab/terrains')
if not root.exists():
 paths=list(Path('/home/egde').glob('**/isaaclab/terrains/sub_terrain_cfg.py'));assert len(paths)==1,paths;root=paths[0].parent
names=['sub_terrain_cfg.py','terrain_generator.py']
sdk={n:dict(path=str(root/n),source=(root/n).read_text(),sha256=hashlib.sha256((root/n).read_bytes()).hexdigest()) for n in names}
p=Path(SOURCE);assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA
print(json.dumps(dict(epoch=time.time(),sdk=sdk,source_path=str(p),source_sha256=SHA,source_bytes=p.stat().st_size,no_GPU_PPO_budget_or_queue_write=True)))
""".replace('SOURCE',repr(row['completed_first_task']['checkpoint']['path']) if 'completed_first_task' in row else repr('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009/learning_logs/2026-10-09_17-50-07_e1_gentle_route_recovery_1791539206096646372/model_32053.pt')).replace('SHA',repr('655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f'))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace')
  v=json.loads(b);(R/'G1_TARGET_INSPECTED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps({k:v for k,v in v.items() if k!='sdk'}))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
