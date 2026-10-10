"""Read own frozen training sources and saved CURB spawn state; never launch a trainer."""
from review133_io import *
import shlex,traceback
from stage_formal_dispatch_reviewed_once import PY

def main():
 n,w=connect_both()
 try:
  folder=D/'actual_training_source'/str(time.time_ns());folder.mkdir(parents=True)
  files=[]
  with n.open_sftp() as f:
   freeze=json.loads(f.open(NEW+'/reports/SOURCE_FREEZE.json').read())
   for name in ('isaac/mod4/e1_full_pose_reset.py','isaac/mod4/e1_terrain_runtime.py','isaac/mod4/curb20_geometry.py','isaac/mod4/curb20_retention_runtime.py','isaac/mod4/curb20_fullstate_checkpoint.py'):
    if name not in freeze['sha256']:continue
    raw=f.open(NEW+'/'+name).read();assert H(raw)==freeze['sha256'][name]
    p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    files.append(dict(source=NEW+'/'+name,local=str(p),sha256=H(raw),bytes=len(raw),own_source_freeze_exact=True))
  code=r'''from pathlib import Path
import json,torch,hashlib
torch.set_num_threads(1)
R=Path(ROOT)/'reports';p=json.loads((R/'e1_CURB20_independent_observation_PASSED.json').read_bytes())['checkpoint'];path=Path(p['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
c=torch.load(path,map_location='cpu',weights_only=False);s=c['E1_terrain_state'];spawn=s['spawn_xy'];q=s['reset_expected_q'];assert not torch.cuda.is_initialized()
print(json.dumps(dict(checkpoint=p,terrain_identity={k:v for k,v in s.items() if not isinstance(v,torch.Tensor)},spawn_xy=spawn.tolist(),episode_min=int(s['episode'].min()),episode_max=int(s['episode'].max()),reset_joint_shape=list(q.shape),no_CUDA_or_PPO=True)))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  assert rc==0,err.decode(errors='replace')
  result=json.loads(raw);result.update(files=files,read_only=True,new_budget_seconds=0)
  p=save('CURB_TRAINING_RESET_ACTUAL_'+str(time.time_ns())+'.json',result)
  xy=result['spawn_xy'];print(json.dumps(dict(report=str(p),checkpoint_sha=result['checkpoint']['sha256'],spawn_count=len(xy),first_spawn=xy[:4],sources_captured=len(files),no_CUDA_or_PPO=True)))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('CURB_RESET_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,no_mutation=True));raise
