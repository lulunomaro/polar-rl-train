"""Read saved data and exact source on CPU; never import Isaac or initialize CUDA."""
from pathlib import Path
from types import SimpleNamespace
import ast, hashlib, importlib.util, json, math, time, traceback
import numpy as np
import torch

D = Path(__file__).resolve().parent
W = D.parents[1]
C = W / 'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/isaac/mod4'
B = W / 'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/cases/clk2500-closure-episode-d3-153-e1-wave50-route-lifecycle-repair-terrain-flat'
DEC = W / 'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/reports/SCOPE_DECISION_ACTUAL.json'
RUN = W / 'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'

def index(p):
    return dict(path=str(p), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def dump(name, x):
    p=D/name
    assert not p.exists(), 'Independent report is immutable'
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
    return p

def environment(c,v,g,w):
    data=SimpleNamespace(root_lin_vel_b=v,projected_gravity_b=g,root_ang_vel_b=w)
    return SimpleNamespace(scene={'robot':SimpleNamespace(data=data)},
                           command_manager=SimpleNamespace(get_command=lambda _:c))

def inverse_rotate_xyzw(q,v):
    # Independent cross-product expression; no installed SDK import.
    xyz=q[...,:3]
    return v-2*q[...,3,None]*np.cross(xyz,v)+2*np.cross(xyz,np.cross(xyz,v))

def main():
    inputs=[C/'mod4_task.py',C/'scut_flat_rescue.py',C/'wave50_direction_runtime.py',
            C/'world_drift_reward.py',B/'probe.json',B/'route_raw.npz',DEC,RUN/'run_manifest.json']
    actual=[index(x) for x in inputs]
    assert actual[5]['sha256']=='7e54ffd4392565e6ce5d55617f4f7ea96091861807d4b9d63ffbe3ad3f623375'
    assert not torch.cuda.is_initialized()
    spec=importlib.util.spec_from_file_location('isolated_cpu_scut',C/'scut_flat_rescue.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    # Exact production functions, simultaneous velocity and command sign flip.
    c=torch.tensor([[.3,0.,0.],[-.3,0.,0.],[.3,0.,.2]],dtype=torch.float64)
    v=torch.tensor([[.2,.01,0.],[-.1,.03,0.],[.29,0.,0.]],dtype=torch.float64)
    g=torch.tensor([[.1,.04,-math.sqrt(.9884)],[-.2,.02,-math.sqrt(.9596)],[0.,0.,-1.]],dtype=torch.float64)
    w=torch.tensor([[0.,0.,.03],[0.,0.,-.05],[0.,0.,.19]],dtype=torch.float64)
    c2=c.clone();c2[:,[0,2]]*=-1
    v2=v.clone();v2[:,0]*=-1
    w2=w.clone();w2[:,2]*=-1
    e1=environment(c,v,g,w);e2=environment(c2,v2,g,w2)
    symmetry={}
    for name,kw in [('linear_exp',{'std':.25}),('linear_exp',{'std':.01}),
                    ('linear_square',{}),('linear_gap',{}),('yaw_exp',{}),
                    ('orientation',{'mode':'pitch'}),('orientation',{'mode':'pitch_velocity'}),
                    ('orientation',{'mode':'roll_velocity'})]:
        a=getattr(m,name)(e1,**kw);b=getattr(m,name)(e2,**kw)
        key=name+json.dumps(kw,sort_keys=True)
        symmetry[key]=dict(max_abs_difference=float((a-b).abs().max()),
                           exact=torch.equal(a,b),original=a.tolist(),sign_flipped=b.tolist())
        assert torch.equal(a,b), key
    # Wheels use default_offset=False, offset=0, common scale=10 from source contract.
    task=(C/'mod4_task.py').read_text(encoding='utf-8')
    assert 'use_default_offset=False, offset=0.0, preserve_order=True' in task
    assert 'root_lin_vel_b[:,0]*cos_pitch' in (C/'scut_flat_rescue.py').read_text(encoding='utf-8')
    manifest=json.loads((RUN/'run_manifest.json').read_bytes())
    knobs={k:v for k,v in manifest['env'].items() if any(s in k for s in ['SCUT','HEIGHT_GATE','WORLD_DRIFT','SPIN_ROLLING','W_HEIGHT'])}
    p=json.loads((B/'probe.json').read_bytes())
    dec=json.loads(DEC.read_bytes())
    rows=dec['full_fourcase_actual_review']['terrain']['full_route_rows']
    with np.load(B/'route_raw.npz',allow_pickle=False) as z:
        root=z['root'].astype(np.float64);before=z['before_root'].astype(np.float64)
        episode=z['episode'];command=z['command'].astype(np.float64);action=z['action'].astype(np.float64)
        q=root[:,:,3:7]; velb=inverse_rotate_xyzw(q,root[:,:,7:10]);angb=inverse_rotate_xyzw(q,root[:,:,10:13])
        grav=inverse_rotate_xyzw(q,np.broadcast_to(np.array([0.,0.,-1.]),root[:,:,:3].shape))
        pitch=np.arcsin(np.clip(2*(q[:,:,3]*q[:,:,1]-q[:,:,2]*q[:,:,0]),-1,1))
        yaw=np.arctan2(2*(q[:,:,3]*q[:,:,2]+q[:,:,0]*q[:,:,1]),1-2*(q[:,:,1]**2+q[:,:,2]**2))
        err=command[:,:,0]-velb[:,:,0]*np.sqrt(np.clip(1-grav[:,:,0]**2,0,1))
        source_linear=np.exp(-err**2/.25)+.2*np.exp(-err**2/.01)-(err**2>.5)-(0.25*err)**2
        worlderr=command[:,:,0]-root[:,:,7]
        world_linear=np.exp(-worlderr**2/.25)+.2*np.exp(-worlderr**2/.01)-(worlderr**2>.5)-(0.25*worlderr)**2
        # Above are just the four ungated scalar linear terms; not the total step reward.
        # They are recomputed independently, no actor action changed and no PPO replay.
        summaries=[];per_env=[]
        for gname in ['forward','reverse']:
            members=[x for x in rows if x['group']==gname]
            for outcome in ['all','completed','incomplete']:
                subset=[x for x in members if outcome=='all' or bool(x['complete_episodes'])==(outcome=='completed')]
                masks=[(episode[:,x['env']]==0) for x in subset]
                vals=lambda a:np.concatenate([a[ms,x['env']] for x,ms in zip(subset,masks)])
                y=vals(yaw);pit=vals(pitch);ac=vals(action);e=vals(err)
                summaries.append(dict(group=gname,outcome=outcome,environments=len(subset),
                    initial_episode_only=True,controls=int(len(y)),
                    mean_abs_pitch_deg=float(np.abs(pit).mean()*180/np.pi),
                    pitch_deg_p05_p50_p95=np.percentile(pit*180/np.pi,[5,50,95]).tolist(),
                    mean_abs_yaw_deg=float(np.abs(y).mean()*180/np.pi),
                    mean_abs_BODY_horizontal_velocity_error_m_s=float(np.abs(e).mean()),
                    mean_BODY_horizontal_tracking_4terms=float(vals(source_linear).mean()),
                    mean_world_X_tracking_4terms_counterfactual_only=float(vals(world_linear).mean()),
                    mean_wheel_requested_action=ac[:,4:6].mean(axis=0).tolist(),
                    mean_abs_wheel_requested_action=np.abs(ac[:,4:6]).mean(axis=0).tolist(),
                    mean_abs_leg_requested_action=np.abs(ac[:,:4]).mean(axis=0).tolist()))
            for row in members:
                e=row['env'];mask=episode[:,e]==0;n=int(mask.sum())
                per_env.append(dict(env=e,group=gname,complete=bool(row['complete_episodes']),
                    initial_episode_controls=n,max_abs_yaw_deg=float(np.abs(yaw[mask,e]).max()*180/np.pi),
                    max_abs_pitch_deg=float(np.abs(pitch[mask,e]).max()*180/np.pi),
                    mean_abs_pitch_deg=float(np.abs(pitch[mask,e]).mean()*180/np.pi),
                    source_BODY_horizontal_4terms_mean=float(source_linear[mask,e].mean()),
                    world_X_4terms_counterfactual_mean=float(world_linear[mask,e].mean()),
                    mean_BODY_vx_m_s=float(velb[mask,e,0].mean()),
                    mean_world_X_vx_m_s=float(root[mask,e,7].mean()),
                    yaw_rate_abs_mean_rad_s=float(np.abs(angb[mask,e,2]).mean()),
                    final_initial_episode_rootXY=root[np.flatnonzero(mask)[-1],e,:2].tolist(),
                    valid_first_episode_after_reset_not_used=True))
        assert not torch.cuda.is_initialized()
    report=dict(epoch=time.time(),passed=True,stage='CPU source symmetry and saved153 factor diagnosis',
       inputs=actual,source_environment_knobs=knobs,sign_symmetry_fixture=symmetry,
       source_has_no_explicit_forward_backward_linear_reward_penalty=True,
       observation_policy35_includes_command_and_gravity_but_no_absolute_heading=True,
       wheel_action_processing_same_scale_zero_offset_sign_symmetric=True,
       raw_group_metrics=summaries,raw_per_environment=per_env,
       candidate_hypothesis='Body-frame velocity and yaw-rate reward can retain velocity credit after route heading drift; policy-level heading and pitch response is direction dependent in saved data.',
       no_claim_that_reward_asymmetry_bug_or_robot_mechanics_is_unique_cause=True,
       no_training_or_GPU_execution=True,
       reward_values_are_four_linear_scalar_terms_not_total_reward_or_saved_manager_receipt=True,
       counterfactual_reward_does_not_change_frozen_policy_actions=True,
       original_scope_not_relabelled_qualified=True,
       preparatory_reader_errors_retained=[
          'Get-Content scut_rescue_math.py missing guessed filename; actual import is scut_flat_rescue.',
          'rg literal wildcard scut* invalid Windows path; no production modification.',
          'rg scut_rescue_reward.py missing guessed filename; source import then inspected.'])
    path=dump('POLICY_REWARD_CPU_ACTUAL_REVIEW.json',report)
    factor=dict(epoch=time.time(),status='prepared_only_no_GPU',
       factor='linear_velocity_reward_reference_frame',baseline='original BODY_vx*cos(pitch) scalar forward error',
       isolated_variant='replace only four linear forward_error references with vx projected on episode-initial heading; same saved source / DR / pose / commands / plant / seed / full evaluation',
       frozen_GPU_reward_only_variant_expected_no_behavior_change=True,
       learning_needed_for_causal_behavior_test=True,
       do_not_add_live_heading_command_correction_or_teacher_or_actor_privileged_inputs=True,
       necessary_before_learning='Root decision and strict new reward-axis scope admission, original component refs retained; do not mutate running trainer.',
       failure_observable='Expected lower reward after sideways drift; full route contact/position remains original.',
       current_minimal_CPU_test='Exact longitudinal sign symmetry fixture using production scalar reward functions; passed all numerical comparisons.',
       optional_frozen_policy_factor='Paired same complete initial DR/pose and opposite command sign to isolate learned policy response; this is a diagnostic pair, not an assumed physical mirror equivalence.')
    fp=dump('POLICY_REWARD_FACTOR_CASE_PREPARED.json',factor)
    print(json.dumps(dict(report=str(path),factor=str(fp),passed=True,summaries=summaries),ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except BaseException:
        dump('ORIGINAL_CPU_READER_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),not_GPU=True))
        raise
