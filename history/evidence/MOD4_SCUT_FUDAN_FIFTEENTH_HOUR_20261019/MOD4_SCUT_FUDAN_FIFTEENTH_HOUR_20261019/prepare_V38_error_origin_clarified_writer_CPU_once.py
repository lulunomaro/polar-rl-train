"""Keep the first prepared writer and explicitly classify the saved local generator error."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;p=B/'prepare_actual_fifteenth_three_learning_monitor_V38_once.py';s=p.read_text('utf8')
needle='仅用新51f4完整源本机CPU MuJoCo'
note='本轮本机handoff生成器首稿因嵌套三引号分隔冲突发生SyntaxError，在生成器主体执行前退出；原source/错误报告保留，独立V2仅修外层字符串分隔后CPU AST过。它没有重GPU/Task/native、改变remote/账或重跑任何行为case，不冒GPU故障或网络错误。\n'
assert s.count(needle)==1;s=s.replace(needle,note+needle)
s=s.replace('本阶段metadata原错误索引（若非空保留原件，finite实际返回后只补缺，不冒网络已修复）','本阶段原错误索引（含本机生成器错误；类别以原报告为准，不冒GPU故障/网络已修复）')
ast.parse(s);q=B/'prepare_actual_fifteenth_three_learning_monitor_V38_V2_once.py'
with q.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
with (B/'reports/V38_LOCAL_GENERATOR_ERROR_ORIGIN_CLARIFICATION_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),initial_prepared_writer_retained=str(p),initial_writer_not_executed=True,clarified_writer=str(q),actual_file_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),AST_parsed=True,local_generator_SyntaxError_not_GPU_network_or_behavior_failure=True,no_transport_GPU_Task_native_or_case_replay=True),stream,indent=2)
print(json.dumps(dict(prepared=str(q),AST_parsed=True)))
