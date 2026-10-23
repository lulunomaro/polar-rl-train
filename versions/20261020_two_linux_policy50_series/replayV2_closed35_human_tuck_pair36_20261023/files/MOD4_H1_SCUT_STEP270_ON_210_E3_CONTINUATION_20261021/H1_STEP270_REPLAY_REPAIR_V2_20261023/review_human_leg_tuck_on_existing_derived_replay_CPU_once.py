"""New human question: leg retraction in the already extracted old31 clip.

Read only the small derived motion/kinematic artifacts; no original raw, model,
policy, physics, optimizer or RNG execution. This does not assess new35 policy.
"""
from pathlib import Path
import json,time,traceback
import numpy as np

D=Path(__file__).resolve().parent;R=D/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def main():
    report=json.loads((R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json').read_bytes())
    with np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z, np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
        names=report['body_names'];order=report['joint_order_derived_from_actual_31link_order_each_one_DOF_incoming_joint']
        pose=k['body_pose'];wheel=pose[:,:,[names.index('left_wheel'),names.index('right_wheel')],:3,3]
        root=pose[:,:,0,:3,3];delta=wheel-root[:,:,None,:];length=np.linalg.norm(delta,axis=-1)
        bottom=k['wheel_min'][:,:,:,2].min(-1);front=k['wheel_max'][:,:,:,0].min(-1)
        q=z['q30'];out=[]
        for env in (10042,2887,13576):
            e=int(np.where(z['env_ids']==env)[0][0]);apex=int(bottom[:,e].argmax());near=int(front[:,e].argmax())
            def row(f):
                return dict(frame=f,control=int(z['control_rows'][f]),body_to_wheel_axle_3D_m=length[f,e].tolist(),body_above_wheel_axle_world_z_m=(-delta[f,e,:,2]).tolist(),root_z_m=float(root[f,e,2]),lower_wheel_bottom_z_m=float(bottom[f,e]),trailing_front_gap_m=float(.35-front[f,e]),world_vx=float(z['root13'][f,e,7]),joint_rad={n:float(q[f,e,order.index(n)]) for n in ('left_hip','left_crank','right_hip','right_crank')})
            out.append(dict(env_id=env,first=row(0),wheel_bottom_apex=row(apex),closest_to_edge=row(near),last=row(47),leg_length_min_m=length[:,e].min(0).tolist(),leg_length_max_m=length[:,e].max(0).tolist(),net_length_change_first_to_apex_m=(length[apex,e]-length[0,e]).tolist(),takeoff_count_recorded_max=int(z['takeoff_count'][:,e].max()),landing_count_recorded_max=int(z['landing_count'][:,e].max()),not_complete_episode_or_airborne_mask=True))
    result=dict(epoch=time.time(),passed_descriptive_CPU=True,human_question='还有看你的图里，跳上台阶后腿以旧保持站立状态，我觉得跳上台阶时因该收腿，有感觉吗？',source_scope='Old closed31 already extracted 48-frame .48s clip and existing USD kinematic reconstruction; new question on leg retraction, no reread of original two NPZ, no new rollout or new35 policy conclusion.',source_artifacts=[dict(path=str(D/'SELECTED_RECORDED_MOTION.npz'),bytes=1594963,producer_SHA='e9e51fb811ea1d368ba64396eb551e0f48cc08f253f45975406baadc08b51256'),report['artifact']],cases=out,existing_tuck_reward=dict(body_to_wheel_3D_target_m=.22,current_weight=.5,existing_scope='original active request AND original measured air_ticks>0',no_weight_change=True),interpretation='Compare actual body-to-wheel length, not appearance alone. Existing clip is insufficient to claim a full takeoff-to-landing sequence or unique cause. Longer legs at the wheel-height apex can reduce clearance for a fixed body pose; whether folding changes horizontal reach, contact or stability requires actual task evidence.',no_original_raw_PT_GPU_policy_optimizer_RNG_or_PhysX=True,no_new_reward_or_training_gate=True,joint_order_derived_not_fresh_PhysX_readback=True)
    put('HUMAN_LEG_TUCK_EXISTING_DERIVED_REPLAY_CPU_ACTUAL.json',result)
    print(json.dumps(dict(cases=[dict(env=x['env_id'],first=x['first']['body_to_wheel_axle_3D_m'],apex=x['wheel_bottom_apex']['body_to_wheel_axle_3D_m'],min=x['leg_length_min_m'],max=x['leg_length_max_m']) for x in out],no_new_training_change=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        put('HUMAN_LEG_TUCK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
