"""Add read-only full-array and worst-environment evidence to the original smoke."""
import ast,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
text=(D/'spin_rate_fullscale_probe.py').read_text()
def replace(a,b):
 global text
 assert text.count(a)==1,a
 text=text.replace(a,b)
replace('import time\n','import time\nimport sys,hashlib\nsys.path.insert(0,"/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/isaac/mod4")\n')
replace('import torch\n','os.environ["RM_SPIN_MAX_RAD_S"]=str(args.max_rate)\nimport torch\n')
replace('    initial_parameters=env._mild_dr.audit()','''    # Read only: no force, RNG, command or reset alteration.
    initial_q=robot.data.joint_pos.detach().cpu().contiguous().numpy()
    initial_root=robot.data.root_state_w.detach().cpu().contiguous().numpy()
    import numpy as np
    np.savez_compressed(args.output+'.initial.npz',root=initial_root,q=initial_q)
    initial_state={k:{'sha256':hashlib.sha256(v.tobytes()).hexdigest(),'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in [('root',initial_root),('q',initial_q)]}
    initial_parameters=env._mild_dr.audit()''')
replace('    torch.cuda.reset_peak_memory_stats();began=time.time()','''    per_tilt=torch.zeros(n,device=dev);per_height=torch.zeros(n,device=dev)
    per_peak_step=torch.full((n,),-1,device=dev,dtype=torch.long);worst_trace=[]
    torch.cuda.reset_peak_memory_stats();began=time.time()''')
replace('            maxtilt=max(maxtilt,float(tilt.max()))','''            new_peak=tilt>per_tilt
            per_peak_step=torch.where(new_peak,step,per_peak_step);per_tilt=torch.maximum(per_tilt,tilt)
            heights=(task.root_height_above_ground(env)-.25).abs();per_height=torch.maximum(per_height,heights)
            eid=int(tilt.argmax())
            worst_trace.append({'step':step,'env_id':eid,'group_id':int(gids[eid]),'tilt_deg':float(tilt[eid]),'height_error_m':float(heights[eid]),'command_vx':float(targets[eid]),'command_yaw':float(yaw_targets[eid]),'root_state':robot.data.root_state_w[eid].cpu().tolist()})
            maxtilt=max(maxtilt,float(tilt.max()))''')
replace("    Path(args.output).write_text(json.dumps(result,indent=2));print('SPIN_FULLSCALE_SMOKE '+json.dumps(result),flush=True)",'''    result['initial_state_hashes']=initial_state
    result['initial_state_arrays_path']=args.output+'.initial.npz'
    result['diagnostic_only_no_PPO']=True
    result['per_environment']={'group_ids':gids.cpu().tolist(),'max_tilt_deg':per_tilt.cpu().tolist(),'max_height_error_m':per_height.cpu().tolist(),'peak_step':per_peak_step.cpu().tolist()}
    result['worst_trace']=worst_trace
    result['top_tilt_environments']=[{'env_id':int(eid),'group_id':int(gids[eid]),'command_vx':float(targets[eid]),'command_yaw':float(yaw_targets[eid]),'peak_tilt_deg':float(per_tilt[eid]),'peak_step':int(per_peak_step[eid])} for eid in per_tilt.topk(20).indices]
    Path(args.output).write_text(json.dumps(result,indent=2));print('SPIN_FULLSCALE_SMOKE '+json.dumps({k:v for k,v in result.items() if k not in ['per_environment','worst_trace']}),flush=True)''')
ast.parse(text);(D/'fullscale_worst_diagnostic.py').write_text(text)
print('Read-only full-array/worst-environment diagnostic prepared; no deployment.')
