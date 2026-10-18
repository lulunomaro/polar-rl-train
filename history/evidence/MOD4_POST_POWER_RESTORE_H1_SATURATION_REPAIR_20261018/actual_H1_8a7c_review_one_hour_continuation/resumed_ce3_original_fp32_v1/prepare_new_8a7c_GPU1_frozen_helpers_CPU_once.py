"""New closed-source frozen scopes, source-bound FP32 reference fixed before execution."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;P=B.parent;R=B/'reports'
def main():
 proof=json.loads((R/'CR3_CLOSED_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json').read_bytes());assert proof['passed_complete_payload_CPU_only'] and proof['source_Adam']==646580 and proof['source_owned_updates']==24
 names={
 'dispatch_8a7c_GPU1_own_native120_once.py':'dispatch_public4_V2_final_GPU1_unused_native120_after_closedCPU_once.py',
 'dispatch_8a7c_GPU1_unused_full1500_after_nativeCPU_once.py':'dispatch_public4_V2_final_GPU1_unused_full1500_after_nativeCPU_once.py',
 'collect_8a7c_GPU1_native120_existing_finite_once.py':'collect_public4_V2_final_GPU1_native120_existing_finite_once.py',
 'collect_8a7c_GPU1_full1500_existing_finite_once.py':'collect_public4_V2_final_GPU1_native120_existing_finite_once.py',
 'review_8a7c_GPU1_allrow_source_FP32_CPU_once.py':'review_public4_V2_final_Linux_GPU1_allrow_source_CPU_once.py'}
 for name,old in names.items():
  s=(P/old).read_text(encoding='utf8').replace('W=B.parent;','W=B.parent.parent;')
  s=s.replace('frozen_public4_final_linux_v1','frozen_ce3_original_fp32_continued_final_linux_v1').replace('H1pf_1810ev1','H1cr_1810ev1').replace('H1_PUBLIC4_FINAL','H1_CR3_FINAL').replace('h1_public4_finite_final_source_guard_v1','h1_cr3_finite_final_source_guard_v1').replace('PUBLIC4FINAL','CR3FINAL').replace('PUBLIC4_FINAL','CR3_FINAL')
  s=s.replace('PUBLIC4_V2_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json','CR3_CLOSED_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json')
  s=s.replace('tasks/H1mp_1810p2','tasks/H1cr_1810p3').replace('H1mp_1810p2/owner','H1cr_1810p3/owner')
  if name.startswith('dispatch_8a7c_GPU1_own_native'):
   s=s.replace('tasks/H1pn_1810ev1f','tasks/H1pf_1810ev1f').replace('previous_normal_only_first_full','previous_ce3_full').replace('PREVIOUS_NORMAL_ONLY_FIRST_FULL','PREVIOUS_CE3_FULL')
  if 'collect_' in name and 'full1500_' in name:s=s.replace('native120','full1500')
  if name.startswith('review_'):
   assert 'range(0,len(flat),4096)' in s
   s=s.replace('range(0,len(flat),4096)','range(0,len(flat),120000)').replace('flat[start:start+4096]','flat[start:start+120000]').replace('actual[start:start+4096]','actual[start:start+120000]')
   s=s.replace('original_H1_CPUmean_tolerance1e4=True,','original_H1_CPUmean_tolerance1e4=True,actor_reference_protocol="original_FP32_fixed120000row_batch_same_absolute1e-4_declared_before_GPU",')
  ast.parse(s)
  with (B/name).open('x',encoding='utf8') as f:f.write(s)
 report=dict(epoch=time.time(),prepared_helpers=names,source_SHA=proof['source']['SHA'],Adam646580=True,closed24=True,native_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1cr_1810ev1',full_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1cr_1810ev1f',new_source_own_native120_then_allrow_CPU_before_unused_full1500=True,actor_reference='original FP32 fixed120000row batch, weights/obsF32, absolute1e-4 unchanged; fixed before any new GPU data, not per-row or post-hoc precision selection',geometry_reference='original independent FP64 authored34/geometry1e-6 unchanged',all_other_source_physics_phase_event_query_COM_hardware_guards_unchanged=True,no_GPU_or_transport_yet=True,no_PPO_or_budget=True)
 with (R/'NEW_8A7C_FROZEN_NATIVE_FULL_HELPERS_AND_FIXED_REFERENCE_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(helpers=len(names),source_SHA=proof['source']['SHA'],native_and_full_not_yet=True)))
if __name__=='__main__':main()
