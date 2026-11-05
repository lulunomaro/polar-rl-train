"""Offline review of one formally returned SuperMimic final, not PPO17Adam."""
from pathlib import Path
import argparse,hashlib,json,time,traceback
import numpy as np
import torch
N=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_bytes())


def finite(value):
    if torch.is_tensor(value):return bool(torch.isfinite(value).all())
    if isinstance(value,dict):return all(finite(x)for x in value.values())
    if isinstance(value,(tuple,list)):return all(finite(x)for x in value)
    return True


def checkpoint_metrics(value):
    assert value['format']=='MOD4V2_FUDAN_NEWTON_SUPERMIMIC_FULL_V1'
    assert value['reward_family']=='FUDAN_JUMP'and value['args']['horizon']==32
    extension=value['context_reward_extension'];counts=extension['counts']
    assert extension['full_resume']and extension['update_boundary_safe']
    assert counts['pi_bptt_optimizer_steps']>0
    models={name:value[name]for name in ('wm','pi','critic')}
    models['aux']=extension['aux']
    assert all(finite(model)for model in models.values())
    steps={}
    for name,field in [('wm','wm_optimizer_steps'),('pi','pi_optimizer_steps'),
                       ('v','critic_optimizer_steps'),('aux','aux_optimizer_steps')]:
        optimizer=value.get('opt_'+name,extension.get('opt_'+name))
        assert optimizer and optimizer['state']and finite(optimizer)
        values=[int(s['step'])for s in optimizer['state'].values()]
        assert min(values)==max(values)==counts[field],(name,values,counts[field])
        steps[name]=dict(entries=len(values),steps=min(values))
    replay=extension['replay'];T=replay['T'];size=replay['size'];ptr=replay['ptr']
    assert 0<size<=T and 0<=ptr<T
    data=replay['data']
    for field in ('sample_valid','stream_cut','s','s1','r','xi','xi1','term','trunc'):
        assert field in data
    assert all(t.shape[:2]==(T,replay['N'])for t in data.values())
    assert finite(data)
    used=(ptr-size+torch.arange(size))%T
    invalid=~data['sample_valid'][used]
    assert bool(data['stream_cut'][used][invalid].all())
    assert torch.equal(data['done'][used],data['term'][used]|data['trunc'][used])
    streams=extension['environment']['streams']
    assert len(streams['components'])==7
    for key in ('physical_rng','physical_episode','motor_episode_gain','command_fields',
                'source_global_counters','physics_ticks','numerical_reset_counts','constraint_reset_counts'):
        assert key in streams
    for key in ('python','torch_cpu','torch_cuda'):assert key in extension['rng']
    return dict(iteration=value['iteration'],sim_steps=value['sim_steps'],counts=counts,
        policy_residual_scale=value.get('policy_residual_scale',1.),
        four_Adam=steps,all_models_and_optimizers_finite=True,
        replay=dict(T=T,N=replay['N'],size=size,ptr=ptr,
            bytes=sum(t.numel()*t.element_size()for t in data.values()),
            valid_samples=int((~invalid).sum()),invalid_samples=int(invalid.sum()),
            invalid_stream_cuts_preserved=True,all_fields_finite=True),
        all7_components_DR_RNG_queues_counters=True,physical_restore_exact=False,
        source_PPO=value['source_PPO'],original_PPO_checkpoint_preserved=True,
        new_BPTT_optimizers_not_PPO17Adam=True,last_bptt=extension['last_bptt_receipt'],
        physics_ticks=streams['physics_ticks'],
        numerical_resets_cumulative=int(streams['numerical_reset_counts'].sum()),
        constraint_resets_cumulative=int(streams['constraint_reset_counts'].sum()))


