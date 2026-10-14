"""One actual feedback/cache for both frozen experts and gate; training label separate."""
import torch
from s4_supported_rollout_storage_v1 import DOMAIN,actual_supported_domain,bind_original35_supported_identity

class SupportedSharedFeedback:
    def __init__(self,vec,env):
        self.vec=vec;self.env=env;self.runtime=None;self.processed=None
        bind_original35_supported_identity(env)
        self.old_get=vec.get_observations;self.old_step=vec.step
        process=env.action_manager.process_action
        def capture(action):
            result=process(action);self.processed=env.action_manager.action.clone();return result
        env.action_manager.process_action=capture
        def get():return self.label(self.old_get())
        def step(action):
            assert self.runtime is not None and self.runtime.pending
            obs,reward,dones,extras=self.old_step(action)
            obs=self.label(obs)
            self.runtime.finish(self.processed,action.clamp(-6,6),dones,obs)
            return obs,reward,dones,extras
        vec.get_observations=get;vec.step=step

    def label(self,obs):
        # Clone already obtained tensors; no second observation-manager call,
        # sensor draw, physics step, reset, teacher or command write.
        result=obs.clone();result[DOMAIN]=actual_supported_domain(self.env)
        return result

    def bind(self,alg,runtime):
        self.runtime=runtime;original=alg.act
        def act(obs):
            action=original(obs);runtime.begin(obs,alg.actor.z);return action
        alg.act=act
