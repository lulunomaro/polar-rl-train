"""Retain the original failed generator and fix only its outer literal delimiter."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';p=B/'prepare_fifteenth_handoff_builder_CPU_once.py';raw=p.read_bytes();source=p.read_text('utf8')
try:ast.parse(source,filename=str(p))
except SyntaxError as e:original=dict(type=type(e).__name__,message=e.msg,lineno=e.lineno,offset=e.offset,source_line=e.text,traceback=traceback.format_exc())
else:raise AssertionError('Expected the original recorded literal-delimiter SyntaxError')
assert source.count("tail=r'''")==1 and source.count("\n'''\ns+=tail;")==1
source=source.replace("tail=r'''",'tail=r"""').replace("\n'''\ns+=tail;",'\n"""\ns+=tail;')
ast.parse(source);q=B/'prepare_fifteenth_handoff_builder_V2_CPU_once.py'
with q.open('x',encoding='utf8',newline='\n') as stream:stream.write(source)
with (R/'HANDOFF_BUILDER_ORIGINAL_ERROR_AND_QUOTE_FIX_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:
 json.dump(dict(epoch=time.time(),original_generator=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),actual_initial_exitcode=1,consumed_not_reexecuted=True),original_parse_error=original,cause='Outer raw triple-single-quoted generated-program literal collided with its inner triple-single-quoted f-string. Parsing failed before any generator body executed.',fixed_generator=dict(path=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),AST_parsed=True,only_outer_literal_delimiter_changed=True),local_reader_generator_error_not_GPU_or_transport_failure=True,no_remote_GPU_Task_native_case_or_account_replay=True),stream,indent=2)
print(json.dumps(dict(V2_prepared=str(q),original_failure_and_source_retained=True)))
