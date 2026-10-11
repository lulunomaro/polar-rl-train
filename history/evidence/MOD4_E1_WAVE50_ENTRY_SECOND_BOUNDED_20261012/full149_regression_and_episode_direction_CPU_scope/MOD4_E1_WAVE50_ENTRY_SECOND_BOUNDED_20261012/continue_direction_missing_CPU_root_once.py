"""Only unexecuted CPU upload/admission after missing independent root refusal."""
from entry_second_io import *
from admit_direction_component_cpu_actual_once import CPUROOT,latest
def main():
 assert not (R/'DIRECTION_COMPONENT_CPU_PASSED.json').exists()
 own=json.loads(latest('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json').read_bytes());trace=json.loads(latest('ENTRY_SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json').read_bytes());p=D/'direction_cpu_component/wave50_episode_direction_math.py';raw=p.read_bytes()
 text=(D/'admit_direction_component_cpu_actual_once.py').read_text();code=text.split("v=run(n,r'''",1)[1].split("'''.replace('CPUROOT_TOKEN'",1)[0]
 code=code.replace('CPUROOT_TOKEN',repr(CPUROOT)).replace('ROOT_TOKEN',repr(ROOT)).replace('INPUT_TOKEN',repr(json.dumps(dict(checkpoint=own['own_checkpoint'],trace=trace['full_saved_trace_indices'][0])))).replace('MATH_SHA_TOKEN',repr(H(raw))).replace('SOURCE35_TOKEN',repr(old.SOURCE)).replace('SOURCE35_SHA_TOKEN',repr(old.SOURCE_SHA))
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   try:f.stat(CPUROOT)
   except FileNotFoundError:pass
   else:raise AssertionError('IndependentCPUroot alreadyexists; inspectactual instead of replay')
   f.mkdir(CPUROOT);io.put(f,CPUROOT+'/'+p.name,raw)
  v=run(n,code);save('DIRECTION_COMPONENT_CPU_PASSED.json',v);print(json.dumps(dict(component_CPU_passed=True,actual_Wave2820=v['actual20k_Wave2820'],other17180_exact=True,no_new_GPU_or_learning=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_COMPONENT_CPU_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
