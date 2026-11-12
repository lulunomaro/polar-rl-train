"""Condense completed paired diagnostics without changing their raw results."""
from pathlib import Path
import json,numpy as np
T=Path(__file__).resolve().parent;E=T/'evidence';rows=[]
for folder in ('native_control_trace_r1','native_tgs_force_r1','native_velocity32_diag_r1','native_round_wheel_diag_r2'):
 p=E/folder
 if not (p/'trajectory.npz').exists():continue
 d=np.load(p/'trajectory.npz');layout=json.loads((p/'TRACE_LAYOUT.json').read_text());ix=layout['active_ids'];result=json.loads((p/'RESULT.json').read_text())
 for i in range(d['values'].shape[1]):
  model=list(layout['models'])[i//4];variant=layout['variants'][(i//2)%2];h=layout['tasks'][i%2][3]
  q=d['root'][:,:,3:7];x,y,z,w=np.moveaxis(q,2,0);heading=np.stack((1-2*(y*y+z*z),2*(x*y+w*z)),axis=-1);heading/=np.linalg.norm(heading,axis=-1,keepdims=True)
  fd=((np.diff(d['root'][:,:,:2],axis=0)/.02)*heading[1:]).sum(-1)
  row=dict(experiment=folder,model=model,variant=variant,command=2.2,height=h,pre_vx=float(d['values'][180:299,i,0].mean()),tail_vx=float(d['values'][400:,i,0].mean()),tail_vx_std=float(d['values'][400:,i,0].std()),tail_fd_vx=float(fd[400:,i].mean()),wheel_qd_mean=d['joint_vel'][400:,i][:,ix[4:]].mean(0).tolist(),wheel_qd_std=d['joint_vel'][400:,i][:,ix[4:]].std(0).tolist(),leg_q_std=d['joint_pos'][400:,i][:,ix[:4]].std(0).tolist(),action_mean=d['actions'][400:,i].mean(0).tolist(),all_resets=sum(x['resets'] for x in result['rows']),no_optimizer=True)
  rows.append(row)
(E/'NATIVE_VARIANTS.json').write_text(json.dumps(dict(protocol='All frozen actors; each experiment independent full process; matched seed66 and nominal/DR starts; strict2mm guard; sphere diagnostic is not accepted plant',rows=rows),indent=2))
for r in rows:
 if r['variant']=='nominal0':print(r['experiment'],r['model'],r['height'],round(r['pre_vx'],4),round(r['tail_vx'],4),[round(v,3) for v in r['wheel_qd_std']])
