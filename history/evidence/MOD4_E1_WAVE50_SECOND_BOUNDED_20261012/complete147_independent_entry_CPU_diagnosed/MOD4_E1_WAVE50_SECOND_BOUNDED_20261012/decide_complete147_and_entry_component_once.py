"""Complete observed147 decision and explicit next reset-entry CPU scope."""
from second50_io import *
def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 review_path=latest('SECOND50_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');v=json.loads(review_path.read_bytes())
 direct_path=latest('SECOND50_DIRECT146_PREFIX_ACTUAL_[0-9]*.json');direct=json.loads(direct_path.read_bytes())
 final=json.loads((R/'SECOND50_FORMAL_FINAL_ACTUAL_REVIEW.json').read_bytes())
 trace_path=latest('SECOND50_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json');trace=json.loads(trace_path.read_bytes())
 entry_path=latest('SECOND50_SAVED_ENTRY_IDENTITY_CPU_ACTUAL_[0-9]*.json');entry=json.loads(entry_path.read_bytes())
 component_path=latest('WAVE50_ENTRY_V1_SAVED20K_CPU_COMPONENT_ACTUAL_[0-9]*.json');component=json.loads(component_path.read_bytes())
 assert v['review_complete'] and not v['pending'] and direct['passed'] and trace['passed'] and component['passed'] and final['closeout_ready']
 assert v['summary']['terrain']['forward']['complete_envs']==5 and v['summary']['terrain']['reverse']['complete_envs']==25
 assert direct['original1N_contact_matches_position_completions'] and component['full1600_actual_assignments_matched']
 result=dict(epoch=time.time(),decision_complete=True,case_number=147,scope='derived50mm_tenwaves_mirrored_fullroute',
  actual_collection=v['collection'],full_actual_review=str(review_path),direct146_pair_review=str(direct_path),own_formal_review=str(R/'SECOND50_FORMAL_FINAL_ACTUAL_REVIEW.json'),
  full_training_trace=str(trace_path),own_checkpoint=final['own_checkpoint'],source_count=386,own_formal_complete=True,
  summary=v['summary'],terrain_original_health=v['terrain']['base_review'],pairs=direct['pairs'],
  raw_original_indices=json.loads(Path(v['collection']).read_bytes())['files'],
  qualified_observed50mm=False,freeze_accepted50mm=False,duration_only_same50_PPO_ended_after_two_blocks=True,
  no_automatic_third_duration_only_block_or70mm=True,ordinary_training_base_contact_preserved=final['health']['ordinary_episode_reset_events'],
  all_original_false_raw_cost_and_effective_incomplete_prefixes_preserved=True,
  E0_and_observed_CURB20_SLOPE5_8_10_WAVE35_frozen=True,gate_untrained=True,
  next_scope='independent_WAVE50_reset_entry_axis_CPU_component',next_component=str(component_path),
  component_only_not_target_fullstate_or_GPU_admission=True,new_learning_dispatch_not_claimed=True,
  original_2m_training_route_truncation_retained=True,
  new_entry_does_not_allow_claim_of_whole3_006m_test_route_inside2m_training_episode=True,
  need_SDK_actual_sampled_flat_footprint_and_entry_exposure_then_fullstate_before_PPO=True,
  no_causal_learning_explanation_or_permanent_antiforgetting_RM_MoE_graduation=True,no_budget_extension_or_old_once_replay=True)
 save('WAVE50_147_COMPLETE_OBSERVED_SCOPE_DECISION.json',result)
 diagnosis=dict(epoch=time.time(),actual_saved_entry_identity=str(entry_path),actual_full1600_assignment_component=str(component_path),
  actual_start_roots=dict(Wave=2820,center_inside_span=620,full_axis_aligned_footprint_before=940,full_axis_aligned_footprint_after=940,
   first_control_side_commands=entry['first_control_side_command_histogram']),
  facts='620 initial Wave root centers are within the ten-wave span; both sides have inward/outward signed commands and standing. Current root-cell families are dynamic.',
  proposed_axis='Only deterministic reset XY positions move to two separated flat approach lanes on each physical X side. Command sampling, signed speeds, standing, RNG consumption, geometry and route truncation remain original.',
  causal_explanation_not_established=True,exposure_root_proxy_not_contact_fullroute_certificate=True,
  original_route_limit_m=2.,full_test_nominal_distance_m=entry['whole_test_route_nominal_distance_m'],
  component_map_SHA=component['map']['map_sha256'],changed_Wave=2820,other17180_exact=True,
  complete_sampled_footprint_front_support_m=component['map']['minimum_full_flat_front_support_m'],
  origin_mutation_cache_invalidation_test_actual_passed=True,strict_rejections=component['strict_rejections'],
  CPU_only=True,no_training_GPU_fullstate_target_claim=True,
  future_learning_source_choice='Accepted observed35mm own369 b026 with complete ancestor129 3c97 identity, explicit35to50 plusnewentry migration. Own386 a67b is evidence, not a new default warmstart.',
  no_automatic_command_direction_repair_in_same_scope=True,all_failed_valid_prefixes_false_and_source_identity_preserved=True)
 save('WAVE50_ENTRY_NEXT_AXIS_ACTUAL_DIAGNOSIS.json',diagnosis)
 with (R/'NEXT_E1_WAVE50_ENTRY_FULLSTATE_AND_BOUNDED_REPAIR_WORK_ORDER.md').open('x',encoding='utf8') as f:f.write('''# Continue the approved independent50mm reset-entry repair

147 is fully complete and independently reviewed: forward5/27 versus1467/27, reverse25/27 unchanged. Original1N wheel support matches position completion, ordinary0/truncation0/closure.654120871mm. Fullraw182624801B SHA778f301d9e1e9785efaee9583cef84ada35c712a56b47736169b6ec40985c3b8. Allinitialroot30q/parameters/recipes/assignments/6000callbacks/worldmeshquery1e-6/ground-contact integralCOMlinkhardware audit passed; this is valid measured failure, not50mm graduation. Preserve all22forward/2reverse incomplete prefixes, sixforward complete-to-incomplete andfour improvements. Legacy negative4pi0/8 positive3/8/world64/64 andalloriginalstrictfalse/spinphysicalsmokefalse retained. E0 is frozen andgate untrained. Do not add a third duration-only block or70mm.

Own386model32357 a67b/17615730B/CPU102/81module snapshots+386freeze/PID3010588 completePASSED,94updates2256controls45.12Msteps9024callbacks. Unique1825.9359953403473s originalparent settled; ordinary1base_contact preserved/closure1.221559010mm. Actualparentguardianchildgone/twofcntl-free/active-Sactiveempty is a legalreview boundary. Sevenstrictsame50 fullCPUCUDA/sourceepisode+1 receipts passed. Never revive anyoldmain/resume/once/SDK/native/PPO/fresh/publish/budgettail.

New wave50_entry_v1_math.py has actually executed CPU tests on complete saved20k origins, original nativefull1600 assignments and25200point exactcollisionbank. All2820Wave positions change, other17180 exact, mapSH Af42f0b15333c9bedd903921e191940cc0a9e9d3042fd354053f74d5c1ee0eb0d (remove space in identifierwhenreading actualJSON). Halfspan1.203211363593m plus.8/.85rank places separated lanes onbothworldX sides, Yboundedcompletefootprint+.004. Minimum full-flat-frontsupport.517000000335m. Duplicateassignment/wrongfootprint/wrongspan reject; cacheboundactualorigin/assignment/bank/profile identity refreshes afterorigin mutation. This is CPU mathematics only, nottargetCPU/SDK/physicalnonpenetration/learning deployment. Complete assignmentidentity and20kroot match are actual; entryfailure causality remains unproved. Initialroots620insidewave andbothsides inward/outwardcommands are facts, not a causeclaim.

Actively prepare a new isolated root/sourcefreeze for reset-entry only, using exact immutable384 G4geometry/worldmesh components and approvedfull35mmsource own369b026/CPU102/ancestor1293c97. Do not automatically use degradedown384219f/386a67b ordiscard asnew expert default. Verify full old35 actorcriticoptimizerstd/allD0D7/globalnamed anddictprivateCPUCUDA/oldterraincommand identity before explicit35to50 actualassignment plusnewentry-map identity migration. Store independententrydictkey/cache identity andsavedsourceepisode+1; oldnamedstrictset andassignment validation staystrict, no new RNG. Later same50+entry restore mustexact; actualCUDA diskroundtrip needed, nonPhysXexactresume. Preserve standaloneoriginals; nohotpatchold384/386.

Prepare new entry reset wrapper safely around original fullpose placement: buildcache fromactualorigins withfull1600assignment/profile/bank hashes; updateonlymapped XY, original bank30q/root tangentnormal/zero velocity/clearance remain. Handle initialization andselectedreset withoriginalepisode/RNG exactly, bindactualoriginchanges includingSDK placement andfullsave. Add CPU wrongsource/assignment/map/origin roundtrip/independentstorage andimport-main-Popenargv checks. Sourceguard005 verifiesbase10h plussevenextensions1188000 andrealremaining, explicitseed20260928 inallfresh argv. Do not infer PhysX orGPUadmission fromthis CPU component.

Then execute genuinelymissingnew-entry SDK10 actual10G4cells/twosides/fullflatcolliderfootprint/selectedreset/300controls1200callbacks once; new-entry native20k24warm120timed480/576callbacks once with actualmap/groundrewardformula/ordinary andcompletecommandtrace bothsigned+standing. Unchanged50geometry/physics/clockDRhardware exactSHA reuse, no45minclock andnooldGPUreplays. Do not borrowoldSDK10 diagnosticplacement fornewproductionreset oroldnative origins fornewentryscope. Original2mrough_route_boundary fromnewspawn remains; the3.006mwholefrozen test cannot fitthistrainingroute limit. Report actualentry/onset/partialwave exposure andall declaredtruncations, never callthatwholeten-wave trainingcertificate. Commandaxis remains old±.3/yaw0/standing.2/RNGconsumption, no directionbinding/livepositionyawteacher/reward ortruthactor-gate input inthisscope. Ifdirectionaxis laterneeded, diagnose andsplitnewscope.

After ownnewSDK/native/newfullstate contracts pass,128x2 and20kx4 completePPO discardpreflight eachonce samecanonical, thenindependentfreshsame50+entry20k0control0PPO fullstrictCPUCUDA/seed20260928 restore. ManifestbeforefirstPPO bindsdynamiccommandviaoriginal_write_dynamic only ifrequired, noextrareset/RNG; trueownsnapshot filenames, freshonlynewprocess, no uninitializedloggerwriter, explicitseed andimport-main-Popenargv parity. OnlyallownPASSED allow first300sloadlearnsaveexit/save25/15slocalguardian fromb026, ownuniqueparentcanonicalcharge, independentoutput. Newjobnumber actualtwohostqueue/results/jobs unusedcheck beforepublish; no blind148 claim.

Owncompletefullsave/sourcefreeze/CPU/PID/PASSED/uniqueexit-lock-idle boundary thennewterrain-flat-spin-worldfourcases. Reuse145/147 exact50mm peak-to-valley tenwaves2.406422727m/9m mirroring/.4approach/fulltwo-wheel200mmafter/80env1500control15s20260928white3; allroot30qparamsrecipesassignments6000callbacks/worldfloat32query1e-6/groundcontactintegralCOMlinkhardware oldtolerances. Original1Nsupport andposition separate, stand26 no crossing, allvalidordinary-before andincompleteprefixes/sameepisodeprereset-before exclude teleport; no shorteningapproach/windowextension/relabeling. Legacy115/129 fullsignedcirclealongcrossdedrift/two4pi/straightoriginalstrictfalse, ownfiniteCPUbinding andlegacyresultSHA=manifestSHA=ownSHA/precisejobcheckpoint, actualreset schema, finalsensor dynamicbiasvsstaticrecipe/.0075bound retained. Fullperenvtrainingtrace dynamicfamily/currentrootcell andbeforephysicscommand versusafterupdatehist separate, rootproxy notcontact/fullroute. Completecandidate andexposure audit beforemorePPO/70; ≤2h eachblock, atmosttwo justifiedscope blocks thenfullaudit, systematicfailurediagnosis insteadblindthird.

005canonical1188000/sevenextensions no newbudget; actualactive/accounted tails override snapshots. CPU/SDK/native/frozen/fresh0PPO nocharge. No copy/clearactive/tail/recharge/extension; twofcntlactualfree/held, no kill/hotpatch/dual20k/otherAI. E0/acceptedCURB20/SLOPE5-8-10/WAVE35 frozen, gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused/WASDuntouched. FixedclockDRrewardLRhardware/fivefamilies/healthv3/commands/fullsignedcircle/ground-contact-COM thresholds unchanged, otherexpert/gate/min(18h,.13B) planning protected. Allsavedsource/rawfalsecost/errors/sync/monitor/workorders/Gitreceipts continuousGit, largeoriginalactualpathsizeSHA only/credentialsneveroutputGit. Newrealstage uniqueannotatedtrial withremote main/tag/peeled; pushfailed originalobjects only, nooldrecord/tag replay. SamehourlyACTIVE mod4-10 quiethealthy, onlymeaningfulnotification; reviewready notcoursefinished.
'''.replace('mapSH A','mapSHA'))
 save('LOCAL_READER_PATH_LOOKUP_ERRORS_RETAINED.json',dict(epoch=time.time(),stage='CPU_readonly_source_lookup',no_GPU_or_physical_failure=True,attempts=[
  dict(path='g4_*.py literal Windows filename',error='rg invalidfilenamegrammar; then rg --files used',source_preserved=True),
  dict(path='guessed wave50_learning_cpu filenames',error='File not found; actual_src_snapshot names enumerated',source_preserved=True),
  dict(path='actual_src_snapshot/terrain_intro_runtime.py',error='rg systemcannotfindfile(oserror2); original e1_terrain_runtime.py used'),
  dict(path='archive_second50_stage_once.py',error='Get-Content pathdoesnotexist; rg --files foundarchive_second50_real_stage_once.py')],original_false_not_changed=True))
 print(json.dumps(dict(decision_complete=True,qualified50=False,forward=5,reverse=25,entry_CPU_component_passed=True,new_learning_not_deployed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE147_DECISION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
