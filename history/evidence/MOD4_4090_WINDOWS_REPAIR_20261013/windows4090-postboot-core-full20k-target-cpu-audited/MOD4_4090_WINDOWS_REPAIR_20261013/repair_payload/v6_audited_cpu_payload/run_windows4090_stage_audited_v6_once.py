"""New unique parent entry; original V5 bytes plus exact V6 source/receipt guards."""
import ast
from v6_closed_source_wrapper import run_closed
def transform(tree):
 renamed=0;manifest_bound=0;prereq=0;exit_reason=0
 for n in ast.walk(tree):
  if isinstance(n,ast.Constant) and n.value=='windows4090_repair_worker.py':n.value='windows4090_repair_worker_audited_v6.py';renamed+=1
 main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 for i,n in enumerate(main.body):
  if isinstance(n,ast.Assert) and ast.unparse(n.test).startswith("manifest['approved_for_new_Windows4090_scope']"):
   main.body[i+1:i+1]=ast.parse("assert manifest['max_formal_updates']==256 and manifest['substep_readback_V6']['profile']=='windows4090_actual_substep_readback_bounded_v6'\nassert H(P/'windows4090_substep_readback_v6.py')==manifest['substep_readback_V6']['source_sha256']").body;manifest_bound+=1;break
 for n in ast.walk(tree):
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='contract' for t in n.targets):
   for parent in ast.walk(tree):
    for field,value in ast.iter_fields(parent):
     if isinstance(value,list) and n in value:
      i=value.index(n);check=ast.parse("substep=contract['actual_substep_readback_V6']\nassert substep['passed'] and substep['all_env_every_substep_checked'] and substep['contact_integral_mean_error_N']<=.1 and substep['COM_world_formula_max_error_m']<1e-5 and substep['COM_link_point_velocity_max_error_m_s']<=.001 and substep['motor_torque_speed_bounds_exact']\nassert substep['actual_physical_callbacks']==substep['actual_controls']*4").body
      value[i+1:i+1]=check;prereq+=1;break
    else:continue
    break
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='atomic' and n.args and ast.unparse(n.args[0])=="A / 'EXIT_RECEIPT.json'":
   value=n.args[1]
   if isinstance(value,ast.Call) and any(k.arg=='expected_complete_receipt' for k in value.keywords):
    value.keywords.extend([ast.keyword(arg='actual_worker_stop_reason',value=ast.parse("receipt.get('stop_reason') if receipt else None",mode='eval').body),ast.keyword(arg='max_formal_updates',value=ast.Constant(256))]);exit_reason+=1
 assert renamed==2 and manifest_bound==1 and prereq==1 and exit_reason==1,'Unexpected original parent layout'
 return tree
if __name__=='__main__':run_closed('run_windows4090_stage_once.py',globals(),transform)
