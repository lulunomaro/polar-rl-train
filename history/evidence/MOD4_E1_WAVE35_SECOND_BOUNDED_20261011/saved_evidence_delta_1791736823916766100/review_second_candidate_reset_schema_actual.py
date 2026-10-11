"""Review complete130 actual candidate routes and inherited skills; no GPU or publication."""
from pathlib import Path
import sys,json,time,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';read=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
sys.path.insert(0,str(W/'MOD4_E1_G3_MATCHED_REVIEW_20261010'))
from review_approach128_actual import audit
def final_sensor_receipt_pair(candidate, reference):
    a = candidate['sensor_recipe']
    b = reference['sensor_recipe']
    dynamic = 'max_abs_actual_bias_rad'
    assert set(a) == set(b) and all((a[k] == b[k] for k in a if k != dynamic))
    assert a['episode_leg_encoder_bias_bound_rad'] == b['episode_leg_encoder_bias_bound_rad'] == 0.0075
    assert a['bias_finite'] and b['bias_finite'] and (0 <= a[dynamic] <= 0.0075) and (0 <= b[dynamic] <= 0.0075)
    assert candidate['sensor_manager']['tick'] == reference['sensor_manager']['tick'] == 1500
    return dict(static_sensor_configuration_and_noise_draw_counts_exact=True, final_observation_key=dynamic, candidate_final_bias_max=a[dynamic], reference_final_bias_max=b[dynamic], final_bias_observation_exact=a[dynamic] == b[dynamic], actual_bias_resampled_on_physical_episode_reset_as_original_source=True, not_an_initial_recipe_parameter=True, initial_sensor_bias_vectors_not_raw_captured_no_new_exact_claim=True, original_bias_bound_and_finite_checks_unchanged=True)

def reset_audit(p):

    def rows(a, b, path=''):
        if isinstance(a, dict):
            assert set(a) == set(b)
            for k in a:
                yield from rows(a[k], b[k], path + '/' + k)
        elif isinstance(a, list):
            assert len(a) == len(b)
            yield (path, a, b)
        else:
            assert a == b, (path, 'non-row metadata differs')
    increments = None
    for name in ('physical_action', 'spring_pressure', 'gas_damping', 'chassis_PD'):
        parts = list(rows(p[name + '_initial_episode_assignments'], p[name + '_final_episode_assignments']))
        for key, a, b in parts:
            if key.endswith('/episode'):
                delta = [y - x for x, y in zip(a, b)]
                assert all((v >= 0 and int(v) == v for v in delta))
                if increments is None:
                    increments = delta
                else:
                    assert increments == delta
        for key, a, b in parts:
            for i, (x, y) in enumerate(zip(a, b)):
                if increments[i] == 0:
                    assert x == y, (name, key, i)
                elif key.endswith('/delay_us'):
                    assert y in (0, 2500, 5000)
    assert increments is not None
    if 'resets' in p:
        assert sum(increments) == p['resets']
    elif any(increments):
        assert 'alive' in p and 'first_failure_step' in p
        assert len(p['alive']) == len(p['first_failure_step']) == len(increments)
        assert all(v in (0, 1) for v in increments)
        assert [i for i,v in enumerate(increments) if v] == [i for i,v in enumerate(p['alive']) if not v]
        for i,v in enumerate(increments):
            if v: assert not p['alive'][i] and 0 <= p['first_failure_step'][i] < p['steps']
        assert all(p['first_failure_step'][i] == p['steps'] for i,v in enumerate(increments) if not v)
    else:
        assert sum(increments) == 0
    return dict(changed_rows=[i for i, v in enumerate(increments) if v], episode_increments=increments, unreset_rows_exact=True, original_task_flags_retained=True, total_resets_field_present='resets' in p, episode_increment_sum=sum(increments), missing_total_not_assumed_zero=True)

def main():
 v=read(sorted(R.glob('WAVE143_COLLECTED_*.json'))[-1]);b=v['passed'];assert b and not b['discarded_preflight'] and len(b['unique_completed_segment'])==1
 cpu=read(sorted(R.glob('SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]);assert cpu['passed'] and cpu['actual_source_count']==369 and cpu['own_checkpoint']['sha256']==b['checkpoint']['sha256']
 h=b['health'];assert h['control_steps']==b['actual_updates']*24 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 rows={};retention={};terrain=None
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256'] and r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==cpu['actual_finite_tensor_count']==102
  if 'full_route_raw' in p:assert p['checkpoint_sha256']==b['checkpoint']['sha256']
  else:assert p['checkpoint'].replace('\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
  assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  if 'full_route_raw' in p:
   assert r['runtime_archive_sha256']=='858ad4ef431f188f3275dc8b3c3690bf1d987a5c074f9aed698e15343ad66d2b' and row['raw_SHA_exact']
   terrain=audit(p,R/'cases'/jid)
   anchor=read(W/'MOD4_E1_G3_MATCHED_REVIEW_20261010/reports/cases/clk2500-closure-episode-d3-128-e1-g3-source32058-approach040-fullroute-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k
   terrain['sensor_final_receipt_reference128']=final_sensor_receipt_pair(p,anchor)
   source=read(W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-129-e1-g3-command-retention-terrain-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==source[k],('selected129',k)
   terrain['sensor_final_receipt_selected129']=final_sensor_receipt_pair(p,source)
  else:
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   baseline=read(common.BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json')
   keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
   assert all(p[k]==baseline[k] for k in keys)
   params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters');assert params(p)==params(baseline)
   if 'probe_sha256' in baseline:assert p['probe_sha256']==baseline['probe_sha256']
   a=p['physical_action_delay_audit'];assert a['callback_counts']==dict(legs=6000,wheels=6000) and a['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=reset_audit(p);age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert resets['episode_increment_sum']>0
   retention[kind]=dict(candidate=common.facts(p,kind),baseline32053=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_pair_exact=True,reset_audit=resets,feedback_age_pair_exact=age)
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 summary=dict(terrain=terrain['groups'] if terrain else None,retention={kind:{role:compact(x[role]) for role in ('baseline32053','candidate')} for kind,x in retention.items()})
 report=dict(epoch=time.time(),trial_id='E1-WAVE-G3-143-CANDIDATE-ACTUAL-REVIEW-01',collection=str(sorted(R.glob('WAVE143_COLLECTED_*.json'))[-1]),own=b,terrain=terrain,retention=retention,summary=summary,pending=v['pending'],review_complete=terrain is not None and set(retention)=={'flat','spin','world'} and not v['pending'],reviewed_cases_have_matched_initial_conditions=True,original_flags_failures_and_residuals_preserved=True,no_RM70mm_or_all_E1_graduation=True,no_permanent_anti_forgetting_proof=True,requires_actual_in_scope_decision_before_more_PPO=True,inherited_flat_skills_diagnostic_E0_separately_frozen=True,no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0)
 out=R/('WAVE143_REVIEW_'+str(int(report['epoch']))+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),summary=summary,pending=v['pending'],review_complete=report['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except Exception:
  out=R/('WAVE143_RESET_SCHEMA_REVIEW_ERROR_'+str(int(time.time()))+'.json');assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-WAVE-G3-143-CANDIDATE-CPU-READER-01',error=traceback.format_exc(),original_source_and_error_retained=True,no_production_change=True),indent=2),encoding='utf8');raise
