"""One local full-state and independent80 review after the sole receiver ends."""
from pathlib import Path
import argparse,hashlib,json,re,time,traceback
import numpy as np
import torch

p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);a=p.parse_args()
A=a.root.resolve();R=A/'reports'
read=lambda path:json.loads(Path(path).read_bytes())
assert read(R/'POSTROUND_COMPLETED.json')['complete']
assert not(R/'NEWTON_CLOSED_LEARNER_AND_ALL80.json').exists()
returned=R/('LOCAL_COMPLETE_RETURNED.json'if(R/'LOCAL_COMPLETE_RETURNED.json').exists()else'POSTROUND_FULL_RETURNED.json')
f=read(returned)['files'];final=f['production/FINAL.json'];ck=final['checkpoint']
assert f['OWNER_EXIT.json']['all_own_waited']and not f['OWNER_EXIT.json']['error']
assert f['OWNER_EXIT.json']['original_leases_released']
model=A/'production'/Path(ck['path']).name
with model.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==ck['SHA']
assert model.stat().st_size==ck['bytes']
once=R/'NEWTON_FINAL_LEARNER_DIAGNOSIS_ONCE.json'
with once.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),checkpoint=ck,model_decodes=1,SSH=0,physics=0),stream)
report=dict(epoch=time.time(),checkpoint=ck,production_PT_decodes=1,SSH=0,new_physics=0,passed=False)
try:
    saved=torch.load(model,map_location='cpu',weights_only=False)
    assert saved['format']=='MOD4V2_FUDAN_NEWTON_FULL_V1'and saved['iter']==ck['iteration']
    assert saved['num_envs']==20000 and saved['reward_family']=='FUDAN_JUMP'
    def finite(value):
        if torch.is_tensor(value):return bool(torch.isfinite(value).all())
        if isinstance(value,dict):return all(finite(x)for x in value.values())
        if isinstance(value,(tuple,list)):return all(finite(x)for x in value)
        return True
    for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert finite(saved[name]),name
    steps=[int(s['step'])for s in saved['optimizer_state_dict']['state'].values()]
    assert len(steps)==17 and min(steps)==max(steps)==saved['iter']*20
    assert len(saved['components'])==7
    for key in ('physical_rng','physical_episode','motor_episode_gain','cpu_rng','cuda_rng','python_rng','numpy_rng','command_fields','source_reward_state','source_reward_dicts','source_global_counters'):assert key in saved
    logs={name:f[name]for name in ('WORKER.log','EVAL.log','OWNER.log')}
    errors={name:[]for name in logs};timing_values={key:[]for key in ('Collection time','Learning time','Steps per second')}
    warning_count=0
    for name,row in logs.items():
        lines=Path(row['local_path']).open('r',encoding='utf8')if row.get('text_external')else row['text'].splitlines()
        try:
            for line in lines:
                if any(t in line.lower()for t in ('traceback (most recent call last)','outofmemoryerror','cooking failure','patch buffer overflow')):errors[name].append(line.rstrip())
                if name=='WORKER.log':
                    warning_count+=line.count('linesearch iterations limit reached')
                    for label in timing_values:
                        m=re.search(re.escape(label)+r':\s*([0-9.]+)',line)
                        if m:timing_values[label].append(float(m[1]))
        finally:
            if hasattr(lines,'close'):lines.close()
    timings={}
    for label in ('Collection time','Learning time','Steps per second'):
        values=timing_values[label]
        timings[label]=dict(count=len(values),mean=float(np.mean(values))if values else None,last=values[-1]if values else None)
    result=f['evaluation/RESULT.json'];rows=f['evaluation/ALL80.json']['first_episodes'];curves=f['evaluation/CONTROL_CURVES.json']['curves']
    assert len(rows)==80 and result['source_SHA']==ck['SHA']and result['optimizer_operations']==0
    with np.load(A/'evaluation/actual400hz.npz')as tick:
        active=tick['active']
        numeric=dict(callbacks=len(active),active_samples=int(active.sum()),
            ground_flight_envs=int(((tick['flight_id']>0)&active).any(0).sum()),
            upward_flight_envs=int((tick['upward_flight']&active).any(0).sum()),
            wholeclear_envs=int((tick['wholeclear']&active).any(0).sum()),
            landed_top_envs=int((tick['landed_top']&active).any(0).sum()),
            success_envs=int((tick['strict']&active).any(0).sum()),
            top_force_max=float(tick['top_force'][active].max()),
            root_x=[float(tick['root_pos'][...,0][active].min()),float(tick['root_pos'][...,0][active].max())],
            root_vz=[float(tick['root_velocity'][...,2][active].min()),float(tick['root_velocity'][...,2][active].max())])
    numeric['controls_range']=[min(r['controls']for r in rows),max(r['controls']for r in rows)]
    numeric['done_counts']={k:sum(bool(r.get(k,False))for r in rows)for k in ('terminated','time_out','numerical_reset')}
    numeric['closure_error_max']=max(r['closure_error']for r in rows)
    numeric['mimic_error_max']=max(r['mimic_error']for r in rows)
    numeric['leg_length']={k:float(fn(np.asarray([r['leg_length']for r in rows])))for k,fn in [('min',np.min),('max',np.max),('mean',np.mean)]}
    arr=lambda key:np.asarray([r[key]for r in curves]);active=arr('active')
    numeric['commands']=dict(vx=np.unique(arr('command')[...,0][active]).tolist(),height=np.unique(arr('command_height')[active]).tolist())
    target=arr('joint_target');delta=target[...,[0,2]]-target[...,[1,3]]
    numeric['mechanical_delta']=[float(delta[active].min()),float(delta[active].max())]
    numeric['motor_tracking_MAE']=float(np.abs(arr('motor_position')[...,:4]-target)[active].mean())
    numeric['reward16_mean']={k:float(np.mean([r['weighted_reward_active_mean'][k]for r in curves]))for k in curves[0]['weighted_reward_active_mean']}
    report.update(passed=True,iteration=saved['iter'],PPO_updates=final['PPO_updates'],
        samples=final['PPO_updates']*480000,Adam_entries=17,Adam_steps=min(steps),
        learning_rate=saved['learning_rate'],STD=saved['actor_state_dict']['distribution.std_param'].tolist(),
        complete_7components_DR_RNG_queue_counter=True,actor_critic_Adam_finite=True,
        counters=saved['source_global_counters'],timings=timings,full_log_errors=errors,
        logmeta={k:{x:v for x,v in row.items()if x!='text'}for k,row in logs.items()},
        linesearch_warning_count=warning_count,
        training_numerical_resets=final.get('numerical_resets'),all80=numeric,
        native_pose_visual_review_pending=True,old_PhysX_conclusions_not_reused=True)
except BaseException:report['error']=traceback.format_exc()
with(R/'NEWTON_CLOSED_LEARNER_AND_ALL80.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))
if not report['passed']:raise SystemExit(1)
