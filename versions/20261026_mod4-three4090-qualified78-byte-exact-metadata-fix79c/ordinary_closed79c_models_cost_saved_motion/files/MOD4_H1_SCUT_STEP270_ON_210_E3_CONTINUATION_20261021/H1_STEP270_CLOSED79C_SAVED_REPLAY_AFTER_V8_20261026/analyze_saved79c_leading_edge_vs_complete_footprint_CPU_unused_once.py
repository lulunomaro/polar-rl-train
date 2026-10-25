"""New descriptive question on existing small76 arrays; no raw extraction or dynamics rerun."""
from pathlib import Path
import json,time,traceback
import numpy as np
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
U=N
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    source=json.loads((U/'reports/CLOSED79C_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes())
    with np.load(U/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
        lo=k['wheel_min'];hi=k['wheel_max'];continuous=z['continuous_no_reset'];frames=lo.shape[0]
        front=hi[...,0].min(-1);rear=lo[...,0].min(-1);bottom=lo[...,2].min(-1)
        inside=((lo[...,0]>=.35)&(hi[...,0]<=1.15)&(lo[...,1]>=-.6)&(hi[...,1]<=.6)).all(-1)
        high=bottom>=.27;front_beyond=front>=.35;rear_beyond=rear>=.35
        launched=(z['takeoff_count']>0);clean=np.broadcast_to(continuous,front.shape)
        mask=clean&launched&high&front_beyond
        ids=z['env_ids'];cases=[]
        for e,env in enumerate(ids):
            if not mask[:,e].any():continue
            rows=np.flatnonzero(mask[:,e]);last=int(rows[-1]);near=int(rows[np.argmin(.35-front[rows,e])])
            cases.append({'env_id':int(env),'selected_frames_leading_beyond_and_high':len(rows),'selected_frames_complete_footprint_inside_while_high':int((inside[:,e]&high[:,e]&clean[:,e]&launched[:,e]).sum()),'last_eligible_frame':last,'last_front_x':float(front[last,e]),'last_rear_x':float(rear[last,e]),'remaining_rear_distance_to_original_edge_m':float(max(0,.35-rear[last,e])),'last_both_bottom_m':float(bottom[last,e]),'original_recorded_crossed_any':bool(z['step_wheel_crossed'][:,e].all(-1).any()),'original_recorded_landing_max':int(z['landing_count'][:,e].max()),'original_recorded_recovery_max':int(z['recovery_count'][:,e].max())})
        report={'epoch':time.time(),'scope':source['scope'],'selected_continuous_envs':int(continuous.sum()),'new_question':'Leading edge crossing is not the original complete wheel footprint inside top condition.',
                'continuous_launched_high_and_leading_beyond_envframes':int(mask.sum()),'among_these_complete_footprint_inside_envframes':int((mask&inside).sum()),'among_these_rear_still_before_edge_envframes':int((mask&~rear_beyond).sum()),
                'continuous_launched_high_complete_footprint_inside_envframes':int((clean&launched&high&inside).sum()),'cases':cases,
                'original_goal_geometry_reproduced_only_for_description':{'edge_x':.35,'depth':.8,'width':1.2,'minimum_height':.27},
                'no_platform_contact_ID_force_or_callback_truth_reconstructed':True,'necessary_geometry_only_not_sufficient_landing_or_success':True,'not_a_new_training_or_physics_threshold':True,
                'no_wholewindow_frozen_policy_or_causal_before_after_claim':True,'no_PT_original_raw_GPU_policy_physics_remote_or_account_action':True}
    put('SAVED76_LEADING_EDGE_VS_COMPLETE_WHEEL_FOOTPRINT_DESCRIPTIVE_CPU_ACTUAL.json',report)
    print(json.dumps(report))
except BaseException:
    put('SAVED76_FOOTPRINT_READER_ORIGINAL_ERROR_ACTUAL.json',{'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_replay':True});raise
