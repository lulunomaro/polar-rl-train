"""Bind the newly collected phase-clock data before the R3 owner launches."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
args=parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect
plan=json.loads((T/'PLAN_R3.json').read_bytes())
client=connect()
try:
    s=client.open_sftp()
    with s.open(plan['root']+'/teacher_demos_r2/SAFE_CLOSED.json','rb') as f:
        closed=json.loads(f.read())
    assert closed['outcome']=='complete'
    with s.open(plan['root']+'/teacher_demos_r2/RESULT.json','rb') as f:
        result=json.loads(f.read())
    dataset=T/'weights/teacher_demos_r2__successful_demos.pt'
    if not dataset.exists():s.get(plan['root']+'/teacher_demos_r2/successful_demos.pt',str(dataset))
    assert hashlib.sha256(dataset.read_bytes()).hexdigest()==result['dataset_sha256']
    import torch
    data=torch.load(dataset,map_location='cpu',weights_only=False)
    assert data['policy'].shape[1]==35 and float(data['policy'][:,34].max())>.9
    assert bool(torch.isfinite(data['policy']).all()) and bool(torch.isfinite(data['actions']).all())
    (T/'PLAN_R3_BEFORE_DEMO.json').write_bytes((T/'PLAN_R3.json').read_bytes())
    plan['jump_bc'].update(dataset=plan['root']+'/teacher_demos_r2/successful_demos.pt',dataset_sha256=result['dataset_sha256'])
    (T/'PLAN_R3.json').write_text(json.dumps(plan,indent=2)+'\n')
    assert not any(name=='CONTINUATION_OWNER_R3.json' for name in s.listdir(plan['root']))
    s.put(str(T/'PLAN_R3.json'),plan['root']+'/PLAN_R3.json')
    s.close()
finally:client.close()
check=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'check_guidance.py'),'--dataset',str(dataset),
    '--report','R3_CLOCK_GUIDANCE_NO_UPDATE_CHECK.json'],cwd=T,capture_output=True,text=True,encoding='utf8')
(T/'evidence/R3_CLOCK_GUIDANCE_CHECK.log').write_text(check.stdout+check.stderr)
assert check.returncode==0,check.stdout+check.stderr
receipt=dict(epoch=time.time(),dataset=result,clock_input_max=float(data['policy'][:,34].max()),
    PLAN_sha256=hashlib.sha256((T/'PLAN_R3.json').read_bytes()).hexdigest(),
    native_successful_collection_passed=True,no_optimizer_check_passed=True,
    original_deadline_epoch=plan['original_training_start_epoch']+7200.,
    root_parent_sha256=plan['root_parent_sha256'])
(T/'evidence/R3_FINAL_INPUT_BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(dataset_sha256=result['dataset_sha256'],samples=data['metadata']['samples'],
    successful_demonstrations=data['metadata']['successful_episodes'],gradient_check_passed=True,
    original_deadline_epoch=receipt['original_deadline_epoch'])),flush=True)
