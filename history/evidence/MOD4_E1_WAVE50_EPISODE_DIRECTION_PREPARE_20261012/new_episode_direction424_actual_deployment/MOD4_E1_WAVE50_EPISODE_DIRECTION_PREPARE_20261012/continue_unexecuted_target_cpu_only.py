"""Root/upload completed; duplicate immutable local job receipt rejected before CPU."""
from wave_direction_io import *
import textwrap
def main():
 save('TARGET_CPU_CONTINUATION_REQUESTED.json',dict(epoch=time.time(),root_and_upload_completed=True,original_duplicate_local_job_receipt_rejection_retained=True,no_stage_upload_GPU_replay=True))
 s=(D/'stage_direction_target_cpu_once.py').read_text();start=s.index('  result=run(n,');end=s.index('  save(\'DIRECTION_TARGET_CPU_PASSED.json\'',start)
 code=textwrap.dedent(s[start:end]);n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   frozen=json.loads(f.open(ROOT+'/reports/SOURCE_FREEZE.json','rb').read());local=json.loads((R/'SOURCE_FREEZE.json').read_bytes());assert frozen==local
  ns=dict(globals(),n=n,w=w);exec(compile(code,'<only-unexecuted-targetCPU>','exec'),ns);result=ns['result']
  save('DIRECTION_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(root=ROOT,source_count=result['source_count'],target_CPU_passed=True,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGET_CPU_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
