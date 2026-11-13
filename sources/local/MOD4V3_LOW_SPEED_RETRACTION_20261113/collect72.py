"""Collect complete checkpoints and compact status from this experiment only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import sys
import time

T=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--access-dir',required=True);a=p.parse_args()
sys.path.insert(0,a.access_dir)
from ssh72 import connect,execute
r='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_LOW_SPEED_RETRACTION_20261113_R1'
E=T/'evidence';E.mkdir(exist_ok=True)
c=connect();records=[];models=[]
try:
    s=c.open_sftp()
    for name in ['native_nominal_r1','train010m_parent_r1','train010m_teacher_r1']:
        folder=r+'/'+name;dest=E/name;dest.mkdir(exist_ok=True)
        try:files=s.listdir_attr(folder)
        except FileNotFoundError:continue
        for item in files:
            if not stat.S_ISREG(item.st_mode) or item.filename.endswith('.partial'):
                continue
            if Path(item.filename).suffix not in ('.json','.pt','.npz'):
                continue
            target=dest/item.filename
            if target.exists() and target.stat().st_size==item.st_size and int(target.stat().st_mtime)==item.st_mtime:
                continue
            s.get(folder+'/'+item.filename,str(target))
            os.utime(target,(item.st_mtime,item.st_mtime))
            if target.suffix=='.pt':
                models.append(dict(path=str(target.relative_to(T)),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
        for remote_name in [name+'.log']:
            try:s.get(r+'/'+remote_name,str(E/remote_name))
            except FileNotFoundError:pass
        progress=dest/('PROGRESS.json' if name=='native_nominal_r1' else 'LATEST_PROGRESS.json')
        info=json.loads(progress.read_text()) if progress.exists() else {}
        part=dict(job=name,complete=(dest/'SAFE_CLOSED.json').exists(),error=(dest/'ERROR.json').exists())
        if name=='native_nominal_r1':
            part.update({k:info.get(k) for k in ['step','wall_seconds','success','finished']})
        else:
            counts=info.get('terrain',{}).get('continuous_stair',{}).get('counts_DR_then_nominal')
            part.update(iteration=info.get('iteration'),ppo_elapsed_s=info.get('training_elapsed_seconds'),done=info.get('done_totals'),stair_counts=counts)
        records.append(part)
    status,out,err=execute(c,'nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader; nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader',20)
    (E/'GPU_READBACK_LATEST.json').write_text(json.dumps(dict(epoch=time.time(),status=status,stdout=out,stderr=err),indent=2)+'\n')
    s.close()
finally:c.close()
all_models=[]
for path in sorted(E.glob('train010m_*/*.pt')):
    all_models.append(dict(path=path.relative_to(T).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(E/'MODEL_COLLECTION.json').write_text(json.dumps(dict(epoch=time.time(),complete_PT_files=all_models,status=records),indent=2)+'\n')
print(json.dumps(dict(status=records,new_PT=models,gpu=out),indent=2),flush=True)
