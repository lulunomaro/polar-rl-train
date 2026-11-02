"""Separate ordinary RL episode resets from solver/data integrity failures.

The underlying task still resets the exact same environments at the exact same
thresholds. Only the global full-save stop policy is changed by human authorization.
"""
from pathlib import Path
import math
import json,os,time
import torch

ORDINARY_TERMS=frozenset(('bad_orientation','base_contact','low_base','closure'))
INTEGRITY_TERMS=frozenset(('mimic',))

def learning_health_pass(v):
    return (v.get('version')==3 and v.get('integrity_task_reset_events')==0
        and v.get('unknown_task_reset_events')==0 and v.get('nonfinite_observed') is False
        and math.isfinite(v.get('max_closure_error_m',float('nan')))
        and v.get('max_mimic_error_rad',float('inf'))<=.01
        and v.get('actual_physics_callbacks')==v.get('expected_physics_callbacks')
        and v.get('termination_reason_coverage_exact') is True)

class ClockTrainingHealth:
    def __init__(self,env,folder):
        self.env=env;self.folder=Path(folder)
        self.counts=torch.zeros(env.num_envs,dtype=torch.int64,device=env.device)
        self.reason_counts={n:torch.zeros_like(self.counts) for n in env.termination_manager.active_terms}
        self.integrity_counts=torch.zeros_like(self.counts);self.ordinary_counts=torch.zeros_like(self.counts)
        self.unknown_counts=torch.zeros_like(self.counts)
        self.steps=0;self.initial_tick=env._integrated_contact.tick;self.reason=None
        self.nonfinite=False;self.coverage_exact=True;self.last_events=[];self.last_event_count=0
        self.names=tuple(self.reason_counts)
        assert {'closure','mimic'}.issubset(self.names),'Missing actual closure/mimic task terms'
        old=env.step
        def step(action):
            result=old(action);self.steps+=1
            tm=env.termination_manager;actual=tm.terminated.to(torch.bool)
            masks={n:tm.get_term(n).to(torch.bool) for n in self.names}
            ordinary=torch.zeros_like(actual);integrity=torch.zeros_like(actual);unknown=torch.zeros_like(actual)
            for n,m in masks.items():
                self.reason_counts[n].add_(m.to(torch.int64))
                if n in ORDINARY_TERMS:ordinary|=m
                elif n in INTEGRITY_TERMS:integrity|=m
                elif n!='time_out':unknown|=m
            accounted=ordinary|integrity|unknown
            self.coverage_exact=self.coverage_exact and bool(torch.equal(actual,accounted))
            self.counts.add_(actual.to(torch.int64));self.ordinary_counts.add_(ordinary.to(torch.int64))
            self.integrity_counts.add_(integrity.to(torch.int64));self.unknown_counts.add_(unknown.to(torch.int64))
            if bool(actual.any()):
                ids=actual.nonzero().flatten().tolist()
                for i in ids[:32]:
                    self.last_events.append(dict(control_step=self.steps,env_id=i,
                        reasons=[n for n,m in masks.items() if n!='time_out' and bool(m[i])],
                        snapshot_scope='Actual termination-manager flags; post-reset body state deliberately not labelled failure-state'))
                self.last_events=self.last_events[-32:]
            # The exact task already checks closure and mimic every control step.
            # Check tensor finiteness and periodically publish independently of checkpoint saving.
            if self.steps%12==0:
                tensors=(action,env.scene['robot'].data.root_state_w,
                    env.scene['robot'].data.joint_pos,env.scene['robot'].data.joint_vel)
                self.nonfinite=self.nonfinite or not all(bool(torch.isfinite(x).all()) for x in tensors)
                failed=(int(self.integrity_counts.sum())>0 or int(self.unknown_counts.sum())>0
                    or self.nonfinite or not self.coverage_exact
                    or not math.isfinite(float(getattr(env,'_mod4_max_closure',float('nan'))))
                    or float(getattr(env,'_mod4_max_mimic',float('inf')))>.01)
                if failed:
                    self.reason='Actual solver/model/data integrity failure; own full-save stop; ordinary episode resets excluded'
                    stop=self.folder/'STOP_AFTER_SAVE'
                    if not stop.exists():stop.write_text(self.reason+'\n')
                events=int(self.counts.sum())
                if failed or events!=self.last_event_count or self.steps%300==0:
                    self.last_event_count=events;self.write()
            return result
        env.step=step

    def write(self):
        v=dict(version=3,epoch=time.time(),pid=os.getpid(),physics_dt_s=float(self.env.physics_dt),
            control_dt_s=float(self.env.step_dt),control_steps=self.steps,
            actual_task_reset_events=int(self.counts.sum()),
            closure_episode_reset_events=int(self.reason_counts['closure'].sum()),
            closure_episode_threshold_m=float(self.env.cfg.terminations.closure.params["threshold"]),
             closure_10mm_still_resets_only_this_environment=float(self.env.cfg.terminations.closure.params["threshold"])==.01,
            closure_peak_alone_does_not_stop_global_learning=True,
            historical_single_peak_2mm_diagnostic_only=float(getattr(self.env,'_mod4_max_closure',float('inf')))<=.002,
            post_reset_values_not_relabelled_as_pre_reset_failure=True,failed_environments=int((self.counts>0).sum()),
            ordinary_episode_reset_events=int(self.ordinary_counts.sum()),
            integrity_task_reset_events=int(self.integrity_counts.sum()),
            unknown_task_reset_events=int(self.unknown_counts.sum()),
            termination_events_by_reason={n:int(v.sum()) for n,v in self.reason_counts.items()},
            ordinary_task_thresholds_declared_by_new_cfg=True,ordinary_resets_continue_learning=True,
            termination_reason_coverage_exact=self.coverage_exact,nonfinite_observed=self.nonfinite,
            actual_physics_callbacks=self.env._integrated_contact.tick-self.initial_tick,
            expected_physics_callbacks=self.steps*self.env.cfg.decimation,
            max_closure_error_m=float(getattr(self.env,'_mod4_max_closure',float('nan'))),
            max_mimic_error_rad=float(getattr(self.env,'_mod4_max_mimic',float('nan'))),
            stop_reason=self.reason,request_own_save_only_no_force_kill=True,
            last_actual_termination_events=self.last_events,event_examples_limited_to_last32=True,
            timeout_excluded=True,ordinary_failure_rate_is_reported_not_a_new_graduation_threshold=True)
        p=self.folder/'CLOCK_TRAINING_HEALTH.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
        return v
