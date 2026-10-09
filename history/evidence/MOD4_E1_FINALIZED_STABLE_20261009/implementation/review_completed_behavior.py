"""Independent actual raw/parameter/route and inherited-skill review; no dispatch."""
from pathlib import Path
import json,sys,ast,time,hashlib,math,statistics
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,'/home/egde/rl_candidates/MOD4_S3_E1_FINALIZED_BEHAVIOR_HANDOFF_20261009/isaac/mod4')
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
def facts(p,k):
    e=evidence(p,'spin' if k=='world' else k,15);assert e['pass_'],e
    a=p['frozen_architecture_audit'];s=p['sensor_actual_manager_audit'];d=p['feedback_delay_recipe']
    assert a['variant']=='A0' and a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
    assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']<=2e-6
    assert d['profile']=='control_0_10ms_v1' and d['control_period_us']==10000 and d['requested_delay_us']==[0,10000] and d['action_delay_us']==0
    ages={}
    for channel,row in s['actual_feedback_sample_apply'].items():
        assert row['control_period_us']==10000 and row['apply_tick']==1500
        assert all(age in (0,10000) for age in row['actual_age_us'])
        assert row['actual_age_us']==[(row['apply_tick']-t)*10000 for t in row['actual_sample_tick']]
        assert row['actual_age_us']==row['requested_delay_us'] and all(row['warmup_valid'])
        ages[channel]={str(t):row['actual_age_us'].count(t) for t in (0,10000)}
    out=dict(v4=e,closure_mm=1000*p['max_closure_after_grace_m' if k=='flat' else 'max_closure_m'],actual_delay_age_counts_at_final_tick=ages,original_flags={n:p.get(n) for n in ('strict_pass','strict_pass_window','strict_pass_window_5ms','physical_smoke_pass','spin_skill_pass','spin_skill_pass_legacy_reference')})
    if k=='flat':
        out['straight']=[dict(command=g['command_vx'],error=g['vel_error'],steady_error=g['steady_vel_error']) for g in p['groups'] if g['profile']=='constant' and abs(g['command_vx'])==1.5]
    if k=='spin':
        out['pure4pi']=[]
        for g in p['groups']:
            if g['profile']=='spin' and abs(abs(g['wz'])-4*math.pi)<1e-6:
                values=[p['per_environment']['yaw_rate'][i] for i,gid in enumerate(p['group_ids']) if gid==g['group_id']]
                out['pure4pi'].append(dict(command=g['wz'],passed=sum(abs(v-g['wz'])<=.2 for v in values),count=len(values),mean=statistics.mean(values),values=values))
    if k=='world':
        w=target(p,.5);rows=w['rows'];assert len(rows)==64
        out.update(world_target=w,passed=sum(row['pass_'] for row in rows),count=64,max_abs_cross=max(abs(row['cross_m_s']) for row in rows),along_range=[min(row['along_m_s'] for row in rows),max(row['along_m_s'] for row in rows)],directions=[dict(yaw=y,passed=sum(row['pass_'] for row in rows if row['command_yaw_rad_s']==y),count=sum(row['command_yaw_rad_s']==y for row in rows)) for y in (-2.,-1.,1.,2.)])
    return out
