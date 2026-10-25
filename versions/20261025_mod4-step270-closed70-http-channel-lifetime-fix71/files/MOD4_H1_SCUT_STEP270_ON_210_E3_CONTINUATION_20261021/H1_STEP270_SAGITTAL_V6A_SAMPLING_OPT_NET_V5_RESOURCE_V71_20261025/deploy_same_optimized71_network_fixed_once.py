"""One new70 namespace, qualified closed69 models, unchanged guards/controllers and route."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
try:
 assert json.loads((R/'NETWORK71_EXACT_SOURCE_AST_CPU_ACTUAL.json').read_bytes())['passed']
 assert not (R/'PAIR_DEPLOY_STARTED_ACTUAL.json').exists()
 p=N/'deploy_selected_pair_unused_once.py';sp=importlib.util.spec_from_file_location('same_optimized71_deployer',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 m.d.t.connect=route.connect;original=m.d.code
 expected="import runpy,sys;sys.argv=['target_two50_source_sdk_cpu_review.py',v['root']];runpy.run_path(v['root']+'/target_two50_source_sdk_cpu_review.py',run_name='__main__')"
 def code(c,py,source,args,timeout=90):
  if source==expected:
   assert args['root'].endswith('/H1step270_sampling_opt1_sagtuck6a_net2_2510v71/recovery')
   source=source.replace('import runpy,sys;','import runpy,sys;sys.path.insert(0,v[\'root\']);',1)
  return original(c,py,source,args,timeout=timeout)
 m.d.code=code;m.main()
except BaseException:
 with (R/'SAME_OPTIMIZED71_FORWARD_ROUTE_DEPLOY_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_root_or_refund=True),f,indent=2)
 raise
