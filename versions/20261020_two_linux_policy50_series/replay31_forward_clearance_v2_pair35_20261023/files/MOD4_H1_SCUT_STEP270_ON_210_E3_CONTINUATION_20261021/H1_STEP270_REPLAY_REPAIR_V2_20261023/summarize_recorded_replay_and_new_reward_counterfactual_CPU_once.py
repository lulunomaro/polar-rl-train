from pathlib import Path
import hashlib,importlib.util,json,time,traceback
import numpy as np
import torch

D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
read=lambda p:json.loads(Path(p).read_bytes())

def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

try:
    source=read(R/'EXTRACTION_SOURCE_CPU_ACTUAL.json');geo=read(R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json')
    cpu=read(R/'REPLAY_V2_REWARD_RUNTIME_AND_ACTUAL_SDK_COMPUTE_CPU_V3_ACTUAL.json');assert cpu['passed']
    z=np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False);k=np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False)
    old=load(T/'H1_STEP270_REWARD_PATH_V1_20261022/h1_step270_path_reward_v1.py','old_reward_counterfactual')
    new=load(D/'candidate_reward_V3/h1_step270_path_reward_v1.py','new_reward_counterfactual');torch.set_num_threads(2)
    rows=[]
    for eid in (10042,2887,13576):
        e=int(np.where(z['env_ids']==eid)[0][0]);root=torch.from_numpy(z['root13'][:,e]);quat=root[:,3:7];x,y,zz,w=quat.unbind(-1)
        roll=torch.atan2(2*(w*x+y*zz),1-2*(x*x+y*y));pitch=torch.asin((2*(w*y-zz*x)).clamp(-1,1))
        req=torch.from_numpy(z['public_request'][:,e]).bool();yes=torch.ones_like(req);no=~yes
        # Every selected row has a recorded takeoff counter and no landing/reset:
        # the original attempt/!landed truth follows, without reading another PT.
        assert (z['takeoff_count'][:,e]>0).all() and not z['landing_count'][:,e].any() and not z['done'][:,e].any()
        kwargs=dict(request=req,attempt=yes,landed=no,vx=root[:,7],vy=root[:,8],roll=roll,pitch=pitch)
        baseline=old.requested_forward_rate(**kwargs)*.03
        actual=torch.from_numpy(z['reward_term_contribution'][:,e,source['reward_terms'].index('h1_step270_requested_forward')])
        assert torch.allclose(baseline,actual,atol=1e-6,rtol=1e-5)
        candidate=new.requested_forward_rate(**kwargs,airborne=no,wheel_bottom=torch.from_numpy(k['wheel_min'][:,e,:,2]).float(),wheel_front=torch.from_numpy(k['wheel_max'][:,e,:,0]).float(),origin_x=torch.zeros(48))*.03
        case=next(row for row in geo['case_summaries'] if row['env_id']==eid)
        front=k['wheel_max'][:,e,:,0].min(-1);height=k['wheel_min'][:,e,:,2].min(-1);closest=int(front.argmax())
        rows.append(dict(case=case,closest_row=closest,closest_wheel_bottom_m=float(height[closest]),closest_actual_world_vx=float(root[closest,7]),old_actual_requested_forward_control_sum=float(actual.sum()),counterfactual_new_requested_forward_same_recorded_states_sum=float(candidate.sum()),reverse_requested_frames=int((req&(root[:,7]<0)).sum()),counterfactual_keeps_postrequest_airborne_false_because_phase_air_ticks_not_recorded=True,not_new_policy_rollout_or_reward_result=True))
    result=dict(epoch=time.time(),source_scope='Closed31 stochastic PPO prefixes117/118; 48 measured control frames / .48s, all20k descriptive root statistics plus selected continuous examples. Not frozen FINAL rollout, whole-window event counts or physical-callback replay.',source_producer_identity=source['sources'],full_source_recorded_request_envframes=source['requested_rows'],all_recorded_request_world_vx_quantiles=source['requested_world_vx_m_s_quantiles'],recorded_event_counter_positive_increments=source['recorded_event_counter_positive_increments'],selected_cases=rows,visual_geometry_scope=geo['scope'],joint_order_derived_not_new_PhysX_readback=True,observed_failure='Selected high-lift case is still329mm from the edge at248mm wheel-bottom peak; near-edge case reaches42mm gap only after wheel bottoms drop to4mm. Other selected near-edge traces reverse. These show spatial/timing misalignment and insufficient clearance in these snippets; not a unique global cause.',source_confirmed_reward_issue='Original SCUT positive push-vz term pays upward supported motion throughout request regardless of front-to-edge position or actual forward velocity. V1 requested-forward clamps reverse to0 and pays only during the short request; its near-edge clearance potential begins at front x=.10 and does not reward carrying raised wheels at a sustained positive vx.',repair=dict(recipe='step270_forward_clearance_replay_v2',signed_measured_forward=True,carry_bonus='Actual lower wheel bottom /270mm squared times trailing front proximity and signed actual vx; both wheels must be high, stationary vertical motion earns no forward rate.',takeoff='Original push-vz value multiplied by smooth measured trailing-front gate [-.05,.15]m and positive actual vx/.8; no actuation or phase/command generation.',flight_continuation='Forward learning reward may continue only while existing actual air_ticks>0 after public request, while attempt and !landed remain true.',unchanged='Signed bounded potential and strict edge6/landing8/stable16, runtime, 270mm goal, actual contact/footprint, .5s stability, physics, command publisher, actor inputs, six STD, all17Adam, PPO, save and accounting.'),candidate_CPU=cpu,candidate_not_installed_or_GO=True,no_training_signal_or_midwindow_model_load=True,no_additional_original_raw_read_or_full_raw_hash=True,limits='Counterfactual scalar scores on saved states are not evidence that a newly trained policy will jump, clear or land. New installed CPU and actual PPO must be checked in a fresh root at a complete saved/settled boundary.')
    put('RECORDED_STEP_REPLAY_V2_DIAGNOSIS_AND_REPAIR_SCOPE_ACTUAL.json',result)
    print(json.dumps(dict(recorded_cases_and_original_rate_reproduction_passed=True,case_ids=[r['case']['env_id'] for r in rows],candidate_SHA=cpu['reward_module_SHA'],not_skill_success=True)))
except BaseException:
    put('REPLAY_DIAGNOSIS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
