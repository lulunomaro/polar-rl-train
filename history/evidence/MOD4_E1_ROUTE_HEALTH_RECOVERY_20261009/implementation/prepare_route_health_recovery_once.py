"""Isolated observer repair; preserve all production/task/physics source bytes."""
from pathlib import Path
import sys,json,ast,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;N=B/'MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009';NR=N/'reports'
assert not N.exists();NR.mkdir(parents=True)
v=json.loads((R/'E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json').read_text());assert v['actual_old_parent_guardian_child_exit'] and v['active_and_Sactive_empty']
health=(R/'route_health_source_reads/clock_training_health.py').read_text()
health=health.replace('class ClockTrainingHealth:', '''TRUNCATION_TERMS=frozenset(('time_out','rough_route_boundary'))

def declared_truncation_terms(tm):
    declared={n:bool(tm.get_term_cfg(n).time_out) for n in tm.active_terms}
    assert set(n for n,v in declared.items() if v)==TRUNCATION_TERMS,('Unexpected truncation declaration',declared)
    assert {'closure','mimic'}.issubset(declared) and not declared['closure'] and not declared['mimic']
    return declared

class E1TerrainTrainingHealth:''')
health=health.replace('self.names=tuple(self.reason_counts)', 'self.names=tuple(self.reason_counts)\n        self.term_timeout_flags=declared_truncation_terms(env.termination_manager)\n        self.truncated_counts=torch.zeros_like(self.counts)\n        self.truncation_coverage_exact=True')
health=health.replace('ordinary=torch.zeros_like(actual);integrity=torch.zeros_like(actual);unknown=torch.zeros_like(actual)', 'ordinary=torch.zeros_like(actual);integrity=torch.zeros_like(actual);unknown=torch.zeros_like(actual);truncated=torch.zeros_like(actual)')
health=health.replace("elif n!='time_out':unknown|=m", "elif n in TRUNCATION_TERMS:truncated|=m\n                else:unknown|=m")
health=health.replace('accounted=ordinary|integrity|unknown', 'self.truncated_counts.add_(truncated.to(torch.int64))\n            self.truncation_coverage_exact=self.truncation_coverage_exact and bool(torch.equal(tm.time_outs.to(torch.bool),truncated))\n            accounted=ordinary|integrity|unknown')
health=health.replace("n!='time_out' and bool(m[i])", "n not in TRUNCATION_TERMS and bool(m[i])")
health=health.replace('or self.nonfinite or not self.coverage_exact', 'or self.nonfinite or not self.coverage_exact or not self.truncation_coverage_exact\n                    or env._integrated_contact.tick-self.initial_tick!=self.steps*round(.01/env.physics_dt)')
health=health.replace('termination_reason_coverage_exact=self.coverage_exact,nonfinite_observed=self.nonfinite,', 'termination_reason_coverage_exact=self.coverage_exact and self.truncation_coverage_exact,nonfinite_observed=self.nonfinite,\n            explicit_truncation_term_timeout_flags=self.term_timeout_flags,\n            actual_truncation_reset_events=int(self.truncated_counts.sum()),\n            route_boundary_truncation_events=int(self.reason_counts["rough_route_boundary"].sum()),\n            truncation_reason_coverage_exact=self.truncation_coverage_exact,\n            original_task_reset_reward_and_PPO_timeout_bootstrap_unchanged=True,')
files={'isaac/mod4/e1_terrain_training_health.py':health.encode()}
test='''from pathlib import Path
from types import SimpleNamespace as S
import tempfile,json,torch
from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass,declared_truncation_terms
class Manager:
 def __init__(self):
  self.active_terms=['time_out','rough_route_boundary','closure','mimic','bad_orientation','base_contact','low_base','unexpected'];self.flags={n:n in ('time_out','rough_route_boundary') for n in self.active_terms};self.masks={n:torch.zeros(3,dtype=torch.bool) for n in self.active_terms}
 def get_term_cfg(self,n):return S(time_out=self.flags[n])
 def get_term(self,n):return self.masks[n]
 @property
 def terminated(self):return torch.stack([v for n,v in self.masks.items() if not self.flags[n]]).any(0)
 @property
 def time_outs(self):return torch.stack([v for n,v in self.masks.items() if self.flags[n]]).any(0)
class Env:
 def __init__(self,reason=None,missing=False,nan=False):
  self.num_envs=3;self.device='cpu';self.physics_dt=.0025;self.step_dt=.01;self.termination_manager=Manager();self._integrated_contact=S(tick=0);self._mod4_max_closure=.001;self._mod4_max_mimic=.001;self.missing=missing
  data=S(root_state_w=torch.zeros(3,13),joint_pos=torch.zeros(3,30),joint_vel=torch.zeros(3,30));self.scene={'robot':S(data=data)}
  if reason:
   for n in reason:self.termination_manager.masks[n][0]=True
  if nan:data.joint_pos[1,0]=float('nan')
 def step(self,a):self._integrated_contact.tick+=3 if self.missing else 4;return ('original-result',)
def run(reasons=(),missing=False,nan=False,mimic=.001):
 with tempfile.TemporaryDirectory() as folder:
  e=Env(reasons,missing,nan);e._mod4_max_mimic=mimic;h=E1TerrainTrainingHealth(e,folder)
  a=torch.zeros(3,6)
  for _ in range(24):assert e.step(a)==('original-result',)
  v=h.write();return v,(Path(folder)/'STOP_AFTER_SAVE').exists()
def main():
 torch.set_num_threads(1)
 v,stop=run(('rough_route_boundary',));assert learning_health_pass(v) and not stop and v['unknown_task_reset_events']==0 and v['route_boundary_truncation_events']==24 and v['actual_task_reset_events']==0
 v,stop=run(('time_out','rough_route_boundary'));assert learning_health_pass(v) and v['actual_truncation_reset_events']==24 and not stop
 v,stop=run(('closure','rough_route_boundary'));assert learning_health_pass(v) and v['actual_task_reset_events']==v['ordinary_episode_reset_events']==24 and not stop
 v,stop=run(('mimic','rough_route_boundary'));assert not learning_health_pass(v) and v['integrity_task_reset_events']==24 and stop
 v,stop=run(('unexpected',));assert not learning_health_pass(v) and v['unknown_task_reset_events']==24 and stop
 v,stop=run(missing=True);assert not learning_health_pass(v) and stop
 v,stop=run(nan=True);assert not learning_health_pass(v) and stop
 v,stop=run(mimic=.02);assert not learning_health_pass(v) and stop
 m=Manager();m.flags['rough_route_boundary']=False
 try:declared_truncation_terms(m)
 except AssertionError:pass
 else:raise AssertionError('Route must be actual declared truncation')
 m=Manager();m.flags['unexpected']=True
 try:declared_truncation_terms(m)
 except AssertionError:pass
 else:raise AssertionError('Unknown truncation not silently permitted')
 e=Env();e.termination_manager.masks['unexpected'][0]=True;e.termination_manager.flags['unexpected']=False
 # Genuine unnamed terminated flag absent from masks must retain coverage failure.
 class BadManager(Manager):
  @property
  def terminated(self):return torch.ones(3,dtype=torch.bool)
 with tempfile.TemporaryDirectory() as folder:
  e=Env();e.termination_manager=BadManager();h=E1TerrainTrainingHealth(e,folder)
  for _ in range(24):e.step(torch.zeros(3,6))
  assert not learning_health_pass(h.write()) and (Path(folder)/'STOP_AFTER_SAVE').exists()
 assert not torch.cuda.is_initialized();print('CPU11 route truncation / overlap / unknown / integrity / callback / nonfinite / manager coverage contracts passed; no CUDA initialized')
if __name__=='__main__':main()
'''
files['isaac/mod4/test_e1_terrain_health_cpu.py']=test.encode()
worker=(D/'isaac/mod4/train_e1_reset_evidence_resume_ppo.py').read_text()
worker=worker.replace('from clock_training_health import ClockTrainingHealth','from e1_terrain_training_health import E1TerrainTrainingHealth as ClockTrainingHealth')
worker=worker.replace('manifest["src_sha256"] = snapshot', '''for name in ('e1_terrain_training_health.py','train_e1_route_health_resume_ppo.py'):
        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)
    manifest['health_observer']='E1 declared route-boundary truncation, exact manager time_out audit'
    manifest["src_sha256"] = snapshot''')
