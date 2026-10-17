"""Prepare readers/builders only; no training, transport, checkpoint change or GPU."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent

def write(name,source):
 ast.parse(source)
 with (B/name).open('x',encoding='utf8') as f:f.write(source)

def main():
 s=(B/'review_mean_final_full_original_valid_prefix_phase_factors_CPU_once.py').read_text('utf8')
 s=s.replace("'MEANFINAL');", "'MEANFINAL','PUBLIC4N1','PUBLIC4FINAL');")
 assert "'PUBLIC4N1','PUBLIC4FINAL'" in s
 write('review_public4_V2_original_valid_prefix_phase_factors_CPU_once.py',s)
 s=(B/'compare_b326_mean_repair_final_full_matched_initial_CPU_once.py').read_text('utf8')
 s=s.replace("str(B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018/reports/LINUX_GPU1_B326_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json')", "'LINUX_GPU1_MEANFIRST_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'")
 s=s.replace("B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018/reports/H1_B326_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json'", "R/'H1_MEANFIRST_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json'")
 s=s.replace('LINUX_GPU1_MEANFINAL_FULL1500','LINUX_GPU1_PUBLIC4N1_FULL1500').replace('H1_MEANFINAL_LINUX72_1500','H1_PUBLIC4N1_LINUX72_1500')
 s=s.replace('source_old_b326=x,source_new_mean_repair_complete_final=y','source_old_global_aux_first=x,source_new_public4_normal_only_first=y,first24_normal_controls_aux0_not_post_auxiliary_effectiveness=True')
 s=s.replace('H1_B326_VS_MEAN_REPAIR_FINAL_FULL1500_ACTUAL_INITIAL_RESIDUAL_COMPARISON_CPU_ACTUAL.json','H1_GLOBAL_FIRST_VS_PUBLIC4_NORMAL_FIRST_FULL1500_ACTUAL_INITIAL_COMPARISON_CPU_ACTUAL.json')
 write('compare_global_first_public4_normal_only_first_actual_initial_CPU_once.py',s)
 s=(B/'prepare_public4_V2_normal_only_first_Linux_GPU1_frozen_CPU_once.py').read_text('utf8')
 s=s.replace('frozen_public4_normal1_linux_v1','frozen_public4_final_linux_v1')
 s=s.replace("proof=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json').read_bytes());assert proof['passed_real_immutable_first_complete_local_CPU'];row=next(x for x in proof['all_models'] if x['kind']=='immutable_first');", "proof=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert proof['passed_whole_final_model_local_CPU'];row=proof['complete_final'];step=proof['all17Adam_after'];updates=proof['updates'];assert 0<updates<=24 and step==645620+20*updates;")
 s=s.replace('H1_public4_normal_only_update1.pt','H1_public4_finite_final.pt').replace('h1_public4_normal_update1_source_guard_v1','h1_public4_finite_final_source_guard_v1')
 s=s.replace('H1_PUBLIC4_NORMAL1','H1_PUBLIC4_FINAL')
 s=s.replace(".replace('645620','645640')", ".replace('645620',str(step))")
 s=s.replace(".replace(\"ck['owned_H1_completed_updates']==24\",\"ck['owned_H1_completed_updates']==1\")", ".replace(\"ck['owned_H1_completed_updates']==24\",\"ck['owned_H1_completed_updates']==\"+str(updates))")
 s=s.replace(".replace('Exact latest H1 closed24/Adam645640 source','Exact H1 mean-repair immutable first1/Adam645640 source')", ".replace('Exact latest H1 closed24/Adam'+str(step)+' source','Exact public4-only finite final/Adam'+str(step)+' source')")
 s=s.replace('source_is_immutable_first1_not_closed24_or_future_final=True,actual_source_Adam645640=True','source_is_actual_closed_public4_finite_final=True,actual_source_Adam=step,actual_source_owned_updates=updates')
 s=s.replace("source_Adam645640=True", "source_Adam=step")
 s=s.replace('source_immutable_first1_Adam645640=True,first_control24_normal_only_aux0_not_public4_loss_effectiveness_test=True','source_actual_closed_public4_finite_final=True,source_Adam=step,source_owned_updates=updates,requires_own_native_and_full_actual_rows=True')
 s=s.replace('PUBLIC4_V2_NORMAL_ONLY_FIRST_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json','PUBLIC4_V2_FINAL_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json')
 s=s.replace('frozen_normal_only_first_CPU=True','frozen_public4_final_CPU=True').replace('PUBLIC4_V2_NORMAL_FIRST_FROZEN_CPU_ORIGINAL_ERROR_','PUBLIC4_V2_FINAL_FROZEN_CPU_ORIGINAL_ERROR_')
 assert "proof['complete_final']" in s and "'source_is_immutable_first" not in s
 write('prepare_public4_V2_complete_final_Linux_GPU1_frozen_CPU_once.py',s)
 with (B/'reports/PUBLIC4_V2_LOCAL_POST_FINAL_READERS_PREPARED_NOT_EXECUTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_only=True,no_GPU_or_transport_or_source_model_change=True,final_builder_requires_actual_closed_full_model_CPU=True,normal_first_is_aux0_control=True),f,indent=2)

if __name__=='__main__':main()
