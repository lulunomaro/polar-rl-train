"""Evaluate a frozen policy only after each recorded real blocked approach."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from replay_probe import T, MODELS, setup, run_case

p=argparse.ArgumentParser()
p.add_argument('--model',choices=['parent','teacher'],required=True)
p.add_argument('--checkpoint')
p.add_argument('--out',required=True)
p.add_argument('--limit',type=int,default=17)
p.add_argument('--intervention')
a=p.parse_args()
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=False)
if a.checkpoint:
    path=Path(a.checkpoint).resolve();MODELS[a.model]=(path,hashlib.sha256(path.read_bytes()).hexdigest())
show=setup(out,a.model)
bank=json.loads((T/'evidence/BLOCKED_BANK.json').read_text())[:a.limit]
rows=[]
for state in bank:
    case=out/('from_'+state['id']);case.mkdir()
    row=run_case(show,case,a.model,state['speed'],state['seed'],16.,
                 restore=dict(path=state['path'],index=state['snapshot']),intervention=a.intervention)
    trace=next(case.glob('*/trajectory.npz'))
    with np.load(trace) as data:
        row['recovery_actual_vx_peak']=float(data['vx_body'].max())
        row['recovery_actual_vx_mean']=float(data['vx_body'].mean())
        row['pair_wheel_clearance_peak_m']=float((data['wheel'][:,:,2].min(1)-.2625).max())
        row['minimum_leg_lengths_m']=data['hip_to_wheel'].min(0).tolist()
        row['max_abs_pitch_roll_deg']=np.abs(data['pose_deg'][:,:2]).max(0).tolist()
        base=int(data['base_body_id']);force=data['body_contact_force'][:,base]
        row['chassis_contact_peak_N']=float(np.linalg.norm(force,axis=1).max())
        row['chassis_contact_duration_s']=float((np.linalg.norm(force,axis=1)>1).sum()*.0025)
    row['blocked_source']=state['id']
    rows.append(row)
    (out/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),first_landed=sum(x['first_landed'] for x in rows),two_steps=sum(x['success'] for x in rows),rows=rows),indent=2)+'\n')
(out/'RESULT.json').write_text(json.dumps(dict(requested=len(rows),first_landed=sum(x['first_landed'] for x in rows),two_steps=sum(x['success'] for x in rows),rows=rows),indent=2)+'\n')
