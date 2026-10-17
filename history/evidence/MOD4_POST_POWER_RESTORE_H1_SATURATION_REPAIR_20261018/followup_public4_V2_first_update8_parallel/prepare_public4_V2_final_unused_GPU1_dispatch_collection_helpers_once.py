"""Prepare unique finite frozen-only cases. Does not upload, dispatch, collect or mutate source."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent

def main():
 sources={
 'dispatch_public4_V2_final_GPU1_unused_native120_after_closedCPU_once.py':'dispatch_public4_V2_normal_first_GPU1_unused_native120_parallel_once.py',
 'dispatch_public4_V2_final_GPU1_unused_full1500_after_nativeCPU_once.py':'dispatch_public4_V2_normal_first_GPU1_unused_full1500_after_nativeCPU_once.py',
 'collect_public4_V2_final_GPU1_native120_existing_finite_once.py':'collect_public4_V2_normal_first_GPU1_native120_existing_finite_once.py',
 'collect_public4_V2_final_GPU1_full1500_existing_finite_once.py':'collect_public4_V2_normal_first_GPU1_native120_existing_finite_once.py',
 'review_public4_V2_final_Linux_GPU1_allrow_source_CPU_once.py':'review_public4_V2_normal_first_Linux_GPU1_allrow_source_CPU_once.py',
 }
 for name,old in sources.items():
  s=(B/old).read_text('utf8').replace('frozen_public4_normal1_linux_v1','frozen_public4_final_linux_v1')
  s=s.replace('H1pn_1810ev1','H1pf_1810ev1').replace('H1_PUBLIC4_NORMAL1','H1_PUBLIC4_FINAL').replace('h1_public4_normal_update1_source_guard_v1','h1_public4_finite_final_source_guard_v1')
  s=s.replace('PUBLIC4_V2_NORMAL_ONLY_FIRST_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json','PUBLIC4_V2_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json')
  s=s.replace('PUBLIC4N1','PUBLIC4FINAL').replace('PUBLIC4_N1','PUBLIC4_FINAL')
  if 'unused_native120_' in name:
   s=s.replace('tasks/H1mc_1810ev2f','tasks/H1pn_1810ev1f').replace('previous_global_aux_final_full','previous_normal_only_first_full').replace('PREVIOUS_GLOBAL_AUX_FINAL_FULL','PREVIOUS_NORMAL_ONLY_FIRST_FULL')
  if 'collect_' in name and 'full1500_' in name:s=s.replace('native120','full1500')
  ast.parse(s)
  with (B/name).open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/PUBLIC4_V2_FINAL_FROZEN_UNUSED_GPU1_HELPERS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_only=True,helpers=sources,own_final_native120_CPU_before_unused_full1500=True,no_GPU_transport_or_new_paid_window=True,no_reuse_of_normal_only_first_native=True),f,indent=2)

if __name__=='__main__':main()
