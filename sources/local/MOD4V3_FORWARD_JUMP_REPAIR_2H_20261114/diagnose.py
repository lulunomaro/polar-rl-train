"""Read frozen predecessor trajectories and labels; never create an optimizer."""
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn

T = Path(__file__).resolve().parent
P = T.parent/'MOD4V3_FORWARD_JUMP_RL_2H_20261114'
config = json.loads((P/'native_package/runtime_config.json').read_bytes())
print('runtime keys', list(config))
data = torch.load(P/'weights/teacher_demos_r3__successful_demos.pt', map_location='cpu', weights_only=False)
state = torch.load(T/'weights/parent_r3_080m.pt', map_location='cpu', weights_only=False)
actor = nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
actor.load_state_dict({k.removeprefix('mlp.'):v for k,v in state['actor_state_dict'].items() if k.startswith('mlp.')})
with torch.inference_mode():
    prediction = actor(data['policy']).clamp(-6,6)
    error = prediction-data['actions']
    phase_errors = []
    for phase in range(5):
        mask = data['phase']==phase
        e = error[mask]
        phase_errors.append(dict(phase=phase,states=int(mask.sum()),action_mse=e.square().mean(0).tolist(),
            bilateral_delta_bias=(.25*(e[:,0]-e[:,1]+e[:,2]-e[:,3])).mean().item(),
            slots_mean=data['policy'][mask,28:35].mean(0).tolist()))
results = []
for label in ('eval_r3_model_080m','eval_r4_model_final'):
    path = P/'evidence'/label
    trace = np.load(path/'trajectory.npz')
    rows = json.loads((path/'RESULT.json').read_bytes())['episodes']
    names = trace['joint_names'].tolist()
    ids = [names.index(n) for n in ('left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint')]
    q = trace['native_q'][:,:,ids]
    delta = .5*(q[:,:,0]-q[:,:,1]+q[:,:,2]-q[:,:,3])
    cases = []
    for row in rows:
        i = row['env']
        valid = np.arange(trace['phase'].shape[0]) < row['steps']-1
        air = (trace['phase'][:,i]==3)&valid
        if not air.any():
            continue
        frames = np.flatnonzero(air)
        j = frames[np.argmin(delta[air,i])]
        cases.append(dict(env=i,nominal=row['nominal'],min_air_delta=float(delta[air,i].min()),
            at_min_flight_seconds=float((j-frames[0])*.02),
            air_frames=len(frames),action_at_min=trace['action'][j,i].tolist(),
            first_actions=trace['action'][frames[:10],i].tolist(),
            first_measured_delta=delta[frames[:10],i].tolist(),retracted=row['retracted'],success=row['success']))
    summary = {}
    for nominal, name in ((False,'fullDR'),(True,'nominal')):
        values = [c['min_air_delta'] for c in cases if c['nominal']==nominal]
        summary[name] = dict(n=len(values),minimum=float(np.min(values)),median=float(np.median(values)),maximum=float(np.max(values)))
    results.append(dict(checkpoint=label,summary=summary,cases=cases))
report = dict(optimizer_created=False,optimizer_updates=0,parent_sha256=hashlib.sha256((T/'weights/parent_r3_080m.pt').read_bytes()).hexdigest(),
    phase_fit_on_R4_teacher_dataset=phase_errors,trajectories=results,
    native_PPO_actor_critic_gradient_clipping='Separate clip_grad_norm_ calls; critic cannot directly scale actor gradients',
    confirmed_target_conflict='Old air reward switches to extension at vz<0; cue/teacher switch at vz<-0.10 regardless of measured tuck')
(T/'evidence/DIAGNOSIS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(phase_fit=phase_errors,trajectory_summaries=[dict(checkpoint=r['checkpoint'],summary=r['summary'],example=next(c for c in r['cases'] if c['nominal'])) for r in results]),indent=2))
