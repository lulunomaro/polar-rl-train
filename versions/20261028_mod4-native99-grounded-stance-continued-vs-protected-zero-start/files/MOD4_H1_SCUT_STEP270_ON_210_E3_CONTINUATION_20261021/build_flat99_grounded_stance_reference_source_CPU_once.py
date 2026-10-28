from pathlib import Path
import ast,copy,hashlib,json,os,sys,time
T=Path(__file__).resolve().parent;B=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028/payload';S=T/'H1_NATIVE97_FLAT_FROZEN_MOTION_WM_N1_V98_20261028';F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/H1_99_STANCE_GOAL_AND_CLEAN_START_SOURCE_V1/reference_candidate_v1'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,v):
 with (F/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not F.exists();F.mkdir()
put('SOURCE_DERIVATION_PURPOSE_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='Use existing NEW98 grounded pre-request physical evidence to calibrate only the absolute body-height cue for the same50mm wheel-clearance task. Concrete new reference source purpose, no model statistics or Git-driven raw read.',no_models_GPU_physics_or_remote=True))
index=json.loads((S/'reports/FROZEN98_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes());row=next(x for x in index['rows'] if x['relative']=='case/episode/ACTUAL_100HZ_CONTROLS.jsonl');raw=Path(row['local_path']).read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'];controls=[json.loads(x) for x in raw.decode('utf8').splitlines()];assert len(controls)==500
selected=[x for x in controls if 50<=x['age_for_action'][0]<150];assert len(selected)==100
import torch,statistics,math
torch.set_num_threads(2);assert not torch.cuda.is_initialized();sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps')]
from native_flat_jump_adapter_v1 import OwnFlatJumpReference,encode_frame
from flat_jump_phase_objective_source_v1 import FlatJumpPhase
floor_offsets=[];wheelmax=0.;tiltmax=0.;speedmax=0.
for item in selected:
 state=item['terminal_pre_reset']['state'];height=state['metrics']['wheel_bottom_above_floor_m'];tilt=state['metrics']['tilt_rad'];speed=math.hypot(*state['root13_sdk_xyzw'][7:9]);age=item['age_for_action'][0]
 assert max(abs(v) for v in height)<.002 and abs(tilt)<.15 and speed<.15,'selected source window is not the declared grounded upright slow stance'
 assert not bool(FlatJumpPhase().targets(torch.tensor([age]),torch.tensor([0]))['flight'][0])
 floor_offsets.append(state['root13_sdk_xyzw'][2]-min(height));wheelmax=max(wheelmax,max(abs(v) for v in height));tiltmax=max(tiltmax,abs(tilt));speedmax=max(speedmax,speed)
baseline=statistics.median(floor_offsets)
oldpath=B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json';originalraw=oldpath.read_bytes();old=json.loads(originalraw);assert H(originalraw)=='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502';new=copy.deepcopy(old);oldbase=old['neutral_packed73'][2]
new['neutral_packed73'][2]=baseline
calibration=dict(schema='mod4.flat99.grounded_standing_body_height_cue.v1',actual_case_seed=20260928,source_control_text=row,predeclared_private_age_window=[50,149],sample_controls=100,estimator='median(root_z - minimum_actual_wheel_bottom_above_floor)',baseline_body_height_m=baseline,offset_range_m=[min(floor_offsets),max(floor_offsets)],original_initial_crouch_body_height_m=oldbase,only_body_height_neutral_value_changed=True,source_wheel_max_abs_m=wheelmax,source_tilt_max_rad=tiltmax,source_planar_speed_max_m_s=speedmax,grounded_standing_witness_not_jump_demo=True,no_joint_motion_or_dynamics_proof=True,not_a_new_runtime_reset_or_precision_gate=True)
new['metadata']['stance_calibration']=calibration;new['metadata']['neutral_source']='Original initial witness retained except body-height cue calibrated from declared actual grounded NEW98 stance window; joint trajectory remains unmeasured and masked'
check=copy.deepcopy(new);check['neutral_packed73'][2]=oldbase;check['metadata'].pop('stance_calibration');check['metadata']['neutral_source']=old['metadata']['neutral_source'];assert check==old
with (F/'ORIGINAL_OWN_FLAT5CM_REFERENCE_UNMODIFIED.json').open('xb') as f:f.write(originalraw)
put('OWN_FLAT5CM_STANCE99_REFERENCE_SOURCE.json',new)
old_provider=OwnFlatJumpReference(old);new_provider=OwnFlatJumpReference(new)
ages=torch.tensor([0,50,100,149,190,199,200,205,210,215,221,300,450,460,499]);frames=encode_frame(ages,torch.zeros_like(ages));a=old_provider.future_goal(frames,10);b=new_provider.future_goal(frames,10);assert a.shape==b.shape==(len(ages),1460)
expected=torch.zeros_like(a)
for i in range(10):expected[:,i*146+2]=baseline-oldbase
assert torch.allclose(b-a,expected,atol=2e-7,rtol=1e-6)
for i in range(10):
 assert torch.equal(a[:,i*146+73:(i+1)*146],b[:,i*146+73:(i+1)*146])
 assert torch.equal(a[:,i*146+13:i*146+73],b[:,i*146+13:i*146+73])
assert new['metadata']['height_m']==.05 and new['metadata']['control_dt_s']==.01 and new['metadata']['physical270_success_unchanged'] is True and new['metadata']['joint_trajectory_unmeasured_and_masked'] is True
def validate(document):
 c=document['metadata']['stance_calibration'];assert c==calibration and document['neutral_packed73'][2]==baseline
 d=copy.deepcopy(document);d['neutral_packed73'][2]=oldbase;d['metadata'].pop('stance_calibration');d['metadata']['neutral_source']=old['metadata']['neutral_source'];assert d==old
validate(new)
negatives=[]
for key in ('body_height','height_target','source_SHA','joint_pose'):
 bad=copy.deepcopy(new)
 if key=='body_height':bad['neutral_packed73'][2]+=.01
 elif key=='height_target':bad['metadata']['height_m']=.10
 elif key=='source_SHA':bad['metadata']['stance_calibration']['source_control_text']['SHA']='0'*64
 else:bad['neutral_packed73'][13]+=.01
 try:validate(bad)
 except AssertionError:negatives.append(key)
 else:raise AssertionError('undeclared reference change passed '+key)
put('STANCE99_REFERENCE_SOURCE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),source_math_only=True,calibration=calibration,original_reference_SHA=H(originalraw),candidate_reference_SHA=H((F/'OWN_FLAT5CM_STANCE99_REFERENCE_SOURCE.json').read_bytes()),old_body_cue_range_m=[oldbase,oldbase+.05],new_body_cue_range_m=[baseline,baseline+.05],exact_only_known_goal_body_z_values_shifted=True,goal_dimensions_and_all_masks_and_unknown_joint_paths_unchanged=True,negative_cases_rejected=negatives,reward_phase_actions_plant_reset_RNG_skill_criteria_unchanged=True,no_model_actor_WM_forward_GPU_SDK_physics_or_remote=True,not_installed_no_GO_no_learning_gain_claim=True))
(F/'HANDOFF.md').write_text('Source-only candidate99 fixes the absolute body-height cue using a predeclared grounded stance window of already collected NEW98 own-plant evidence. Same5cm wheel-clearance objective; all joint goals stay unknown/masked, no invented jump limb path. Only neutral_packed73[2] plus provenance metadata differ from b4d801. Physical reset/RNG/phase/reward/actions/400 plant unchanged. Requires typed output reference/contract, exact current97 continuation versus protectednative0 source admission before genuine paired finite GO. Neither branch is training yet. This does not prove causality, airborne model accuracy or mechanical feasibility.\n',encoding='utf8')
put('FROZEN_STANCE99_REFERENCE_SOURCE_INDEX_V1.json',dict(frozen=True,rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p.read_bytes())) for p in sorted(F.iterdir()) if p.is_file()]))
print(json.dumps(dict(passed=True,old_baseline_m=oldbase,new_baseline_m=baseline,new_apex_body_cue_m=baseline+.05,source_only_no_training=True)))
