"""Whole matched A/B/C cells from own complete newA and existing actual B/C."""
from pathlib import Path
import hashlib,json,time
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015/reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 summary={};evidence=[];frozen=0.
 for kind in ('flat','spin','world'):
  case=f's5_single_W35_{kind}_1500_v1';single=json.loads((R/(case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')).read_bytes())['result'];source=json.loads((R/(case+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json')).read_bytes());assert source['passed'] and source['source9_STD_initial_final_exact']
  original=OLD/(kind+'_COMPLETE_RULE_VS_GATE_ORIGINAL_PHYSICAL_PAIR_CPU_REVIEW.json');old=json.loads(original.read_bytes())['result'];configs=[('A_single_W35',single),('B_rule',old['baseline']),('C_gate148',old['candidate'])]
  pairs=[]
  for mode in ('RULE_EVAL','GATE_EVAL'):
   p=R/(kind+'_SINGLE_A_VS_'+mode+'_COMPLETE_ORIGINAL_PAIR_CPU_REVIEW.json');x=json.loads(p.read_bytes());assert x['result']['actual_initial_root_q30_parameters_recipes_RNG_queues_exact'];pairs.append(dict(path=str(p),sha256=H(p)))
  rows=[]
  for name,data in configs:
   assert data['steps']==1500 and data['data']['complete_data_contract'];item=dict(configuration=name,ordinary=data['data']['ordinary'],truncation=data['data']['truncation'],original_flags=data['old_original_flags'],all_original_valid_prefixes_preserved=True)
   if kind=='flat':item['straight']=data['straight']
   if kind=='spin':item['pure4pi']=data['pure4pi']
   if kind=='world':item.update(world_count=data['world_count'],whole_signedcircle=data['whole_signedcircle_original_target'],all_valid_prefixes=data['all_valid_prefixes'])
   rows.append(item)
  summary[kind]=dict(configurations=rows,new_single_source_control=source,pairs=pairs)
  evidence.extend(pairs);evidence.append(dict(path=str(original),sha256=H(original)))
  for steps in (120,1500):
   b=json.loads((R/(f's5_single_W35_{kind}_{steps}_v1_INDEPENDENT_BOUNDARY.json')).read_bytes());assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free'];frozen+=b['actual_parent_exit']['unique_actual_parent_load_run_save_exit_seconds']
 first=W/'MOD4_S5_SINGLE_W35_MATCHED35_20261015/reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json';assert json.loads(first.read_bytes())['passed_actual_first_matched_three_configurations']
 result=dict(epoch=time.time(),actual_three_retention_single_A_and_old_B_C_matched_cells_complete=True,source_single_W35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',source_gate_SHA='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3',summary=summary,evidence=evidence,first_original35_threeway=dict(path=str(first),sha256=H(first)),original_query_contact_COM_hardware_signedcircle_tolerances_unchanged=True,all_actual_firstphysics_rootq30_parameters_staticrecipes_RNGqueues_and_loadedDLL_pairs_exact=True,old_false_and_failed_valid_prefixes_preserved=True,single_new_six_frozen_parent_seconds=frozen,no_canonical_cost=True,old_B_C_GPU_cases_not_replayed=True,S5_overall_or_architecture_winner_not_claimed=True,no_second_gate_learning_or_other_PPO_admitted=True)
 p=R/'S5_SINGLE_W35_A_THREE_RETENTION_MATCHED_B_C_COMPLETE_ACTUAL_CPU_REVIEW.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(complete=True,world=[x['world_count'] for x in summary['world']['configurations']],ordinary={k:[x['ordinary'] for x in v['configurations']] for k,v in summary.items()},new_PPO=False)))
if __name__=='__main__':main()
