"""Complete architecture/RNG/history serialization; physical simulator state is not resumed."""
import random
import numpy as np
import torch

def attach_runtime_save(runner,vec):
    original=runner.alg.save
    def save():
        state=original()
        state['rng_state']=dict(python=random.getstate(),numpy=np.random.get_state(),torch_cpu=torch.random.get_rng_state(),
          torch_cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else [])
        state['feedback_history_state']=vec.history_state_dict()
        state['history_resume_semantics']='Serialized for audit/roundtrip. Fresh simulated episodes clear all history; no cross-episode replay or claim of PhysX exact-state resume.'
        state['common_step_counter']=int(vec.env.common_step_counter)
        return state
    runner.alg.save=save

def restore_rng(state):
    random.setstate(state['python']);np.random.set_state(state['numpy']);torch.random.set_rng_state(state['torch_cpu'].cpu())
    if state['torch_cuda']:
        if not torch.cuda.is_initialized():raise ValueError('Saved CUDA RNG requires an actual initialized device')
        torch.cuda.set_rng_state_all(state['torch_cuda'])
