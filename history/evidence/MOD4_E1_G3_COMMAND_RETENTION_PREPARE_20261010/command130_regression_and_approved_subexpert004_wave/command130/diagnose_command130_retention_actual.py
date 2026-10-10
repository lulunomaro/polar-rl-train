"""Diagnose completed inherited-skill cases and saved actual sampling, without production mutation."""
from pathlib import Path
import hashlib,json,math,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(root):
 paths=list((D/'remote_evidence'/root).glob('RETENTION_COMMAND_ACTUAL.json.*'))
 return max(((p,read(p)) for p in paths),key=lambda x:x[1]['actual_controls'])
def main():
 review_path=sorted(R.glob('CANDIDATE_130_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1]
 v=read(review_path);assert set(v['retention'])=={'flat','spin','world'}
 assert v['selected_checkpoint_SHA']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
 assert v['candidate_checkpoint_SHA']=='f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a'
 sp,s=artifact('MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010')
 cp,c=artifact('MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010')
 assert s['actual_controls']==144 and c['actual_controls']==1008
 a,b=s['audit'],c['audit'];assert a['profile']==b['profile'] and a['assignment_sha256']==b['assignment_sha256']
 assert not a['pure_high_spin'] and not b['pure_high_spin'] and a['projection_error']==b['projection_error']==0
 assert a['histogram_rows']==b['histogram_rows'] and a['histogram_columns']==b['histogram_columns']
 delta=[[y-x for x,y in zip(ar,br)] for ar,br in zip(a['control_histogram'],b['control_histogram'])]
 assert all(x>=0 for row in delta for x in row)
 total=sum(map(sum,delta));expected=20000*c['actual_controls']
 assert total==expected,(total,expected)
 plane=b['histogram_rows'].index('plane_for_rm')
 retained=sum(delta[plane][2:6]);nonplane=sum(sum(row[2:6]) for i,row in enumerate(delta) if i!=plane)
 assert nonplane==0 and all(delta[plane][j]>0 for j in range(2,6))
 negative=[]
 for role in ('selected_source364_129','candidate_source365'):
  x=next(x for x in v['retention']['spin'][role]['pure4pi'] if x['command']<0)
  negative.append(dict(role=role,passed=x['passed'],count=x['count'],signed_target=x['command'],signed_actual_mean=x['mean'],signed_error_mean=x['mean']-x['command'],original_tolerance_rad=.2,errors=[z-x['command'] for z in x['values']],values=x['values']))
 world={role:{k:v['retention']['world'][role][k] for k in ('passed','count','max_abs_cross','along_range','directions')} for role in ('selected_source364_129','candidate_source365')}
 out=dict(epoch=time.time(),trial_id='E1-G3-COMMAND-130-INHERITED-SKILL-REGRESSION-DIAGNOSIS-01',actual_review=str(review_path),actual_review_SHA=sha(review_path),retention_all_three_complete_matched=True,all_four_case_review_complete=v['review_complete'],pending=v['pending'],selected_checkpoint_SHA=v['selected_checkpoint_SHA'],candidate_checkpoint_SHA=v['candidate_checkpoint_SHA'],negative_pure4pi=negative,world=world,actual_sampling=dict(rows=b['histogram_rows'],columns=b['histogram_columns'],source_cumulative_control_histogram=a['control_histogram'],candidate_cumulative_control_histogram=b['control_histogram'],actual365_control_histogram_delta=delta,actual365_control_entries=total,expected1008controls_times20000=expected,actual_retained_control_entries=retained,actual_retained_control_share=retained/total,actual_nonplane_retained_control_entries=nonplane,all_four_signed_straight_world_branches_actually_used=True,no_pure_spin_modes_in_this_scope=True,projection_error=0,mesh_eligibility_not_contact_force_certification=True,source_capture=dict(path=str(sp),sha256=sha(sp)),candidate_capture=dict(path=str(cp),sha256=sha(cp))),findings=['All three inherited-skill cases completed with matching source and initial conditions; this is a behavioral regression despite healthy learning/fullsave.','The online old straight and signed world branches were actually sampled on eligible plane support; the mechanism was not simply absent or a no-op.','This scoped repair did not train pure high-rate spin, so low-rate world sampling cannot establish preservation of the old negative4pi behavior.','The mean negative4pi signed error grew beyond the unchanged .2rad criterion; per-environment errors and original flags remain preserved.','World positive yaw2 worsened; both signed directions and complete-circle along/cross rows are preserved.','Sampling coverage or multi-objective interference remains a hypothesis; no causal ablation or permanent anti-forgetting proof.'],decision=dict(no_more_PPO_from_candidate_source365=True,no_automatic_third_same_scope_block=True,no_50mm_promotion=True,wait_for_actual_terrain130_before_final_source_decision=True,rollback_source_candidate_is_complete129_source364_not_discard_or_maxiter=True,next_repair_must_explicitly_review_old_skill_coverage_and_new_command_contract=True,no_new_S7_S8_or_highroughspin_authority=True),original_false_raw_cost_retained=True,reader_locator_notes=[dict(requested=str(D/'implementation'),result='rg directory absent',resolved_actual_source=str(D/'payload/isaac/mod4'),no_production_change=True)],no_GPU_learning_queue_canonical_signal_or_old_once_action=True,new_budget_seconds=0)
 p=R/('COMMAND130_RETENTION_DIAGNOSIS_'+str(int(out['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(out,ensure_ascii=False,indent=2).encode())
 print(json.dumps(dict(report=str(p),actual_retained_control_share=retained/total,negative4pi=negative,world=world,full_four_review_complete=v['review_complete'],pending=v['pending'],candidate365_more_PPO_rejected=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/('COMMAND130_DIAGNOSIS_READER_ERROR_'+str(time.time_ns())+'.json');assert not p.exists()
  p.write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-COMMAND-130-CPU-DIAGNOSIS-READER-01',error=traceback.format_exc(),read_only_no_production_mutation=True),indent=2).encode());raise
