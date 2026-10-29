from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'native110_preedge_monotone_task_reward_source_v2';B=L/'native110_preedge_monotone_task_reward_source_v3'
assert not B.exists();B.mkdir();(B/'reports').mkdir()
rn='mod4_fudan_contact_phase_reward_candidate_v2.py';an='native_fudan_step_adapter_candidate_v2.py';qn='OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'
old=(A/rn).read_bytes();a=b'support_surface_height=p.step_top_z_m*footprint)';b=b'support_surface_height=p.step_top_z_m*top_support)'
assert old.count(a)==1;new=old.replace(a,b);assert new.replace(b,a)==old;ast.parse(new)
for n,d in [(rn,new),(an,(A/an).read_bytes()),(qn,(A/qn).read_bytes())]:(B/n).write_bytes(d)
contract=json.loads((A/'SOURCE_DELTA_TYPED_CONTRACT_110_V2.json').read_bytes())
contract.update(kind='SOURCE_ONLY_NATIVE107_TO110V3_SUPPORTED_SURFACE_AND_MODE_REWARD',epoch=time.time(),parent_candidate_reward_SHA=hashlib.sha256(old).hexdigest(),candidate_reward_SHA=hashlib.sha256(new).hexdigest(),support_surface_height_change='top_z*top_support replaces top_z*footprint; support height no longer anticipates a raised surface solely from horizontal footprint.',inverse_to_V2_reward_bytes_exact=True,CPU_tests_pending=True)
contract['scope']+=['V2 deterministic grid passed after classifying actual FP32 preedge gap, but its explanatory text assumed recovery height was independent of x. Original footprint-only support height invalidated that statement in general; original reports/source retained, not overwritten.',
 'V3 height cue requires top support. For unchanged supported floor poses with P=0, command and support height are constant. Thus R,J,E remain unchanged and derivative_w=J-E>=0 combined with monotone preedgew proves no adverse mode approach term on that domain.',
 'P=0 is a measurement-domain condition; no claim for arbitrary soft top-support transitions, contact/model errors, postedge or resets.',
 'Old CPUv1 failed at literalx0.27 represented as0.2700000107; exact computedgap was negative and selected declared postedge decay. Fixed only test domain classification, no runtime source tolerance/FP64/physicalguard change.']
(B/'SOURCE_DELTA_TYPED_CONTRACT_110_V3.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf8')
s=(A/'verify_reward_counterexamples_actual_preedge_domain_CPU_v2_UNUSED_once.py').read_text(encoding='utf8')
s=s.replace('candidate110v2','candidate110v3').replace('REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V2.json','REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V3.json')
needle=" # At request-off, exact recovery reward is preserved."
block=""" # Check supported-floor support-height invariance across actual-case body-height range.
 support_heights={}
 for height in (.247,.30,.34,.3824462629854679,.406):
  xx=torch.tensor([.056,.20,.25],requires_grad=True)
  sr,sm,measure=evaluate('candidate110v3',xx,z=height)
  gg=torch.autograd.grad(sr['total'].sum(),xx)[0]
  assert torch.all(sm['top_support']==0) and torch.all(measure['relative_base_height']==measure['relative_base_height'][0]) and gg.min()>=-2e-7
  support_heights[str(height)]=dict(reward=sr['total'].detach().tolist(),relative_height=measure['relative_base_height'].detach().tolist(),gradient=gg.tolist())
"""
assert s.count(needle)==1;s=s.replace(needle,block+needle)
s=s.replace("saved_model_reads=0,raw_reads=0,remote_calls=0,actual_training_started=False)","supported_floor_height_invariance=support_heights,saved_model_reads=0,raw_reads=0,remote_calls=0,actual_training_started=False)")
q=B/'verify_reward_counterexamples_and_supported_floor_domain_CPU_V3_UNUSED_once.py';ast.parse(s);q.write_text(s,encoding='utf8')
(B/'reports/PRIOR_SOURCE_CPU_FAILURES_AND_SCOPE_CORRECTIONS_RETAINED_ACTUAL.json').write_text(json.dumps(dict(original_V2_main_CPU_report=str(A/'reports/REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL.json'),original_V2_fixed_domain_grid_report=str(A/'reports/REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V2.json'),diagnostic_v1_error='AssertionError importing original fixture prefix because report-exclusive guard found its consumed output; no tensor diagnostic executed.',diagnostic_v2_error='SyntaxError: extracted partial comment started with of these explicit synthetic measurement values; no tensor diagnostic executed.',diagnostic_v3_report=str(A/'reports/NEW110_V2_FIRST_MONOTONICITY_FAILURE_DIAGNOSIS_ACTUAL.json'),no_old_model_or_fixture_entry_rerun=True,no_runtime_tolerance_changed=True),indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,reward_SHA=hashlib.sha256(new).hexdigest(),new_CPU_entry=str(q))))

