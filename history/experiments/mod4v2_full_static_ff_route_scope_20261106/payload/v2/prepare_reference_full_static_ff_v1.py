"""One M3 preparation, source-checked before creating the new runtime/case dir.
No SDK/models/FK/physics/old QA/raw. Original M2 artifacts untouched.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;OLD=R/'T01_REFERENCE_STATIC_FF_V1';D=R/'T01_REFERENCE_FULL_STATIC_FF_V1'

def replace_once(text,a,b):
 if text.count(a)!=1:raise RuntimeError('Source anchor is not unique: '+a)
 return text.replace(a,b,1)

def main():
 runtime=(R/'runtime_reference_static_ff_v1.py').read_text(encoding='utf-8')
 runtime=replace_once(runtime,'# Derived M2 runtime ONLY;','# Derived M3 runtime ONLY;')
 runtime=replace_once(runtime,'from controller_reference_static_ff_v1 import GroundController','from controller_reference_full_static_ff_v1 import GroundController')
 runner=(OLD/'run_reference_static_ff_v1.py').read_text(encoding='utf-8')
 runner=replace_once(runner,'# ONE M2 forward reference-static FF candidate;','# ONE M3 full reference-static FF candidate;')
 runner=replace_once(runner,'import runtime_reference_static_ff_v1 as runtime','import runtime_reference_full_static_ff_v1 as runtime')
 runner=replace_once(runner,'M2_REFERENCE_STATIC_FF_NOMINAL_CASE_NOT_WHOLE_T01_OR_RELIABILITY','M3_REFERENCE_FULL_STATIC_FF_NOMINAL_CASE_NOT_WHOLE_T01_OR_RELIABILITY')
 proto=json.loads((OLD/'PROTOCOL.json').read_text(encoding='utf-8'));oldgates=proto['gates'].copy()
 proto.update(id='MOD4V2_HW300N60_T01_REFERENCE_FULL_STATIC_FF_001',status='frozen_before_only_M3_nominal_case',
  scope='M3 retain full nominal reference static bias including common; original common LQR FEEDBACK/PD/K,driver and gates unchanged',
  controller='coord_soft_MOD4v2_reference_full_static_ff_v1',formal_cases=[dict(id='nominal_full_static_ref_ff',seed=520151,nominal=True,profile='slow')])
 proto['observer']['controller_candidate']='M3_reference_full_static_ff_only'
 proto['hypothesis']=dict(source='NEW M2 one-pass REDUCTION001 plus existing model formula;not old QA',
  observed_M2_ref_hip_excursion_peak_rad=.22076902837274615,
  observed_M2_removed_common_peak2_Nm=[.5752944557961261,.7311269973791825],
  common_deletion_breaks_full_reference_static_balance=True,
  rationale='restoring discarded nominal model common bias,not scanning gains/FF weight or changing reference geometry',
  unique_contact_failure_cause_proven=False,fixed_design_F0_not_measured=True,gas_curve_not_calibrated=True,
  static_design_not_measured_alpha=True,no_measured_or_proxy_force_or_DR_feedback=True,
  only_M3_one_case_no_automatic_DR=True,stage_mechanism_limit=3)
 proto['notes']+=['M3 replaces M2 projection with full reference model correction; no added reference-geometry change.',
  'Nominal simulation only; Python static model runtime is not 100Hz wallclock/ARM WCET qualified.']
 assert proto['gates']==oldgates and proto['direction_sign']==1 and proto['slow_command']['forward_m_s']==.3
 targets=[R/'runtime_reference_full_static_ff_v1.py',D/'run_reference_full_static_ff_v1.py',D/'PROTOCOL.json',D/'PREPARATION.json']
 if D.exists()or any(p.exists()for p in targets):raise RuntimeError('M3 prefix already exists,do not prepare twice')
 compile(runtime,str(targets[0]),'exec');compile(runner,str(targets[1]),'exec')
 compile((R/'controller_reference_full_static_ff_v1.py').read_text(encoding='utf-8'),'new_M3_controller','exec')
 D.mkdir(exist_ok=False)
 targets[0].write_text(runtime,encoding='utf-8');targets[1].write_text(runner,encoding='utf-8')
 targets[2].write_text(json.dumps(proto,indent=2),encoding='utf-8')
 pre=dict(kind='M3_PREPARATION_ONLY',simulation_model_builds=0,SDK_imports=0,forward=0,FK=0,physics_steps=0,
  old_raw_reads=0,only_change='M2 removed joint-common correction -> retain FULL nominal reference static correction',
  preserved='same public forward route/start,100Hz/.5ms/K/PD/shaper/estimator/DR/PD-target-D4-currentPD-twoDC/limits/windows/gates',
  cases_planned=1,case_id='v2_t01_reference_full_static_ff_nominal_slow_520151_001',source=str(OLD))
 targets[3].write_text(json.dumps(pre,indent=2),encoding='utf-8')
 print('M3_PREPARED_ONE_NOMINAL_520151; no models/FK/physics/oldraw; no coefficient/grid/gatechange')
if __name__=='__main__':main()
