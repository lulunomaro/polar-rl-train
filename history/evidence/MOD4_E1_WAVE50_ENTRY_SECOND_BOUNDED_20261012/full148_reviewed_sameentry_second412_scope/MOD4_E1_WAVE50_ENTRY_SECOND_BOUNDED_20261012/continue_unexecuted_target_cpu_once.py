"""Continue only CPU not yet executed after local duplicate-unused receipt refusal."""
from entry_second_io import *
def main():
 assert not (R/'ENTRY_SECOND_TARGET_CPU_PASSED.json').exists()
 text=(D/'stage_entry_second_and_cpu_once.py').read_text()
 code=text.split("result=run(n,r'''",1)[1].split("'''.replace('ROOT_TOKEN'",1)[0].replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(SOURCE_SHA))
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   frozen=json.loads(f.open(ROOT+'/reports/SOURCE_FREEZE.json','rb').read());assert frozen==json.loads((R/'SOURCE_FREEZE.json').read_bytes())
   unused=json.loads(f.open(ROOT+'/reports/CANDIDATE_JOB_UNUSED_ACTUAL.json','rb').read());assert unused==json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())
   assert 'ENTRY_SECOND_TARGET_CPU_PASSED.json' not in f.listdir(ROOT+'/reports') and 'E1_DISPATCH_STARTED.json' not in f.listdir(ROOT+'/reports')
  result=run(n,code);save('ENTRY_SECOND_TARGET_CPU_PASSED.json',result)
  print(json.dumps(dict(targetCPU_passed=True,source_count=result['source_count'],no_stage_GPU_replay=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('UNEXECUTED_CPU_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
