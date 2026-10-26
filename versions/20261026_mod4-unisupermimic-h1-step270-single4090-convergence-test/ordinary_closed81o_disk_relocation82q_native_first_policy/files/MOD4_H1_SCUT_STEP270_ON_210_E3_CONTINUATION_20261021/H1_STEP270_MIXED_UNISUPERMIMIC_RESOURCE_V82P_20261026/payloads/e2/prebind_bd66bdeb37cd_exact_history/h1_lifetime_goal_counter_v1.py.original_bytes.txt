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

ORIGINAL_V8_TRACE_BASE64='IiIiUmVhZC1vbmx5IHNhbXBsaW5nL2NvbnRyb2wgZXZpZGVuY2UgYW5kIGltbXV0YWJsZSBwcmUtdXBkYXRlIGZ1bGwgY2hlY2twb2ludHMuDQoNCk5ldmVyIHJlY29tcHV0ZXMgb2JzZXJ2YXRpb25zLCBzYW1wbGVzIGFjdGlvbnMsIGFkdmFuY2VzIFJORywgY2hhbmdlcyBmb3JjZXMgb3IgaW5wdXRzLg0KQ29udHJvbC1yYXRlIHRyYWluaW5nIHJlY29yZHMgYXJlIG5vdCBmdWxsIHBoeXNpY2FsLWNhbGxiYWNrIHJlcGxheSBldmlkZW5jZS4NCiIiIg0KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoDQppbXBvcnQgdGltZSxqc29uLGhhc2hsaWIsdHJhY2ViYWNrDQppbXBvcnQgdG9yY2gsbnVtcHkgYXMgbnANCmZyb20gc2FtcGxpbmdfdHJhY2VfbnB6X2xvc3NsZXNzX3YxIGltcG9ydCB3cml0ZV90cmFjZV9yb3dzX25weixzaGEyNTZfZmlsZQ0KZGVmIEgocCk6cmV0dXJuIHNoYTI1Nl9maWxlKHApDQpkZWYgcHV0KHAsdik6DQogcD1QYXRoKHApO3E9cC53aXRoX3N1ZmZpeChwLnN1ZmZpeCsnLnBhcnRpYWwnKTtxLndyaXRlX3RleHQoanNvbi5kdW1wcyh2LGluZGVudD0yKSk7cS5yZXBsYWNlKHApDQpjbGFzcyBIMUNvbnRyb2xQcmVmaXhUcmFjZToNCiBkZWYgX19pbml0X18oc2VsZixydW5uZXIsZm9sZGVyKToNCiAgc2VsZi5ydW5uZXI9cnVubmVyO3NlbGYudmVjPXJ1bm5lci5lbnY7c2VsZi5lbnY9c2VsZi52ZWMudW53cmFwcGVkO3NlbGYuZm9sZGVyPVBhdGgoZm9sZGVyKTtzZWxmLmZvbGRlci5ta2RpcigpO3NlbGYucm93cz1bXTtzZWxmLmluZGV4PVtdO3NlbGYuc291cmNlX21vZGVscz1bXTtzZWxmLm9ic2VydmVkPU5vbmU7c2VsZi5mcmFtZT1Ob25lO3NlbGYudGVybXM9bGlzdChzZWxmLmVudi5yZXdhcmRfbWFuYWdlci5fdGVybV9uYW1lcyk7c2VsZi50b3RhbD0wDQogZGVmIGluc3RhbGwoc2VsZik6DQogIG9sZF9hY3Q9c2VsZi5ydW5uZXIuYWxnLmFjdDtvbGRfc3RlcD1zZWxmLnZlYy5zdGVwO29sZF90ZXJtPXNlbGYuZW52LnRlcm1pbmF0aW9uX21hbmFnZXIuY29tcHV0ZTtvbGRfcmV3YXJkPXNlbGYuZW52LnJld2FyZF9tYW5hZ2VyLmNvbXB1dGUNCiAgZGVmIGFjdChvYnMsKmFyZ3MsKiprd2FyZ3MpOg0KICAgaWYgbm90IHNlbGYucm93czoNCiAgICBwPXNlbGYuZm9sZGVyLygncHJldXBkYXRlX2Z1bGxzb3VyY2VfJytzdHIobGVuKHNlbGYuc291cmNlX21vZGVscykpKycucHQnKTt0bXA9cC53aXRoX3N1ZmZpeCgnLnB0LnBhcnRpYWwnKTtzZWxmLnJ1bm5lci5zYXZlKHN0cih0bXApKTt0bXAucmVwbGFjZShwKTtzZWxmLnNvdXJjZV9tb2RlbHMuYXBwZW5kKGRpY3QocGF0aD1zdHIocCksYnl0ZXM9cC5zdGF0KCkuc3Rfc2l6ZSxTSEE9SChwKSxiZWZvcmVfY29udHJvbD1zZWxmLnRvdGFsLG5vX29wdGltaXplcl9jYWxsPVRydWUpKQ0KICAgc2VsZi5vYnNlcnZlZD1kaWN0KHBvbGljeTM1PW9ic1sncG9saWN5J10uZGV0YWNoKCkuY2xvbmUoKSxjcml0aWMzOD1vYnNbJ2NyaXRpYyddLmRldGFjaCgpLmNsb25lKCkpO3JldHVybiBvbGRfYWN0KG9icywqYXJncywqKmt3YXJncykNCiAgZGVmIHRlcm0oKmFyZ3MsKiprd2FyZ3MpOg0KICAgdmFsdWU9b2xkX3Rlcm0oKmFyZ3MsKiprd2FyZ3MpDQogICBpbXBvcnQgbW9kNF90YXNrIGFzIHRhc2sNCiAgIGU9c2VsZi5lbnY7cj1lLnNjZW5lWydyb2JvdCddO3A9ZS5oMV9waGFzZTtzZWxmLmZyYW1lPWRpY3Qocm9vdDEzPXIuZGF0YS5yb290X3N0YXRlX3cuZGV0YWNoKCkuY2xvbmUoKSxxMzA9ci5kYXRhLmpvaW50X3Bvcy5kZXRhY2goKS5jbG9uZSgpLGpvaW50X3ZlbG9jaXR5PXIuZGF0YS5qb2ludF92ZWwuZGV0YWNoKCkuY2xvbmUoKSxhcHBsaWVkX3RvcnF1ZT1yLmRhdGEuYXBwbGllZF90b3JxdWUuZGV0YWNoKCkuY2xvbmUoKSxleGVjdXRlZDY9ZS5hY3Rpb25fbWFuYWdlci5hY3Rpb24uZGV0YWNoKCkuY2xvbmUoKSxoaXN0b3J5NW1zPWUuX2ludGVncmF0ZWRfY29udGFjdC5oaXN0b3J5LmRldGFjaCgpLmNsb25lKCksaW1wdWxzZT1lLl9pbnRlZ3JhdGVkX2NvbnRhY3QuaW1wdWxzZS5kZXRhY2goKS5jbG9uZSgpLGNsb3N1cmU9dG9yY2guc3RhY2sobGlzdCh0YXNrLmNsb3N1cmVfZXJyb3JzKGUpLnZhbHVlcygpKSkuYW1heCgwKSxtaW1pYz10b3JjaC5zdGFjayhsaXN0KHRhc2subWltaWNfZXJyb3JzKGUpLnZhbHVlcygpKSkuYW1heCgwKSxwdWJsaWNfcmVxdWVzdD1wLnJlcXVlc3RfZm9yX2FjdGlvbi5kZXRhY2goKS5jbG9uZSgpLGV2ZW50X2V4cGVjdGVkPXAuZXZlbnRfY29udHJvbC5kZXRhY2goKS5jbG9uZSgpLHByb2dyZXNzX2V4cGVjdGVkPXAucHJvZ3Jlc3NfY29udHJvbC5kZXRhY2goKS5jbG9uZSgpLHByb2dyZXNzX3BlYWs9cC5wZWFrLmRldGFjaCgpLmNsb25lKCkscHJvZ3Jlc3NfcGFpZD1wLmdvYWwucHJvZ3Jlc3MuZGV0YWNoKCkuY2xvbmUoKSxzdGVwX3N0YWJsZV90aWNrcz1wLmdvYWwuc3RhYmxlX3RpY2tzLmRldGFjaCgpLmNsb25lKCksc3RlcF9zdWNjZXNzPXAuZ29hbC5zdWNjZXNzLmRldGFjaCgpLmNsb25lKCksc3RlcF93aGVlbF9jcm9zc2VkPXAuY3Jvc3NlZC5kZXRhY2goKS5jbG9uZSgpLHRha2VvZmZfY291bnQ9cC50YWtlb2ZmX2NvdW50LmRldGFjaCgpLmNsb25lKCksbGFuZGluZ19jb3VudD1wLmxhbmRpbmdfY291bnQuZGV0YWNoKCkuY2xvbmUoKSxyZWNvdmVyeV9jb3VudD1wLnJlY292ZXJ5X2NvdW50LmRldGFjaCgpLmNsb25lKCksZXBpc29kZT1lLl9zZW5zb3JfbWlsZC5lcGlzb2RlLmRldGFjaCgpLmNsb25lKCkpO3JldHVybiB2YWx1ZQ0KICBkZWYgcmV3YXJkKGR0LCphcmdzLCoqa3dhcmdzKToNCiAgIHJlc3VsdD1vbGRfcmV3YXJkKGR0LCphcmdzLCoqa3dhcmdzKQ0KICAgaWYgc2VsZi5mcmFtZSBpcyBub3QgTm9uZTpzZWxmLmZyYW1lWydyZXdhcmRfdGVybV9jb250cmlidXRpb24nXT1zZWxmLmVudi5yZXdhcmRfbWFuYWdlci5fc3RlcF9yZXdhcmQuZGV0YWNoKCkuY2xvbmUoKSpzZWxmLmVudi5oMV9yZXdhcmRfcmVhZG91dF9zY2FsZQ0KICAgcmV0dXJuIHJlc3VsdA0KICBkZWYgc3RlcChhY3Rpb25zKToNCiAgIHJhdz1hY3Rpb25zLmRldGFjaCgpLmNsb25lKCk7c2VsZi5mcmFtZT1Ob25lDQogICBzZWxmLmVudi5faDFfc2FtcGxlZF9leGNlc3NfdHJhaW5pbmdfYWN0aXZlPVRydWUNCiAgIHNlbGYuZW52Ll9oMV9zYW1wbGVkX2FjdGlvbnNfZm9yX3Jld2FyZD1yYXcNCiAgIHRyeToNCiAgICBvdXRwdXQ9b2xkX3N0ZXAoYWN0aW9ucyk7b2JzLHJld2FyZCxkb25lLGluZm89b3V0cHV0O2Fzc2VydCBzZWxmLmZyYW1lIGlzIG5vdCBOb25lIGFuZCBzZWxmLm9ic2VydmVkIGlzIG5vdCBOb25lO3Jvdz17KipzZWxmLm9ic2VydmVkLCoqc2VsZi5mcmFtZSwncmF3X3NhbXBsZWQ2JzpyYXcsJ3RvdGFsX3Jld2FyZCc6cmV3YXJkLmRldGFjaCgpLmNsb25lKCksJ2RvbmUnOmRvbmUuZGV0YWNoKCkuY2xvbmUoKX07c2VsZi5yb3dzLmFwcGVuZCh7azp2LmRldGFjaCgpLmNwdSgpLm51bXB5KCkuY29weSgpIGZvciBrLHYgaW4gcm93Lml0ZW1zKCl9KTtzZWxmLnRvdGFsKz0xDQogICAgaWYgbGVuKHNlbGYucm93cyk9PTI0OnNlbGYucGVyc2lzdCgpDQogICAgcmV0dXJuIG91dHB1dA0KICAgZXhjZXB0IEJhc2VFeGNlcHRpb246DQogICAgcHV0KHNlbGYuZm9sZGVyLydBQ1RVQUxfU1RFUF9PUklHSU5BTF9FUlJPUi5qc29uJyxkaWN0KGVwb2NoPXRpbWUudGltZSgpLGVycm9yPXRyYWNlYmFjay5mb3JtYXRfZXhjKCksY29tcGxldGVkX2NvbnRyb2xfcm93cz1zZWxmLnRvdGFsLGZhaWxlZF9jdXJyZW50X2NvbnRyb2xfbm90X2NsYWltZWRfY29tcGxldGU9VHJ1ZSkpO3NlbGYucGVyc2lzdCgpO3JhaXNlDQogICBmaW5hbGx5Og0KICAgIHNlbGYuZW52Ll9oMV9zYW1wbGVkX2FjdGlvbnNfZm9yX3Jld2FyZD1Ob25lDQogICAgc2VsZi5lbnYuX2gxX3NhbXBsZWRfZXhjZXNzX3RyYWluaW5nX2FjdGl2ZT1GYWxzZQ0KICBzZWxmLnJ1bm5lci5hbGcuYWN0PWFjdDtzZWxmLnZlYy5zdGVwPXN0ZXA7c2VsZi5lbnYudGVybWluYXRpb25fbWFuYWdlci5jb21wdXRlPXRlcm07c2VsZi5lbnYucmV3YXJkX21hbmFnZXIuY29tcHV0ZT1yZXdhcmQNCiBkZWYgcGVyc2lzdChzZWxmKToNCiAgaWYgc2VsZi5yb3dzOg0KICAgcD1zZWxmLmZvbGRlci8oJ2NvbnRyb2xfcHJlZml4Xycrc3RyKGxlbihzZWxmLmluZGV4KSkrJy5ucHonKTt0bXA9cC53aXRoX3N1ZmZpeCgnLm5wei5wYXJ0aWFsJykNCiAgIHdpdGggdG1wLm9wZW4oJ3hiJykgYXMgZjp3cml0ZV90cmFjZV9yb3dzX25weihmLHNlbGYucm93cyxjb21wcmVzc2xldmVsPTEpDQogICB0bXAucmVwbGFjZShwKTtzZWxmLmluZGV4LmFwcGVuZChkaWN0KHBhdGg9c3RyKHApLGJ5dGVzPXAuc3RhdCgpLnN0X3NpemUsU0hBPUgocCksY29udHJvbHM9bGVuKHNlbGYucm93cykscHJldXBkYXRlX3NvdXJjZT1zZWxmLnNvdXJjZV9tb2RlbHNbbGVuKHNlbGYuaW5kZXgpXSkpO3NlbGYucm93cy5jbGVhcigpDQogIHB1dChzZWxmLmZvbGRlci8nQ09OVFJPTF9WQUxJRF9QUkVGSVhfSU5ERVhfQUNUVUFMLmpzb24nLGRpY3QoZXBvY2g9dGltZS50aW1lKCksY29udHJvbHM9c2VsZi50b3RhbCxpbmRleD1zZWxmLmluZGV4LHByZXVwZGF0ZV9mdWxsX3NvdXJjZXM9c2VsZi5zb3VyY2VfbW9kZWxzLHJld2FyZF90ZXJtcz1zZWxmLnRlcm1zLHBoeXNpY2FsX2NhbGxiYWNrX3JlcGxheT1GYWxzZSxub19leHRyYV9hY3Rvcl9mb3J3YXJkX29yX1JOR19kcmF3PVRydWUscmF3X3NhbXBsZWRfYWN0aW9uX2FuZF9hY3R1YWxjbGlwX2V4ZWN1dGlvbl9zZXBhcmF0ZT1UcnVlLGFsbF9zdWNjZXNzX2FuZF9mYWlsZWRfY29udHJvbF9wcmVmaXhlc19yZXRhaW5lZD1UcnVlKSkNCg0KZnJvbSBoMV9wcmVmaXhfcGFpcl9yZXRlbnRpb25fdjEgaW1wb3J0IHdyYXBfdHJhY2VfcGVyc2lzdA0KSDFDb250cm9sUHJlZml4VHJhY2UucGVyc2lzdD13cmFwX3RyYWNlX3BlcnNpc3QoSDFDb250cm9sUHJlZml4VHJhY2UucGVyc2lzdCkNCg=='
ORIGINAL_V8_TRACE_SHA='84e31ea3a0e49003a8ee2671659411dfd528a9d70ef44c4ac75282fc271a59f7'

