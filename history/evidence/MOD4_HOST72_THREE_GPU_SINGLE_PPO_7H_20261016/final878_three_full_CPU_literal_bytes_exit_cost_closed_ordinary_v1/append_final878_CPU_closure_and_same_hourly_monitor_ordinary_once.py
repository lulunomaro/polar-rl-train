"""Append final same-run evidence; never record/tag/restart again."""
from pathlib import Path
import importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';BASE='f78cd58e8555c183f941dd5c3c5b761809729cad'
def main():
 for n in ('FINAL878_THREE_COMPLETE_MODELS_LOCAL_CPU_AND_ACTUAL_CLOSURE_VERIFIED.json','FINAL878_LITERAL_TENSOR_BYTES_AND_OPTIMIZER_TREE_THREE_RANK_CPU_SUPPLEMENT.json'):assert json.loads((R/n).read_bytes())['passed']
 src=(D/'append_current_throughput_snapshot_ordinary_once.py').read_text(encoding='utf8')
 src=src.replace("BASE='5e9c0ca47bf4a34ffbd5e2912e6b3385deecafe5'",'BASE='+repr(BASE))
 src=src.replace("/'shared_PPO_throughput_live_question_actual_ordinary_v1'","/'final878_three_full_CPU_literal_bytes_exit_cost_closed_ordinary_v1'")
 src=src.replace("/'real_shared_update1_three_full_models_CPU_and_active_7h_ordinary_v1/REPORT_CAPTURE_INDEX.json'","/'clock_corrected_same_control_rank_phase_question_ordinary_v1/REPORT_CAPTURE_INDEX.json'")
 src=src.replace('MONITOR_FIRST_REAL_THREE_GPU_SHARED_PPO_UPDATE1_CPU_VERIFIED_SEVEN_HOUR_ACTIVE_20261016.txt','MONITOR_WORLD3_FINAL878_CPU_LITERAL_VERIFIED_COST_EXIT_CLOSED_RETENTION_PENDING_20261016.txt')
 src=src.replace('Append current shared-PPO throughput snapshot, installed logger units and wall-rate distinction','Append final878 three-rank full-model CPU bytes, natural exits, unique cost and retention work order')
 src=src.replace('current_live_throughput_snapshot_timer_vs_wall_distinction=True','same_original_run_final878_CPU_literal_bytes_cost_exit_closed_retention_pending=True')
 src=src.replace("if __name__=='__main__':","if __name__=='__unused__':")
 scope={'__file__':str(D/'append_current_throughput_snapshot_ordinary_once.py'),'__name__':'final_append_once_implementation'}
 exec(compile(src,str(Path(__file__)),'exec'),scope);scope['main']()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FINAL878_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_objects_no_duplicate_record_tag_commit_or_runtime=True),f,indent=2)
  raise
