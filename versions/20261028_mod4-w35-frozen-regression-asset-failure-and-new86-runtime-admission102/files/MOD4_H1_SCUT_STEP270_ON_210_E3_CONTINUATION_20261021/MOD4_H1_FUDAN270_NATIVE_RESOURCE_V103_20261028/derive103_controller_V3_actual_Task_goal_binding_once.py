from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent
p=N/'derive103_signed_goal_conditioning_controller_V2_and_actual_GO_CPU_once.py';s=p.read_text('utf8')
s=s.replace("B=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V2'","B=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V3'")
needle=" prepared=json.loads((N/'reports/TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json').read_bytes())\n";assert s.count(needle)==1
s=s.replace(needle,needle+" for item in prepared['payloads'].values():public['experts'][item['logical_slot']]['goal_conditioning']=copy.deepcopy(item['task']['goal_conditioning'])\n")
s=s.replace("put(B/'reports/CONTROLLER103_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',","put(B/('reports/CONTROLLER103_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),")
s=s.replace('FROZEN_UNUSED_TWO103_FUDAN270_CONTROLLER_INDEX_V2.json','FROZEN_UNUSED_TWO103_FUDAN270_CONTROLLER_INDEX_V3.json')
ast.parse(s)
with (N/'derive103_signed_goal_conditioning_controller_V3_and_actual_GO_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/CONTROLLER103_V2_ORIGINAL_KEY_AND_ERROR_READER_FAILURE_RETAINED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_errors=["KeyError: goal_conditioning in old controller spec; actual task contains the typed encoding", "error reporter itself TypeError: WindowsPath + str"],original_tool_exit1=True,original_V2_partial_retained_unused=True,repair='bind goal_conditioning from exact actual admitted Task, parenthesize error filename, new unused controller V3',no_remote_GPU_model_or_GO=True),f,indent=2)
