"""Independent review of completed route raw and matched inherited skills; CPU only."""
from pathlib import Path
import ast, hashlib, json, math, statistics, sys, time, traceback
import numpy as np

D=Path(__file__).resolve().parent;W=D.parent;R=D/'block2'
BASE=W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/actual_cases'
read=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(W/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
old=W/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(old.read_text(encoding='utf8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts')
node.body[0].value if False else None
node.body=[n for n in node.body if not (isinstance(n,ast.Assert) and ast.unparse(n.test)=="e['pass_']")]
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(old),'exec'))

def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    path=R/name;assert not path.exists(),('Preserve previous result',name)
    path.write_text(json.dumps(v,indent=2),encoding='utf8')
def recipe_manager(p):
    a=p['frozen_actor'];s=p['sensor_manager']
    assert a['variant']=='A0' and a['current_actor_dimension']==35 and a['actual_command_error']==0
    assert a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
    assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']<=2e-6
    for channel,row in s['actual_feedback_sample_apply'].items():
        assert row['control_period_us']==10000 and row['apply_tick']==1500
        assert row['actual_age_us']==[(1500-t)*10000 for t in row['actual_sample_tick']]
        assert row['actual_age_us']==row['requested_delay_us'] and all(x in (0,10000) for x in row['actual_age_us']) and all(row['warmup_valid'])
def terrain(p,folder):
    assert p['protocol']=='approved_E1_gentle_route_behavior_v1' and p['not_user_paused93_94']
    assert not p['new_learning'] and p['optimizer_updates']==0 and p['steps']==1500 and p['seconds']==15 and p['num_envs']==80 and p['seed']==20260928
    assert p['reason_coverage_exact'] and not p['nonfinite'] and p['max_mimic_rad']<=.01
    assert p['independent_ground_max_error_m']<=1e-6 and p['height_reward_formula_max_error']<=1e-6
    assert p['actual_physical_callbacks']==6000 and p['actual_action_callbacks']==dict(legs=6000,wheels=6000)
    assert p['physical_action_audit']['application_formula_max_error']==0
    assert p['initial']['parameters']['parameter_auditor']['actual_parameters_pass'] and p['final']['parameters']['parameter_auditor']['actual_parameters_pass']
    recipe_manager(p)
    file=folder/p['full_route_raw']['name'];assert hashfile(file)==p['full_route_raw']['sha256'] and file.stat().st_size==p['full_route_raw']['bytes']
    with np.load(file) as a:
        assert all(list(a[k].shape)==shape and np.isfinite(a[k]).all() for k,shape in p['full_route_raw']['shapes'].items())
        counts={n:int(a['reasons'][...,i].sum()) for i,n in enumerate(p['reason_names'])};assert counts==p['termination_counts']
        assert int(a['terminated'].sum())==p['actual_union_ordinary'] and int(a['truncated'].sum())==p['actual_union_truncation']
        assert np.array_equal(a['episode'][1:]-a['episode'][:-1],(a['terminated']|a['truncated'])[:-1].astype(np.int64))
        ordinary_mask=np.zeros_like(a['terminated']);truncation_mask=np.zeros_like(a['truncated'])
        for i,name in enumerate(p['reason_names']):
            if p['declared_time_outs'][name]:truncation_mask|=a['reasons'][...,i]
            else:ordinary_mask|=a['reasons'][...,i]
        assert np.array_equal(ordinary_mask,a['terminated']) and np.array_equal(truncation_mask,a['truncated'])
        assert counts.get('mimic',0)==0
        forces=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
        impulse=np.maximum(forces[...,2],0).sum(1)*.0025
        force_error=float(np.abs(impulse-a['impulse']).max())/.01
        assert force_error<=.1 and abs(force_error-p['independent_control_mean_load_max_error_N'])<=1e-6
        q=a['before_root'][:,:,3:7]
        yaw=np.arctan2(2*(q[:,:,3]*q[:,:,2]+q[:,:,0]*q[:,:,1]),1-2*(q[:,:,1]**2+q[:,:,2]**2))
        delta=a['root'][:,:,:2]-a['before_root'][:,:,:2]
        along=delta[:,:,0]*np.cos(yaw)+delta[:,:,1]*np.sin(yaw)
        first=np.where(a['terminated'],np.arange(1500)[:,None],1500).min(0)
        errors=[]
        for g in p['groups']:
            ids=np.zeros(80,dtype=bool);ids[g['env_ids']]=True
            valid=(np.arange(1500)[:,None]<first[None,:])[:,ids];speed=along[:,ids]/.01
            per=np.where(valid,speed,0).sum(0)/valid.sum(0).clip(1)
            err=float(np.abs(per-np.asarray(g['per_env_valid_prefix_along_m_s'])).max());assert err<=1e-7
            errors.append(err)
            assert abs(float(along[:,ids].sum())-g['total_signed_along_m'])<=1e-4
            assert np.allclose(a['command'][:,ids,0],g['command_vx_m_s']) and (a['command'][:,ids,1:]==0).all()
        assert p['geometry']['all_faces_and_winding_retained'] and not p['geometry']['geometry_simplified']
    return dict(groups=p['groups'],termination_counts=counts,ordinary=p['actual_union_ordinary'],unique_truncations=p['actual_union_truncation'],closure_mm=p['max_closure_m']*1000,mimic_rad=p['max_mimic_rad'],raw_sha256=p['full_route_raw']['sha256'],full_raw_reviewed=True,reset_teleport_excluded=True,ground_formula_error_m=p['independent_ground_max_error_m'],independent_mean_load_error_N=force_error,independent_signed_prefix_max_error_m_s=max(errors),original_flags={'legacy_single_peak_2mm_pass':p['legacy_single_peak_2mm_pass']})
