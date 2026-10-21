from pathlib import Path
import hashlib,json,time,sys,shutil,torch
B=Path(__file__).resolve().parent;P=B/'H1_step270_candidate_uninstalled';sys.path.insert(0,str(P))
from step270_goal_and_scut_rates_candidate import Step270Events,Contract,scut_phase_rates
torch.set_num_threads(2);rng=torch.get_rng_state().clone();tests=[]
def fixture():
 t=Step270Events(1)
 v=dict(request=torch.tensor([False]),ground_ready=torch.tensor([True]),nonwheel_clean=torch.tensor([True]),known_integrity=torch.tensor([True]),wheel_N=torch.ones(1,2)*10,wheel_bottom_world_z=torch.zeros(1,2),wheel_contact_platform=torch.zeros(1,2,dtype=torch.bool),wheel_footprints_inside_top=torch.zeros(1,2,dtype=torch.bool),both_wheel_edge_crossed=torch.tensor([False]),root_vz=torch.zeros(1),planar_speed=torch.zeros(1),roll=torch.zeros(1),pitch=torch.zeros(1),heading_error=torch.zeros(1))
 for _ in range(80):t.physical(**v)
 v.update(request=torch.tensor([True]),ground_ready=torch.tensor([False]),wheel_N=torch.zeros(1,2),wheel_bottom_world_z=torch.ones(1,2)*.28,root_vz=torch.ones(1))
 for _ in range(16):t.physical(**v)
 return t,v
def land(t,v,**changes):
 v.update(wheel_N=torch.ones(1,2)*10,wheel_bottom_world_z=torch.ones(1,2)*.270,wheel_contact_platform=torch.ones(1,2,dtype=torch.bool),wheel_footprints_inside_top=torch.ones(1,2,dtype=torch.bool),root_vz=torch.zeros(1),both_wheel_edge_crossed=torch.tensor([True]))
 v.update(changes)
 for _ in range(220):t.physical(**v)
 return bool(t.success[0])
def test(name,fn):assert fn(),name;tests.append(dict(name=name,passed=True))
def success():
 t,v=fixture();v['both_wheel_edge_crossed'][:]=True;t.physical(**v);return land(t,v)
test('actual_270mm_top_clearance_and_both_wheel_landing_stable_fixture_succeeds',success)
for name,change in [
 ('flight_apex_without_platform_hit_rejected',dict(wheel_contact_platform=torch.zeros(1,2,dtype=torch.bool))),
 ('one_wheel_on_platform_rejected',dict(wheel_contact_platform=torch.tensor([[True,False]]))),
 ('wheel_footprint_outside_top_rejected',dict(wheel_footprints_inside_top=torch.tensor([[True,False]]))),
 ('floor_landing_after_high_COM_not_top_landing',dict(wheel_bottom_world_z=torch.zeros(1,2))),
 ('heading_drift_point3_rejected',dict(heading_error=torch.ones(1)*.3)),
 ('planar_speed_point04_rejected',dict(planar_speed=torch.ones(1)*.04)),
 ('nonwheel_contact_rejected',dict(nonwheel_clean=torch.tensor([False]))),
]:
 def run(change=change):
  t,v=fixture();v['both_wheel_edge_crossed'][:]=True;t.physical(**v);return not land(t,v,**change)
 test(name,run)
def low():
 t,v=fixture();v['wheel_bottom_world_z'][:]=.269;v['both_wheel_edge_crossed'][:]=True;t.physical(**v);return not land(t,v)
test('269mm_edge_crossing_never_credits_270mm_clearance',low)
def no_ground():
 t=Step270Events(1);_,v=fixture();v['both_wheel_edge_crossed'][:]=True
 for _ in range(20):t.physical(**v)
 return not land(t,v)
test('air_drop_without_prepared_ground_takeoff_rejected',no_ground)
for name,key,value in [('unknown_integrity_rejected','known_integrity',torch.tensor([False])),('nonfinite_witness_rejected','root_vz',torch.tensor([float('nan')]))]:
 def reject(key=key,value=value):
  t,v=fixture();v[key]=value
  try:t.physical(**v)
  except ValueError:return True
  return False
 test(name,reject)
def below_min():
 try:Step270Events(1,contract=Contract(platform_top_m=.269))
 except ValueError:return True
 return False
test('configuration_below_human_minimum_rejected',below_min)
# SCUT mathematical branches compared to independent scalar expectations.
r=scut_phase_rates(push=torch.tensor([True,True,False]),airborne=torch.tensor([False,False,True]),landed=torch.tensor([False,False,True]),vz=torch.tensor([-.1,1.,2.]),release_reference_vz=torch.tensor([2.,2.,2.]),wheel_torque=torch.zeros(3,2),wheel_bottom_relative_base=torch.ones(3,2)*-.22,heading_error=torch.zeros(3),planar_speed=torch.zeros(3))
test('SCUT_positive_takeoff_velocity_formula_exact',lambda:torch.equal(r['push_vz'],torch.tensor([0.,1.,0.])))
test('SCUT_release_shortfall_formula_exact',lambda:torch.equal(r['release_shortfall'],torch.tensor([2.1,1.,0.])))
test('SCUT_airwheel_zero_torque_and_below_base_formulas',lambda:torch.equal(r['air_wheel_zero_torque'],torch.tensor([0.,0.,1.])) and torch.equal(r['wheel_below_base'],torch.tensor([0.,0.,1.])))
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
refs=json.loads((B/'reports/H1_SCUT_270MM_STEP_MINIMUM_HUMAN_TARGET_AND_SOURCE_CPU_ACTUAL.json').read_bytes())['reference_sources'];out=P/'reference_source';out.mkdir()
copies=[]
for row in refs:
 p=Path(row['path']);dest=out/p.name;assert not dest.exists();shutil.copy2(p,dest);copies.append(dict(path=str(dest),original_path=str(p),SHA=row['SHA'],bytes=row['bytes']))
v=dict(epoch=time.time(),passed_source_and_CPU_fixture_review=True,CPU_cases=tests,count=len(tests),candidate=dict(path=str(P/'step270_goal_and_scut_rates_candidate.py'),SHA=hashlib.sha256((P/'step270_goal_and_scut_rates_candidate.py').read_bytes()).hexdigest()),source_references=copies,minimum_step_height_m=.270,physical_stable_seconds=.5,not_installed=True,no_actual_terrain_or_SDK_admission=True,no_GPU_or_native_or_training=True,no_current_reward_or_actor_or_canonical_change=True,limits='Synthetic CPU fixtures validate event logic and cited scalar reward branches only. No full SCUT state-machine port/scene adapter/learning runtime/planner/weights has been admitted. CPU success is not actual step performance.')
(B/'reports/H1_STEP270_CANDIDATE_UNINSTALLED_SOURCE_AND_CPU_FIXTURES_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps({k:x for k,x in v.items() if k not in ('source_references','CPU_cases')}))
