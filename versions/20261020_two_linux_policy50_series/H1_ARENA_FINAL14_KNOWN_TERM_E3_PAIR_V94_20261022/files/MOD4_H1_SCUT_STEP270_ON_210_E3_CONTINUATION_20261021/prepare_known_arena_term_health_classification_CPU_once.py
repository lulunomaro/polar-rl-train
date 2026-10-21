from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,time,torch
T=Path(__file__).resolve().parent;R=T/'reports';P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022'
old=P/'payloads/h1/job0/runtime/isaac/mod4/clock_training_health.py';D=T/'health_classifier_candidate_V1_UNINSTALLED';assert not D.exists();D.mkdir()
s=old.read_text('utf8');needle="ORDINARY_TERMS=frozenset(('bad_orientation','base_contact','low_base','closure'))";assert s.count(needle)==1
new=s.replace(needle,"ORDINARY_TERMS=frozenset(('bad_orientation','base_contact','low_base','closure','h1_step270_arena_exit'))")
target=D/'clock_training_health.py';target.write_text(new,encoding='utf8')
def rest(text):
 tree=ast.parse(text);tree.body=[x for x in tree.body if not (isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ORDINARY_TERMS' for t in x.targets))];return ast.dump(tree,include_attributes=False)
assert rest(s)==rest(new)
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
mods=dict(original=module(old,'health_old'),candidate=module(target,'health_known_arena'))
fixtures=T/'known_arena_health_CPU_fixtures';fixtures.mkdir();cases=[]
for version,event,nan,max_mimic,expect_stop in [('original','h1_step270_arena_exit',False,.001,True),('candidate','h1_step270_arena_exit',False,.001,False),('candidate','unregistered_test_term',False,.001,True),('candidate','mimic',False,.001,True),('candidate','closure',False,.001,False),('candidate',None,True,.001,True),('candidate',None,False,.011,True)]:
 names=('time_out','bad_orientation','base_contact','low_base','closure','mimic','h1_step270_arena_exit','unregistered_test_term');n=2
 class Terms:
  active_terms=names
  terminated=torch.zeros(n,dtype=torch.bool)
  def get_term(self,k):return torch.tensor([bool(event==k and env.count==1),False])
 tm=Terms();env=SimpleNamespace(num_envs=n,device='cpu',termination_manager=tm,_integrated_contact=SimpleNamespace(tick=0),physics_dt=.0025,step_dt=.01,_mod4_max_closure=.0038,_mod4_max_mimic=max_mimic,count=0)
 env.scene={'robot':SimpleNamespace(data=SimpleNamespace(root_state_w=torch.zeros(n,13),joint_pos=torch.zeros(n,30),joint_vel=torch.zeros(n,30)))}
 def step(action):
  env.count+=1;env._integrated_contact.tick+=4;tm.terminated=torch.tensor([bool(event and env.count==1),False]);return ()
 env.step=step;folder=fixtures/(str(len(cases))+'_'+version);folder.mkdir();health=mods[version].ClockTrainingHealth(env,folder)
 action=torch.zeros(n,6)
 if nan:action[0,0]=float('nan')
 for _ in range(24):env.step(action)
 result=health.write();actual=(folder/'STOP_AFTER_SAVE').exists();assert actual==expect_stop
 cases.append(dict(version=version,event=event,nonfinite_fixture=nan,max_mimic=max_mimic,expected_stop=expect_stop,actual_stop=actual,ordinary=result['ordinary_episode_reset_events'],integrity=result['integrity_task_reset_events'],unknown=result['unknown_task_reset_events'],passed=True))
actual=json.loads((P/'reports/H1_EARLY_COMPLETE_FINAL_AND_STOP_REASON_ACTUAL.json').read_bytes());healthrows=[json.loads(text) for name,text in actual['actual_early_H1_complete_texts'].items() if name.endswith('CLOCK_TRAINING_HEALTH.json')];assert len(healthrows)==1
v=healthrows[0];assert v['unknown_task_reset_events']==v['termination_events_by_reason']['h1_step270_arena_exit']==1 and v['integrity_task_reset_events']==0 and not v['nonfinite_observed'] and v['termination_reason_coverage_exact'] and v['actual_physics_callbacks']==v['expected_physics_callbacks']==1344
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=dict(epoch=time.time(),passed_known_task_term_CPU_classification=True,original_actual_health_unknown1_and_stop_preserved=True,not_relabel_original_health_pass=True,only_added_ordinary_name='h1_step270_arena_exit',normalized_rest_AST_exact=True,original=dict(path=str(old),SHA=H(old)),candidate=dict(path=str(target),SHA=H(target)),relative='job0/runtime/isaac/mod4/clock_training_health.py',cases=cases,all_other_unknown_mimic_nonfinite_callback_guards_unchanged=True,source_known_term_event_count=1,actual_H1_saved_complete14_Adam675020_pending_wholeCPU=True,candidate_not_installed=True,no_GPU_native_or_query_replayed=True,requires_new_unused_root_after_current_E3_allout_and_original_cost_settled=True)
with (R/'H1_ARENA_KNOWN_ORDINARY_TERM_HEALTH_CLASSIFIER_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
