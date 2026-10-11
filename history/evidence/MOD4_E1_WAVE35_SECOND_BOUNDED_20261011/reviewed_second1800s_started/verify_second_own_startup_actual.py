from second_io import *
import ast
tree=ast.parse((PRIOR/'verify_wave_own_startup_save_cpu_actual.py').read_text(encoding='utf8'))
code=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('from pathlib import Path\nimport sys,json,time,torch,hashlib'))
code=code.replace('import supervise_wave35_exposure_005_once as own','import supervise_wave35_second_bounded_once as own').replace('source_count=368','source_count=369')
code=code.replace("health=j(run/'CLOCK_TRAINING_HEALTH.json')","health=j(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None")
code=code.replace("assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and own.m.learning_health_pass(health)","if health:assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and own.m.learning_health_pass(health)")
needle="assert h(own.source())==own.SOURCE_SHA"
assert code.count(needle)==1
code=code.replace(needle,needle+"\ntrace=j(run/'RETENTION_COMMAND_ACTUAL.json');controls=trace['actual_controls'];saved=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(own.source(),map_location='cpu',weights_only=False)\nchanged=sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in saved['actor_state_dict'].items());assert changed>0\ndeltas=[int(v['step'].item())-int(source['optimizer_state_dict']['state'][k]['step'].item()) for k,v in saved['optimizer_state_dict']['state'].items()];assert deltas and min(deltas)>0 and len(set(deltas))==1 and deltas[0]%20==0\nupdates=deltas[0]//20;assert controls>=24*updates and controls>0")
code=code.replace("actual_PPO_controls=health['control_steps'],actual_updates_observed=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,","actual_PPO_controls=controls,actual_updates_observed=updates,actual_environment_steps=controls*20000,actor_changed_tensor_count=changed,optimizer_step_delta=deltas[0],health_pending=health is None,")
def main():
 n,w=io.connect_both()
 try:
  v=run(n,code.replace('ROOT_TOKEN',repr(ROOT)));p=save('SECOND_OWN_STARTUP_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=True,updates=v['actual_updates_observed'],controls=v['actual_PPO_controls'],actor_changed_tensors=v['actor_changed_tensor_count'],own_child=v['own_child'],health_pending=v['health_pending'],formal_final=False)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_STARTUP_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_replay=True));raise