files['isaac/mod4/train_e1_route_health_resume_ppo.py']=worker.encode()
ctl=(D/'supervise_e1_reset_evidence_review.py').read_text().replace('train_e1_reset_evidence_resume_ppo.py','train_e1_route_health_resume_ppo.py')
ctl=ctl.replace("assert read(R/'E1_RESET_EVIDENCE_CPU_PASSED.json')['passed']", "assert read(R/'E1_RESET_EVIDENCE_CPU_PASSED.json')['passed']\n    assert read(R/'E1_ROUTE_HEALTH_CPU_PASSED.json')['passed']")
i=ctl.index('def source():');j=ctl.index('\ndef freeze_run(',i)
ctl=ctl[:i]+'''def source():
    audit=read(R/'E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json');row=audit['saved_exit'];p=Path(row['checkpoint']['path'])
    assert audit['only_declared_route_truncation_flag_is_unknown'] and audit['actual_old_parent_guardian_child_exit'] and audit['snapshot_bytes_exact']
    h=row['health'];assert h['actual_task_reset_events']==h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==0
    assert h['unknown_task_reset_events']==h['termination_events_by_reason']['rough_route_boundary']>0 and h['nonfinite_observed'] is False
    assert h['actual_physics_callbacks']==h['expected_physics_callbacks'] and h['max_mimic_error_rad']<=.01
    assert fullsave(p)==row['checkpoint'] and len(row['unique_completed_segment'])==1
    return p

def wait_existing():
    previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_RESET_EVIDENCE_REVIEW_20261009');pr=previous/'reports';ps=read(pr/'E1_STATE.json');att=read(pr/'E1_ATTENTION.json')
    assert att['own_child_still_alive']==False and att['active_segment'] is None
    locators=[ps['owner'],ps['child'],read(pr/'E1_GUARDIAN_STARTED.json')]
    assert all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in locators)
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    write('E1_ROUTE_OBSERVER_FAILURE_EXIT_AUDITED.json',dict(epoch=time.time(),previous_parent_guardian_child_actual_exit=True,old_health_rejection_retained=True,no_old_pass_rewritten=True,new_budget_seconds=0))

'''+ctl[j:]
ctl=ctl.replace("'train_e1_resource_fresh_preflight_ppo.py'}", "'train_e1_resource_fresh_preflight_ppo.py','train_e1_reset_evidence_resume_ppo.py'}")
ctl=ctl.replace('source=fullsave(init,require_e1=False)', 'source=fullsave(init)')
ctl=ctl.replace("assert before==s.q.ctl.CANONICAL.read_bytes();native20k(init)", "assert before==s.q.ctl.CANONICAL.read_bytes()\n    proof=read(R/'REUSED_E1_NATIVE20K_PASSED.json');assert proof['no_PPO'];write('E1_NATIVE20K_PASSED.json',dict(proof,reused_exact_scope_no_GPU_replay=True))")
i=ctl.index("    row=read(R/'REUSED_E1_DISCARD128_PASSED.json')",ctl.index('def main():'));j=ctl.index("    write('E1_REVIEW_READY.json'",i)
ctl=ctl[:i]+'''    proof=read(R/'REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json');assert proof['weights_discarded'] and proof['real6144_and1920000_steps']
    write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(proof,reused_exact_physics_PPO_scope_no_replay=True,observer_CPU11_new_scope_passed=True))
    audit=read(R/'E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json');remaining=2700-audit['segment_seconds'];assert 120<remaining<=2700
    write('E1_ROUTE_OBSERVER_RECOVERY_SOURCE.json',dict(epoch=time.time(),source=fullsave(init),audited_own_interrupted_E1_save_not_directory_max=True,not_behavior_graduation=True,old_rejected_health_retained=True,first_task_window_remaining_seconds=remaining,new_budget_seconds=0))
    if s.left()>120:
        init,row=train(init,20000,10000,remaining,'e1_gentle_route_recovery',False)
        assert row['health']['route_boundary_truncation_events']>0 and row['health']['truncation_reason_coverage_exact']
        write('E1_TERRAIN_BEHAVIOR_PUBLICATION_PENDING.json',dict(epoch=time.time(),source=row['checkpoint'],reason='Need real matched new-terrain full route and old-skill frozen cases before extending new geometry task',not_terrain_graduation=True))
'''+ctl[j:]
files['supervise_e1_route_health_review.py']=ctl.encode()
for n,b in files.items():ast.parse(b.decode());p=N/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+N.name;old='/home/egde/rl_candidates/'+D.name
try:
 code=r'''
from pathlib import Path
import json,hashlib,shutil
D=Path(ROOT);OLD=Path(OLDROOT);assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==306
for n,h in f.items():
 p=OLD/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for n in ('SELECTED_E0_FOR_E1_BEHAVIOR_SOURCE.json','E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json','E1_FULL_TARGET_CPU_PASSED.json','E1_RESET_EVIDENCE_CPU_PASSED.json','E1_FROZEN_BEHAVIOR_PACKAGES.json','REUSED_E1_NATIVE_COMPACT.json'):shutil.copy2(OLD/'reports'/n,D/'reports'/n)
for a,b in (('E1_NATIVE20K_PASSED.json','REUSED_E1_NATIVE20K_PASSED.json'),('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'),('E1_ATTENTION.json','PREDECESSOR_ROUTE_HEALTH_ATTENTION_RETAINED.json')):shutil.copy2(OLD/'reports'/a,D/'reports'/b)
print('306 original source bytes preserved')
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n,b in files.items():sf.put(str(N/n),root+'/'+n);assert sf.open(root+'/'+n).read()==b
  sf.put(str(R/'E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json'),root+'/reports/E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json')
 code=r'''