def canonical_V8_trace_tree(path):
    tree=ast.parse(Path(path).read_text('utf8'))
    expected_import=ast.parse('from h1_lifetime_goal_counter_v1 import LifetimeGoalCounter, EVENTS').body[0]
    matches=[n for n in tree.body if ast.dump(n)==ast.dump(expected_import)];assert len(matches)==1;tree.body.remove(matches[0])
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1ControlPrefixTrace')
    install=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='install')
    expected_init=ast.parse("self.lifetime_goal_counter=LifetimeGoalCounter({k:getattr(self.env.h1_phase,k).detach().cpu().numpy().copy() for k in EVENTS},self.env.h1_phase.crossed.detach().cpu().numpy().copy())").body[0]
    matches=[n for n in install.body if ast.dump(n)==ast.dump(expected_init)];assert len(matches)==1 and install.body.index(matches[0])==4;install.body.remove(matches[0])
    step=next(n for n in install.body if isinstance(n,ast.FunctionDef) and n.name=='step');tr=next(n for n in step.body if isinstance(n,ast.Try))
    expected_complete=ast.parse('self.lifetime_goal_counter.complete(self.rows[-1])').body[0]
    matches=[n for n in tr.body if ast.dump(n)==ast.dump(expected_complete)];assert len(matches)==1
    pos=tr.body.index(matches[0]);assert ast.dump(tr.body[pos-1])==ast.dump(ast.parse('self.total+=1').body[0]) and isinstance(tr.body[pos+1],ast.If)
    tr.body.remove(matches[0])
    persist=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='persist')
    expected_save=ast.parse('self.lifetime_goal_counter.save(self.folder)').body[0]
    assert ast.dump(persist.body[-1])==ast.dump(expected_save);persist.body.pop()
    original=base64.b64decode(ORIGINAL_V8_TRACE_BASE64)
    assert hashlib.sha256(original).hexdigest()==ORIGINAL_V8_TRACE_SHA
    assert ast.dump(tree)==ast.dump(ast.parse(original.decode('utf8')))
    return tree

