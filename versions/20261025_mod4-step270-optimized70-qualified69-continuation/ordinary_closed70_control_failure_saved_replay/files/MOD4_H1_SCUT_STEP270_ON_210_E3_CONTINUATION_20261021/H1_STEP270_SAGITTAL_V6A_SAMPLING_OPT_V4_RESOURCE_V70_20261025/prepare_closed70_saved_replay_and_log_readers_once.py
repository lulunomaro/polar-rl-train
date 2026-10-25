"""New closed70 data only; preserve consumed69 helpers without execution or mutation."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;D=T/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025'
U=T/'H1_STEP270_CLOSED70_SAVED_REPLAY_AFTER_V6A_20261025';U.mkdir();(U/'reports').mkdir()
old=T/'H1_STEP270_CLOSED69D_SAVED_REPLAY_AFTER_COMBINED_20261025'
for source,target in [('extract_closed69d_last_two_saved_prefixes_CPU_unused_once.py','extract_closed70_last_two_saved_prefixes_CPU_unused_once.py'),('reconstruct_closed69d_saved_motion_USD_CPU_unused_once.py','reconstruct_closed70_saved_motion_USD_CPU_unused_once.py'),('analyze_render_closed69d_saved_step_timing_CPU_unused_once.py','analyze_render_closed70_saved_step_timing_CPU_unused_once.py')]:
 text=(old/source).read_text('utf8').replace('V4_RESOURCE_V69_20261025','V4_RESOURCE_V70_20261025').replace('2510v69d','2510v70').replace('CLOSED69D','CLOSED70').replace('Closed69d','Closed70').replace('closed69d','closed70').replace('Unused69d','Unused70')
 ast.parse(text)
 with (U/target).open('x',encoding='utf8') as f:f.write(text)
text=(D/'read_closed69d_saved_text_throughput_and_health_once.py').read_text('utf8')
text=text.replace("D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'","N=Path(__file__).resolve().parent;T=N.parent;D=T/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025';R=N/'reports'")
text=text.replace('from closed_window_throughput_text_cpu_reader_v1 import read_worker_log',"import sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025'))\nfrom closed_window_throughput_text_cpu_reader_v1 import read_worker_log")
text=text.replace("R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json'","D/'reports/CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json'")
text=text.replace('closed69d','closed70').replace('CLOSED69D','CLOSED70').replace('current69','current70')
ast.parse(text)
with (N/'read_closed70_saved_text_throughput_and_health_once.py').open('x',encoding='utf8') as f:f.write(text)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';text=(B/'same_authorized_session_compressed_transport_v101.py').read_text('utf8');needle="        'collect_current70_finals_original_cost_unused_once.py',";assert text.count(needle)==1
text=text.replace(needle,needle+"\n        'extract_closed70_last_two_saved_prefixes_CPU_unused_once.py',",1)
with (B/'same_authorized_session_compressed_transport_v102.py').open('x',encoding='utf8') as f:f.write(text)
with (N/'reports/NEW_CLOSED70_READERS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),new70_saved_data_scope_only=True,old69_helpers_read_as_source_only_not_reexecuted=True,source_models_CPU_closed=True,no_new_GPU_policy_or_physics=True),f,indent=2)
print(json.dumps(dict(prepared=True,new_replay_namespace=str(U),no_old_data_reader_rerun=True)))