from pathlib import Path
import sys,json,hashlib,ast,time,torch,subprocess
D=Path(ROOT);OLD=Path(OLDROOT);R=D/'reports';torch.set_num_threads(1)
out=subprocess.check_output([sys.executable,str(D/'isaac/mod4/test_e1_terrain_health_cpu.py')],text=True);assert 'CPU11' in out and not torch.cuda.is_initialized()
(R/'E1_ROUTE_HEALTH_CPU_PASSED.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,tests=11,no_CUDA_initialized=True,output=out,observer_only_no_task_term_change=True),indent=2))
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());f['candidate_root']=str(D);f['epoch']=time.time()
for n,h in f['sha256'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
for n in NEW:ast.parse((D/n).read_text());f['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest()
f['source_count']=len(f['sha256']);assert f['source_count']==310;f['all_original306_source_bytes_exact']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2));sys.path.insert(0,str(D));import supervise_e1_route_health_review as w
w.verify();w.wait_existing();src=w.source();assert not torch.cuda.is_initialized();before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_e1_route_health_review.py')],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
ident=w.identity(p.pid);assert ident and ident['argv'][1]==str(D/'supervise_e1_route_health_review.py')
row=dict(epoch=time.time(),parent=ident,source=w.fullsave(src),source_count=310,new_files=NEW,old_classifier_failure_exited_unique_segment_retained=True,no_native_or_PPO_preflight_replay=True,new_budget_seconds=0,budget_bytes_exact_at_dispatch=before==w.s.q.ctl.CANONICAL.read_bytes())
w.write('E1_ROUTE_HEALTH_DISPATCH_LAUNCHED.json',row);print(json.dumps(row))
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root)).replace('NEW',repr(list(files)))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','E1_ROUTE_HEALTH_CPU_PASSED.json','E1_ROUTE_HEALTH_DISPATCH_LAUNCHED.json'):sf.get(root+'/reports/'+n,str(NR/n))
 print(raw.decode())
finally:c.close()
