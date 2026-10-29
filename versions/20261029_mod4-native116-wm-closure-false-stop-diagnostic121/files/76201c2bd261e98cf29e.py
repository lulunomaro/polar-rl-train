"""Necessary actual-action WM closure calibration. No I/O or checkpoint loads."""
from __future__ import annotations
import torch


def require(value, message):
    if not bool(value):
        raise ValueError(message)


def quat_apply_xyzw(q, v):
    twice = 2 * torch.cross(q[..., :3], v, dim=-1)
    return v + q[..., 3:4]*twice + torch.cross(q[..., :3], twice, dim=-1)


def anchor_errors(position, rotation, indices0, indices1, anchors0, anchors1):
    a = position[..., indices0, :] + (rotation[..., indices0, :, :] @ anchors0[..., None]).squeeze(-1)
    b = position[..., indices1, :] + (rotation[..., indices1, :, :] @ anchors1[..., None]).squeeze(-1)
    return torch.linalg.vector_norm(a-b, dim=-1)


def closure_stop(errors, public_age, threshold=.002, grace=10):
    return (errors.amax(-1) > threshold) & (public_age >= grace)


def valid_starts(frames, done, episode, horizon):
    starts=[]
    for i in range(len(frames)-horizon+1):
        if bool(done[i:i+horizon-1].any()):
            continue
        if not torch.equal(frames[i:i+horizon], frames[i]+torch.arange(horizon)):
            continue
        if not bool((episode[i:i+horizon] == episode[i]).all()):
            continue
        starts.append(i)
    return starts


def decode_records(rows, count, body_count=31):
    require(isinstance(rows,list) and len(rows)==count, 'exact actual control count')
    for i,r in enumerate(rows):
        require(r['control']==i+1 and r['age_for_action']==[i], 'complete control/actual action age')
        require(r['physics_dt_s']==.0025 and r['control_dt_s']==.01, 'original400Hz/100Hz typed clock')
        phase=r['actual_phase_record']
        request=200<=i<2000
        require(phase['control']==i+1 and phase['age_for_action']==i, 'phase/control binding')
        require(phase['public_request_for_action']==request, 'public request')
        require(r['task_relative_features7_for_action'][5]==float(request), 'relative request feature')
        require(r['actor_obs86_for_action'][-2]==float(request), 'actor request feature')
        require(type(r['actual_original_done']) is bool, 'typed actual done')
    def tensor_rows(key, width):
        out=torch.tensor([r[key] for r in rows], dtype=torch.float32)
        require(out.shape==(count,width) and torch.isfinite(out).all(), key+' finite width')
        return out
    terminal=[r['terminal_pre_reset']['state'] for r in rows]
    done=torch.tensor([r['actual_original_done'] for r in rows],dtype=torch.bool)
    require(done.tolist()==[False]*(count-1)+[True], 'one genuine final termination/no reset crossing')
    frames=torch.tensor([r['packed_frame_for_action'] for r in rows],dtype=torch.long)
    ages=torch.arange(count,dtype=torch.long)
    require(torch.equal(frames,ages), 'actual N1 private4096 frame/public age binding')
    s=tensor_rows('packed127_for_action',127)
    target=tensor_rows('terminal_packed127_same_point',127)
    xi=tensor_rows('xi31_for_action',31)
    require(torch.equal(xi,xi[:1].expand_as(xi)), 'actual episode-fixed static DR context')
    action=torch.tensor([r['executed6'] for r in terminal],dtype=torch.float32)
    require(action.shape==(count,6) and torch.isfinite(action).all(), 'actual manager executed6, not PD processed target')
    positions=torch.tensor([r['body_position31_world'] for r in terminal],dtype=torch.float32)
    quaternions=torch.tensor([r['body_quaternion31_sdk_xyzw'] for r in terminal],dtype=torch.float32)
    require(positions.shape==(count,body_count,3), 'actual31body position shape')
    require(quaternions.shape==(count,body_count,4), 'recorded SDK xyzw body rotation shape')
    require(torch.isfinite(positions).all() and torch.isfinite(quaternions).all(), 'finite saved body poses')
    episode=torch.tensor([r['episode'] for r in terminal],dtype=torch.long)
    require(episode.unique().numel()==1, 'no actual episode reset within these431 controls')
    cached_closure=torch.tensor([bool(r['terminal_pre_reset']['termination_terms']['values']['closure']) for r in rows])
    require(torch.equal(cached_closure,done), 'actual118 final closure-only terminal')
    origin=tensor_rows('env_origin3_world',3)
    require(torch.equal(origin,origin[:1].expand_as(origin)), 'same fixed scene origin')
    physical_processed=torch.tensor([r['physical_applied_processed6'] for r in terminal],dtype=torch.float32)
    require(torch.equal(target[:,-6:],physical_processed), 'terminal auxiliary contains actual last PD/queue processed6')
    q=torch.tensor([r['q30'] for r in terminal],dtype=torch.float32)
    require(torch.equal(target[:,13:43],q), 'actual thirty-joint state and terminal127 same point')
    return dict(s=s,t=target,a=action,xi=xi,frames=frames,ages=ages,done=done,
        episode=episode,position=positions,quaternion=quaternions,cached_closure=cached_closure,
        origin=origin,terminal=terminal,phases=[r['actual_phase_record'] for r in rows],
        saved_GPU_one_step_z=torch.tensor([r['frozen_WM_one_step']['predicted_root_z'] for r in rows]),
        continuity=(s[1:]-target[:-1]).abs().amax(0))


