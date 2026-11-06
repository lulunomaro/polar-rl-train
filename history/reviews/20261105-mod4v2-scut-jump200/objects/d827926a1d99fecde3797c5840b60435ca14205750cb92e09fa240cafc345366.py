from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--directory', default='matrix01')
args = parser.parse_args()
folder = ROOT / args.directory
meta = json.loads((folder/'CASES.json').read_text(encoding='utf-8'))
data = np.load(folder/'PHYSICAL.npz')
wheel = [meta['body_names'].index(f'{side}_wheel_link') for side in ('left','right')]
cs_wheel = [meta['contact_names'].index(f'{side}_wheel_link') for side in ('left','right')]
cs_other = [i for i,n in enumerate(meta['contact_names']) if not n.endswith('_wheel_link')]
origins = np.array(meta['origins'])
result = []
for i, case in enumerate(meta['cases']):
    active = data['active'][:,i].astype(bool)
    root = data['root'][:,i].copy()
    root[:,:3] -= origins[i]
    wp = data['body_pos'][:,i,wheel].copy() - origins[i]
    force = np.linalg.norm(data['force'][:,i,cs_wheel],axis=-1)
    other = np.linalg.norm(data['force'][:,i,cs_other],axis=-1).max(axis=-1)
    no_contact = (force < 1.).all(axis=-1)
    ground_support = (force > 1.).all(axis=-1) & (wp[:,:,2] < .075).all(axis=-1)
    clearance = (wp[:,:,2] - .06 > case['step_height'] + .002).all(axis=-1)
    crossed = (wp[:,:,0] - .06 > (case['edge'] + (.4 if case['kind'] == 'small_stairs' else 0.))).all(axis=-1)
    top = crossed & (np.abs(wp[:,:,2] - .06 - (.2 if case['kind'] != 'flat' else 0)) < .015).all(axis=-1) & (force > 1.).all(axis=-1) & (other < 1.)
    q=root[:,3:7]
    w,x,y,z=q.T
    roll=np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y))
    pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1))
    yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
    quiet=top & (np.linalg.norm(root[:,7:9],axis=-1)<=.03) & (np.abs(root[:,9])<=.03) & (np.abs(roll)<=np.deg2rad(10)) & (np.abs(pitch)<=np.deg2rad(10)) & (np.abs(yaw)<=.2)
    def run(mask):
        maximum=cur=0
        for yes in mask & active:
            cur=cur+1 if yes else 0
            maximum=max(maximum,cur)
        return maximum
    armed=False; jumps=[]
    for t in range(len(active)):
        if not active[t]: break
        if ground_support[t]: armed=True
        if armed and no_contact[t] and root[t,9]>.05 and clearance[t] and crossed[t]: jumps.append(t)
    post=np.arange(len(active))*.005>1.5
    a=active&post
    entry={'case':i,**case,'first_episode_seconds':float(active.sum()*.005),'root_x_max':float(root[active,0].max()),'root_z_max_post_settle':float(root[a,2].max()),'wheel_bottom_min_pair_max':float((wp[a,:,2]-.06).min(axis=1).max()),'both_ground_supported_ticks':int((ground_support&active).sum()),'both_airborne_ticks_after_support_candidate':int((no_contact&a).sum()),'whole_wheels_crossed_any':bool((crossed&active).any()),'upward_airborne_whole_clear_tick_count':len(jumps),'top_contact_seconds_max':run(top)*.005,'quiet_top_seconds_max':run(quiet)*.005,'final_root_x':float(root[active,0][-1]),'root_forward_velocity_mean_post_settle':float(root[a,7].mean()),'max_abs_pitch_post_settle':float(np.rad2deg(np.abs(pitch[a]).max()))}
    result.append(entry)
report={'directory':str(folder),'criterion':'ground support followed by upward no-wheel-contact whole-wheel clearance, both wheel top support and quiet 0.5s; first episode only; 200Hz contact','results':result}
(folder/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for r in result:
    print(r['case'],r['kind'],r['velocity'],r['height_command'],'xmax',round(r['root_x_max'],3),'minwheelmax',round(r['wheel_bottom_min_pair_max'],3),'cross',r['whole_wheels_crossed_any'],'top',r['top_contact_seconds_max'],'quiet',r['quiet_top_seconds_max'],'life',r['first_episode_seconds'])
