"""Change only terrain after the source owner has saved, closed and evaluated."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
from .train import put


def main():
    plan_path=Path(sys.argv[1]);plan=json.loads(plan_path.read_bytes())
    root=plan_path.parent;source=Path(plan['map_source_root'])
    owner=json.loads((source/'OWNER.json').read_bytes())
    put(root/'WAITING_FOR_BOUNDARY.json',dict(epoch=time.time(),pid=os.getpid(),
        source=str(source),terrain='official_rough',full_PPO_resume=True))
    while not (source/'OWNER_COMPLETE.json').exists():
        current=json.loads((source/'OWNER_CURRENT.json').read_bytes())
        job=source/current['job']
        if (job/'ERROR.json').exists():
            raise RuntimeError('Source failed before the saved/closed/evaluated boundary')
        owner=json.loads((source/'OWNER.json').read_bytes())
        if not Path('/proc/'+str(owner['pid'])).exists():
            raise RuntimeError('Source owner exited without its completion receipt')
        time.sleep(10)
    final=json.loads((source/plan['map_source_job']/'FINAL.json').read_bytes())
    checkpoint=final['checkpoint'];path=Path(checkpoint['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=checkpoint['SHA']:
        raise ValueError('Source final checkpoint changed')
    plan['resume_checkpoint']=str(path)
    plan['source_checkpoint_identity']=checkpoint
    put(plan_path,plan)
    put(root/'MAP_SWITCH_BOUNDARY.json',dict(epoch=time.time(),source_final=checkpoint,
        source_owner_complete=json.loads((source/'OWNER_COMPLETE.json').read_bytes()),
        requested_change='Isaac Lab installed ROUGH_TERRAINS_CFG.copy() only'))
    bootstrap='import runpy,sys;sys.path.insert(0,'+repr(str(root/'code'))+');sys.argv=["owner",'+repr(str(plan_path))+'];runpy.run_module("mod4v3_ppo.owner",run_name="__main__")'
    env=dict(os.environ)
    # Wait only for the old owner's already-completed lease to be released.
    while Path('/proc/'+str(owner['pid'])).exists():
        time.sleep(1)
    with (root/'owner.log').open('x') as log:
        process=subprocess.Popen([plan['python'],'-B','-c',bootstrap],stdout=log,stderr=subprocess.STDOUT,env=env)
        status=process.wait()
    put(root/'MAP_OWNER_EXIT.json',dict(epoch=time.time(),returncode=status))
    if status or not (root/'OWNER_COMPLETE.json').exists():
        raise RuntimeError('Official rough continuation failed')


if __name__=='__main__':main()
