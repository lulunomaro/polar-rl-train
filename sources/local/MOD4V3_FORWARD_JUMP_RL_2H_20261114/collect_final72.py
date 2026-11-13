"""Freeze this finished experiment's owner/evaluator logs and release evidence."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
args=parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan=json.loads((T/'PLAN_R4.json').read_bytes())
root=plan['root']
client=connect()
try:
    s=client.open_sftp()
    with s.open(root+'/train_cont_r4/SAFE_CLOSED.json','rb') as f:
        closed=json.loads(f.read())
    assert closed['outcome']=='complete'
    destination=T/'evidence/frozen_remote'
    destination.mkdir(exist_ok=True)
    files=[]
    pids=set()
    for name in s.listdir(root):
        include=(name.endswith('.log') and name.startswith(('train','eval','admit','teacher')))
        include|=name.endswith('.json') and name.startswith(('LAUNCH_','PLAN','TRAIN_OWNER','CONTINUATION_OWNER'))
        if not include:continue
        target=destination/name
        s.get(root+'/'+name,str(target))
        files.append(dict(remote=root+'/'+name,local=str(target),bytes=target.stat().st_size,
            sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
        if name.startswith(('LAUNCH_','TRAIN_OWNER','CONTINUATION_OWNER')):
            data=json.loads(target.read_bytes())
            if 'pid' in data:pids.add(str(data['pid']))
    for job in ('train120m_r1','train_cont_r2','train_cont_r3','train_cont_r4'):
        try:s.get(root+'/'+job+'/REQUEST_STOP',str(destination/(job+'_REQUEST_STOP.txt')))
        except FileNotFoundError:pass
    s.close()
    status,out,err=execute(client,'nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name --format=csv,noheader',20)
    assert status==0,err
    owners=list(csv.reader(out.splitlines()))
    remaining=[row for row in owners if len(row)>=2 and row[1].strip() in pids]
    receipt=dict(epoch=time.time(),root=root,files=files,own_launch_pids=sorted(pids),
        current_compute_apps=owners,own_gpu_owners_remaining=remaining,
        scene_closed=closed,all_experiment_gpu_contexts_released=not remaining)
    (T/'evidence/FINAL_REMOTE_COLLECTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(logs_and_receipts=len(files),all_experiment_gpu_contexts_released=not remaining,
        own_gpu_owners_remaining=remaining)),flush=True)
finally:client.close()
