"""Read this task only; freeze finished reports and complete checkpoints locally."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
parser.add_argument('--job',required=True)
parser.add_argument('--collect',action='store_true')
parser.add_argument('--weights',action='store_true')
args = parser.parse_args()
assert args.job.replace('_','').isalnum()
sys.path.insert(0,args.access_dir)
from ssh72 import connect
plan = json.loads((T/'PLAN.json').read_bytes())
remote = plan['root']+'/'+args.job
client = connect()
try:
    sftp = client.open_sftp()
    names = sftp.listdir(remote)
    result = dict(epoch=time.time(),job=args.job)
    for name in ('ADMISSION.json','ERROR.json','TRAINING_STARTED.json','FIRST_UPDATE.json','LATEST_PROGRESS.json','FINAL.json','RESULT.json','SAFE_CLOSED.json'):
        if name in names:
            with sftp.open(remote+'/'+name,'rb') as stream:
                value = json.loads(stream.read())
            if name == 'RESULT.json':
                value = {k:v for k,v in value.items() if k != 'episodes'}
            if name in ('FIRST_UPDATE.json','LATEST_PROGRESS.json'):
                value = {k:v for k,v in value.items() if k not in ('losses',)}
            result[name] = value
    print(json.dumps(result,indent=2),flush=True)
    if args.collect:
        dest = T/'evidence'/args.job
        dest.mkdir(exist_ok=True)
        files = []
        for name in names:
            if name == 'LATEST_PROGRESS.json':
                continue
            if name.endswith(('.json','.py','.npz')) or (name.endswith('.json.partial') and 'ERROR.json' in names):
                target = dest/name
            elif name.endswith('.pt') and args.weights:
                target = T/'weights'/(args.job+'__'+name)
            else:
                continue
            if target.exists():
                continue
            temp = target.with_name(target.name+'.partial')
            sftp.get(remote+'/'+name,str(temp))
            temp.replace(target)
            files.append(dict(remote=remote+'/'+name,local=str(target),bytes=target.stat().st_size,
                              sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
        if files:
            index = dest/('COLLECTION_'+str(time.time_ns())+'.json')
            index.write_text(json.dumps(dict(epoch=time.time(),files=files),indent=2)+'\n')
        print(json.dumps(dict(newly_frozen_files=len(files))),flush=True)
    sftp.close()
finally:
    client.close()