def installed_counter_CPU_checks(B):
    import torch,types,time,traceback
    from unittest import mock
    B=Path(B);rng=torch.get_rng_state().clone();n=20000;out=B/'reports/lifetime_goal_diagnostic_CPU_fixture';out.mkdir(parents=True)
    phase=types.SimpleNamespace(**{k:torch.zeros(n,dtype=torch.long) for k in EVENTS},crossed=torch.zeros(n,2,dtype=torch.bool))
    env=types.SimpleNamespace(h1_phase=phase,_h1_sampled_excess_training_active=False,_h1_sampled_actions_for_reward=None)
    actions=torch.zeros(n,6);actions[:,0]=106.;original=actions.clone();calls=[];errors=[];persists=[];holder={}
    witness=types.SimpleNamespace(env=env,frame=None,observed={'policy35':torch.zeros(n,35),'critic38':torch.zeros(n,38)},rows=[],total=0,folder=out,persist=lambda:persists.append('original_persist_called'))
    tree=ast.parse((B/'h1_production_control_prefix_trace_v1.py').read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef));install=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='install')
    init=next(x for x in install.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='lifetime_goal_counter' for t in x.targets));scope={'self':witness,'LifetimeGoalCounter':LifetimeGoalCounter,'EVENTS':EVENTS}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[init],type_ignores=[])),'actual_counter_init','exec'),scope)
    def old_step(value):
        assert value is actions and torch.equal(value,original) and env._h1_sampled_excess_training_active
        assert env._h1_sampled_actions_for_reward.data_ptr()!=value.data_ptr() and torch.equal(env._h1_sampled_actions_for_reward,value)
        rowno=len(calls);calls.append(value.data_ptr());done=torch.zeros(n,dtype=torch.bool)
        if rowno<2:phase.takeoff_count[0]+=1;phase.crossed[0]=True
        if rowno==0:done[0]=True
        if rowno==1:phase.landing_count[0]=1
        if rowno==2:phase.recovery_count[0]=1
        witness.frame={k:getattr(phase,k).clone() for k in EVENTS};witness.frame['step_wheel_crossed']=phase.crossed.clone();witness.frame['executed6']=value.clamp(-6,6)
        result=({'policy':torch.zeros(n,35)},torch.full((n,),.5),done,{})
        for k in EVENTS:getattr(phase,k)[done]=0
        phase.crossed[done]=False;holder['result']=result;return result
    step=next(x for x in install.body if isinstance(x,ast.FunctionDef) and x.name=='step')
    scope={'self':witness,'old_step':old_step,'torch':torch,'np':np,'time':time,'traceback':traceback,'put':lambda p,v:errors.append(v)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[step],type_ignores=[])),'actual_complete_step','exec'),scope)
    for _ in range(3):
        result=scope['step'](actions);assert result is holder['result'] and torch.equal(actions,original)
        assert env._h1_sampled_actions_for_reward is None and not env._h1_sampled_excess_training_active
    s=witness.lifetime_goal_counter.snapshot();assert s['events']==dict(takeoff_count=2,landing_count=1,recovery_count=1) and s['both_leading_edges_cross_event_count']==2 and s['complete_control_rows']==3 and s['diagnostic_valid']
    for _ in range(21):scope['step'](actions)
    assert witness.total==24 and len(persists)==1 and witness.lifetime_goal_counter.rows==24 and witness.lifetime_goal_counter.snapshot()['events']==s['events']
    def failed(value):raise RuntimeError('EXPECTED_CPU_ORIGINAL_STEP_FAILURE')
    scope['old_step']=failed
    try:scope['step'](actions)
    except RuntimeError as error:assert str(error)=='EXPECTED_CPU_ORIGINAL_STEP_FAILURE'
    else:raise AssertionError('Original failure swallowed')
    assert len(errors)==1 and len(persists)==2 and witness.total==24 and witness.lifetime_goal_counter.rows==24 and env._h1_sampled_actions_for_reward is None and not env._h1_sampled_excess_training_active
    # Real unwrapped persist ordering: original index publication must succeed before optional accounting save.
    pd=out/'persist_success';pd.mkdir();counter=witness.lifetime_goal_counter;events=[]
    test=types.SimpleNamespace(rows=[{'x':np.arange(4)} for _ in range(24)],folder=pd,index=[],source_models=[{'synthetic_fixture':True}],total=24,terms=[],lifetime_goal_counter=counter)
    def put(p,v):events.append('original_index');Path(p).write_text(json.dumps(v),encoding='utf8')
    persist=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='persist')
    def writer(f,rows,compresslevel):np.savez_compressed(f,x=np.stack([r['x'] for r in rows]))
    ps={'self':test,'write_trace_rows_npz':writer,'H':lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(),'put':put,'time':time}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[persist],type_ignores=[])),'actual_persist_order','exec'),ps);ps['persist'](test)
    saved=json.loads((pd/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json').read_bytes());assert saved['complete_control_rows']==24 and events==['original_index'] and not (pd/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json.partial').exists()
    failure=out/'persist_failure';failure.mkdir();test.folder=failure;test.rows=[]
    def original_failure(p,v):raise RuntimeError('EXPECTED_ORIGINAL_PERSIST_FAILURE')
    ps['put']=original_failure
    try:ps['persist'](test)
    except RuntimeError as error:assert str(error)=='EXPECTED_ORIGINAL_PERSIST_FAILURE'
    else:raise AssertionError('Original persistence failure swallowed')
    assert not (failure/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json').exists()
    # Optional diagnostic I/O errors never replace original training/persistence failures.
    with mock.patch.object(Path,'write_text',side_effect=OSError('EXPECTED_DIAGNOSTIC_WRITE_FAILURE')):assert counter.save(pd) is False
    assert len(counter.write_errors)==1 and counter.save(pd) is True
    malformed={k:v.copy() for k,v in witness.rows[-1].items()};malformed['done']=np.zeros(2,dtype=bool);assert counter.complete(malformed) is False and not counter.snapshot()['diagnostic_valid']
    negative=LifetimeGoalCounter({k:np.ones(n,dtype=np.int64) for k in EVENTS},np.zeros((n,2),dtype=bool));zero={k:np.zeros(n,dtype=np.int64) for k in EVENTS};zero.update(done=np.zeros(n,dtype=bool),step_wheel_crossed=np.zeros((n,2),dtype=bool));assert negative.complete(zero) and not negative.snapshot()['diagnostic_valid']
    original_text=(B/'h1_production_control_prefix_trace_v1.py').read_text('utf8');negative_sources=[]
    for name,text in [('forwarding',original_text.replace('old_step(actions)','old_step(actions.clamp(-5,5))')),('clear',original_text.replace('self.env._h1_sampled_actions_for_reward=None','self.env._h1_sampled_actions_for_reward=raw')),('duplicate_complete',original_text.replace('self.lifetime_goal_counter.complete(self.rows[-1])','self.lifetime_goal_counter.complete(self.rows[-1]);self.lifetime_goal_counter.complete(self.rows[-1])')),('skip_save',original_text.replace('self.lifetime_goal_counter.save(self.folder)','self.lifetime_goal_counter.save(self.folder.parent)'))]:
        p=out/(name+'.negative_source.txt');p.write_text(text,encoding='utf8')
        try:canonical_V8_trace_tree(p)
        except AssertionError:negative_sources.append(name)
        else:raise AssertionError('Unexpected trace change accepted: '+name)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    artifacts=[{'path':str(p),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in pd.iterdir() if p.is_file()]
    return {'passed':True,'synthetic_environments':n,'actual_trace_step_forwarding_and_reset_row_order_tested':True,'same_original_actions_object_values_and_output_tuple':True,'no_partial_failed_control_counted':True,'original_persist_before_optional_counter_publish_and_original_errors_preserved':True,'diagnostic_IO_error_nonblocking_and_recorded':True,'invalid_counter_diagnostic_not_training_gate':True,'negative_source_cases_rejected':negative_sources,'no_GPU_RNG_policy_model_or_physics':True,'not_actual_runtime_goal_events':True,'synthetic_artifacts':artifacts}
