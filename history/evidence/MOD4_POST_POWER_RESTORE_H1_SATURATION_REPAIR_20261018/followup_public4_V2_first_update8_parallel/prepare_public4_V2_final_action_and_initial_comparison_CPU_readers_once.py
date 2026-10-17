"""Only prepare local final diagnostics; original gates and data remain unchanged."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent

def main():
 p=B/'review_mean_final_closed_loop_action_target_factors_CPU_once.py';s=p.read_text('utf8')
 s=s.replace('frozen_mean_final_linux_v2','frozen_public4_final_linux_v1').replace('H1_MEANREPAIR_FINAL_LINUX4090_MANIFEST_V2.json','H1_PUBLIC4_FINAL_LINUX4090_MANIFEST_V1.json')
 s=s.replace('source_checkpoint_Adam646100=True',"source_actual_final_CPU_report=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes())")
 s=s.replace('MEAN_REPAIR_FINAL_','PUBLIC4_V2_FINAL_').replace('MEAN_FINAL_ACTION_FACTOR_','PUBLIC4_V2_FINAL_ACTION_FACTOR_')
 ast.parse(s)
 with (B/'review_public4_V2_final_closed_loop_action_target_factors_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
 print('prepared_final_action_factors_only')

if __name__=='__main__':main()
