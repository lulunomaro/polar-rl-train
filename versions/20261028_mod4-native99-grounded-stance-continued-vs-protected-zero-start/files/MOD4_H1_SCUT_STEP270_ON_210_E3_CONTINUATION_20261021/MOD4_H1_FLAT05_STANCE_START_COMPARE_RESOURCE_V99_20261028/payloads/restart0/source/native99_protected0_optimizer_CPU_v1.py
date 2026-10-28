from native88_installed_cpu_helpers_v1 import validate_native_optimizer as old_validate
def validate(module,state,betas):
 from native99_stance_pins_v1 import SOURCE_MODE
 assert SOURCE_MODE=='restart0' and state['state']=={} and len(state['param_groups'])==1
 g=state['param_groups'][0];assert tuple(g['betas'])==tuple(betas) and g['params']==list(range(len(list(module.parameters()))))
 return dict(min_step=0,max_step=0,initial_empty_native_optimizer=True,parameter_count=len(list(module.parameters())))