def assignment_reset_audit(p,kind):
    changed=[];increments=None
    def rows(a,b,path=''):
        if isinstance(a,dict):
            assert set(a)==set(b)
            for k in a:yield from rows(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and len(a)==len(b):yield path,a,b
        else:assert a==b,(path,'non-row metadata differs')
    for name in ('physical_action','spring_pressure','gas_damping','chassis_PD'):
        a=p[name+'_initial_episode_assignments'];b=p[name+'_final_episode_assignments']
        parts=list(rows(a,b));eps=[(x,y) for key,x,y in parts if key.endswith('/episode')]
        assert eps
        for x,y in eps:
            delta=[yy-xx for xx,yy in zip(x,y)]
            if increments is None:increments=delta
            else:assert delta==increments
        for key,x,y in parts:
            for i,(xx,yy) in enumerate(zip(x,y)):
                if increments[i]==0:assert xx==yy,(name,key,i,'unreset row changed')
                elif key.endswith('/delay_us'):assert yy in (0,2500,5000)
    changed=[i for i,v in enumerate(increments) if v]
    if changed:
        assert kind=='flat' and changed==[38] and sum(increments)==p['resets']==1
        assert p['per_environment']['alive'][38] is False
    else:assert all(x==0 for x in increments)
    return dict(changed_rows=changed,episode_increments=increments,unreset_rows_exact=True,original_failure_and_raw_retained=True,initial_final_parameters_not_claimed_equal_after_actual_reset=True)

def main():
    R.mkdir(exist_ok=True)
    v=read(R/'COLLECTED.json');block=v['passed'];ck=block['checkpoint'];h=block['health']
    assert len(v['cases'])==4 and ck['finite_tensors']==96 and not block['discarded_preflight']
    assert h['control_steps']==24*block['actual_updates'] and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4*h['control_steps']
    assert h['actual_task_reset_events']==h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
    assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
    assert len(block['unique_completed_segment'])==1
    terrain_pair={};retention={};baseline_files=[]
    for job,row in v['cases'].items():
        m=row['manifest'];p=row['probe'];r=row['result'];kind=m['kind']
        assert r['phase']=='complete' and r['exit_code']==0 and not r['errors'] and not r['error_files'] and not r['new_learning']
        assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==ck['sha256'] and r['checkpoint']['finite_tensors']==96
        assert r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
        assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
        if 'full_route_raw' in p:
            previous=BASE/'clk2500-closure-episode-d3-114-e1-terrain32053-flat';b=read(previous/'probe.json')
            assert p['initial']==b['initial'] and p['geometry']==b['geometry'] and p['geometry_recipe']==b['geometry_recipe']
            for key in ('feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):assert p[key]==b[key],key
            terrain_pair={'previous32053':terrain(b,previous),'candidate32988':terrain(p,R/'cases'/job),'initial_root30q_parameters_geometry_and_recipes_paired_exact':True}
            baseline_files.append(dict(path=str(previous/'probe.json'),bytes=(previous/'probe.json').stat().st_size,sha256=hashfile(previous/'probe.json')))
        else:
            assert m['seed']==p['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
            previous=BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind);b=read(previous/'probe.json')
            for key in ('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments'):
                assert p[key]==b[key],(kind,key)
            if 'probe_sha256' in b:assert p['probe_sha256']==b['probe_sha256']
            age_pair=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==b['sensor_actual_manager_audit']['actual_feedback_sample_apply']
            if not age_pair:assert kind=='flat' and p['resets']==1

            params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters')
            assert params(p)==params(b)
            assignment_audit=assignment_reset_audit(p,kind)

            audit=p['physical_action_delay_audit'];assert audit['callback_counts']==dict(legs=6000,wheels=6000) and audit['application_formula_max_error']==0
            assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
            retention[kind]=dict(candidate=facts(p,kind),previous32053=facts(b,kind),paired_initial_root30q_parameters_recipes_assignments_exact=True,final_feedback_age_pair_exact=age_pair,actual_reset_assignment_audit=assignment_audit)
            baseline_files.append(dict(path=str(previous/'probe.json'),bytes=(previous/'probe.json').stat().st_size,sha256=hashfile(previous/'probe.json')))
    assert terrain_pair and set(retention)=={'flat','spin','world'}
    compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
    groups=lambda x:[{k:v for k,v in g.items() if not k.startswith('per_env') and k!='env_ids'} for g in x['groups']]
    summary=dict(terrain={role:dict(groups=groups(x),ordinary=x['ordinary'],truncations=x['unique_truncations'],closure_mm=x['closure_mm']) for role,x in terrain_pair.items() if isinstance(x,dict)},retention={k:{role:compact(x[role]) for role in ('previous32053','candidate')} for k,x in retention.items()})
    report=dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK2-MATCHED-20261009',source=ck,source_count=313,snapshot_count=57,block2=block,terrain=terrain_pair,retention=retention,summary=summary,baseline_files=baseline_files,
        actual_four_cases_model_task_data_review_complete=True,all_task_admission_passed=all(x['candidate']['v4']['pass_'] for x in retention.values()),ordinary_eval_failure_not_relabelled_as_pass=True,paired_development_protocol_only=True,no_new_graduation_percentage=True,raw_and_original_strict_flags_preserved=True,not_full_E1_RM_or_all_DR_graduation=True,no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0,
        next='Second block is naturally complete; diagnose all raw failures and select earlier balanced32053 for bounded corrective/progressive scope, no third G0 block')
    save('REVIEW.json',report);print(json.dumps(summary,ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except Exception:
        save('REVIEW_01_ERROR.json',dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK2-REVIEW-01',error=traceback.format_exc(),reader_only_no_production_change=True));raise