def window_phase(start, horizon):
    if start+horizon<=200:
        return 'standing_request_off'
    if start>=200:
        return 'request_on'
    return 'crosses_request_onset_separate'


def summarize(rows):
    if not rows:
        return dict(windows=0)
    return dict(windows=len(rows),
        predicted_any_closure_stop_windows=sum(r['predicted_any_closure_stop'] for r in rows),
        predicted_closure_on_cached_nonclosure_window_count=sum(r['any_predicted_stop_on_cached_nonclosure_step'] for r in rows),
        endpoint_predicted_stop_on_cached_nonclosure=sum(r['endpoint_predicted_stop_on_cached_nonclosure'] for r in rows),
        endpoint_cached_closure_missed=sum(r['endpoint_cached_closure_missed'] for r in rows),
        max_predicted_closure_m=max(x['predicted_max_closure_m'] for r in rows for x in r['steps']),
        mean_endpoint_q30_abs_error_rad=sum(r['endpoint_q30_MAE_rad'] for r in rows)/len(rows),
        endpoint_rootX_MAE_m=sum(abs(r['endpoint_rootX_error_m']) for r in rows)/len(rows),
        endpoint_worldVx_MAE_m_s=sum(abs(r['endpoint_worldVx_error_m_s']) for r in rows)/len(rows),
        all_windows_use_actual_action_at_every_offset=True,
        overlapping_windows_not_independent_trials=True)


def evaluate(wm, unpack, normalize, geometry, closure, data, horizon, deadline):
    starts=valid_starts(data['frames'],data['done'],data['episode'],horizon)
    result=[]
    with torch.inference_mode():
        for begin in range(0,len(starts),128):
            deadline()
            ids=torch.tensor(starts[begin:begin+128],dtype=torch.long)
            predicted=tuple(x.clone() for x in unpack(data['s'][ids]))
            sequences=[[] for _ in ids]
            for k in range(horizon):
                predicted=wm.step(predicted,data['a'][ids+k],normalize(data['xi'][ids+k]))
                require(all(torch.isfinite(x).all() for x in predicted), 'finite open-loop predicted state')
                g=geometry(predicted)
                errors=anchor_errors(g['body_position'],g['body_rotation'],*closure)
                age=data['ages'][ids]+k+1
                stopped=closure_stop(errors,age)
                for j,i in enumerate(ids.tolist()):
                    endpoint=i+k
                    sequences[j].append(dict(offset=k+1,actual_completed_control=endpoint+1,
                        predicted_anchor_errors6_m=errors[j].tolist(),
                        predicted_max_closure_m=float(errors[j].max()),
                        predicted_closure_stop=bool(stopped[j]),
                        actual_cached_closure=bool(data['cached_closure'][endpoint]),
                        predicted_stop_on_cached_nonclosure=bool(stopped[j] and not data['cached_closure'][endpoint])))
                deadline()
            truth=unpack(data['t'][ids+horizon-1])
            for j,i in enumerate(ids.tolist()):
                steps=sequences[j]
                known_input=i>0
                result.append(dict(start_control=i+1,end_control=i+horizon,horizon=horizon,
                    input_public_age=i,phase=window_phase(i,horizon),
                    input_phase_known=known_input,
                    input_supported=(bool(data['phases'][i-1]['both_supported']) if known_input else None),
                    contains_actual_contact_proven_low_air=any(data['phases'][x]['airborne_both_above5mm_and_unloaded'] for x in range(i,i+horizon)),
                    steps=steps,predicted_any_closure_stop=any(x['predicted_closure_stop'] for x in steps),
                    any_predicted_stop_on_cached_nonclosure_step=any(x['predicted_stop_on_cached_nonclosure'] for x in steps),
                    endpoint_predicted_stop_on_cached_nonclosure=steps[-1]['predicted_stop_on_cached_nonclosure'],
                    endpoint_cached_closure_missed=steps[-1]['actual_cached_closure'] and not steps[-1]['predicted_closure_stop'],
                    first_predicted_closure_stop_offset=next((x['offset'] for x in steps if x['predicted_closure_stop']),None),
                    endpoint_q30_MAE_rad=float((predicted[4][j]-truth[4][j]).abs().mean()),
                    endpoint_rootX_error_m=float(predicted[0][j,0]-truth[0][j,0]),
                    endpoint_worldVx_error_m_s=float(predicted[2][j,0]-truth[2][j,0]),
                    CPU_saved_GPU_rootZ_abs_error_if_one_step=(abs(float(predicted[0][j,2]-data['saved_GPU_one_step_z'][i])) if horizon==1 else None),
                    open_loop_after_first_actual_state=True,no_future_actual_state_injection=True,
                    actual_executed_action6_every_step=True,no_policy_action_resampling=True))
    return result
