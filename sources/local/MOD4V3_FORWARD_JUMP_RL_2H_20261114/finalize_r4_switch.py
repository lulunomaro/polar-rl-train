"""Bind R4 data before safely handing GPU0over inside the original window."""
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
plan=json.loads((T/'PLAN_R4.json').read_bytes())
root=plan['root']
client=connect()
try:
    s=client.open_sftp()
    while True:
        try:
            with s.open(root+'/teacher_demos_r3/SAFE_CLOSED.json','rb') as f:closed=json.loads(f.read())
            break
        except FileNotFoundError:
            assert time.time()<plan['original_training_start_epoch']+7100.,'Original budget almost exhausted; R3remains owner'
            print('Waiting for no-optimizer native demonstration collection',flush=True)
            time.sleep(10.)
    assert closed['outcome']=='complete'
    with s.open(root+'/teacher_demos_r3/RESULT.json','rb') as f:result=json.loads(f.read())
    dataset=T/'weights/teacher_demos_r3__successful_demos.pt'
    if not dataset.exists():s.get(root+'/teacher_demos_r3/successful_demos.pt',str(dataset))
    assert hashlib.sha256(dataset.read_bytes()).hexdigest()==result['dataset_sha256']
    import torch
    data=torch.load(dataset,map_location='cpu',weights_only=False)
    flight=data['phase']==3
    flag=data['policy'][flight,31]
    assert len(flag)>0 and bool((flag<.5).any()) and bool((flag>.5).any())
    assert bool(torch.isfinite(data['policy']).all()) and bool(torch.isfinite(data['actions']).all())
    parent=T/'weights'/('train_cont_r3__'+Path(plan['parent']).name)
    check=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'check_guidance.py'),'--dataset',str(dataset),
        '--checkpoint',str(parent),'--report','R4_GUIDANCE_NO_UPDATE_CHECK.json'],cwd=T,capture_output=True,text=True,encoding='utf8')
    (T/'evidence/R4_GUIDANCE_CHECK.log').write_text(check.stdout+check.stderr)
    assert check.returncode==0,check.stdout+check.stderr
    with s.open(root+'/train_cont_r3/REQUEST_STOP','wx') as f:
        f.write('Complete current update and full save; continue from best R3checkpoint with descending-flight cue; original deadline unchanged.')
    while True:
        try:
            with s.open(root+'/train_cont_r3/SAFE_CLOSED.json','rb') as f:previous=json.loads(f.read())
            break
        except FileNotFoundError:time.sleep(2.)
    assert previous['outcome']=='complete'
    with s.open(root+'/train_cont_r3/FINAL.json','rb') as f:final=json.loads(f.read())
    old=json.loads((T/'PLAN_R3.json').read_bytes())
    (T/'PLAN_R4_DRAFT.json').write_bytes((T/'PLAN_R4.json').read_bytes())
    plan.update(draft=False,prior_phase_elapsed_seconds=old['prior_phase_elapsed_seconds']+final['elapsed_seconds'])
    plan['jump_bc'].update(dataset=root+'/teacher_demos_r3/successful_demos.pt',dataset_sha256=result['dataset_sha256'])
    (T/'PLAN_R4.json').write_text(json.dumps(plan,indent=2)+'\n')
    s.put(str(T/'PLAN_R4.json'),root+'/PLAN_R4.json')
    s.close()
finally:client.close()
receipt=dict(epoch=time.time(),R3_final=final,R3_closed=previous,parent=plan['parent'],parent_sha256=plan['parent_sha256'],
    root_parent_sha256=plan['root_parent_sha256'],dataset=result,
    source_change='Expose descending flight through landing-preparation mode; other task, rewards, assets and guards unchanged',
    original_deadline_epoch=plan['original_training_start_epoch']+7200.,
    PLAN_sha256=hashlib.sha256((T/'PLAN_R4.json').read_bytes()).hexdigest(),
    no_update_guidance_check_passed=True,extra_budget_seconds=0)
(T/'evidence/R4_FINAL_INPUT_BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(ready=True,parent=plan['parent'],dataset_sha256=result['dataset_sha256'],
    remaining_wall_seconds=receipt['original_deadline_epoch']-time.time())),flush=True)
