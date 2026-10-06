"""Read-only exact task counter; requests own full-save stop on a real failure."""
from pathlib import Path
import json,os,time
import torch

class ClockTrainingHealth:
    def __init__(self,env,folder):
        self.env=env;self.folder=Path(folder);self.counts=torch.zeros(env.num_envs,dtype=torch.int64,device=env.device)
        self.steps=0;self.initial_tick=env._integrated_contact.tick;self.reason=None
        old=env.step
        def step(action):
            result=old(action);self.counts.add_(env.termination_manager.terminated.to(torch.int64));self.steps+=1
            if self.steps%24==0 and int(self.counts.sum())>0:
                self.reason='Actual task terminations at candidate physical clock; retain full save and reject adoption'
                stop=self.folder/'STOP_AFTER_SAVE'
                if not stop.exists():stop.write_text(self.reason+'\n')
                self.write()
            return result
        env.step=step
    def write(self):
        v=dict(epoch=time.time(),pid=os.getpid(),physics_dt_s=float(self.env.physics_dt),control_dt_s=float(self.env.step_dt),control_steps=self.steps,
            actual_task_reset_events=int(self.counts.sum()),failed_environments=int((self.counts>0).sum()),timeout_excluded=True,
            actual_physics_callbacks=self.env._integrated_contact.tick-self.initial_tick,expected_physics_callbacks=self.steps*round(.01/self.env.physics_dt),
            max_closure_error_m=float(getattr(self.env,'_mod4_max_closure',float('nan'))),max_mimic_error_rad=float(getattr(self.env,'_mod4_max_mimic',float('nan'))),
            stop_reason=self.reason,request_own_save_only_no_force_kill=True)
        target=self.folder/'CLOCK_TRAINING_HEALTH.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2));tmp.replace(target)
        return v