def evaluation_metrics(directory,files,checkpoint_SHA):
    result=files['evaluation/RESULT.json'];rows=files['evaluation/ALL80.json']['first_episodes']
    curves=files['evaluation/CONTROL_CURVES.json']['curves']
    assert len(rows)==80 and all(row is not None for row in rows)
    assert result['source_SHA']==checkpoint_SHA and result['optimizer_operations']==0
    with np.load(directory/'actual400hz.npz')as tick:
        active=tick['active'].astype(bool)
        # Old protocols did not save the400Hz invalid flag. Exclude complete
        # first episodes with any numerical/constraint reset, and state scope.
        valid_env=np.asarray([not(r.get('numerical_reset',False)or r.get('constraint_reset',False))for r in rows])
        mask=active&valid_env[None,:]
        numeric=dict(callbacks=len(active),active_samples=int(active.sum()),
            reset_invalid_envs=np.flatnonzero(~valid_env).tolist(),
            validated_scope='Entire first episodes without numerical/constraint reset',
            per_tick_physical_valid_available='physical_transition_valid'in tick.files)
        for key in ('flight_id','upward_flight','wholeclear','landed_top','strict'):
            flag=tick[key]>0
            numeric[key]=dict(raw_envs=int((flag&active).any(0).sum()),
                no_reset_envs=int((flag&mask).any(0).sum()))
        numeric['top_force_peak']=float(tick['top_force'][active].max())
        numeric['root_x_range']=[float(tick['root_pos'][...,0][active].min()),float(tick['root_pos'][...,0][active].max())]
        numeric['root_vz_range']=[float(tick['root_velocity'][...,2][active].min()),float(tick['root_velocity'][...,2][active].max())]
    numeric['controls_range']=[min(r['controls']for r in rows),max(r['controls']for r in rows)]
    numeric['done_counts']={key:sum(bool(r.get(key,False))for r in rows)
        for key in ('terminated','time_out','numerical_reset','constraint_reset')}
    for key in ('closure_error','mimic_error'):
        numeric[key+'_max']=max(r[key]for r in rows)
    numeric['leg_length']={key:float(fn(np.asarray([r['leg_length']for r in rows])))
        for key,fn in [('min',np.min),('max',np.max),('mean',np.mean)]}
    arr=lambda key:np.asarray([r[key]for r in curves])
    active=arr('active');target=arr('joint_target');delta=target[...,[0,2]]-target[...,[1,3]]
    numeric['command_vx']=np.unique(arr('command')[...,0][active]).tolist()
    numeric['command_height']=np.unique(arr('command_height')[active]).tolist()
    numeric['mechanical_delta_range']=[float(delta[active].min()),float(delta[active].max())]
    numeric['motor_tracking_MAE']=float(np.abs(arr('motor_position')[...,:4]-target)[active].mean())
    numeric['reward16_mean']={key:float(np.mean([r['weighted_reward_active_mean'][key]for r in curves]))
        for key in curves[0]['weighted_reward_active_mean']}
    numeric['perbody_contact_peak']=arr('contact_force')[active].__abs__().max(axis=0).tolist()
    numeric['success_inferred_from_loss_or_reward_flight']=False
    return numeric


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path)
    parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:
        final=read(N/'supermimic_host_replay08/RESULT.json')['checkpoint']
        value=torch.load(final['path'],map_location='cpu',weights_only=False)
        diagnosis=checkpoint_metrics(value)
        local=N/'supermimic_cli04';evaluation=local/'evaluation80'
        files={'evaluation/'+name:read(evaluation/name)for name in ('RESULT.json','ALL80.json','CONTROL_CURVES.json')}
        numeric=evaluation_metrics(evaluation,files,files['evaluation/RESULT.json']['source_SHA'])
        report=dict(epoch=time.time(),passed=True,local_fixture_PT_reads=1,production_PT_reads=0,
            new_physics=0,SSH=0,checkpoint_schema_passed=True,all80_schema_passed=True,
            diagnosis=diagnosis,all80=numeric)
        output=N/'reports/SUPERMIMIC_CLOSED_READER_SELFTEST.json'
    else:
        A=args.root.resolve();R=A/'reports'
        assert read(R/'POSTROUND_COMPLETED.json')['complete']
        output=R/'SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json';assert not output.exists()
        f=read(R/'POSTROUND_FULL_RETURNED.json')['files']
        assert not f['OWNER_EXIT.json']['error']and f['OWNER_EXIT.json']['all_own_waited']
        assert f['OWNER_EXIT.json']['original_leases_released']
        ck=f['production/FINAL.json']['checkpoint'];path=A/'production'/Path(ck['path']).name
        with path.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==ck['SHA']
        assert path.stat().st_size==ck['bytes']
        with(R/'SUPERMIMIC_FINAL_LEARNER_DIAGNOSIS_ONCE.json').open('x',encoding='utf8')as stream:
            json.dump(dict(epoch=time.time(),checkpoint=ck,production_PT_reads=1,physics=0,SSH=0),stream)
        report=dict(epoch=time.time(),passed=False,production_PT_reads=1,new_physics=0,SSH=0,checkpoint=ck)
        try:
            value=torch.load(path,map_location='cpu',weights_only=False)
            diagnosis=checkpoint_metrics(value)
            if (A/'PLAN.json').exists():
                plan=read(A/'PLAN.json')
                assert diagnosis['policy_residual_scale']==plan.get('policy_residual_scale',1.)
            numeric=evaluation_metrics(A/'evaluation',f,ck['SHA'])
            errors={};logs={}
            for name in ('WORKER.log','EVAL.log','OWNER.log'):
                row=f[name];text=row['text'];raw=text.encode('utf8')
                assert row['complete']and len(raw)==row['bytes']
                assert hashlib.sha256(raw).hexdigest()==row['SHA']
                target=R/('CLOSED_'+name)
                if not target.exists():target.write_bytes(raw)
                errors[name]=[line for line in text.splitlines()if any(s in line.lower()
                    for s in ('traceback (most recent call last)','outofmemoryerror','failed to allocate'))]
                logs[name]={k:v for k,v in row.items()if k!='text'}
            report.update(passed=True,learner=diagnosis,all80=numeric,full_log_errors=errors,
                logs=logs,owner=f['OWNER_EXIT.json'],native_pose_visual_review_pending=True)
        except BaseException:report['error']=traceback.format_exc()
    with output.open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
    print(json.dumps(dict(passed=report['passed'],report=str(output),production_PT_reads=report['production_PT_reads'])))
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
