"""New small supplement: source reference JSON range, no native/physics query."""
from pathlib import Path
import csv,datetime,hashlib,json,math,sys,traceback
HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'agent_existing_gas_model_audit_v1';L=HERE.parents[1];T=L.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1';sys.path.insert(0,str(PREV))
from gas_eye_length_and_nominal_force_candidate_v1 import from_import_contract
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranges(ages):
 out=[]
 for a in ages:
  if out and a==out[-1][-1]+1:out[-1].append(a)
  else:out.append([a])
 return [[x[0],x[-1]] for x in out]
put('ENTRY_CONSUMED_ACTUAL.json',dict(purpose='source-only scaled400 nominal law and existing9223 reference gas range',epoch=datetime.datetime.now().astimezone().isoformat(),no_runtime_model_or_physics=True))
checks=[]
try:
 C=B/'job0/assets/import_contract.json';P=B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json'
 c=json.loads(C.read_bytes());ref=json.loads(P.read_bytes());SHA=H(P)
 assert SHA=='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3';checks.append('exact_existing9223_reference_JSON_source_SHA')
 ages=ref['ages'];rows=ref['packed73'];mask=ref['mask73'];names=ref['joint_names'];assert len(names)==30 and len(set(names))==30 and len(ages)==len(rows)==len(mask)==301
 assert all(len(row)==len(m)==73 and all(math.isfinite(v) for v in row) for row,m in zip(rows,mask));checks.append('301_source_goal_frames73_unique30_names_and_finite')
 result={};samples=[]
 for side in ('left','right'):
  mapping=from_import_contract(c,side);index=names.index(side+'_gas_slide');col=13+index
  q=[row[col] for row in rows];dq=[row[43+index] for row in rows];length=[mapping.length_m(x) for x in q];q200=mapping.q_for_length_m(.2)
  above=[int(a) for a,L in zip(ages,length) if L>.2+1e-9];below=[int(a) for a,L in zip(ages,length) if L<.14-1e-9];outside_old=[int(a) for a,x in zip(ages,q) if x<mapping.original_q_limits_m[0]-1e-9 or x>mapping.original_q_limits_m[1]+1e-9]
  oldf=[mapping.old_quasistatic_joint_effort_N(x) for x in q];newf=[2000.*(mapping.original_target_q_m-x) for x in q]
  assert all(abs(n-o*(400/700))<1e-9 for n,o in zip(newf,oldf));checks.append(side+'_k2000_exact400_over700_scaling_of_original_elastic_law')
  F200=2000.*(mapping.original_target_q_m-q200);F140=2000.*(mapping.original_target_q_m-mapping.q_for_length_m(.14))
  assert abs(F200-400)<.001 and abs(F140-520)<.001;checks.append(side+'_400_at200_520_at140_numeric_nominal_only')
  result[side]=dict(joint=side+'_gas_slide',joint_index0=index,packed73_position_column0=col,packed73_velocity_column0=43+index,
   min_q_m=min(q),min_q_ages=[a for a,x in zip(ages,q) if x==min(q)],max_q_m=max(q),max_q_ages=[a for a,x in zip(ages,q) if x==max(q)],
   min_eye_length_m=min(length),max_eye_length_m=max(length),max_excess_over200_m=max(0.,max(length)-.2),minimum_margin_below200_m=.2-max(length),
   above200_frame_count=len(above),above200_age_ranges=ranges(above),above200_ages=above,below140_frame_count=len(below),below140_age_ranges=ranges(below),outside_existing_q_limit_ages=outside_old,
   position_masked_in_frame_count=sum(m[col]>0 for m in mask),above200_with_positive_q_mask_count=sum((L>.2+1e-9) and (m[col]>0) for L,m in zip(length,mask)),
   velocity_min_max_m_s=[min(dq),max(dq)],scaled2000_nominal_elastic_force_range_over_reference_N=[min(newf),max(newf)],
   scale_new_old_k=2000/3500,unchanged_virtual_qref_m=mapping.original_target_q_m,scaled_nominal_elastic_at200_N=F200,scaled_nominal_elastic_at140_N=F140,
   old_joint_range_eye_m=[mapping.length_m(x) for x in mapping.original_q_limits_m],human_stroke_intersection_eye_m=[max(.14,mapping.length_m(mapping.original_q_limits_m[0])),min(.2,mapping.length_m(mapping.original_q_limits_m[1]))],
   retarget_own_reference_required_for_new200mm_hardware_goal=bool(above or below),
   check_scope='source planned-q table geometry, not actual body/closure/contact/actuation or real gas length')
  for a,x,L,old,new,m in zip(ages,q,length,oldf,newf,mask):samples.append(dict(side=side,age=a,q_m=x,eye_m=L,q_mask=m[col],exceeds_human200=L>.2+1e-9,below_human140=L<.14-1e-9,old3500_elastic_N=old,new2000_elastic_N=new))
 anybad=any(row['retarget_own_reference_required_for_new200mm_hardware_goal'] for row in result.values())
 value=dict(passed=True,checks=len(checks),check_names=checks,source_only=True,existing_reference=dict(path=str(P),bytes=P.stat().st_size,SHA=SHA),
  per_side=result,own_reference_retarget_required_for_new_hardware_goal=anybad,
  conclusion='Existing reference contains gas-eye positions beyond human200mm cap; preserving it as a400N/L200 hardware-feasible goal is not justified. A new closed-chain own-reference retarget is required; do not clip only gas q.' if anybad else 'No gas-eye table sample exceeds the inferred140..200 stroke. This source-range check is not dynamic/actual tracking/hardware qualification.',
  candidate_nominal=dict(stiffness_N_per_m=2000.,target_q_unchanged=True,elastic_curve_only_scaled_by=400/700,
   damping='original3Ns/m retained only as unmeasured engineering value; not scaled/identified from400N label',
   D5='if deliberately retained, independent.9..1.1 gives nominal endpoint360..440N; not measured purchased-spring distribution',force_200_N_approx=400.,force_140_N_approx=520.,ratio140_to200=1.3,
   curve_status='new nominal approximation retaining old relative elastic progression convention; no purchased force curve supplied',
   backend='same implicit linear actuator could express it only after all hardcoded3500/source/readback guards are coherently rebound in a NEW source; no setter/patch executed'),
  old_reference_and_all_frozen_files_unchanged=True,no_old_reference_retarget_or_new_IK_performed=True,no_nativequery_actor_physics_SDK_GPU_remote_model_or_raw=True)
 put('SCALED400_ELASTIC_CURVE_AND_9223_REFERENCE_GAS_RANGE_ACTUAL.json',value)
 with (HERE/'REFERENCE_QGAS_EYE_LENGTH_AND_SCALED_FORCE_SOURCE_ONLY.csv').open('x',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(samples[0]));writer.writeheader();writer.writerows(samples)
 inputs=[C,P,PREV/'gas_eye_length_and_nominal_force_candidate_v1.py',PREV/'FROZEN_SHA_INDEX_ACTUAL.json']
 put('SOURCE_INPUT_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in inputs],reference_JSON_is_goal_source_not_raw_trajectory_or_policy=True))
 print(json.dumps(dict(passed=True,checks=len(checks),per_side=result,own_reference_retarget_required=anybad),indent=2))
except BaseException:
 put('ORIGINAL_REFERENCE_RANGE_SOURCE_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),checks=checks,old_files_immutable=True));raise
