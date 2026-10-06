"""Prepare a new named fallback, preserving all old GPU entries and source freezes."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;S=D.parent/'MOD4_PHYSICS_SPEED_REVIEW_20261007'
out=D/'supervise_dt1000_longrun_recovery.py'
assert not out.exists(), 'Preparation already done; do not repeat.'
s=(S/'supervise_clock2000_review.py').read_text(encoding='utf8')
s=s.replace('dt=.002;clock=validate_clock(dt)','dt=.001;clock=validate_clock(dt)',1)
s=s.replace("('crossbin_sdk','contact_crossbin_sdk.py',10,300),('native20k','physics_speed2000_probe.py',20000,120)","('aligned_sdk','contact_aligned_sdk.py',10,300),('native20k','physics_speed_probe.py',20000,120)",1)
s=s.replace("row['cross_bin_SDK_oracle']","row['aligned_SDK_oracle']")
s=s.replace("row.get('cross_bin_SDK_oracle')","row.get('aligned_SDK_oracle')")
s=s.replace("int(base.checkpoint(ck)['iteration'])>=23509+(2 if m['num_envs']==128 else 4)","int(base.checkpoint(ck)['iteration_stored'])>=23509+(1 if m['num_envs']==128 else 3) and health['control_steps']==(48 if m['num_envs']==128 else 96)",1)
s=s.replace("'moe_S1A_A0_selected_clock_learning'","'moe_S1A_A0_clock1000_recovery_learning'")
s=s.replace("'bounded_A0_E0_selected_clock_learning'","'bounded_A0_E0_clock1000_recovery_learning'")
s=s.replace("'A0_selected_clock_saved_review_ready'","'A0_clock1000_saved_review_ready'")
needle=" ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'));ctl.idle();verify()"
insert=''' ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'));ctl.idle();verify()
 assert not ctl.S.get('active_training')
 prior=w.read(R/'DT2000_LONGRUN_FAILURE_AUDIT.json')
 assert not prior['formal_health']['adoption_retained'] and prior['actual_old_authorities_exited']
 assert prior['formal_health']['actual_health']['actual_task_reset_events']==1
 assert base.checkpoint(Path(prior['full_save']['path']))==prior['full_save']
 previous=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007')
 for receipt in ('SELECTED_CLOCK_LAUNCHED.json','SELECTED_CLOCK_GUARDIAN_STARTED.json'):
  row=w.read(previous/'reports'/receipt);ident=row.get('owner',row);actual=helpers.identity(ident['pid'])
  assert actual is None or actual['state']=='Z' or actual['start_ticks']!=ident['start_ticks'],'Prior training authority still alive'
 assert base.budget_state()['active_segment'] is None and not base.trainers()
 raw=w.read(ctl.CANONICAL)
 own=[x for x in raw['completed_segments'] if x['pid']==prior['PID_bound_receipt']['pid']]
 assert len(own)==1 and own[0]==prior['unique_completed_segment']['value'],'Prior segment must be settled exactly once'
 assert float(w.read(w.CODE/'env.json')['RM_PHYSICS_DT_S'])==.001
 write('FALLBACK_INSTALL_BOUNDARY.json',dict(epoch=time.time(),prior_failure=prior,previous_authority_exited=True,
  active_segment=None,prior_completed_segment_reused=True,no_old_tail_recharged=True,no_budget_mutation=True,
  source_original23509=True,failed23875_not_selected=True))'''
assert needle in s;s=s.replace(needle,insert,1)
needle=" before=base.budget_state()['charged_training_seconds'];last=ctl.training(SOURCE,'moe_S1A_A0_clock1000_recovery_learning',duration=min(2700,ctl.remaining()))"
insert=""" raw=w.read(ctl.CANONICAL)
 used=sum(x['ended_epoch']-x['started_epoch'] for x in raw['completed_segments'] if 'moe_S1A' in x['kind'])
 duration=min(2700,ctl.remaining(),21600-used)
 assert duration>120,'S1A stage or budget safe-start limit reached'
 write('S1A_COST_BEFORE_FALLBACK.json',dict(epoch=time.time(),prior_S1A_learning_seconds=used,new_bounded_duration_s=duration,total_stage_cap_seconds=21600,prior_rejected_costs_retained=True))
 before=base.budget_state()['charged_training_seconds'];last=ctl.training(SOURCE,'moe_S1A_A0_clock1000_recovery_learning',duration=duration)"""
assert needle in s;s=s.replace(needle,insert,1)
needle=" write('FORMAL_CLOCK_HEALTH_REVIEW.json',dict(epoch=time.time(),actual_health=health,adoption_retained=health['actual_task_reset_events']==0,all_weights_preserved=True))"
insert=needle+"""
 if health['actual_task_reset_events']:
  write('CLOCK1000_PHYSICAL_REJECTION.json',dict(epoch=time.time(),actual_health=health,all_weights_preserved=True,automatic_new_clock_adoption=False))
  w.phase('clock1000_actual_failure_saved_review',**review)
  status('clock1000_actual_failure_saved_review',training_pid=None,evaluation_pid=None)
 else:
  write('CLOCK1000_LONGRUN_HEALTHY.json',dict(epoch=time.time(),actual_health=health,checkpoint=saved,review_ready=str(R/'SELECTED_CLOCK_REVIEW_READY.json'),matched_architecture_SDK_pending=True))"""
assert needle in s;s=s.replace(needle,insert,1)
ast.parse(s);out.write_text(s,encoding='utf8')
worker=(S/'contact_crossbin_sdk.py').read_text(encoding='utf8')
worker=worker.replace('assert args.dt==.002','assert args.dt==.001',1)
worker=worker.replace('from contact_bin_oracle import ContactBinOracle','from aligned_contact_oracle import ContactBinOracle',1)
worker=worker.replace("report['cross_bin_SDK_oracle']","report['aligned_SDK_oracle']")
ast.parse(worker);(D/'contact_aligned_sdk.py').write_text(worker,encoding='utf8')
oracle=(S/'contact_bin_oracle.py').read_text(encoding='utf8')
oracle=oracle.replace('assert env.physics_dt==.002','assert env.physics_dt==.001',1)
oracle=oracle.replace('self.capture.tick%5==0','self.capture.tick%10==0',1)
oracle=oracle.replace('end=self.capture.tick*2000;start=end-2000','end=self.capture.tick*1000;start=end-1000',1)
ast.parse(oracle);(D/'aligned_contact_oracle.py').write_text(oracle,encoding='utf8')
print('Prepared new isolated1ms native/PPO/bounded adaptation authority; no worker launched by preparation.')
