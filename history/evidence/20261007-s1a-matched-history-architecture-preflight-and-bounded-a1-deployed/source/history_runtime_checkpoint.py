"""Full candidate optimizers, global/independent RNG and history; fresh physical episodes on load."""
import random
import numpy as np
import torch

def named_generators(env):
    owners={'env':env}
    for manager in ('command_manager','event_manager'):
        obj=getattr(env,manager,None)
        if obj is not None:
            owners[manager]=obj
            for name,term in getattr(obj,'_terms',{}).items():owners[manager+'.'+name]=term
    found={}
    def inspect(prefix,value,depth):
        if isinstance(value,torch.Generator):found[prefix]=value
        elif depth and isinstance(value,dict):
            for key,item in value.items():inspect(prefix+'.'+str(key),item,depth-1)
    for prefix,owner in owners.items():
        for name,value in vars(owner).items():inspect(prefix+'.'+name,value,2)
    return found

def attach_runtime_save(runner,vec):
    original=runner.alg.save
    def save():
        state=original()
        state['rng_state']=dict(python=random.getstate(),numpy=np.random.get_state(),torch_cpu=torch.random.get_rng_state(),
          torch_cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else [])
        state['independent_generator_state']={name:g.get_state() for name,g in named_generators(vec.env).items()}
        state['feedback_history_state']=vec.history_state_dict()
        state['history_resume_semantics']='Models/optimizers/RNG saved. Simulator begins fresh reset episodes; history is cleared. No PhysX exact-state resume claimed.'
        state['common_step_counter']=int(vec.env.common_step_counter)
        return state
    runner.alg.save=save

def restore_rng(state):
    random.setstate(state['python']);np.random.set_state(state['numpy']);torch.random.set_rng_state(state['torch_cpu'].cpu())
    if state['torch_cuda']:
        if not torch.cuda.is_initialized():raise ValueError('CUDA RNG requires actual initialized device')
        torch.cuda.set_rng_state_all(state['torch_cuda'])

def restore_independent_rng(state,env):
    actual=named_generators(env)
    if set(actual)!=set(state):raise ValueError('Independent generator registry mismatch')
    for name,value in state.items():actual[name].set_state(value.cpu())
