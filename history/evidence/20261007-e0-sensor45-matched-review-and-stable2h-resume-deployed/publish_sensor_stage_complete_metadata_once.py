"""Publish real results and current authority; approval/master/budget stay unchanged."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
review=json.loads((R/'SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json').read_text());formal=review['formal'];active=json.loads((R/'SENSOR_STABLE_CURRENT_ACTUAL.json').read_text())
assert active['phase']=='bounded_E0_sensor_stable_learning' and active['child'] and active['runs'][0]['SENSOR_RESUME_STARTUP_VERIFIED.json']['sensor_streams_restored']
note=f'''# E0 noise and encoder bias: healthy first stage and matched3060 review

Approved MOD4-MOE-PLAN-001 v1.5 master unchanged. Formal45min completed279 actual PPO updates /6696 control steps /133920000 environment policy steps. Task failures0 excludingtimeouts, closuremaximum0.654246mm, mimic0.001953125rad, actual66960 callbacks exact. Own model24061 SHA6457195e25682c8059e2a9be7c7fb4531299216874ab8100014a9cf75f7f8b7b has74 finite floating tensors and full actor/critic/optimizer/std/sensor state, global and named command/physical RNG. Its own202 run freeze and PID-bound receipt were verified. A unique2715.681592s completed canonical segment is reused, never settled again.

All seven3060 SDK/baseline/candidate jobs completed; fourteen returned probe/result JSON files were byte exact. Noise-aware world direction on matched seed20261002/white_v3 changed63/64 ->64/64; worstabs signed complete-circle cross .050750161 -> .045795810m/s, newalong .478530650–.531670830m/s. Straight -1.5/+1.5 mean error .017857494/.024845606 -> .015562846/.024687234m/s. Pure signed±4pi eachdirection8/8 remains within original±.2. Full windows/cycles/effective prefixes/oldlegacy-quality flags remain intact. The strategy and learning exposure changed; no isolated noise/reward causal claim.

New noise platform scope accepted only for1ms, A0, white_v3, seed20261002 and these full80/88env15s cases plus actual manager/reset SDK. Native baselineworld64/64 versusWindows63/64 has maxpairedcross platform difference .008691594m/s. Initial fullroot/q and physical parameter objects exact; dynamics are not GPU bitexact. This is sufficient for bounded same-scope continuation, not allDR graduation, held-out coverage or hardware certification. Clean-feedback candidate retention is separately pending six new immutable matched3060 cases, not inferred from noisy passes.

New MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007 contains old202 sources byteexact plus four new files (206 total). The new entry adds stochastic warm-start restoration and its own snapshot without changing task/reward/physics/DR/range/PPO/hardware/observation dimensions. NineCPU contracts read actual20000-row savedstate; CUDA RNG representation is validated as bytes and CPU fixture roundtrip is explicitly separate from actualGPU startup. Real startup then verified exact actor/critic/std/optimizer, globalCPU/CUDA and namedcommand/DR streams, followed by exactlyone new physical episode and resampled bias/cache. Full30q initialerror0 and realparameters/readback passed, managerformulaerror5.960464e-8. PhysX exact resume is not claimed. Same-range completed128x2/20kx4 preflights are explicitly reused, weightsdiscarded; no duplicate probes or cost.

At epoch{active['epoch']}, newuniqueparent{active['owner']['pid']}/start{active['owner']['start_ticks']}, guardian{active['guardian']['pid']}/start{active['guardian']['start_ticks']}, trainer{active['child']['pid']}/start{active['child']['start_ticks']} is executing its stable2h block, deadline fromactualstate/Sactive. Prior authorities naturally exited with noactive before locking both original locks. This newblock's future complete source will automatically publish three same-scope3060 jobs using exact202 plant/inference bytes; current newlearned behavior is not yet validated. Parent/guardian plannedexit at its complete review boundary is not failure or graduation.

D3 next first0/10ms component has11 CPU contracts: real unit=10000us percontrol tick, same-tick cache, independent episode latency RNG, selectedreset/new-episode warmup actualage0, timestamp/schema/nonfinite rejection and queueRNG serialization. It is only a CPU component under MOD4_D3_DELAY_COMPONENT_PREPARE_20261007. No SDK, PPO,50Hz sampling,20ms/40ms or actiondelay was installed. Next must validate actual sample/apply timing/frame/scale/reset/cleancritic and new-rangePPO before deployment. Actor35/cleancritic38/action6 remains A0; MoE gate not trained and S8 remains unapproved.

Canonical828000s/230h and six extensions once unchanged; actualremaining is a timestamped snapshot deducting the active tail. No extra budget/clearing/settlement. Only1ms working baseline;2ms closurefailure/suspended lock preserved. Preserve original hardware and model/data contracts and all failures/raw.3060 has frozen evaluation only and no canonical/4090launch authority. No weights/large NPZ/USD or credentials in Git. Every2h meaningful-only monitoring continues.
'''
(R/'SENSOR_STAGE_COMPLETE_AND_STABLE_REPORT.md').write_text(note,encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sf:
  E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';T='/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007'
  for root in (E,T):
   for n in ('SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json','SENSOR_STAGE_COMPLETE_AND_STABLE_REPORT.md','SENSOR_STABLE_CURRENT_ACTUAL.json','SENSOR_STABLE_STAGING_CPU_PASSED.json','D3_DELAY_COMPONENT_CPU_PASSED.json'):
    dest=root+'/reports/'+n;sf.put(str(R/n),dest+'.metadata_review');sf.posix_rename(dest+'.metadata_review',dest)
 code=r'''
from pathlib import Path
import json,time,hashlib
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');R=E/'reports';T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
assert not (R/'SENSOR_STAGE_COMPLETE_METADATA_PUBLISHED.json').exists()
def read(n):return json.loads((R/n).read_text())
def write(n,v):
 p=R/n;t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(v,indent=2));t.replace(p)
a=read('PLAN_APPROVAL.json');approval_before={k:a[k] for k in ('approved','approved_plan_sha256','allowed_stages','S8_authorized')}
assert a['approved_plan_sha256']==hashlib.sha256((R/'MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()
review=read('SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json');formal=review['formal'];actual=read('SENSOR_STABLE_CURRENT_ACTUAL.json');startup=actual['runs'][0]['SENSOR_RESUME_STARTUP_VERIFIED.json']
a['execution_events']['MOD4-E0-SENSOR-D1D2-STAGE1-001'].update(status='ACTUAL_FIRST45MIN_MATCHED_REVIEWED_SAME_SCOPE_STABLE_CONTINUATION',formal_source=formal['checkpoint'],actual_updates=279,actual_environment_steps=133920000,actual_health=formal['health'],limited_noise_platform_scope_accepted=True,firstseed_white3_not_graduation=True,clean_feedback_new_candidate_pending=True)
a['execution_events']['MOD4-E0-SENSOR-STABLE-CONTINUATION-001']=dict(epoch=time.time(),status='ACTUAL_NEW_UNIQUE_STABLE2H_LEARNING',source=formal['checkpoint'],root=str(T),source_count=206,old202_exact=True,actual_stochastic_restore_new_episode=startup,new_human_approval_inferred=False,new_budget_seconds=0)
assert {k:a[k] for k in approval_before}==approval_before;write('PLAN_APPROVAL.json',a)
tracks=read('EXECUTION_TRACKS.json');tracks['epoch']=time.time();tracks['learning']=dict(status=actual['phase'],root=str(T),owner=actual['owner'],guardian=actual['guardian'],child=actual['child'],source_count=206,stage='S2 E0 D1+D2 stable',architecture='A0',source=formal['checkpoint'],own_run=actual['runs'][0]['path'],startup_verified=startup,current_active_segment=actual['budget']['active_segment'],deadline_epoch=actual['Sactive']['deadline'],own_new_candidate_not_yet_behavior_reviewed=True)
tracks['evaluation']['sensor'].update(status='Seven noisySDK/baseline/candidate complete and limitedscope accepted; six cleanfeedback matched cases queued',noise_functional_scope_accepted=True,noise_platform_receipt='SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json',clean_feedback_scope_pending=True,clean_jobs=read('SENSOR_CLEAN_RETENTION_JOBS_PUBLISHED.json')['six_jobs'],publisher_prior_natural_complete=True,current_training_final_automatic_publication=True)
tracks['architecture_preparation'].update(status='HISTORICAL_CPU_COMPONENT_NOW_FULL_S1A_COMPARED_KEEP_A0',SDK_verified=True,architecture_PPO_started=True,selection_receipt='S1A_ARCHITECTURE_SELECTION.json',historical_baseline_field_not_current=True)
tracks['D3_preparation']=dict(root='/home/egde/rl_candidates/MOD4_D3_DELAY_COMPONENT_PREPARE_20261007',status='CPU11_ONLY_NO_SDK_OR_TRAINING',requested_us=[0,10000],actual_physics_dt_us=1000,new_sample_scope_not_installed=True)
write('EXECUTION_TRACKS.json',tracks)
write('SENSOR_FORMAL_CURRENT_SOURCE_VERIFIED.json',dict(epoch=time.time(),actual_final_formal=formal,limited_noisy_behavior_review='SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json',clean_feedback_pending=True,current_new_stable_source_is_this_formal=True,current_stable_own_new_save_requires_ownreceipt=True))
note=(R/'SENSOR_STAGE_COMPLETE_AND_STABLE_REPORT.md').read_text();(R/'LATEST_HANDOFF.md').write_text(note);(T/'reports/LATEST_HANDOFF.md').write_text(note)
write('SENSOR_STAGE_COMPLETE_METADATA_PUBLISHED.json',dict(epoch=time.time(),approval_scope_unchanged=True,master_SHA_unchanged=True,new_budget_seconds=0,formal_segment_not_recharged=True,actual_new_training_root=str(T),D3_CPU_only=True))
print(json.dumps(read('SENSOR_STAGE_COMPLETE_METADATA_PUBLISHED.json')))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_STAGE_COMPLETE_METADATA_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
