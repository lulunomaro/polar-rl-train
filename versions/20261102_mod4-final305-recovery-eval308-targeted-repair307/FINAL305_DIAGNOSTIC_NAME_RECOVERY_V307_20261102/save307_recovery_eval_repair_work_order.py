"""Save a source-backed handoff; no model/network or experiment replay."""
from pathlib import Path
import json, time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent
def read(p):return json.loads(p.read_bytes())
def put(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)

cpu=read(N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json')
E=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102';evaluation=read(E/'reports/ROOT308_EVALUATION_FULL_RETURNED.json')['result']
assert cpu['passed'] and evaluation['passed'] and cpu['SHA']==evaluation['model_SHA']
assert evaluation['strict_successes']==evaluation['crossed_cases']==0
probe=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102'
repair=T/'FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102'
report=read(repair/'reports/ACTUAL312_ORIGINAL305_REPORT_CLASSIFICATION_VALIDATION.json')
assert report['passed']
resource=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_eval_snapshot_20261102_011546.json')
snapshot=read(resource)
old305=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
put(N/'reports/CURRENT_ACTUAL307_RECOVERED305_EVAL308_REPAIR_WORK_ORDER_V1.json',dict(
 epoch=time.time(),status='FINAL305_SAVED_RECOVERED_EVALUATED_FAILED_TARGETED_REPAIR_READY_RESOURCE_WAIT',
 final305=cpu,original305_false_preserved=True,normal305_consumed=True,CPU305_failed_before_model_read=True,postround306_exited_failed_no_eval=True,
 recovery307_consumed=True,CPU307v1='SyntaxError before imports/model read; original preserved',CPU307v2='complete final decoded once,609 finite tensors and full optimizer/state preservation passed',
 evaluation308=dict(root=str(E),receipt=str(E/'reports/ROOT308_EVALUATION_FULL_RETURNED.json'),strict_success=0,crossed=0,cases=80,orientation=evaluation['terminations']['bad_orientation'],full8s=sum(r['full_window']for r in evaluation['results']),mean_seconds=sum(r['seconds']for r in evaluation['results'])/80,terminations=evaluation['terminations'],same_fixed270_course=True,newDR_episode_seed=9137,heldout_new_terrain=False),
 actual_replay=dict(image=str(E/'RECORDED308_NATIVE_FRAMES/ACTUAL308_FINAL305_BODY_POSE_SEQUENCE.png'),native_current_model_viewed=True,review='4cases x3 actual recorded body poses, platform visible. Earlypitch/leg folding and tilt at .26-.32s, far before platform. No cross. No additional physics or network inference for replay.',viewer_opened=True),
 comparison300=dict(strict_success=0,crossed=0,orientation=66,full8s=14),decision='Do not continue305 unchanged:70orientation/10full8s is worse than30066/14. Check reference-task starting physical distribution with a no-model actual control probe; maintain tracking objective and physical contract.',
 source_hypotheses=dict(reference_initial_state='MuJoCo planned q/dq/root at phase0 differs from current originalreset. Not established as causal.311 two-group physical test pending; not the disproved old35obs defaultqABI hypothesis.',model_exploitation='Prior actual training H32 positionRMSE.06415m exists; smooth same-task losses do not establish physical tracking. No new finalWM error measured by this handoff.',critic='305 realTD and matchedsurvival repair did not improve independent skill; do not assert solved.'),
 attempts=dict(local309='producer IndentationError,0 network/SDK/model/physics',physical310='shared finitevalidation EX lock refused before SDK/physics/model; original consumed once retained',physical311=dict(root=str(probe),status='UNUSED_PENDING_SHARED_RELEASE',runner=str(probe/'run311_probe_once.py'),task=str(probe/'TASK311_FROZEN.json'),groups='40 originalreset vs40 planned fullreference0 reset; sameplanned jointq/dq targets, separate draws from same DR distribution',controls_max=64,model_reads=0,optimizer_steps=0,canonical_writes=0),classification312=dict(root=str(repair),status='UNUSED_SOURCE_FIX_VALIDATED_LOCAL',deployed=False,validation=str(repair/'reports/ACTUAL312_ORIGINAL305_REPORT_CLASSIFICATION_VALIDATION.json'))),
 classification_fix='Future independent node/collector recognize only exact successful305 WMdiagnostic by schema and finite metrics; unknown/malformed/realerror remain fatal. Future worker diagnostic uses METRICS name. Original305 frozen source and false receipts unchanged; do not rerun normal/CPU/postround.',
 resource=dict(local_snapshot=str(resource),snapshot_captured=snapshot['captured_local'],shared_owner_job=snapshot['job'],parent=1418833,worker=1418842,worker_creation=1793552711.6,GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842',finite_validation_EX=True,latest_observation='Native24 and fullrestore active; no local terminal/released marker yet. GPU1 unused does not authorize bypassing shared lock.',read_only_status='No new H1 SSH while known shared controller executing; read local handoff first.'),
 next='Read fresh local W35 terminal/lock release first. If current exact local serialcontrol leaseFREE and shared job released, execute only unused311 once via original parent admission (samebudget0writes); review actual initialstate/termination/replay. If resources remain busy, finish Git+automation and leave concrete311pending without polling GPU/creatingwatcher. If311 consumed, read results and create independent version for actual failure, never replayonce. Based on actual probe choose within-task repair; no unchanged305trainingGO.',
 physics='400Nengineeringk2000,50policy100feedback400physics2.5msTGS32/4,fullD0whitev3D1-D7,closure10mm perenv,mimic.01rad; original canonical and full save boundaries',
 scope='103actor35proprio+9currentdepth+59plannedreference,106critic,continuousphase0..249,lookahead0/10,exp(-weightedcost/5),PPO0,Fudanfalse; plannedreference tracker not autonomous depth-only student. No LQR/MPC torque action cloning; future real depth/GTmap not actor/H32.',
 new_mod4v1='Read current rootAGENTS and newexpertregistry; this historicalH1 remainsproducerjoinpending. Do not silently switch currentphysicalprobe to other USD/contract or claim expertadapted. Coordinate existing tasks at proper fullsave boundaries.',
 budget=dict(new_GO=False,originalfee305=cpu['originalfee'],historical_closing_balance305=383272.1536028385,sole_canonical_preserved=True,no_grant_copy_clear_refund_or_secondwriter=True),
 ssh=dict(all_owned_closed=True,SESSION_restored=True,serial_control_lease='FREE',last_receipt=str(T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V310_20261102/reports/ROOT310_ALL_SSH_CLOSED_FREE.json')),
 git=dict(status='PENDING_THIS307_RECOVERY_EVAL_AND_REPAIR_PHASE_ARCHIVE',phase='mod4-final305-recovery-eval308-targeted-repair307',old305_tag_unchanged=True,old300_tag_unchanged=True),
 prohibitions='No oldconsumedonce replay,healthyrestart,hotpatch,unknownPID/GPUscan/kill,newbudget,Luna/OpenRouter. Success requires real firstflightcross/fullwheelfootprint/top contactmanifold/.5sstability. Preserve every originalfalse/raw/report/source and oldtagobjectpeels/lqr.'
))
put(N/'reports/LOCAL307_CONTINUATION_TOOL_ERRORS_AND_SCOPE.json',dict(epoch=time.time(),errors=[
 'CODEX_HOME not set in exec environment; attempted /automations path missing; read actual C:/Users/lulu/.codex/automations/mod4-10/automation.toml successfully.',
 'Exploratory nonexistent source/reference_student305.py search; corrected to actual tracking_learner305.py without running a model.',
 'Unbounded rg matched an embedded UTF8 multiline payload; output oversized; no experiment/model/network triggered.'
],model_read_for_these_errors=0,network_for_these_errors=0,known_original_failures_preserved=True))
print(json.dumps(dict(work_order=str(N/'reports/CURRENT_ACTUAL307_RECOVERED305_EVAL308_REPAIR_WORK_ORDER_V1.json'),strict=0,orientation=70,new_GO=False)))
