"""Correct local TOML snake_case reader only; preserve V1 KeyError and runtime unchanged."""
from pathlib import Path
import json,time,hashlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';p=B/'prepare_actual_target72_h1_handoff_work_order_v1_once.py';s=p.read_text('utf8')
with (R/'TARGET72_WORK_ORDER_TOML_V1_KEYERROR_PRESERVED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_source=str(p),original_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_actual_exception="KeyError: 'targetThreadId'",actual_TOML_key='target_thread_id',failure_before_any_prompt_copy_or_workorder_write=True,no_GPU_transport_runtime_or_account_effect=True),f,indent=2)
assert s.count("old['targetThreadId']")==1;s=s.replace("old['targetThreadId']","old['target_thread_id']")
ns=dict(__file__=str(p),__name__='corrected_workorder_v2_only');exec(compile(s,'corrected_TOML_schema_v2','exec'),ns)
try:ns['main']()
except BaseException:
 with (R/('TARGET72_WORK_ORDER_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),local_reader_only_no_runtime_mutation=True),f,indent=2)
 raise
