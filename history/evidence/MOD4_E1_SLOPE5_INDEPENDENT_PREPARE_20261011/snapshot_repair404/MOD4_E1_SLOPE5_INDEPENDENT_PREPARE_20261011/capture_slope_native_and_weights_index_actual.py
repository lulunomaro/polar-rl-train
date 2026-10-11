from slope_io import *
def main():
 n,w=connect_both()
 try:
  index=linux_json(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or 'own_source_freeze' in str(p) or 'e1_source_freeze' in str(p):continue
 if p.suffix in ('.pt','.npz','.npy','.usd','.zip') or (p.parent==D and p.suffix=='.json'):
  rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),actual_original_retained=True,large_original_index_only=True))
for name in ('SLOPE_SDK10.json','SLOPE_NATIVE20K.json'):
 p=D/name;v=json.loads(p.read_bytes());rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),actual_ground_error_m=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],ordinary=v['actual_task_failed_environments'],nonfinite=v['nonfinite'],solver=v['actual_solver_readback'],callback_count=v['physical_callback_count'],health_callbacks=v['health']['actual_physics_callbacks'],conditional_command_audit=v['command_retention'],initial_and_final_full_raw_parameters_root30q_preserved_in_actual_original=True))
print(json.dumps(dict(epoch=time.time(),rows=rows,no_GPU_PPO_or_budget_write=True,actual_native_and_artifact_index=True)))
'''.replace('ROOT',repr(NEW)))
  p=save('ACTUAL_NATIVE_AND_WEIGHT_INDICES_'+str(time.time_ns())+'.json',index);print(json.dumps(dict(report=str(p),indices=len(index['rows']))))
 finally:cleanup(n,w)
if __name__=='__main__':main()
