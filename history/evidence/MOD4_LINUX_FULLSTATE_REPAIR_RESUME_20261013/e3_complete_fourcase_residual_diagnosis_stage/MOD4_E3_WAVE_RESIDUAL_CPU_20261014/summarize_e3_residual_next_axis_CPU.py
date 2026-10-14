"""Compact result and next diagnostic from actual saved data; no candidate."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
I=R/'E3_VS2B_REMAINING_FOUR_FULL_VALIDPREFIX_CPU_ACTUAL.json'
O=R/'E3_FOUR_RESIDUAL_COMPACT_AND_NEXT_MINIMAL_AXIS_CPU_ACTUAL.json';assert not O.exists()
j=json.loads(I.read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
rv=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes())
p=json.loads(Path(rv['original_report']['local_path']).read_bytes());par=p['initial']['actual_all_physical_parameters'];ass=p['initial']['assignments']
rows=[]
for r in j['remaining4_paired']+j['improved21_72_70_paired']:
 i=r['env'];old=r['old']['all_valid_episodes'][0];new=r['new']['all_valid_episodes'][0]
 def compact(e):
  k=['valid_controls','original_complete','best_deficit_to_original_after200mm_m','best_minwheel_beyond_wave_end_m','yaw_final_deg','root_cross_last_m','last_valid3s_signed_world_vx_m_s','double1N_fraction','raw6_clip_lower_fraction','CAD_lower_projection_fraction','CAD_target_lower_fraction','actual_per_motor_bound_lower_fraction','actual_per_motor_bound_upper_fraction','ending_event']
  out={x:e[x] for x in k};out['mean_signed_world_vx_m_s']=e['signed_world_vx']['mean'];out['mean_signed_body_along_m_s']=e['signed_body_along']['mean']
  out['ten_spatial_interval_both1N_crossing_controls']=[x['first_both_wheel_COM_beyond_with_double1N_control'] for x in e['ten_section_spatial_interval_tables']]
  out['last3s_world_body_yaw']=e['three_second_bins'][-1]
  return out
 rows.append(dict(env=i,old=compact(old),new=compact(new),postreset_valid_episodes_separately_retained=r['new']['all_valid_episodes'][1:],initial_static_parameters=dict(COM_delta_m=ass['COM']['delta_m'][i],leg_delay_us=ass['action']['legs']['delay_us'][i],wheel_delay_us=ass['action']['wheels']['delay_us'][i],feedback_requested_us=par['feedback_requested_us'][i],wheel_motor_episode_scale=par['motors']['wheels']['episode_scale'][i],mild_friction_mu=par['mild_mu'][i])))
overview=[]
for label in ['old','new']:
 for g in [0,1]:
  for complete in [False,True]:
   vals=[x[label]['all_valid_episodes'][0] for x in j['all54_paired'] if x[label]['original_contact_complete']==complete and x[label]['all_valid_episodes'][0]['group']==g]
   overview.append(dict(source=label,group=g,complete=complete,count=len(vals),left_lower_guard_fraction_range=[min(x['CAD_target_lower_fraction'][0] for x in vals),max(x['CAD_target_lower_fraction'][0] for x in vals)] if vals else None,rawleft_lower_clip_fraction_range=[min(x['raw6_clip_lower_fraction'][0] for x in vals),max(x['raw6_clip_lower_fraction'][0] for x in vals)] if vals else None))
out=dict(epoch=time.time(),passed=True,parent_report=dict(path=str(I),bytes=I.stat().st_size,sha256=sha(I)),source_old=j['source_old'],source_new=j['source_new'],residuals_and_new_success_controls=rows,success_failure_domain_negative_control=overview,
 interpretation=dict(
  remaining_forward='Env6/15/69 retain late yaw97.86/76.76/102.07deg and cross2.48/2.33/3.00m. All three still fail actual ten-wave crossing, not merely original200mm tail requirement. Their best both-wheel deficits are368/795/519mm to the original finish. Contact remains98.73-99.80percent double1N.',
  forward_route='Env69 crosses lateral3m boundary atcontrol1494, not time-out; original firstepisodevalid1494 controls retained. Final5controlresetepisode does not earn route credit. Late body-along~.298m/s while prescribed signedworldvx~-.0075m/s is a turn, not a lack of forward wheel motion.',
  reverse='Env67 has uniquebase_contactatcontrol1161 (11.61s), not ordinary closure/mimic/nonfinite. Preordinaryvalid1161 controls yaw32.33deg, cross92mm, double1N97.85percent; at9-11.61s yaw changes+36.97deg and actualwheelvelocityleft/right means-9.13/-17.19rad/s. Actualrequestedwheel targets differ, but delayedqueue rows are not saved, so exact appliedtarget causation is unknown. Reset338controlprefix is separatelypreserved.',
  paired_terrain='Newsuccess21/72/70 correspond to much lowerfinalyaw -17.22/+7.10/-18.63deg and betterworldprogress. Env6 staysfail but besttail deficit worsens50→368mm, showing completion counts alone hide residualseverity.',
  left_domain='Left CAD lower projection is100percent in everyremainingprimaryprefix, but also100percent in new successes21/72/70 and nearlyevery other successfulprefix. Left rawclipincreased on these new successes. Thus saturation persists yet is not a unique cause or reason for anotherblindleftrecenter.',
  motor_bounds='Actual saved torque-speed limits hold. Forward6 isnever at anymotorbound; forward15/69 wheel-bound fractions are small, so there is no blanket motor-torque-capacity explanation. Reverse67 actualleftwheel lowerbound7.13percent occurs but stilldoesnotidentify unique cause.',
  delay_negative_control='Forward6/15 haveactualfeedbackrequested0us and neverthelessfail; anotherblanketD3currentfeedback factor cannot explain these two. Both haveactiondelay2500/5000us, which is not feedbackdelay. No productiondelay/noise change proposed.',
  no_qualification='50mm and70mm remain unqualified; all original thresholds and false/prefixes preserved.'),
 next_minimal_axis=dict(priority='First CPU mathematically isolate gyro-z observation sensitivity of the unchanged e3 actor wheel differential output.',
  fixed_inputs='Use actual saved35vectors only as explicit post-stepvector fixtures, not same-control actorinputs. On each fixture perturb only gyro-z observation coordinate over +/-smallbound with original observation scale confirmed by frozen source. Keepother34elements/state/weights/DR/Adam/std unchanged; evaluate deterministicactorCPU.',
  outputs='Report sixactoroutputs and d(actionR-actionL)/d(gyro_z), raw andclippedwheelrequest plusoriginalprocessor. Check the expected correcting sign for positive/negative command and contrast savedfixturecontexts of6/15/69/67 versus21/72/70. This is a direct policy math diagnostic with no newcheckpoint.',
  falsification='If sign/response remains corrective andunsaturated, weakgyrofeedback is not established; prioritize one actualsame-initial action-delay factor rather thanchangingtwo axes. If responsehaswrong-sign/deadzone onlyinresidualcontexts, prepare a singleobservation/headlearningaxisworkorder with explicitbounds andsamefull20k source, rather thanreinitializeleftdomain oraddliveheadingcorrection.',
  physical_causal_gate='CPU derivative is not physical replay or rewardcertificate. A future new3060singleaxisfactor needs actualrootowner safe slot/sourcefreeze/sameinitialDRRNG/fullraw/contactCOMhardware andfull4case review. No factor dispatched, no CPUcandidate generated, no thirdsame-axisPPO.'),
 no_new_candidate_checkpoint=True,no_GPU_SSH_PPO_RNG_or_budget=True,Git_archive_pending_root_owner=True)
O.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(O),bytes=O.stat().st_size,sha256=sha(O),next_axis=out['next_minimal_axis']['priority'],no_candidate=True)))
