from pathlib import Path
import ast,json,time,hashlib
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'native110_preedge_monotone_task_reward_source_v3';B=L/'native110_task_reward_contact_semantics_source_v4'
assert not B.exists();B.mkdir();(B/'reports').mkdir()
rn='mod4_fudan_contact_phase_reward_candidate_v2.py';an='native_fudan_step_adapter_candidate_v2.py';qn='OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'
old=(A/rn).read_bytes()
a=b"    support=torch.sigmoid((force_z-1.)/1.)";b=b"    positive_force=force_z.clamp_min(0)\n    support=positive_force/(positive_force+1.)  # force unit N; exact zero at unloaded history"
c=b"""    # Before the leading wheel edge crosses, approach gating is monotone.
    # Preserve a continuous decay after the edge rather than fading beforehand.
    post_edge_decay=torch.where(front_gap>=0,torch.ones_like(front_gap),
        torch.sigmoid((front_gap+.10)/.03)/torch.sigmoid(front_gap.new_tensor(.10/.03)))
    near=torch.sigmoid((.18-front_gap)/.03)*post_edge_decay"""
d=b"""    # Approach/crossing band lasts to the actual platform far edge.
    near=torch.sigmoid((.18-front_gap)/.03)*torch.sigmoid(far_gap/.03)"""
assert old.count(a)==old.count(c)==1;new=old.replace(a,b).replace(c,d)
assert new.replace(d,c).replace(b,a)==old;ast.parse(new)
for n,data in [(rn,new),(an,(A/an).read_bytes()),(qn,(A/qn).read_bytes())]:(B/n).write_bytes(data)
contract=json.loads((A/'SOURCE_DELTA_TYPED_CONTRACT_110_V3.json').read_bytes())
contract.update(kind='SOURCE_ONLY_NATIVE107_TO110V4_TASK_REWARD_WITH_UNLOADED_CONTACT_SEMANTICS',epoch=time.time(),parent_candidate_reward_SHA=hashlib.sha256(old).hexdigest(),candidate_reward_SHA=hashlib.sha256(new).hexdigest(),inverse_to_V3_reward_bytes_exact=True,CPU_tests_pending=True)
contract['changes']+=['Support surrogate f_positive/(f_positive+1N) gives exact0 at unloaded history0 and.5at1N; original sigmoid gave.26894support and.07233top_support at zero. This is explicit source semantics, not actual contact truth.',
 'Near band extends from actual leading edge to actual platform far edge, avoiding premature front-edge decay while still crossing. Unloaded history gives flight1/P0/w1 throughout crossing.']
contract['scope']+=['Old signed worldFz history/max-two-samples input and its latency remain unchanged; force0 means this representation is unloaded, not a new instant contact sensor.',
 'Rational support is a new declared differentiable surrogate. Exact actualbodycontacts and270mm criteria remain external/unchanged.',
 'V3 source/grid results retained but not used for training after discovering zero-history false support and crossing-band concern. V4 is selected only after additional semantic tests.']
(B/'SOURCE_DELTA_TYPED_CONTRACT_110_V4.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf8')
s=(A/'verify_reward_counterexamples_and_supported_floor_domain_CPU_V3_UNUSED_once.py').read_text(encoding='utf8').replace('candidate110v3','candidate110v4').replace('REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V3.json','REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V4.json')
s=s.replace(">.1285+.02",">.1285+.001")
needle=" # Nonfinite state must still be rejected, no negative test exception hidden."
extra=""" # Zero contact-history force must not imply support on a platform-height airborne pose.
 xx=torch.linspace(.20,1.07,256)
 ar,am,_=evaluate('candidate110v4',xx,vx=.5,vz=2.3,force=0.,lowz=.27,z=ps['candidate110v4'].standing_body_height_m+.27)
 oldair,oldmode,_=evaluate('original107',torch.tensor(.75),vx=.5,vz=2.3,force=0.,lowz=.27,z=ps['candidate110v4'].standing_body_height_m+.27)
 assert torch.all(am['flight']==1) and torch.all(am['top_support']==0) and torch.all(am['jump']==1)
 assert ar['total'].max()-ar['total'].min()<=1e-7
 contact_semantics=dict(original_zero_force_flight=float(oldmode['flight']),original_zero_force_top_support=float(oldmode['top_support']),candidate_zero_force_flight=1.,candidate_zero_force_top_support=0.,unloaded_crossing_positions=len(xx),reward_range=[float(ar['total'].min()),float(ar['total'].max())])
"""
assert s.count(needle)==1;s=s.replace(needle,extra+needle)
s=s.replace("supported_floor_height_invariance=support_heights,","contact_semantics=contact_semantics,supported_floor_height_invariance=support_heights,")
q=B/'verify_reward_counterexamples_domain_and_unloaded_crossing_CPU_V4_UNUSED_once.py';ast.parse(s);q.write_text(s,encoding='utf8')
ext=(A/'verify_extended_flight_velocity_contact_domain_CPU_UNUSED_once.py').read_text(encoding='utf8').replace("verify_reward_counterexamples_and_supported_floor_domain_CPU_V3_UNUSED_once.py","verify_reward_counterexamples_domain_and_unloaded_crossing_CPU_V4_UNUSED_once.py").replace('candidate110v3','candidate110v4')
(B/'verify_extended_flight_velocity_contact_domain_CPU_V4_UNUSED_once.py').write_text(ext,encoding='utf8')
print(json.dumps(dict(source_only=True,reward_SHA=hashlib.sha256(new).hexdigest(),path=str(B))))

