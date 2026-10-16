"""Durable human preference only; existing trial ordinary append, no new runtime."""
from pathlib import Path
import json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 assert (R/'HUMAN_THREE4090_UTILIZATION_LONG_TERM_PREFERENCE_AND_SCOPE_ACTUAL.json').exists();src=(D/'archive_V2_postcapture_native_actual_monitor_readers_ordinary_v1_once.py').read_text('utf8');src=src.replace("BASE='b5ff9c40959f021511a61e3f31e5ef3526e77bb1'","BASE='b55b667e67889b5241ec5328a18b523402fd0123'")
 src=src.replace("/'grounded_reward_V2_source_target_CPU_native_started_actual_v1/REPORT_CAPTURE_INDEX.json'","/'human_three_GPU_current_tasks_readonly1718_append_v2/REPORT_CAPTURE_INDEX.json'").replace("/'postcapture_native_actual_readers_monitor_append_v1'","/'human_maximum_three4090_utilization_preference_AGENTS_append_v3'")
 src=src.replace("and not git('status','--porcelain')","and git('status','--porcelain').strip()=='M AGENTS.md'").replace("('71f1e3142d83a5a6003e8573a210de6deaa0aad0',BASE)","('71f1e3142d83a5a6003e8573a210de6deaa0aad0','b5ff9c40959f021511a61e3f31e5ef3526e77bb1')")
 src=src.replace("git('add','--',*files);","files.append('AGENTS.md');git('add','--',*files);").replace('Archive H1 grounded V2 actual admission reader and monitor continuation','Persist human three4090 utilization scheduling preference and original monitor rules').replace('V2_POSTCAPTURE_ORDINARY_APPEND_ORIGINAL_ERROR_','HUMAN_UTILIZATION_PREFERENCE_ORDINARY_APPEND_ORIGINAL_ERROR_');ns=dict(__name__='human_utilization_preference_ordinary_pure',__file__=str(D/'archive_human_utilization_preference_derived_v3.py'));exec(compile(src,ns['__file__'],'exec'),ns);ns['main']()
if __name__=='__main__':
 try:main()
 except BaseException:(R/('HUMAN_UTILIZATION_PREFERENCE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_HEAD_existing_objects_only_no_repeat_commit_tag=True),indent=2),encoding='utf8');raise
