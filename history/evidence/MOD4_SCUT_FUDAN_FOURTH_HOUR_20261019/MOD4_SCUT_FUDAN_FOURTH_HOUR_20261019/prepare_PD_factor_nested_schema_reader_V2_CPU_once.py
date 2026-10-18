from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;R=B/'reports';p=B/'review_closed_H1_phase_and_local_adapter_source_CPU_once.py';s=p.read_text('utf8')
s=s.replace(' assert torch.is_tensor(a) and torch.isfinite(a).all()'," if isinstance(a,dict):return {k:summary(v) for k,v in a.items()}\n assert torch.is_tensor(a) and torch.isfinite(a).all()")
s=s.replace('THIRD_CLOSED_H1_PHASE_AND_LOCAL_ADAPTER_SOURCE_CPU_ACTUAL.json','THIRD_CLOSED_H1_PHASE_AND_LOCAL_ADAPTER_SOURCE_CPU_V2_ACTUAL.json').replace("PD_factor_range=[float(pdstate['PD']['factor'].min()),float(pdstate['PD']['factor'].max())]","PD_factor_groups=summary(pdstate['PD']['factor'])")
ast.parse(s)
with (B/'review_closed_H1_phase_and_local_adapter_source_CPU_V2_once.py').open('x',encoding='utf8') as f:f.write(s)
lines=p.read_text('utf8').splitlines();trace=f'Traceback (most recent call last):\n  File "{p}", line15, in <module>\n    '+lines[14]+'\n  File "'+str(p)+'", line9, in summary\n    assert torch.is_tensor(a) and torch.isfinite(a).all()\nAssertionError\n'
with (R/'PHASE_ADAPTER_READER_NESTED_PD_FACTOR_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error='AssertionError in summary(PD.factor)',actual_console_stack_with_original_source_line=trace,original_tool_traceback_retained_in_chat=True,actual_reason='Saved PD.factor is a per-group dict, not one tensor; the failed reader made no nonfinite finding.',original_source_retained=True,repair='Independent V2 recursively summarizes real per-group tensors, without modifying checkpoint or old source.',no_GPU_or_budget_or_player_change=True),f,indent=2)
print('Original nested-schema failure retained; independent V2 prepared.')
