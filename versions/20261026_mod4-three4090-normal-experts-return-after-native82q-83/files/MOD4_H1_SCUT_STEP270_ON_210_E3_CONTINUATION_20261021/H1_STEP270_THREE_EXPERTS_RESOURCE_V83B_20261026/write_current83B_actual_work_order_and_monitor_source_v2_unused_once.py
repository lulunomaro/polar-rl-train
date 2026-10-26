from pathlib import Path
import json,time,traceback
N=Path(__file__).resolve().parent;original=N/'write_current83B_actual_work_order_and_monitor_source_unused_once.py';text=original.read_text('utf8')
try:compile(text,str(original),'exec')
except SyntaxError:
 with (N/'reports/LOCAL_MONITOR_WRITER_V1_NUMERIC_KEYWORD_SYNTAX_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),original_source_retained=True,no_files_or_training_change_before_parse=True),f,indent=2)
else:raise AssertionError('Expected original parse rejection missing')
assert text.count(',83_preGO_')==1 and text.count(',83B_new_namespace_')==1
text=text.replace(',83_preGO_',',original83_preGO_',1).replace(',83B_new_namespace_',',actual83B_new_namespace_',1)
fixed=N/'write_current83B_monitor_source_v2_exact_generated.py'
with fixed.open('x',encoding='utf8') as f:f.write(text)
exec(compile(text,str(fixed),'exec'),dict(__name__='__main__',__file__=str(fixed)))
