"""Original runtime byte-preserved; only probe audit imports and safety cap added."""
import ast
from v6_closed_source_wrapper import run_closed
def transform(tree):
 imports=0;bound=0;stop=0;reason=0;saves=0
 for n in ast.walk(tree):
  if isinstance(n,ast.ImportFrom) and n.module=='windows4090_probe_contract':n.module='windows4090_probe_contract_audited_v6';imports+=1
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name=='restore_and_run':
   block=ast.parse("max_formal_updates=json.loads(Path(args.manifest).read_bytes())['max_formal_updates']\nassert type(max_formal_updates) is int and max_formal_updates==256, 'Root approved finite save/trace resource bound'").body
   n.body[1:1]=block;bound+=1
   for i,node in enumerate(n.body):
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in node.targets):
     block=ast.parse("assert int(source['iter'])>0\nrunner.cfg['save_interval']=int(source['iter'])+max_formal_updates+1\nwrite('WINDOWS4090_SAVE2_RESOURCE_BOUND_ACTUAL.json',dict(max_formal_updates=max_formal_updates,legacy_automatic_save_interval_disabled_with_absolute_iteration_bound=True,runner_save_interval=runner.cfg['save_interval'],manual_fullsave_every2_updates=True,maximum_periodic_plus_final_files=129,source_iteration=int(source['iter']),no_optimizer_order_or_physics_change=True))").body
     n.body[i+1:i+1]=block;saves+=1;break
 for n in ast.walk(tree):
  if isinstance(n,ast.If) and ast.unparse(n.test)=="time.monotonic() >= deadline or Path(args.stop_after_save).exists() or health.reason is not None":
   n.test=ast.BoolOp(op=ast.Or(),values=[n.test,ast.parse('updates>=max_formal_updates',mode='eval').body]);stop+=1
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='write' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json':
   value=n.args[1];assert isinstance(value,ast.Call)
   for k in value.keywords:
    if k.arg=='stop_reason':k.value=ast.parse("health.reason or ('resource_guard_max256_updates' if updates>=max_formal_updates else 'human_or_parent_STOP_AFTER_SAVE' if Path(args.stop_after_save).exists() else 'bounded3600s_wall_window')",mode='eval').body;reason+=1
   value.keywords.append(ast.keyword(arg='max_formal_updates',value=ast.Name(id='max_formal_updates',ctx=ast.Load())))
 assert imports==1 and bound==1 and stop==1 and reason==1 and saves==1,'Unexpected original runtime layout'
 return tree
run_closed('windows4090_training_runtime.py',globals(),transform)
