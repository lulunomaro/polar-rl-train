"""Prepare an isolated 50 Hz candidate and exercise actual clock/queue/phase code on CPU.

This does not install, start, stop, or mutate a training process. Target admission
and fresh saved-boundary handoff remain required before any 50 Hz GO.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports'
A=W/'MOD4_E3_AUTOMATIC_CONTINUATION_20261020'
OLD=A/'cpu_factory_probe/windows/hour0001/recovery'
OUT=B/'candidate_overlay';CHANGES=[]
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def changed(rel,replacements):
 p=OLD/rel;raw=p.read_bytes();s=raw.decode('utf8').replace('\r\n','\n')
 for before,after in replacements:
  assert before in s,(rel,before);s=s.replace(before,after)
 q=OUT/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(s.encode('utf8'))
 if q.suffix=='.py':ast.parse(s)
 CHANGES.append(dict(relative=rel,baseline_path=str(p),baseline_bytes=len(raw),baseline_SHA=H(p),candidate_bytes=q.stat().st_size,candidate_SHA=H(q)))
 return q
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def rejects(f):
 try:f()
 except (AssertionError,ValueError):return
 raise AssertionError('Invalid clock/queue fixture admitted')
def main():
 R.mkdir(exist_ok=True);put('POLICY50_CPU_PREPARATION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),no_remote_or_GPU=True));assert not OUT.exists();OUT.mkdir()
 prefix='job0/runtime/isaac/mod4/'
 clock=changed('job0/runtime/physics_clock.py',[
  ('100 Hz control','50 Hz policy control'),('control_s=.01','control_s=.02'),
  ('abs(control_s-.01)','abs(control_s-.02)'),('decimation=10000//us','decimation=20000//us'),
  ('decimation*us!=10000','decimation*us!=20000'),('policy_hz=100.','policy_hz=50.')])
 delivery=OLD/'job0/runtime/train/deploy/contract_rm2025_later.json';d=json.loads(delivery.read_bytes());assert d['policy_hz']==100;d['policy_hz']=50
 q=OUT/'job0/runtime/train/deploy/contract_rm2025_later.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(d,indent=2),encoding='utf8');CHANGES.append(dict(relative=q.relative_to(OUT).as_posix(),baseline_path=str(delivery),baseline_bytes=delivery.stat().st_size,baseline_SHA=H(delivery),candidate_bytes=q.stat().st_size,candidate_SHA=H(q)))
 queue=changed(prefix+'action_delay_physics_queue.py',[
  ('control_us=10000','control_us=20000'),
  ('physics_us==2500 and control_us==10000','physics_us==2500 and control_us in (10000,20000)'),
  ("state['control_us']==10000","state['control_us']==self.control_us"),
  ('physics_period_us=2500,control_period_us=10000','physics_period_us=2500,control_period_us=self.control_us')])
 adapter=changed(prefix+'action_delay_sdk_adapter.py',[
  ('import torch,types','import torch,types,os'),
  ('env.step_dt==.01 and env.cfg.decimation==4','env.step_dt==.02 and env.cfg.decimation==8'),
  ('seed,enabled=enabled)','seed,enabled=enabled,control_us=int(os.environ["MOD4_RESUME_QUEUE_CONTROL_US"]))')])
 phase=changed(prefix+'e3_public_recovery_phase_v1.py',[
  ('self.stable+1,0','self.stable+2,0'),('self.age+=1','self.age+=2')])
 # Phase age/stable retain their original integer 10 ms units and tensor schema.
 # A policy step advances two units; 3 s request and .5 s stability remain fixed.
 feedback=changed(prefix+'feedback_delay_runtime.py',[
  ('tick = env.common_step_counter',"tick = getattr(env, '_feedback_100hz_tick', env.common_step_counter)"),
  ('tick = int(self.common_step_counter)',"tick = int(getattr(self, '_feedback_100hz_tick', self.common_step_counter))"),
  ("        super().__init__(**kwargs)\n        assert sum", "        self._feedback_100hz_tick = 0\n        super().__init__(**kwargs)\n        self._install_feedback_100hz_sampling()\n        assert sum"),
  ("    def clean_policy(self):", "    def _install_feedback_100hz_sampling(self):\n        assert self.physics_dt == .0025 and self.step_dt == .02\n        previous = self.scene.update\n        def update(dt):\n            previous(dt)\n            tick = int(self._sim_step_counter)\n            if tick % 4 == 0:\n                self._feedback_100hz_tick = tick // 4\n                for name in WIDTHS:\n                    term = getattr(self.cfg.observations.policy, name)\n                    term.func(self, **term.params)\n        self.scene.update = update\n\n    def clean_policy(self):")])
 health=changed(prefix+'clock_training_health.py',[
  ('self.steps%24==0','self.steps%12==0'),('self.steps%600==0','self.steps%300==0'),
  ('self.steps*round(.01/self.env.physics_dt)','self.steps*self.env.cfg.decimation')])
 train=changed(prefix+'train_E3_fullstate_v1.py',[
  ('schedule=RM_SCHEDULE, gamma=0.99','schedule=RM_SCHEDULE, gamma=0.9801'),
  ('lam=0.95, desired_kl','lam=0.9025, desired_kl')])
 worker=changed('recovery_worker.py',[
  ("src=J/'source/RECOVERY_auto_source.pt'", "src=J/'source/RECOVERY_auto_source.pt'"),
  (" assert H(src)==task['source_SHA']", " assert H(src)==task['source_SHA']\n assert task['policy_clock_migration_authorized'] is True and task['source_policy_hz'] in (50,100)\n os.environ['MOD4_RESUME_QUEUE_CONTROL_US']=str(1000000//task['source_policy_hz'])"),
  ("  zero=save(OUT/'own_startup0.pt',0);", "  assert env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8\n  assert env._sim_step_counter==0\n  env._physics_action_delay.queue.control_us=20000\n  clock=dict(policy_hz=50,control_period_s=.02,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,contact_bin_s=.005,action_transition_delay_us=[0,2500,5000],source_policy_hz=task['source_policy_hz'],source_SHA=task['source_SHA'],same_173_96_state_schema=True,gamma=.9801,lam=.9025,rollout_decisions=24,rollout_simulated_seconds=.48,not_a_skill_pass=True)\n  put(OUT/'POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json',clock)\n  zero=save(OUT/'own_startup0.pt',0);")])
 # The worker is an unbound overlay: the new boundary source and Adam must be
 # bound by a new preparer after authenticated actual old-series closure.
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();cases=[]
 c=load('policy50_clock_candidate',clock)
 for dt in (.0005,.001,.002,.0025,.005):
  v=c.validate_clock(dt);assert abs(v['decimation']*dt-.02)<1e-12 and v['policy_hz']==50 and v['contact_bin_s']==.005
 rejects(lambda:c.validate_clock(.0025,.01));rejects(lambda:c.validate_clock(.003));rejects(lambda:c.validate_clock(.0025,.02,.01));assert c.fragments(3,2000)==[(1000,True),(1000,False)]
 cases.append('actual_clock_all_reviewed_dt_and_100Hz_unreviewed_dt_bin_negative_cases')
 qm=load('policy50_queue_candidate',queue);q=qm.PhysicsActionQueue(3,'cpu',20260928)
 neutral={'legs':torch.zeros(3,4),'wheels':torch.zeros(3,2)}
 for key in neutral:q.reset(key,torch.arange(3),neutral[key]);q.groups[key]['lag_steps'].copy_(torch.arange(3))
 for i in range(3):
  for key in neutral:q.submit(key,torch.ones_like(neutral[key])*(i+1),8*i)
  for tick in range(8*i,8*i+8):
   for key in neutral:
    q.apply(key,tick);z=q.receipt(key,tick)
    if tick>=8*i+2:assert z['actual_first_transition_delay_us'].tolist()==[0,2500,5000]
 saved=q.state_dict();q.validate_state(saved)
 bad=copy.deepcopy(saved);bad['control_us']=10000;rejects(lambda:q.validate_state(bad))
 fresh=qm.PhysicsActionQueue(3,'cpu',20260928,control_us=10000);fresh.load_state_dict(bad)
 assert fresh.control_us==10000
 rejects(lambda:q.submit('legs',torch.zeros(3,4),20))
 cases.append('real_50Hz_target_queue_8_ticks_0_2point5_5ms_latency_and_100Hz_resume_compatibility')
 pm=load('policy50_phase_candidate',phase);p=pm.RecoveryPhase(1,'cpu');p.reset(torch.tensor([0]));z=torch.zeros(1)
 for i in range(24):p.begin();p.update(torch.tensor([-1.]),z,z);assert not p.credited.any()
 p.begin();p.update(torch.tensor([-1.]),z,z);assert p.credited.all() and p.stable.item()==50
 for i in range(125):p.begin();p.update(torch.tensor([-1.]),z,z)
 assert p.age.item()==300 and p.mode().item()==0
 p2=pm.RecoveryPhase(1,'cpu');p2.load_state_dict(p.state_dict());assert torch.equal(p2.age,p.age)
 cases.append('real_phase_25_decisions_half_second_credit_150_decisions_three_second_request_and_schema_roundtrip')
 # Execute the actual added scene callback against a local fake clock. This
 # verifies 100 Hz feedback updates within 50 Hz policy without Isaac or GPU.
 tree=ast.parse(feedback.read_text('utf8'));cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='DelaySensorMod4Env');fn=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name=='_install_feedback_100hz_sampling');e={'WIDTHS':{'base_ang_vel':3,'projected_gravity':3,'leg_pos':4,'leg_vel':4,'wheel_vel':2}};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual candidate feedback callback>','exec'),e)
 from types import SimpleNamespace
 calls=[];terms=SimpleNamespace(**{k:SimpleNamespace(func=lambda env,_k=k,**kw:calls.append((_k,env._feedback_100hz_tick)),params={}) for k in e['WIDTHS']});env=SimpleNamespace(physics_dt=.0025,step_dt=.02,scene=SimpleNamespace(update=lambda dt:None),cfg=SimpleNamespace(observations=SimpleNamespace(policy=terms)),_sim_step_counter=0)
 e['_install_feedback_100hz_sampling'](env)
 for tick in range(1,17):env._sim_step_counter=tick;env.scene.update(.0025)
 assert len(calls)==20 and {v for _,v in calls}=={1,2,3,4}
 cases.append('actual_feedback_callback_100Hz_inside_50Hz_policy_no_20ms_feedback_latency_relabel')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('POLICY50_ISOLATED_OVERLAY_AND_CLOCK_COMPONENTS_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_components=True,changes=CHANGES,cases=cases,source_runtime_kind='last verified unchanged original E3 automatic series runtime; fixture copy only',target_GPU_runtime_admission_passed=False,source_bound_to_latest_closed_model=False,deployed=False,actual_50Hz_GO=False,actual_50Hz_PPO=False,original_100Hz_boundary_request_sent=False,authentication_pending=True,phase_units='10ms integer units retained; increment two per policy decision',feedback_sampling='100Hz before scale, original 0/10ms delay and private RNG preserved; actual target SDK callback integration still unverified',PPO_temporal_discount=dict(gamma_before=.99,gamma_after=.9801,lam_before=.95,lam_after=.9025,preserve_per_second_exponents=True,rollout_steps=24),core_network_optimizer_STD_unchanged=True,no_remote_GPU_Task_or_canonical_IO=True,CPU_RNG_unchanged=True))
 print(json.dumps(dict(component_CPU_passed=True,cases=len(cases),changed_files=len(CHANGES),deployed=False,actual_50Hz_GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('POLICY50_CPU_PREPARATION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once=True,no_remote_GPU_or_account_change=True));raise