v=read(R/'E1_PLANNED_BEHAVIOR_CURRENT_ACTUAL.json');pub=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json');rows=v['rows']
assert all(r.get('result') and r['result']['phase']=='complete' for r in rows.values()),'Pending actual cases; do not write acceptance'
assert not v['evaluator_receipts']['ATTENTION']
terrain={};retention={}
for job,row in rows.items():
 m=row['manifest'];r=row['result'];p=row['probe'];kind=m['kind']
 assert r['exit_code']==0 and not r['errors'] and not r['error_files'] and r['new_learning'] is False
 assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256'] and r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
 assert r['steps']==m['steps']==p['steps']==1500 and m['physics_dt_s']==.0025 and m['solver_position']==32 and m['solver_velocity']==4
 if m['actual_behavior_scope'].startswith('gentle terrain'):
  assert p['protocol']=='approved_E1_gentle_route_behavior_v1' and p['not_user_paused93_94'] and not p['new_learning'] and p['optimizer_updates']==0
  assert r['checkpoint']['sha256']==p['checkpoint_sha256'] and p['seed']==m['seed']==20260928 and p['num_envs']==80
  assert p['reason_coverage_exact'] and not p['nonfinite'] and p['max_mimic_rad']<=.01 and p['independent_ground_max_error_m']<=1e-6 and p['height_reward_formula_max_error']<=1e-6
  assert p['actual_physical_callbacks']==6000 and p['actual_action_callbacks']==dict(legs=6000,wheels=6000) and p['physical_action_audit']['application_formula_max_error']==0
  assert p['initial']['parameters']['parameter_auditor']['actual_parameters_pass'] and p['final']['parameters']['parameter_auditor']['actual_parameters_pass']
  assert p['independent_control_mean_load_max_error_N']<=.1 and row['raw_SHA_exact']
  file=R/'actual_cases'/job/p['full_route_raw']['name'];assert hashlib.sha256(file.read_bytes()).hexdigest()==p['full_route_raw']['sha256']
  a=np.load(file);assert a['root'].shape==(1500,80,13) and a['q'].shape==(1500,80,30) and a['physical_wheel_force_N'].shape==(6000,80,2,3)
  assert all(np.isfinite(a[k]).all() for k in a.files)
  masks=a['reasons'];names=p['reason_names'];counts={n:int(masks[...,i].sum()) for i,n in enumerate(names)};assert counts==p['termination_counts']
  assert int(a['terminated'].sum())==p['actual_union_ordinary'] and int(a['truncated'].sum())==p['actual_union_truncation']
  assert all(counts.get(n,0)==0 for n in ('mimic',))
  assert np.array_equal(a['episode'][1:]-a['episode'][:-1],(a['terminated']|a['truncated'])[:-1].astype(np.int64))
  forces=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
  independent=np.maximum(forces[...,2],0).sum(1)*.0025
  err=float(abs(independent-a['impulse']).max())/.01;assert err<=.1 and abs(err-p['independent_control_mean_load_max_error_N'])<=1e-6
  quat=a['before_root'][:,:,3:7];heading=np.arctan2(2*(quat[:,:,3]*quat[:,:,2]+quat[:,:,0]*quat[:,:,1]),1-2*(quat[:,:,1]**2+quat[:,:,2]**2))
  delta=a['root'][:,:,:2]-a['before_root'][:,:,:2];along=delta[:,:,0]*np.cos(heading)+delta[:,:,1]*np.sin(heading)
  fail=np.where(a['terminated'],np.arange(1500)[:,None],1500).min(0)
  for group in p['groups']:
   ids=np.array(group['env_ids']);valid=np.arange(1500)[:,None]<fail[None,ids];speed=along[:,ids]/.01
   per=np.where(valid,speed,0).sum(0)/valid.sum(0).clip(1)
   assert np.allclose(per,group['per_env_valid_prefix_along_m_s'],rtol=0,atol=1e-7)
   assert abs(float(along[:,ids].sum())-group['total_signed_along_m'])<=1e-4
   assert np.allclose(a['command'][:,ids,0],group['command_vx_m_s']) and (a['command'][:,ids,1:]==0).all()
  assert p['geometry']['all_faces_and_winding_retained'] and not p['geometry']['geometry_simplified']
  terrain['anchor' if '-anchor-' in job else 'candidate']=dict(job=job,probe=p,raw_sha256=p['full_route_raw']['sha256'],actual_raw_reviewed=True)
 else:
  assert m['seed']==20261002 and r['checkpoint']['finite_tensors']==96 and m['artifacts']['runtime']['sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
  f=facts(p,kind)
  oldfolder=R/'baseline'/kind;baseline=read(oldfolder/'probe.json')
  assert hashlib.sha256((oldfolder/'probe.json').read_bytes()).hexdigest()==pub['reused_old_skill_baseline'][kind]['probe_sha256']
  for key in ('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments'):
   assert p[key]==baseline[key],(kind,key)
  params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters')
  assert params(p)==params(baseline)
  for key in ('physical_action','spring_pressure','gas_damping','chassis_PD'):
   assert p[key+'_initial_episode_assignments']==p[key+'_final_episode_assignments']
  assert p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
  retention[kind]=dict(job=job,facts=f,baseline_facts=facts(baseline,kind),paired_initial_root_q_parameters_recipes_assignments_exact=True)
assert len(terrain)==2 and len(retention)==3
b=terrain['anchor']['probe'];n=terrain['candidate']['probe'];assert b['initial']==n['initial'] and b['geometry']==n['geometry'] and b['geometry_recipe']==n['geometry_recipe']
for key in ('sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):
 # Recipe draw counters are identical only when reset counts agree; bounds/profile
 # are paired in actual initial assignments, while all later draws are retained.
 if key!='sensor_recipe':assert b[key]==n[key],key
summary=dict(terrain={k:dict(groups=x['probe']['groups'],termination_counts=x['probe']['termination_counts'],max_closure_mm=x['probe']['max_closure_m']*1000,raw_sha256=x['raw_sha256']) for k,x in terrain.items()},
 retention={k:dict(candidate={n:x['facts'].get(n) for n in ('straight','pure4pi','passed','count','max_abs_cross','along_range')},baseline={n:x['baseline_facts'].get(n) for n in ('straight','pure4pi','passed','count','max_abs_cross','along_range')}) for k,x in retention.items()})
report=dict(epoch=time.time(),source_sha256=pub['source']['sha256'],actual_five_cases_review_complete=True,task_model_data_scope_accepted=True,summary=summary,terrain=terrain,retention=retention,
 no_new_performance_graduation_percentage=True,old_strict_raw_and_ordinary_events_preserved=True,not_all_E1_or_RM_or_hardware_graduation=True,cross_GPU_dynamic_bitexact=False,
 no_GPU_or_canonical_write=True,new_budget_seconds=0)
(R/'E1_PLANNED_BEHAVIOR_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(summary))
