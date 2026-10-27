"""Write-once local source/status scalar audit. No torch, NPZ, model or simulator."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math,ast
D=Path(__file__).resolve().parent
T=D.parent.parent
B=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
S3=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'
FILES={
 'hard_cfg':B/'job0/runtime/isaac/mod4/mod4_task.py',
 'mdp':B/'source/converted_MOD4_jump_mdp_v4.py',
 'objective_v1':B/'source/own_step_differentiable_objective_v1.py',
 'objective_v2':B/'source/own_step_differentiable_objective_v2.py',
 'bridge':B/'source/native_wheel_leg_bridge_v4.py',
 'geometry':B/'source/supermimic_wheel_leg_v3/geometry.py',
 'status':S3/'actual210/seed_20260928/episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json',
 'admission':S3/'actual210/seed_20260928/ACTUAL_FRESH_N1_SDK_BEFORE_FORWARD_ADMISSION.json',
 'eval_driver':S3/'code/native88C_frozen_acceptance_driver_v1.py',
 'reference':B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json',
}
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def sig(x):return 1/(1+math.exp(-x))
def clamp(x,a,b):return max(a,min(b,x))
def mat(q):
 n=math.sqrt(sum(x*x for x in q));w,x,y,z=[x/n for x in q]
 return [[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
         [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
         [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]]
def main():
 source={};lineage={}
 for key,path in FILES.items():
  assert path.suffix in ('.py','.json')
  raw=path.read_bytes();source[key]=raw.decode('utf-8-sig')
  row=dict(path=str(path),bytes=len(raw),SHA=H(raw))
  if path.suffix=='.py':
   row['definitions']=[dict(name=n.name,line=n.lineno,end_line=n.end_lineno) for n in ast.walk(ast.parse(source[key])) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
  lineage[key]=row
 def ev(key,anchor):
  hits=[i for i,line in enumerate(source[key].splitlines(),1) if anchor in line]
  assert hits,(key,anchor)
  return dict(path=lineage[key]['path'],SHA=lineage[key]['SHA'],lines=hits,anchor=anchor)
 status=json.loads(source['status']);ref=json.loads(source['reference'])
 x=status['last_original_state'];root=x['root13_sdk_xyzw'];theta=x['metrics']['tilt_rad'];age=x['public_age']
 terms=status['last_termination_terms']['values']
 assert status['controls']==61 and age==61 and terms['bad_orientation'] is True
 assert all(v is False for k,v in terms.items() if k!='bad_orientation')
 assert status['policy_parameters_and_saved_normalizers_literal_unchanged'] is True
 assert '"limit_angle": 0.75' in source['hard_cfg']
 assert 'torch.sigmoid((.3-state[1][...,2,2])/.04)' in source['mdp']
 assert 'self.weights=dict(bottom=2.,forward=2.,lateral=.5,wall=4.,support=1.,footprint=1.,contact=.15,stable=.3,style_deficit=.05)' in source['objective_v1']
 # SDK xyzw -> native wxyz is the already verified correct original conversion.
 R=mat([root[6],root[3],root[4],root[5]])
 target=ref['packed73'][age];Rt=mat(target[3:7])
 ori_error=sum((R[i][j]-Rt[i][j])**2 for i in range(3) for j in range(3))/9
 orientation_term=math.exp(-ori_error/.4**2)
 style_orientation_cost=.05*(1-orientation_term)/6
 z=root[2];rzz=R[2][2];p_tilt=sig((.3-rzz)/.04);p_low=sig((.12-z)/.02)
 p_union=1-(1-p_low)*(1-p_tilt)
 aligned=sig((math.cos(.75)-rzz)/.04)
 touch=ref['metadata']['first_touch_age'];support=ref['metadata']['support_age']
 alpha=clamp((age-touch)/(support-touch),0,1)
 report=dict(schema='mod4.native88C.actual_single_prejump_hard_soft_source_scalar_audit.v1',
  scope='local source/status/reference JSON plus scalar arithmetic; no model/raw/SDK/forward/physics',
  case=dict(seed=status['seed'],source_SHA=status['source_identity']['model']['SHA'],source_updates=status['source_identity']['model']['updates'],
   controls=status['controls'],physics_callbacks=status['physics_callbacks'],elapsed_s=status['controls']*.01,
   public_age=age,public_request=x['public_request'],actual_cached_terms=terms,
   policy_and_norm_literal_unchanged=status['policy_parameters_and_saved_normalizers_literal_unchanged']),
  hard=dict(config_limit_rad=.75,config_limit_deg=math.degrees(.75),observed_tilt_rad=theta,observed_tilt_deg=math.degrees(theta),
   excess_rad=theta-.75,excess_deg=math.degrees(theta-.75),observed_cached_bad_orientation=True,
   note='Configured threshold and actual cached term verified. SDK bad_orientation implementation source was not acquired anew; no recomputation of actual term.'),
  soft=dict(formula='sigmoid((.3-Rzz)/.04), union with sigmoid((.12-z)/.02)',
   fifty_percent_Rzz=.3,fifty_percent_tilt_rad=math.acos(.3),fifty_percent_tilt_deg=math.degrees(math.acos(.3)),
   actual_Rzz_from_original_quaternion= rzz,minus_projected_gravity_z=-x['projected_gravity_b'][2],
   consistency_difference=rzz+x['projected_gravity_b'][2],cos_observed_tilt=math.cos(theta),
   low_height_input_z=z,tilt_failure=p_tilt,low_height_failure=p_low,combined_failure=p_union,continuation=1-p_union,
   d_tilt_failure_d_tilt=p_tilt*(1-p_tilt)*math.sin(theta)/.04,
   broken_autograd=False,classification='angle-vs-Rzz termination boundary mismatch; soft model underrepresents observed hard failure'),
  posture=dict(reference_age=age,reference_wxyz=target[3:7],reference_tilt_rad=math.acos(clamp(Rt[2][2],-1,1)),
   source_orientation_error_matrix_mean=ori_error,orientation_tracking_term=orientation_term,
   weighted_orientation_deficit_component=style_orientation_cost,
   maximum_any_orientation_deficit_component=.05/6,
   largest_possible_reward_drop_from_this_component_with_other_costs_zero=.06-.06/(1+style_orientation_cost),
   actual_full_reward_not_computed=True,
   note='All six tracking terms lie0..1; orientation contributes only1/6 inside bounded style deficit. R also influences always-active wheel FK costs; no claim orientation has no geometric effect.'),
  frame_gates=dict(age=age,touch_age=touch,support_age=support,alpha=alpha,
   zero_at_this_age=['support','footprint','contact','stable including angular-velocity tracking'],
   always_active=['bottom','forward','lateral','wall','style_deficit including orientation'],
   soft_termination_frame_independent=True,hard_cfg_has_no_request_or_phase_gate=True),
  source_only_candidate=dict(implemented_or_deployed=False,original_hard_threshold_unchanged=.75,
   minimal_direction='Use the same configured hard angle as the imagined tilt boundary: Rzz threshold cos(limit_angle), maintaining an explicitly declared smooth width. This is a future typed objective/model change, not permission to weaken real termination.',
   diagnostic_same_width_Rzz=.04,diagnostic_aligned_tilt_failure=aligned,
   caveats=['This fixes a demonstrated semantic mismatch, not a proven sole cause or convergence guarantee.',
    'Do not lower actual hard threshold or change actual success/age/request/RNG/action.',
    'Review pre-request posture/survival sensitivity on saved same-state records before another training window; direct posture cost is a separate design choice, not automatically added.',
    'No new test episode, actor/WM forward or toy rollout was run.']),
  evidence=[ev('hard_cfg','bad_orientation = DoneTerm'),ev('hard_cfg','"limit_angle": 0.75'),ev('mdp','tilt_failure='),
   ev('mdp','ori_error='),ev('mdp','orientation=torch.exp'),ev('objective_v1','alpha='),ev('objective_v1','style=(1-original'),
   ev('objective_v2','score=(1+cost).reciprocal()'),ev('bridge','root[:,3:7]=root[:,[6,3,4,5]]'),ev('eval_driver','tilt_rad=')])
 put('SOURCE_AND_JSON_LINEAGE_ACTUAL.json',lineage)
 put('SINGLE_PREJUMP_HARD_SOFT_SCALAR_AUDIT_ACTUAL.json',report)
 put('SOURCE_READER_ERRORS_ACTUAL.json',dict(errors=[
  dict(kind='bounded_tool_output_truncation',description='Initial status JSON included nested producer metadata and body arrays; tool output truncated. Follow-up selected only required scalar fields. Original file untouched.'),
  dict(kind='source_path_missing',path=str(T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/saved_actual_SDK_source'),description='Read-only rg found no such local folder; no claim SDK bad_orientation source was obtained; no remote query attempted.')],
  model_or_runtime_failure=False))
 put('HANDOFF.md',f'''# Frozen source/scalar audit: singleC pre-request orientation termination

Actual cached `bad_orientation=True` at control61/244callbacks (0.61s), seed20260928, age61/requestFalse. The other six termination terms areFalse. Policy/norms are literal unchanged. This is one frozen attempt, not a full-window success-rate estimate or unique-cause proof.

The hard config is `.75rad` = {math.degrees(.75):.6f}°. Observed tilt {theta:.10f}rad = {math.degrees(theta):.6f}° exceeds it by {theta-.75:.10f}rad. The actual cached term is authoritative; its SDK function was not recomputed.

**Concrete mismatch:** imagined `sigmoid((.3-Rzz)/.04)` has its50% failure boundary at acos(.3) = {math.degrees(math.acos(.3)):.6f}°, rather than the real{math.degrees(.75):.6f}°. At this actual terminal pose Rzz={rzz:.10f}, soft tilt failure={p_tilt:.10g}; with z={z:.10f} height failure={p_low:.10g}, union failure={p_union:.10g} and continuation={1-p_union:.10g}. Thus the native imagination treats this truly terminated pose as almost fully alive. The source comment calling these original tilt thresholds is inaccurate. This is a termination-model/threshold-type mismatch, not a detached gradient graph or brokenautograd.

OwnwheelV2 posture style remains active before request. At age61 its reference tilt is{report['posture']['reference_tilt_rad']:.8f}rad, orientation tracking term={orientation_term:.8f}; weighted orientation deficit adds only{style_orientation_cost:.8f} to cost, bounded by.05/6=.00833333. Full reward was not computed. Always-active wheel geometry costs also depend on rootR, so orientation is not wholly absent. Support/footprint/contact/stable (including angular-velocity tracking) are all alpha0 at age61, become active after touch145, reachfull at165. Soft tilt/height and actual hard orientation have no request gate.

Minimal future direction: parameterize imagined tilt boundary from the actual configured angle, i.e. Rzz threshold cos(.75)={math.cos(.75):.10f}; keep a declared smooth width. With current Rzz width.04 only as a scalar diagnostic, this terminal pose would yield tilt failure{aligned:.8f}. **Not implemented or deployed.** Do not weaken real hard termination/success, alter age/request/RNG/action or automatically add/reset anything. This mismatch is demonstrated; whether fixing it enables stepping remains unproved. Direct posture cost weighting is a separate candidate requiring review, not an automatic change.

Original SDK xyzw→native wxyz mapping is correct and unchanged; quaternion-derived Rzz and negative projected-gravityZ agree within normal float representation ({report['soft']['consistency_difference']:.4g}). Prior wrong-quaternion claims remain refuted. No new precision/physical graduation gate is introduced.

`SINGLE_PREJUMP_HARD_SOFT_SCALAR_AUDIT_ACTUAL.json` contains all scalar inputs/results and exact code line/SHA anchors. `SOURCE_AND_JSON_LINEAGE_ACTUAL.json` lists10 source/JSON files. Source-reader truncation/missing local SDK folder are preserved in `SOURCE_READER_ERRORS_ACTUAL.json`; neither is a training failure. No PT/raw/NPZ, actor/WM forward, SDK/physics/GPU, SSH/network, Git or original-file edit occurred. Ordinary Git supplementation remains root-owned; no new trial/tag is created.
''')
 put('FREEZE_STATUS_ACTUAL.json',dict(frozen_UTC=datetime.now(timezone.utc).isoformat(),complete=True,source_scalar_only=True,
  actual_training_or_model_qualification=False,original_directories_unchanged=True,Git_supplementation='PENDING_ROOT'))
 rows=[]
 for p in sorted(D.iterdir()):
  if p.is_file() and p.name!='INDEX.json':
   raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
 put('INDEX.json',dict(files=rows,self_excluded='INDEX.json'))
 print(json.dumps(dict(frozen=True,directory=str(D),INDEX_SHA=H((D/'INDEX.json').read_bytes()),
  tilt_failure=p_tilt,combined_failure=p_union,style_orientation_cost=style_orientation_cost)))
if __name__=='__main__':main()
