"""Freeze two existing nominal landing-equilibrium schedules; nominal admission."""
from pathlib import Path
import ast,hashlib,json,copy
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'MINIHOP_LANDING_V3/preflight001/RESULT.json').read_bytes());assert qa['failures']==0 and qa['physics_steps']==0
base=json.loads((R/'batches/r45_quarantine4/r45_quarantineDR_4221.json').read_bytes())
specs=[('l40',dict(file='JUMP270_V1/GAIN_BANK.json',bank_key='landing')),('l20',dict(file='nominal_gain_v1.json'))]
configs=[]
for label,spec in specs:
    c=copy.deepcopy(base);name=f'r46_{label}_nominal';c.update(case_id=name,cohort='new_nominal_landing_schedule_TRAIN',nominal=True,seed=0,landing_gain=spec)
    c['hop'].update(landing_transition_enable=True,landing_transition_s=.20)
    configs.append((name,c))
source=[]
for f in('MINIHOP_LANDING_V3/controller.py','run_minihop_landing_v3.py',Path(__file__).name,'JUMP270_V1/GAIN_BANK.json','nominal_gain_v1.json'):
    raw=(R/f).read_bytes();source.append(dict(path=f,SHA=hashlib.sha256(raw).hexdigest()))
keys=['complete','stop','controls','physics_steps','first_all_world_air_s','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m',
      'end_stable_s','proposed_flat_clear80mm_recover2s_v2','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','peak_positive_mechanical_power_W','trace_artifact','physical_artifact']
launch(R,'r46_landing_nominal2','run_minihop_landing_v3.py',configs,dict(kind='R46_CAPTURE_REFERENCE_GAIN_SCHEDULE_NOMINAL_ADMISSION',
       source_before_physics=source,candidates_frozen=specs,landing_transition_s=.20,observer_quarantine_after_push_s=.50,
       unchanged='original_model_DR_actuator_path_and_v2_private_grade',controller_change='smooth_capture_only_K_and_nominal_feedforward_and_leg_position_reference',
       default_features_disabled=True,no_trusted_contact_cue=True,not_hardware_or_contact_FSM_release=True,
       next_DR_rule='only candidates passing unchanged nominal flat80mm/no-guide-hard/endstable2s gate may enter new paired4221..4224 TRAIN without source changes'),keys,max_workers=2)
