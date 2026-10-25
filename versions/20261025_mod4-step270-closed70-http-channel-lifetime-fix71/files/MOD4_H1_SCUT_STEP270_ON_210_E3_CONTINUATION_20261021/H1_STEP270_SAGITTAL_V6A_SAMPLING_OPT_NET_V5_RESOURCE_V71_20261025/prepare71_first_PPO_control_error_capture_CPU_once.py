"""Single unused firstPPO reader adds exact own control-error evidence, no second watcher."""
from pathlib import Path
import ast,json,shutil,time
N=Path(__file__).resolve().parent;R=N/'reports'
assert not (R/'PAIR_FIRST_METADATA_STARTED_ACTUAL.json').exists()
old=N/'collect_selected_pair_first_PPO_unused_once.py';text=old.read_text('utf8')
needle="print(json.dumps(dict(epoch=time.time(),node=node,worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()),";assert text.count(needle)==1
text=text.replace(needle,"control_errors=[dict(path=str(x),value=json.loads(x.read_bytes())) for x in sorted(B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'))]\n"+needle,1)
needle="source_CPU=v['row']['closed_source_CPU'],latest_save=v['row']['latest_save'],not_continuous_alive_or_future_FINAL=True)))";assert text.count(needle)==1
text=text.replace(needle,"source_CPU=v['row']['closed_source_CPU'],latest_save=v['row']['latest_save'],control_original_errors=control_errors,control_error_count=len(control_errors),not_continuous_alive_or_future_FINAL=True)))",1)
new=N/'collect_selected71_pair_first_PPO_and_own_control_errors_unused_once.py';ast.parse(text)
with new.open('x',encoding='utf8') as f:f.write(text)
wrapper=N/'collect71_first_PPO_pinned_route_once.py';shutil.copy2(wrapper,N/'PRE_EXECUTION_71_FIRST_PPO_WRAPPER_BASE.py')
s=wrapper.read_text('utf8');needle="N/'collect_selected_pair_first_PPO_unused_once.py'";assert s.count(needle)==1;s=s.replace(needle,"N/'collect_selected71_pair_first_PPO_and_own_control_errors_unused_once.py'",1);wrapper.write_text(s,encoding='utf8')
with (R/'FIRST71_PPO_CONTROL_ERROR_SCOPE_ADDED_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),only_extra_read='New71 own NODE_CONTROL_ORIGINAL_ERROR files at existing single firstPPO snapshot; no repeat oldmetadata or peer identity',same_original_bounded_GO_PPO_UUID_process_checks=True,old_unused_reader_and_wrapper_bytes_preserved=True,no_runtime_controller_or_budget_change=True,preparation_nonfatal_warnings=[r'<unknown>:11: SyntaxWarning: "\S" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\S"? A raw string is also an option.']*2,warning_original_source_location_not_captured=True),f,indent=2)
print(json.dumps(dict(prepared=True,single_firstPPO_reader_only=True,no_remote_query_yet=True)))
