"""Same8TRAIN paired landing-profile ablation after actual R58 admission.
Only landing_gain file changes vs R57, hence coupled K/ff/eq/ref, not height-only.
"""
from pathlib import Path
import copy,hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;A=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003';D=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_paired004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base_path=R/'results/r58_tall0_position_rm/result.json';raw=base_path.read_bytes();r=json.loads(raw)
assert r['complete']is True and r['proposed_manual_first_bar_clear_stop_v1']is True
assert r['config']['nominal']is True and r['config']['landing_gain']=={'file':'TALL_ROUGH_BANK_V1/gain_delta0.json'}
assert r['config']['hop']['position_trigger_enable']is True
refs=json.loads((A/'SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
base=copy.deepcopy(r['config']);cases=[];pairs=[]
def neutral(c):
    v=copy.deepcopy(c)
    for k in('case_id','cohort','landing_gain'):v.pop(k,None)
    return v
for seed in range(4501,4509):
    name=f'r59_tall0_RM_DR_{seed}';c=copy.deepcopy(base);c.update(case_id=name,nominal=False,seed=seed,cohort='R59_PAIRED_LANDING_PROFILE_TRAIN_NOT_HOLDOUT')
    bp=R/f'results/r57_position_RM_DR_{seed}/result.json';br=bp.read_bytes();old=json.loads(br)
    assert neutral(c)==neutral(old['config'])and old['config']['landing_gain']=={'file':'nominal_gain_v1.json'}
    cases.append((name,c));pairs.append(dict(seed=seed,baseline_result_path=str(bp),baseline_SHA=hashlib.sha256(br).hexdigest(),baseline_not_rerun=True))
D.mkdir(exist_ok=False)
dump(D/'SOURCE_PREEXEC.json',dict(files=refs,launcher_SHA=sha(Path(__file__)),nominal_admission_result_SHA=hashlib.sha256(raw).hexdigest(),paired_baselines=pairs))
p=dict(kind='R59_TALL0_LANDING_PROFILE_PAIRED_TRAIN',configs=cases,max_workers=4,
    selection='Nearest existing higher landing equilibrium delta0 chosen as TRAIN hypothesis for more geometric reserve, not a certified cure; original nominal geometry also had positive margin.',
    only_config_control_change='landing_gain file; V3 interpolates K/ff/eq/ref together. Scheduler/relativetimes/guards/DR/driver/gates all unchanged.',
    same8TRAIN_not16independent_samples=True,old_R55_R57_results_and_H1_H2_H4_H5_immutable=True,
    full_original_D0_D7_once_no_cancellation=True,original_100Hz_sensors_no_RAW2K=True,
    robot_failures_continue_and_preserved=True,software_errors_stop_future_waves=True,
    scope='manual local first6cmbar with.9mps approach and stop, not wholeRM/270mm/independentholdout/hardware',PH7_pending=True)
dump(D/'PROTOCOL.json',p)
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
launch(R,'r59_tall0_paired_DR8','run_manual_position_v4.py',cases,dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),max_physics_CPU=4,pairedTRAIN_not_holdout=True,PH7_pending=True),keys,max_workers=4)
