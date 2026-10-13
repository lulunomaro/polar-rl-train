"""Fresh ungranted V6 SDK draft, explicit readback source and max256 save cap."""
import ast
from v6_closed_source_wrapper import run_closed
def transform(tree):
 imported=0;names=0;added=0
 for n in ast.walk(tree):
  if isinstance(n,ast.ImportFrom) and n.module=='materialize_windows20k_target_cpu_once':n.module='materialize_windows20k_target_audited_v6_cpu_once';imported+=1
  if isinstance(n,ast.Constant) and isinstance(n.value,str):
   replacements={'windows20k_left_repair_sdk10_v1':'windows20k_left_repair_audited_v6a_sdk10_v1','windows20k_left_repair_sdk10_v[1-9][0-9]*':'windows20k_left_repair_audited_v6a_sdk10_v[1-9][0-9]*','windows4090_repair_worker.py':'windows4090_repair_worker_audited_v6.py','run_windows4090_stage_once.py':'run_windows4090_stage_audited_v6_once.py'}
   if n.value in replacements:n.value=replacements[n.value];names+=1
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in n.targets) and isinstance(n.value,ast.Call):
   n.value.keywords.extend([ast.keyword(arg='max_formal_updates',value=ast.Constant(256)),ast.keyword(arg='substep_readback_V6',value=ast.parse("dict(profile='windows4090_actual_substep_readback_bounded_v6',source_sha256=H(scope/'repair_payload/windows4090_substep_readback_v6.py'),actual_GPU_readback_pass_still_pending=True)",mode='eval').body)]);added+=1
 assert imported==1 and names==5 and added==1,'Unexpected original builder layout'
 return tree
if __name__=='__main__':run_closed('prepare_windows20k_sdk_manifest_cpu_once.py',globals(),transform)
