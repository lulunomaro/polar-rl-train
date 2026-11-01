"""Source/JSON-only mapping audit; no model,SDK import,asset or raw reader."""
from pathlib import Path
import ast,hashlib,json,time,traceback

N=Path(__file__).resolve().parent
T=N.parent
W=T.parent
PACKAGE=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package'
M=PACKAGE/'payload/job0/runtime/isaac/mod4'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def method(p,cls,name):
 text=p.read_text(encoding='utf8');tree=ast.parse(text)
 c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
 f=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return dict(file=ref(p),class_name=cls,method=name,line=f.lineno,end_line=f.end_lineno,
             source='\n'.join(text.splitlines()[f.lineno-1:f.end_lineno]))


def main():
 purpose=json.loads((N/'reports/PURPOSE_SOURCE_MAPPING_FROZEN.json').read_bytes())
 put(N/'reports/SOURCE_MAPPING_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=purpose['ID']))
 for row in purpose['inputs']:assert ref(Path(row['path']))==row
 p229=T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101/reports/ROOT229_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json'
 p228=T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101/reports/ROOT228V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json'
 r229=json.loads(p229.read_bytes())['original_parent']['result'];r228=json.loads(p228.read_bytes())['original_parent']['result']
 q=r229['proof'];old=r228['proof'];src=r229['actual_original_action_source'];adapter=r228['actual_action_source']
 assert q['actual_original_action_term_verified'] and q['original_process_receiver_verified']
 assert ref(M/'mod4_task.py')['SHA']==src['SHA']=='7e326cdd9c3507f16109b3503c3cffd37c6f5fa312b42451d2de513af9e2b993'
 assert hashlib.sha256(src['UTF8'].encode()).hexdigest()==src['SHA']
 assert ref(M/'action_delay_sdk_adapter.py')['SHA']==adapter['SHA']=='0053820a778b3c956bf1bd8754b269de28a35c7ea9fe2fb93f75061bf142b375'
 assert q['policy_order']==old['policy_order']==['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin']
 assert q['leg_scales']==[.5]*4 and q['leg_default_offsets']==[0.]*4
 assert (q['diff_min'],q['diff_max'])==(-1.0843,.85)
 contract_path=PACKAGE/'payload/job0/assets/import_contract.json';contract=json.loads(contract_path.read_bytes())
 delivery_path=PACKAGE/'payload/job0/runtime/train/deploy/contract_rm2025_later.json';delivery=json.loads(delivery_path.read_bytes())
 assert ref(contract_path)['SHA']=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
 limits={k:contract['joints'][k]['limits_si'] for k in q['policy_order']}
 assert limits['left_hip']==limits['right_hip']==[-.5,.5] and limits['left_crank']==limits['right_crank']==[-1.2,.9]
 assert delivery['leg_action_scale']==.5 and delivery['leg_kp']==60. and delivery['leg_kd']==2.
 methods=[method(M/'mod4_task.py','DelayedJointPositionAction','process_actions'),
          method(M/'mod4_task.py','_DelayMixin','process_actions'),
          method(M/'mod4_task.py','Mod4DCMotor','_clip_effort'),
          method(M/'action_delay_sdk_adapter.py','PhysicalActionDelayAdapter','_wrap'),
          method(M/'explicit_pd_component.py','ExplicitPD','coefficients'),
          method(M/'explicit_pd_sdk_adapter.py','ExplicitPDSDK','apply')]
 project=methods[0]['source']
 assert 'out=pa[:, 0]' in project and 'out=pa[:, 2]' in project
 assert 'out=pa[:, 1]' not in project and 'out=pa[:, 3]' not in project
 historical_joint=W/'MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008/reviewed_sources/joint_actions.py'
 historical_pd=W/'MOD4_D6_DAMPING_SOURCE_PREPARE_20261008/reviewed_sources/installed_actuator_pd.py'
 historical=[method(historical_joint,'JointAction','process_actions'),method(historical_joint,'JointPositionAction','apply_actions'),
             method(historical_pd,'IdealPDActuator','compute'),method(historical_pd,'DCMotor','compute'),method(historical_pd,'DCMotor','_clip_effort')]
 # These four scalar examples exercise only affine + the proven project CAD
 # projection. They do not execute inherited SDK processing or a physical plant.
 examples=[]
 for label,c_raw,h_raw in [('prompt_low_hip_high_crank',6.,1.67),('prompt_high_hip_low_crank',-6.,2.08),
                           ('negative_hip_high_crank',6.,-2.08),('raw6_is_not_joint_radians',6.,6.)]:
  c=.5*max(-6.,min(6.,c_raw));h=.5*max(-6.,min(6.,h_raw))
  projected=min(max(c,h+q['diff_min']),h+q['diff_max'])
  assert h==.5*h_raw and q['diff_min']-1e-12<=projected-h<=q['diff_max']+1e-12
  examples.append(dict(label=label,raw_crank=c_raw,raw_hip=h_raw,affine_crank=c,affine_hip=h,
   project_crank_target=projected,project_hip_unchanged=h,hip_outside_static_joint_range=not(-.5<=h<=.5),
   example_only_not_actual_target_or_torque_measurement=True))
 original_env=json.loads((PACKAGE/'payload/job0/original_run_manifest.json').read_bytes())['env']
 selected_env={k:v for k,v in original_env.items() if any(x in k for x in ('DR_OFF','MILD_DR','EXPLICIT_PD','ACTION_DELAY','EFFORT_NOISE','SENSOR_PROFILE','FEEDBACK_DELAY'))}
 mapping=[]
 reward_order=[0,1,4,2,3,5]
 for i,name in enumerate(q['policy_order']):
  mapping.append(dict(policy_slot=i,name=name,leg_or_wheel_slot=i if i<4 else i-4,
   metadata_actuated_order_slot=contract['actuated_joint_names'].index(name),
   reward_named_order_slot=reward_order.index(i),static_joint_limits=limits[name],
   scale=.5 if i<4 else delivery['wheel_action_scale'],offset=0.))
 report=dict(epoch=time.time(),ID=purpose['ID'],status='SOURCE_MAPPING_REVIEW_NOT_RUNTIME_FIX_OR_LEARNING',
  source229_report=ref(p229),source228_report=ref(p228),actual229_binding=q,
  previous228_original_action_guard_false_preserved=old['actual_original_action_term_verified'] is False,
  exact_actual_source_matches=[ref(M/'mod4_task.py'),ref(M/'action_delay_sdk_adapter.py')],
  policy_and_target_mapping=mapping,static_import_contract=ref(contract_path),delivery_contract=ref(delivery_path),
  mechanical_stop=contract['mechanical_stop'],training_window=contract['training_window'],
  consumed_project_methods=methods,historical_SDK_methods=historical,
  historical_SDK_scope='Read-only old210/3.0-beta source references;current72 base JointAction/apply/actuator sourceSHA is NOT in actual228/229 proof and remainsUNKNOWN',
  original_selected_environment=selected_env,scalar_project_boundary_examples=examples,
  nominal_PD_hypothetical_examples=[dict(hip_target=.835,hypothetical_q=.5,hypothetical_qdot=0.,kp=60.,kd=2.,nominal_PD_before_torque_envelope=20.1),
                                   dict(hip_target=1.04,hypothetical_q=.5,hypothetical_qdot=0.,kp=60.,kd=2.,nominal_PD_before_torque_envelope=32.4)],
  main_finding='Proven project CAD projection changes crank only;static hip joint limits±.5 are narrower than clip6*.5. Source does not establish a hip processed-target clip at±.5.',
  SDK_inherited_path='Historical reference:affine,optional cfg.clip,position target setter,explicitPD truejoint error,DC torque-speed clip,outputgain,secondclip for white_v3;current72 exact inherited methods/cfg.clip value UNKNOWN',
  PD_DR='Project D7 changes explicit motor Kp/Kd factors[.95,1.05],nominal60/2,wheel0/.6;implicit motor drive stiffness/damping remain0;does not change targets or hardware envelope',
  sensor_action_separation='D3 delays/noises actor observation channels;D4 delays already processed coherent targets0/2500/5000us;neither source changes hip target magnitude',
  unknowns=['Actual current72 inherited SDK JointAction/process/apply/set_target/PD source hashes and resolved cfg.clip',
            'No actual processed target or joint_pos_target time series is read here',
            'CAD/import joint range is source metadata;no new actual PhysX limits readback',
            'No measured torque/saturation fraction,PD error,current gains or motor response is inferred',
            'q near.5 is compatible with static upper joint range but not proof of clipping or unique flight/heading cause'],
  model_NPZ_USD_actualraw_Torch_SDK_GPU_network_Git_calls=0,old_fixture_replays=0,
  physical_controls=0,changes_to_225_E0_W35_rewards_physics_guards_or_model=0,new_skill_or_SuperMimic_completion=False)
 put(N/'reports/ACTION_PROCESS_APPLY_MAPPING_SOURCE_REVIEW_ACTUAL.json',report)
 print(json.dumps(dict(source_review_saved=True,actual_project_SHA_matched=True,scalar_examples=len(examples),new_physical_controls=0,model_reads=0)))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/SOURCE_MAPPING_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
