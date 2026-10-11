"""Select the original unexecuted CPU statement by AST, preserving reader indentation error."""
from wave_direction_io import *
import ast
def main():
 save('TARGET_CPU_AST_CONTINUATION_REQUESTED.json',dict(epoch=time.time(),only_unexecuted_targetCPU=True,original_indentation_reader_error_retained=True,no_root_upload_GPU_replay=True))
 s=(D/'stage_direction_target_cpu_once.py').read_text();tree=ast.parse(s)
 node=next(x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='result' for t in x.targets))
 code=ast.get_source_segment(s,node);compile(code,'cpu-only-statement','exec');n,w=io.connect_both()
 try:
  with n.open_sftp() as f:assert json.loads(f.open(ROOT+'/reports/SOURCE_FREEZE.json','rb').read())==json.loads((R/'SOURCE_FREEZE.json').read_bytes())
  ns=dict(globals(),n=n,w=w);exec(compile(code,'<unexecutedCPU-AST>','exec'),ns);v=ns['result'];save('DIRECTION_TARGET_CPU_PASSED.json',v)
  print(json.dumps(dict(root=ROOT,source_count=v['source_count'],target_CPU_passed=True,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGET_CPU_AST_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
