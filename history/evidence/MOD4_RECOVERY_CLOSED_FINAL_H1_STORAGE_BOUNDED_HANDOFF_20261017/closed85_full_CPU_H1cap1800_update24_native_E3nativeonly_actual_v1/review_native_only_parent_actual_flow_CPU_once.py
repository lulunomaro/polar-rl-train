"""Exercise the real native-only parent with mock worker/CPU/lock, never CUDA or remote state."""
from pathlib import Path
import sys,types,io,json,time,tempfile,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def main():
 sys.modules['fcntl']=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=lambda *a:None)
 import three_slot_common_v1 as b
 import three_slot_resource_v1 as resource
 sp=importlib.util.spec_from_file_location('native_only_parent_actual_source_CPU',B/'recovery_source85_native_only_finite_parent_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 class Worker:
  pid=12345
  def __init__(self,rc):self.returncode=rc
  def poll(self):return self.returncode
  def wait(self):return self.returncode
 resource.acquire=lambda *x:io.StringIO('mock lock');b.validate_payload=lambda s:None;b.ident=lambda pid:dict(pid=pid,mock_identity=True)
 results=[]
 for mode in ('pass','GPU_exit1','CPU_false'):
  tmp=Path(tempfile.mkdtemp(prefix='mod4_nativeonly_'+mode+'_CPU_'));m.B=tmp;b.B=tmp;b.J=tmp/'job0';b.J.mkdir();b.spawn=lambda *x:Worker(1 if mode=='GPU_exit1' else 0);b.state=lambda s,phase,p:dict(returncode=p.returncode,final=dict(passed=p.returncode==0),errors=[]);b.native_CPU=lambda s:dict(actual_CPU_waited_EXIT0=True,value=dict(passed=mode!='CPU_false',source_SHA=s['source_SHA']))
  rejected=False
  try:m.run(dict(key='recovery',role='native_only',source_SHA='fixture-source'))
  except RuntimeError:rejected=True
  exitrow=b.read(tmp/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json');assert exitrow['all_actual_own_GPU_children_waited'] and exitrow['private_GPU_fcntl_released_if_acquired'] and exitrow['no_PPO_or_canonical_or_production_GO'];assert exitrow['passed_native_CPU']==(mode=='pass') and rejected==(mode!='pass')
  results.append(dict(case=mode,actual_parent_flow_expected_result=True,fixture=str(tmp),exit=exitrow))
 out=dict(epoch=time.time(),passed_actual_parent_flow_CPU=True,one_positive_two_negative_GPU_CPU_cases=results,all_children_waited_and_own_lock_released_on_pass_or_reject=True,no_production_spawn_GO_or_budget_path_in_parent=True,mock_worker_CPU_fcntl_only_no_GPU_SDK_remote_or_original_canonical=True)
 with (R/'RECOVERY_NATIVE_ONLY_PARENT_REAL_FLOW_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(passed_CPU=True,cases=3,no_real_GPU_or_original_canonical=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NATIVE_ONLY_PARENT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True),f,indent=2)
  raise
