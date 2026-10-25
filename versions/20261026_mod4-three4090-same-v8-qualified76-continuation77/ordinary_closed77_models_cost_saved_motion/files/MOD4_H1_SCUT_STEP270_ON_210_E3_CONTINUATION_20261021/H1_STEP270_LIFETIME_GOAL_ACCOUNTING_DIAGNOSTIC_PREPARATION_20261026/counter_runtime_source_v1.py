"""Read-only accounting of existing completed control records, never a training gate."""
from pathlib import Path
import ast,base64,hashlib,json,os
import numpy as np

EVENTS=('takeoff_count','landing_count','recovery_count')

class LifetimeGoalCounter:
    def __init__(self,initial_counts,initial_crossed):
        self.before={k:np.asarray(initial_counts[k]).copy() for k in EVENTS};self.n=len(self.before[EVENTS[0]])
        assert all(a.shape==(self.n,) and a.dtype.kind in 'iu' and (a>=0).all() for a in self.before.values())
        self.initial_sums={k:int(a.sum()) for k,a in self.before.items()}
        self.before_cross=np.asarray(initial_crossed,dtype=bool).copy();assert self.before_cross.shape==(self.n,2)
        self.total={k:0 for k in EVENTS};self.by_env={k:np.zeros(self.n,dtype=np.uint64) for k in EVENTS}
        self.cross_by_env=np.zeros(self.n,dtype=np.uint64);self.rows=0;self.negative_counter_envframes=0
        self.invalid_rows=0;self.last_error=None;self.write_errors=[]

    def complete(self,row):
        try:
            after={k:np.asarray(row[k]) for k in EVENTS};done=np.asarray(row['done'],dtype=bool);cross=np.asarray(row['step_wheel_crossed'],dtype=bool)
            if done.shape!=(self.n,) or cross.shape!=(self.n,2):raise ValueError('Counter row shape')
            if not all(a.shape==(self.n,) and a.dtype.kind in 'iu' and (a>=0).all() for a in after.values()):raise ValueError('Counter row integer schema')
            deltas={k:a.astype(np.int64)-self.before[k].astype(np.int64) for k,a in after.items()}
        except (KeyError,ValueError,TypeError) as error:
            self.invalid_rows+=1;self.last_error=type(error).__name__+': '+str(error);return False
        for k,delta in deltas.items():
            self.negative_counter_envframes+=int((delta<0).sum());delta=np.maximum(delta,0).astype(np.uint64)
            self.total[k]+=int(delta.sum(dtype=np.uint64));self.by_env[k]+=delta
            self.before[k]=after[k].copy();self.before[k][done]=0
        self.cross_by_env+=(cross.all(-1)&~self.before_cross.all(-1)).astype(np.uint64)
        self.before_cross=cross.copy();self.before_cross[done]=False;self.rows+=1
        return True

    def snapshot(self):
        return {'schema':'completed_control_goal_events_v1','complete_control_rows':self.rows,'num_envs':self.n,
                'environment_control_transitions':self.rows*self.n,'events':dict(self.total),'initial_counter_snapshot_sums':self.initial_sums,
                'unique_env_ids_with_event':{k:int((a>0).sum()) for k,a in self.by_env.items()},
                'both_leading_edges_cross_event_count':int(self.cross_by_env.sum()),'negative_counter_envframes':self.negative_counter_envframes,
                'invalid_rows':self.invalid_rows,'last_error':self.last_error,'diagnostic_valid':self.invalid_rows==0 and self.negative_counter_envframes==0,
                'diagnostic_write_errors':list(self.write_errors),'selected_resets_accounted_from_previous_complete_row_done':True,
                'only_completed_control_rows_not_partial_physics_callbacks':True,
                'cross_event_is_original_leading_edge_truth_not_complete_footprint_landing':True,
                'not_frozen_policy_skill_graduation_or_new_training_gate':True}

    def save(self,folder):
        p=Path(folder)/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json';tmp=p.with_suffix('.json.partial')
        try:
            tmp.write_text(json.dumps(self.snapshot(),indent=2),encoding='utf8');os.replace(tmp,p);return True
        except OSError as error:
            self.write_errors.append({'type':type(error).__name__,'message':str(error),'complete_control_rows':self.rows});return False
