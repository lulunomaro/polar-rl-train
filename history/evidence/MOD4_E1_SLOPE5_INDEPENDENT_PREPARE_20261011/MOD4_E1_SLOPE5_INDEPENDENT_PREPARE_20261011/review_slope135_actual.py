from slope_io import *
import numpy as np,traceback
sys.path.insert(0,str(PRE));from review_slope134_actual import terrain
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
read=lambda p:json.loads(p.read_bytes())
def audit(p,folder):
   s=p['route_scope'];assert s['angle_deg']==5. and s['ramp_length_m']==2. and s['required_after_support_m']==.2 and s['no_vertical_riser'] and s['not_actual_RM_geometry']
   g=p['geometry_recipe']['SLOPE_geometry_change'];assert g['other_four_families_unchanged'] and g['proportions_unchanged']
   base=terrain(p,folder);centers=np.array(s['tile_centers']);o=np.array(s['orientation']);assert (o==1).sum()==(o==-1).sum()==40
   starts=np.array(s['requested_starts']);assert np.allclose(np.array(p['initial']['root'])[:,:2],starts.astype(np.float32),atol=1e-6,rtol=0)
   sampled=np.array(s['actual_sampled_ground']);x=np.array(s['actual_sampled_canonical_x_m']);assert np.max(abs(sampled-(np.clip((x+1)/2,0,1)*2*np.tan(np.deg2rad(5)))[None,:]))<=1e-6
   names=p['body_names'];wi=[names.index(n) for n in ('left_wheel','right_wheel')];rows=[]
   with np.load(folder/p['full_route_raw']['name']) as a:
    pos=a['COM_link_pos'];ep=a['episode'];failed=a['terminated'];force=a['physical_wheel_force_N'].reshape(1500,4,80,2,3);supported=np.maximum(force[...,2],0).sum(1)*.0025/.01>1.
    assert np.max(abs(np.linalg.norm(a['normal'],axis=-1)-1))<=.01 and a['normal'][...,2].min()>.01
    for i in range(80):
     u=(pos[:,i,wi,0]-centers[i,0])*o[i];failure=int(np.where(failed[:,i],np.arange(1500),1500).min());segments=[]
     for episode in np.unique(ep[:,i]):
      ids=np.flatnonzero((ep[:,i]==episode)&(np.arange(1500)<failure))
      if not len(ids):continue
      w=u[ids]
      if i%3==0:before=np.flatnonzero(w.max(1)<-1.2);after=np.flatnonzero(w.min(1)>1.2)
      elif i%3==1:before=np.flatnonzero(w.min(1)>1.2);after=np.flatnonzero(w.max(1)<-1.2)
      else:before=after=np.array([],dtype=int)
      complete=bool(len(before) and len(after) and before.min()<after.max());bc=[k for k in before if supported[ids[k],i].all()];ac=[k for k in after if supported[ids[k],i].all()]
      confirmed=bool(complete and bc and ac and min(bc)<max(ac))
      segments.append(dict(episode=int(episode),first_control=int(ids[0]),last_control=int(ids[-1]),canonical_wheel_x_range_m=[float(w.min()),float(w.max())],full_route_complete=complete,original1N_contact_confirmed=confirmed))
     rows.append(dict(env=i,group=('ascending','descending','stand')[i%3],orientation=int(o[i]),first_ordinary_failure_control=failure,complete=any(x['full_route_complete'] for x in segments),contact_confirmed=any(x['original1N_contact_confirmed'] for x in segments),segments=segments))
   summary={g:dict(environments=sum(x['group']==g for x in rows),complete_envs=sum(x['group']==g and x['complete'] for x in rows),contact_confirmed_envs=sum(x['group']==g and x['contact_confirmed'] for x in rows)) for g in ('ascending','descending','stand')}
   return dict(base_review=base,groups=summary,rows=rows,all_valid_prefixes_retained=True,standing_not_required_to_cross=True)
def main():
 collection=sorted(R.glob('SLOPE135_COLLECTED_[0-9]*.json'))[-1];v=read(collection);b=v['passed'];assert b and not b['discarded_preflight'] and len(b['unique_completed_segment'])==1
 h=b['health'];assert h['control_steps']==24*b['actual_updates'] and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4*h['control_steps']
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 terrain=None;retention={};source_root=D.parent/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/cases'
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256']
  if 'full_route_raw' in p:assert p['checkpoint_sha256']==b['checkpoint']['sha256']
  else:assert p['checkpoint'].replace('\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()
  assert r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==102 and r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
  assert r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
  if 'full_route_raw' in p:
   assert r['runtime_archive_sha256']=='f94fc989a1dd8a02a7b535aa7974a8172a9441762563518970a756a46fcb8bc9' and row['raw_SHA_exact']
   terrain=audit(p,R/'cases'/jid)
   anchor=read(PRE/'reports/cases/clk2500-closure-episode-d3-134-e1-slope5-source364-mirrored-fullroute-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k
  else:
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   baseline=read(common.BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json')
   source=read(source_root/('clk2500-closure-episode-d3-129-e1-g3-command-retention-retention-'+kind)/'probe.json')
   keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
   assert all(p[k]==baseline[k]==source[k] for k in keys)
   params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters');assert params(p)==params(baseline)==params(source)
   if 'probe_sha256' in baseline:assert p['probe_sha256']==baseline['probe_sha256']==source['probe_sha256']
   a=p['physical_action_delay_audit'];assert a['callback_counts']==dict(legs=6000,wheels=6000) and a['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=common.reset_audit(p)
   age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert p.get('resets',0)>0
   retention[kind]=dict(candidate=common.facts(p,kind),source364=common.facts(source,kind),baseline32053=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_pair_exact=True,reset_audit=resets,feedback_age_pair_exact=age)
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 summary=dict(terrain=terrain['groups'] if terrain else None,retention={k:{role:compact(x[role]) for role in ('source364','candidate','baseline32053')} for k,x in retention.items()})
 result=dict(epoch=time.time(),trial_id='SLOPE135-COMPLETE-INDEPENDENT-ACTUAL-REVIEW-01',collection=str(collection),own=b,terrain=terrain,retention=retention,summary=summary,pending=v['pending'],review_complete=terrain is not None and set(retention)=={'flat','spin','world'} and not v['pending'],all_valid_incomplete_prefixes_and_original_flags_preserved=True,standing_not_required_to_cross=True,no_gate_or_actual_RM_slope_or_full_E1_graduation=True,no_permanent_anti_forgetting_proof=True,requires_complete_scope_decision_before_more_PPO=True,no_GPU_PPO_queue_or_budget_write=True)
 p=save('SLOPE135_SCHEMA_REVIEW_'+str(time.time_ns())+'.json',result);print(json.dumps(dict(report=str(p),summary=summary,pending=v['pending'],review_complete=result['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE135_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,original_results_not_relabelled=True));raise
