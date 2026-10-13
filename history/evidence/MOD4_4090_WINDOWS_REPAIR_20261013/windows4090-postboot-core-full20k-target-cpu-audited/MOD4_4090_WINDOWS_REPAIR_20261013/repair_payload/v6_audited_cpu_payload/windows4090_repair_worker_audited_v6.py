"""Independent V6 entry; exact V5 worker plus only new readback facade hooks."""
import ast
from v6_closed_source_wrapper import run_closed
def transform(tree):
 imports=0;boundary=0
 for n in ast.walk(tree):
  if isinstance(n,ast.ImportFrom) and n.module=='windows4090_training_runtime':n.module='windows4090_training_runtime_audited_v6';imports+=1
  elif isinstance(n,ast.ImportFrom) and n.module=='windows4090_probe_contract':
   n.module='windows4090_probe_contract_audited_v6';n.names.append(ast.alias(name='audit_control_window_boundary'));imports+=1
 # The probe's health/checkpoint phase ends before SDK selectedreset+forward+
 # scene.update. That existing cache update is separately observed and excluded
 # from actual1200 physics callbacks, never counted as reset/route progress.
 for n in ast.walk(tree):
  if isinstance(n,ast.Assert) and ast.unparse(n.test)=='learning_health_pass(report)':
   for parent in ast.walk(tree):
    for field,value in ast.iter_fields(parent):
     if isinstance(value,list) and n in value:
      i=value.index(n);call=ast.parse('audit_control_window_boundary(env,warm+timed,args.mode,O)').body[0]
      value.insert(i+1,call);boundary+=1;break
    else:continue
    break
 assert imports==3 and boundary==1,'Unexpected original worker layout'
 return tree
if __name__=='__main__':run_closed('windows4090_repair_worker.py',globals(),transform)
