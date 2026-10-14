"""Paired factor inference on WORLD cohorts, with every valid episode prefix."""
from pathlib import Path
import argparse,json,time,traceback
import yawpi_actual_reader_components_v3 as m
def main():
 p=argparse.ArgumentParser();p.add_argument('--new-review',required=True);p.add_argument('--out',required=True);p.add_argument('--baseline-review',default=str(m.W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'));a=p.parse_args();out=Path(a.out);assert not out.exists()
 try:
  old=m.read(a.baseline_review);new=m.read(a.new_review)
  assert old['passed'] is True and new['passed_actual_data_and_factor_admission'] is True and old['source_SHA']==new['source_SHA']==m.SOURCE and old['controls']==new['controls']==1500 and old['callbacks']==new['callbacks']==6000
  assert new['q30_XY_physicalparams_staticrecipes_captured_RNG_and_queue_exact_to_baseline'] is True and new['root30_byteexact_NOT_claimed'] is True and new['world_yaw_pi_quaternion_exact_permutation'] is True and new['physical_birth_safe_Z_and_complete25200point_footprint_original_tolerances_passed'] is True and new['same_WORLD_heading_BODY_command_product_max_error']<=1e-7
  assert new['baseline_full80_review']['sha256']==m.sha(a.baseline_review) and new['native120_own_admission'] is not None
  per=[];groups={}
  for g in (0,1):
   buckets={k:[] for k in ('improved','regressed','passed_both','failed_both')}
   for before,after in zip(old['rows'],new['rows']):
    assert before['env']==after['env'] and before['group']==after['group']
    if before['group']!=g:continue
    x=before['contact_complete'];y=after['contact_complete'];k='improved' if y and not x else 'regressed' if x and not y else 'passed_both' if x else 'failed_both';buckets[k].append(before['env'])
    per.append(dict(env=before['env'],WORLD_group=g,old_BODY_sign=1 if g==0 else -1,new_BODY_sign=-1 if g==0 else 1,old_complete=x,new_complete=y,old_full_valid_episodes=before['all_valid_episodes'],new_full_valid_episodes=after['all_valid_episodes']))
   groups[str(g)]=buckets
  v=dict(epoch=time.time(),passed_actual_sameWORLD_pair=True,source_SHA=m.SOURCE,baseline=dict(path=a.baseline_review,sha256=m.sha(a.baseline_review)),new_review=dict(path=a.new_review,sha256=m.sha(a.new_review)),baseline_WORLD_forward=old['forward_complete'],factor_WORLD_forward=new['WORLD_forward_complete'],baseline_WORLD_reverse=old['reverse_complete'],factor_WORLD_reverse=new['WORLD_reverse_complete'],baseline_ordinary=old['ordinary'],factor_ordinary=new['ordinary'],per_WORLD_group=groups,all_moving54_valid_episode_prefixes=per,standing26_no_transit_requirement=True,root30_NOT_byteexact_declared_quaternion_pi_and_safe_Z=True,q30_XY_physicalparams_recipes_RNG_queues_exact=True,no_threshold_change=True,no_live_heading_or_position_correction=True,frozen_single_frame_factor_not_PPO=True,production_adoption_NOT_claimed=True,qualified50=False,qualified70=False,reader_SHA=m.sha(__file__),Git_pending_root_archive=True)
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),passed_actual=True,WORLD_before=[v['baseline_WORLD_forward'],v['baseline_WORLD_reverse']],WORLD_factor=[v['factor_WORLD_forward'],v['factor_WORLD_reverse']],outcomes=groups,qualified50=False)))
 except BaseException:
  err=out.with_name(out.stem+'_ORIGINAL_READER_ERROR_'+str(time.time_ns())+'.json');err.parent.mkdir(parents=True,exist_ok=True);err.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True,no_SSH_GPU_PPO=True,Git_pending_root_archive=True),indent=2),encoding='utf8');raise
if __name__=='__main__':main()
