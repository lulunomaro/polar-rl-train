"""Summarize actual D4 closeout and D5 fullscale evidence; no remote mutations."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
a=read(R/'D5_FORMAL_OWN_SOURCE_VERIFIED.json');p=read(R/'D5_CURRENT_ACTUAL.json');blocks=read(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
scope=read(D.parent/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008/reports/D4_LATER_BLOCKS_MATCHED_REVIEW.json')
assert a['source']['sha256']==scope['later_blocks']['2']['checkpoint']['sha256']=='7b6504a25a1fc879fc954cdb58b0614e28a91c5d9f8bcc144264c89d58ef5788'
assert p['reports']['D5_COMPLETE_PPO_PREFLIGHT_PASSED.json'] and a['source_count']==255 and a['snapshots']==31
assert not blocks['actual_owner'] and len(blocks['complete_blocks'])==3
v=dict(epoch=time.time(),D4_complete_blocks=blocks['complete_blocks'],D4_paired_later_review=scope,
 selected_D4_source=scope['later_blocks']['2'],D5_native20k=p['reports']['D5_NATIVE20K_PASSED.json'],
 D5_complete_PPO=p['reports']['D5_COMPLETE_PPO_PREFLIGHT_PASSED.json'],D5_formal_own_source=a,
 D5_packages=read(R/'D5_FROZEN_BEHAVIOR_PACKAGES.json'),new_clock45min_trial=False,
 actual_D5_learning=True,D5_frozen_behavior_pending=True,measured_hardware_force_stroke_available=False,
 final_D4_block3_ordinary_events_preserved=True,final_D4_behavior_complete='3' in scope['later_blocks'],new_budget_seconds=0,all_courses_finished=False)
(R/'D4_CLOSEOUT_D5_FORMAL_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
u=sum(b['actual_updates'] for b in blocks['complete_blocks'].values());steps=sum(b['actual_environment_steps'] for b in blocks['complete_blocks'].values())
note=f'''# D4 complete window and approved D5 actual deployment

D4's three bounded blocks completed naturally: {u} actual PPO updates and {steps} environment policy steps. All own CPU88/source243/24 snapshots, callbacks and unique completed segments were checked. The final30745 had465 ordinary bad_orientation events, no closure/integrity/nonfinite or whole-stop; it is retained and the increased rate is disclosed. A newer stored iteration is not automatically a better source.

Select full behavior-reviewed29690 SHA7b6504a25a1fc879fc954cdb58b0614e28a91c5d9f8bcc144264c89d58ef5788. Same3060/firstseed20261002/white_v3/D1-D4 paired flat80,spin88,corrected true-world88 each15s: world64/64,maxabs signed full-circle cross.038810884m/s,along.477908243–.538585908; straight minus/plus1.5 errors.020112012/.031199586; pure left/right4pi each8/8 with original signed yaw facts. Raw and old flags retained. This is limited matched scope, not all-seed/fullDR graduation.

D5255-source authority preserves all243 predecessor files byteexact and adds independent episode spring stiffness.9–1.1 and complete state/resume interfaces. Old parent/guardian/children exited, active segments settled, and original two locks acquired before the new authority. No kill, active clearing or double settlement. Real20k native:144control,576callbacks,task0,closure.837630mm,actual pressure readback/target/parameters passed. New-range128x2 and20kx4 full PPO completed6144 and1920000steps with192/384callbacks,CPU89 full finite; closure.626666/1.101255mm,task0. Each preflight charged once; weights discarded. Existing SDK/CPU and clock evidence reused.

Formal D5 is actually learning from29690, PID{a['trainer']['pid']}/start{a['trainer']['start_ticks']}, run{a['run']}. Own {a['checkpoint']['iteration_stored']} SHA{a['checkpoint']['sha256']} is CPU{a['checkpoint']['finite_tensors']} complete finite, own255 source freeze and31 snapshots exact. It is a save, not a skill result. Actual CUDA spring-state disk roundtrip, D4 action queue restore and all sensor/feedback/optimizer/global/named streams were verified before one new physical episode. First D5 pressure is explicitly new. No PhysX exactresume claim.

Three<=2h stable blocks/save25/15s host guardian continue without waiting for3060. No repeated45min clock experiment. New immutable true-D5 flat/spin/world package SHAfe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c uses the actual training asset/references and correctedworld; old singleGPU worker remains. New D5 closedloop behavior scope is pending.

Nominal3500N/m,damping3Ns/m,preload,cap,armature,PD/COM/reward/hardware remain. SDK effort is a formula approximation, not independent measured drive/constraint/hardware force. Engineering pressure is uncalibrated. No300–700N certification, MoE gate or dangerousreset deployment claim. healthv3 preserves finite closure local reset and all integrity protections.

Old pre-GPU path import error and CPU publisher Path/alias reader errors are preserved with separate corrected entries; no repeated rejected entry or runtime hotpatch. Independent formal reader's missing-first-save wait and wrong restored_exact field were corrected without changing training.

Canonical828000s230h/six extensions once. New budget0. Snapshot remaining{a['actual_tail_adjusted_remaining_seconds']:.3f}s after actual active tail; loading/PPO/save/exit remain charged, frozen work not charged. Masterplanv1.5SHAunchanged. All old once entries remain forbidden; new actualphase/PID/ownreceipts override snapshots. Single-stage closeout is not all-course completion.
'''
(R/'D4_CLOSEOUT_D5_FORMAL_REPORT.md').write_text(note,encoding='utf8')
if '3' in scope['later_blocks']:
 final=scope['later_blocks']['3'];facts={k:c['facts'] for k,c in final['cases'].items()}
 assert all(f['v4']['pass_'] for f in facts.values())
 detail=f"\nFinal30745 subsequently completed true D4 matched three-skill replay: world{facts['world']['passed']}/{facts['world']['count']},worstabsnetcross{facts['world']['max_abs_cross']:.9f}m/s,along{facts['world']['along_range']}; straight{facts['flat']['straight']}; pure left/right each8/8. Same source/root30q/parameters/recipes/actionassignments and per-kind package exact. The training ordinary465 increase is preserved; this limited frozen result shows no observed systemic direction/retention failure. D5 had already safely started from reviewed29690, whose+1.5 error was better; no runtime hot-swap or repeat preflight. Both retained, with their tradeoffs and original flags.\n"
 with (R/'D4_CLOSEOUT_D5_FORMAL_REPORT.md').open('a',encoding='utf8') as out:out.write(detail)
index=dict(epoch=time.time(),scope=scope['scope'],not_global_or_dualseed_best=True,all_flags_raw_preserved=True,
 selected_at_D5_start=scope['later_blocks']['2']['checkpoint'],
 candidates={b:dict(checkpoint=r['checkpoint'],ordinary=r['health']['ordinary_episode_reset_events'],
  facts={k:c['facts'] for k,c in r['cases'].items()}) for b,r in scope['later_blocks'].items()},
 selection_reason='29690 had completed matched retention before D5 launch and best reviewed+1.5 accuracy among these later candidates;30745 later had better netcross but465 ordinary resets. No hot-swap.')
(R/'MOD4_D4_CHECKPOINT_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
work=dict(id='MOD4-D6-DAMPING-FRICTION-WORK-ORDER-001',epoch=time.time(),approved_parent_plan='MOD4-MOE-PLAN-001 v1.5',
 parent_SHA='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',preparation_only=True,learning_executor_deployed=False,
 initial_scope='Independent episode .9-1.1 factors for verified nonzero nominal damping/friction; wider .8-1.2 only separately justified within plan.',
 actual_sources_required=['InstalledSDK setter/readback and frozen USD joint units, damping, static/dynamic/viscous friction',
 'Distinguish gas-slide damping3Ns/m, actuator PD derivative gains and joint friction; do not conflate with wheel-ground friction',
 'Zero nominal multiplied by factor stays zero: no invented absolute friction bounds; retain or explicitly unresolved until source/measurement available',
 'Preserve nominal plant/PD/COM/armature, force caps and gain-after torque-speed hardware envelope',
 'Independent private episode RNG, selected reset/readback of PhysX-buffer-model and unchanged other D0-D5 parameters',
 'Complete checkpoint and actualCUDA streams restore before one new physical episode; clear/rebase existing queues explicitly',
 'Reuse existing exact SDK/CPU scope; genuinely newscope20k completecallback and128x2/20kx4 full PPO only, discard preflight weights and charge once',
 'Use actual fully behavior-reviewed source, safe save/children-exit/two-lock/active boundary; unique new executor without repeated45min clock trial'],
 D5_training_not_blocked=True,new_budget_seconds=0,hardware_calibration_available=False,no_new_human_approval_inferred=True)
(R/'NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json').write_text(json.dumps(work,indent=2),encoding='utf8')
print(json.dumps(dict(updates=u,steps=steps,D5formal=a['checkpoint'],D4later_complete=list(scope['later_blocks']))))
