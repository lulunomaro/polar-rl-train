"""Inspect the exact planned reference and cost without reading any checkpoint.

This is new task-label diagnosis, not archive-only raw decoding or skill testing.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast,hashlib,importlib.util,io,json,sys,time,traceback,xml.etree.ElementTree as ET
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent
D=T/'REFERENCE_LABEL_FEASIBILITY_DIAGNOSIS_V314_20261102'
assert not D.exists();D.mkdir();R=D/'reports';R.mkdir()
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
put('CPU314_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose='Exact plannedreference phase/actuator-range/label/cost consistency diagnosis while remote resources busy',checkpoint_reads=0,SDK=0,physics_steps=0,optimizer_steps=0,network=0,new_GO=False))
try:
    import numpy as np,torch
    torch.set_num_threads(4)
    source=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/source'
    reference_module=module('reference314_original305',source/'tracking_reference305.py')
    task=json.loads((T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102/TASK311_FROZEN.json').read_bytes())
    reference_path=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102/reference305.npz'
    raw=reference_path.read_bytes();assert len(raw)==task['reference']['bytes']and hashlib.sha256(raw).hexdigest()==task['reference']['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as archive:
        names=archive['joint_names'].tolist();times=archive['times'].copy();stored=archive['state78'].copy()
    producer=Path(task['reference']['producer']['path']);producer_raw=producer.read_bytes()
    assert len(producer_raw)==task['reference']['producer']['bytes']and hashlib.sha256(producer_raw).hexdigest()==task['reference']['producer']['SHA']
    rows=json.loads(producer_raw);selected=rows[1::2]
    assert len(rows)==500 and len(selected)==len(times)==250
    assert np.allclose(times,np.array([row['time']for row in selected]))
    # Exact sourcebody hip origin is the original label geometry, no simulation.
    xml=Path('F:/RMPOLAR-RL/traditional_control_20261101/model/mod4_400N.xml');root=ET.fromstring(xml.read_bytes())
    bodies={b.get('name'):b for b in root.find('worldbody').iter('body')}
    hips=torch.tensor([[float(x)for x in bodies[s+'_thigh'].get('pos').split()]for s in('left','right')],dtype=torch.float32)
    reference=reference_module.Reference305(reference_path,task['reference'],names,'cpu',hips)
    phase=torch.arange(250);envs=torch.zeros(250,dtype=torch.long);target=torch.tensor([[.8,0.,.27,0.]])
    label=reference.labels(phase,envs,target);v=label['state'];leg_names=('left_crank','left_hip','right_crank','right_hip');wheel_names=('left_wheel_spin','right_wheel_spin')
    legs=[names.index(n)for n in leg_names];wheels=[names.index(n)for n in wheel_names]
    position=v[:,:3];rotation=v[:,3:12].reshape(-1,3,3)
    aux=torch.zeros(250,151);aux[:,54:56]=label['L'];aux[:,56:58]=label['theta']
    # Shape-correct contactfixture is only a cost-channel unit fixture. It is not
    # a recorded contact or a claim about the teacher's individual wheel forces.
    fixture=torch.zeros(250,31,3)
    support=label['support']
    fixture[:,0:2,2]=support*.25
    aux[:,58:]=torch.einsum('bij,bnj->bni',rotation.transpose(1,2),fixture).flatten(1)
    state=(position,rotation,v[:,12:15],v[:,15:18],v[:,18:48],v[:,48:78],aux)
    cost,terms=reference_module.tracking_cost305(state,label,legs,[0,1],torch.zeros(250,6),torch.zeros(250,6))
    pose_terms=['position','rotation','velocity','omega','joint_pose','joint_velocity','wheel_leg_length','wheel_leg_angle']
    assert all(float(terms[name].abs().max())==0 for name in pose_terms)
    # Translation/yaw covariance of reference goals, evaluated on its own state.
    goals=reference.goals(state,phase,envs,target);assert goals.shape==(250,59)and torch.isfinite(goals).all()
    hold=reference.labels(torch.tensor([249,250,400]),torch.zeros(3,dtype=torch.long),target)
    assert torch.equal(hold['state'][0],hold['state'][1])and torch.equal(hold['state'][0],hold['state'][2])
    motor=torch.cat((v[:,18:48][:,legs]/.5,v[:,48:78][:,wheels]/10.),-1)
    source_joints={j.get('name'):j for j in root.find('worldbody').iter('joint')if j.get('name')}
    limits=[]
    for i,n in enumerate(names):
        j=source_joints[n];bounds=j.get('range')
        if bounds:
            lo,hi=map(float,bounds.split());q=v[:,18+i]
            limits.append(dict(joint=n,limits=[lo,hi],reference_min=float(q.min()),reference_max=float(q.max()),samples_below=int((q<lo-1e-4).sum()),samples_above=int((q>hi+1e-4).sum())))
    gaps=np.diff(times)
    velocity_fd=(v[1:,:3]-v[:-1,:3])/.02
    fd_error=(velocity_fd-(v[1:,12:15]+v[:-1,12:15])*.5).square().mean(0).sqrt()
    durations=[]
    for stop in(.1,.2,.4,.64,1.,2.,5.):
        count=int((times<=stop+1e-8).sum());subset=motor[:max(1,count)]
        durations.append(dict(reference_through_s=stop,samples=count,planned_normalized_target_abs_max=subset.abs().max(0).values.tolist(),root_z_range=[float(v[:max(1,count),2].min()),float(v[:max(1,count),2].max())]))
    put('CPU314_EXACT_REFERENCE_LABEL_DIAGNOSIS.json',dict(epoch=time.time(),passed=True,reference_SHA=task['reference']['SHA'],producer_SHA=task['reference']['producer']['SHA'],samples=250,source_interval_s=[float(gaps.min()),float(gaps.max())],endpoint_first_time=float(times[0]),endpoint_last_time=float(times[-1]),first= dict(position=v[0,:3].tolist(),linear_v=v[0,12:15].tolist(),omega=v[0,15:18].tolist(),leg_q=v[0,18:48][legs].tolist(),leg_dq=v[0,48:78][legs].tolist()),last=dict(position=v[-1,:3].tolist(),linear_v=v[-1,12:15].tolist(),omega=v[-1,15:18].tolist(),leg_q=v[-1,18:48][legs].tolist(),leg_dq=v[-1,48:78][legs].tolist()),planned_normalized_targets=dict(order=list(leg_names+wheel_names),legscale=.5,wheelscale=10.,absmax=motor.abs().max(0).values.tolist(),outside_clip6=(motor.abs()>6.).sum(0).tolist(),time_summaries=durations,interpretation='planned joint-position/wheel-speed targets only, not teacher torque or closedloop state-query actions'),source_joint_limit_comparison=limits,pose_channel_self_cost_zero=True,goal59_finite=True,hold_after249='same fullstate includes nonzero saved terminalvelocities; source condition, not measured PhysX or established failure cause',held_terminal_speed=float(v[-1,12:15].norm()),held_terminal_omega=float(v[-1,15:18].norm()),held_terminal_leg_dq_absmax=float(v[-1,48:78][legs].abs().max()),root_finite_difference_endpointvelocity_RMSE_xyz_mps=fd_error.tolist(),support_fixture_only_cost_range=[float(cost.min()),float(cost.max())],geometry='Exact source MJCF hip anchors; no physical asset or solver changes',model_reads=0,SDK=0,physics_steps=0,optimizer_steps=0,network=0,source_frozen_modified=False,causality='This is label-only diagnosis. Initialphysicalstate/WMgradient failure causality and referencePDtrackability require original311 actual probe; no graduation/repair effectiveness asserted.'))
    print(json.dumps(dict(passed=True,model_reads=0,planned_target_absmax=motor.abs().max(0).values.tolist(),outside6=(motor.abs()>6).sum(0).tolist(),held_speed=float(v[-1,12:15].norm()),held_leg_dq_absmax=float(v[-1,48:78][legs].abs().max()))),flush=True)
except BaseException:
    put('CPU314_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True,checkpoint_reads=0));raise
