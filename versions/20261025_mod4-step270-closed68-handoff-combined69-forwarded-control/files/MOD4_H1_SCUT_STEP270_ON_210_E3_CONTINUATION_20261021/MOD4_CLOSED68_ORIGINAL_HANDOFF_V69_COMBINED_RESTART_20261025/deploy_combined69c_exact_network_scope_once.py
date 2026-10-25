"""New unused69b roots after pre-GO69 import-path error. Exact invocation fix, same guards."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V3_RESOURCE_V69_20261025'
try:
 proof=json.loads((R/'PINNED72_TO_OWNER_CONTROL_CHANNEL_CPU_RETURNED_ACTUAL.json').read_bytes());assert proof['passed'] and proof['actual_finite_returned']
 assert json.loads((R/'NEXT69C_EXACT_NETWORK_ADMISSION_EXTENSION_CPU_ACTUAL.json').read_bytes())['passed']
 assert not(N/'reports/PAIR_DEPLOY_STARTED_ACTUAL.json').exists()
 source=N/'deploy_selected_pair_unused_once.py';sp=importlib.util.spec_from_file_location('combined69b_deployer',source);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 m.d.t.connect=route.connect;original_code=m.d.code
 expected="import runpy,sys;sys.argv=['target_two50_source_sdk_cpu_review.py',v['root']];runpy.run_path(v['root']+'/target_two50_source_sdk_cpu_review.py',run_name='__main__')"
 def code(c,py,source,args,timeout=90):
  if source==expected:
   assert args['root'].endswith('/H1step270_sampling_opt1_sagtuck6a_2510v69c/recovery')
   source=source.replace('import runpy,sys;','import runpy,sys;sys.path.insert(0,v[\'root\']);',1)
  return original_code(c,py,source,args,timeout=timeout)
 m.d.code=code
 m.main()
except BaseException:
 with (R/'COMBINED69C_EXACT_NETWORK_SCOPE_DEPLOY_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_root_or_refund=True),f,indent=2)
 raise
