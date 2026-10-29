"""Freeze actual CPU diagnostic and the source-only next candidate; no binary/host reads."""
from pathlib import Path
import json,hashlib,time
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D=L/'native114_WM_fixed_world_heading_visibility_source_v1'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
actual=load(R/'NEW113_ACTUAL_ACTION_WM_WORLD_X_VELOCITY_CPU_COMPLETE_ACTUAL.json')
proof=load(D/'reports/SOURCE114_OLD_INPUT_ALIAS_OWN_FK_AND_BOUNDED_CANDIDATE_CPU_ACTUAL.json')
assert actual['passed_execution'] and actual['raw_controls_reads']==actual['full_checkpoint_decodes']==1
assert proof['passed_source_CPU'] and proof['model_or_parameter_or_raw_or_SDK_reads']==0
handoff='''NEW114 SOURCE ONLY / NOT ADMITTED / NOT TRAINED

NEW113 necessary CPU-only worldX/worldVx actual-action diagnostic completed after all source/data/lineage gates. One NEW112 control read and one qualified111 checkpoint decode; only WM constructed/forward, no Pi/Critic/optimizer/GPU/physics/account. Mean absolute forward velocity error1/8/32 = .0074218963/.020997759/.0457328372m/s; mean absolute rootX error .0000958995/.0008423873/.0076828133m. Actual low-speed/sub1.2cm trajectory is NOT .5m/s or270mm/counterfactual qualification. All horizons use actual action at each offset and open-loop predicted state, never policy-resampled actions or per-step truth correction. Overlapping windows not independent trials.

The old WM neural inputs remove world yaw while terrain-relative coordinates stay in fixed world axes. A new own-FK source pair with identical old167 input features, equal world position/joint shape/body velocities/actions/zero world-contact histories has opposite world velocities and distinct wheel-plane approach. This is a source observability counterexample. Constant-velocity10ms projection is NOT PhysX dynamics/manifold, observed failure causation or mechanical feasibility. WM.step already rotates outputs: equal neural inputs do not imply equal world outputs. Heading-correlated contact history can help some states; it does not resolve all zero/vertical-force alias cases.

Candidate changes ONLY WM.inputs features1/3 by bounded .005*(cosyaw-1),.005*sinyaw using projected body-forward column. Existing width167/constructor/step/targets/state_error AST identical, exact originalbytes inverse preserved. No architecture/weights/norm tensors/3opts/reward111/actor/critic/physics/action/clock/20s change. No wrapped-angle seam. Source25443 valid SO3 grid: other165 columns literal unchanged, raw cue max .01/.005, normalized shift <=1/.5 under original RunningNorm eps.01 worst zero-variance fixture; finite nonzero combined yaw derivative. This is NOT an actual inherited norm readback or a parameter migration qualification. World-forward projection near vertical is regularized; valid physical tilt scope and synthetic checks do not prove global invertibility.

Original V1 prep LF/CRLF literal assertion before source/model/raw/SDK preserved. NEW V2 preparer uses AST literals only and preserves originalCRLF/exactbyte inverse. Source proof ran once; no more model/raw reads for statistics/Git. This source has no standalone runtime/Task/GO. Next actual use requires typed111 input/114 output source recipe, original source producer versus current output producer correct pins, actual targetSDK/fullstate+norm/input/rewardframe readback, original400 reset/preload, fresh light resources/CNone/private/shared locks/single72writer and a newly sealed finite protocol. Do not treat source-only114 as installed or success; no blind unchanged learning. Remaining far-from-edge jump-bonus tradeoff is separate and still needs a narrow own-wheel-front reward candidate, not simultaneous untracked changes.
'''
with (D/'HANDOFF_SOURCE114_ONLY_NOT_RUNTIME.md').open('x',encoding='utf-8') as f:f.write(handoff)
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and '__pycache__' not in p.parts:
  b=p.read_bytes();files.append(dict(relative=p.relative_to(D).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
for p in (S/'prepare_NEW114_WM_heading_input_source_only.py',S/'prepare_NEW114_WM_heading_input_source_only_v2.py',S/'verify_NEW114_WM_heading_alias_and_candidate_CPU_SOURCE_ONLY_once.py'):
 b=p.read_bytes();files.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
idx=D/'FROZEN_SOURCE114_INPUT_HEADING_CPU_ONLY_INDEX_V1.json'
save(idx,dict(epoch=time.time(),status='COMPLETE_FROZEN_SOURCE_ONLY_NOT_RUNTIME_ADMITTED',files=files,model_raw_SDK_GPU_read_count=0,actual113_model_read_is_separate_new_purpose=True))
work=dict(schema='mod4.actual113.complete_and_source114.only.workorder.v1',epoch=time.time(),actual113_complete=str(R/'NEW113_ACTUAL_ACTION_WM_WORLD_X_VELOCITY_CPU_COMPLETE_ACTUAL.json'),
 actual113_once=dict(raw_control_reads=1,qualified111_checkpoint_decodes=1,model_integrity_hash_passes=1,WM_only=True,normal86_reads=0,Pi_Critic_optimizer_GPU_SDK_physics_SSH_account_actions=0),
 actual113_worldVX_MAE_m_s=[.007421896327286959,.020997758954763412,.04573283717036247],
 source114_frozen_index=str(idx),source114_index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source114_runtime_used=False,
 latest_qualified_native_METHOD='111h1/24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12/global18597-185970WM-17893Pi',
 current_GPU_job_state='All previously run finite GPU tasks closed. This heartbeat only CPU/source work so far. No live availability inference.',
 actual270_goal_achieved=False,H1_reward_before_use_gate_remains=True,
 next_root='Choose separately measured WM heading admission or narrow own-wheel-front far-field jump-bonus repair; do not bundle speculative changes or claim unique cause. Freeze input/output/producer/reward proofs, actual targetSDK/fullstate/readback/resource/solewriter TaskGO before learning.',
 old_experts='Same one sequential child completed early original E0 resample passthrough source. Full newE0V2 caller/Task/metadata/readers explicitpending until frozen handoff. No source-only GPU claim.',
 original_errors='113 V1 syntax, V2 str/Path helper and original guessed source paths retained; NEW114 V1 CRLF literal refusal retained; consumed entries not rerun.',
 archive='New actual CPU113 phase gets unique record once; no retag111/112, all errors/reports/source and frozen child packages, binary existing metadata only. Actual Git refs dominate pending words.')
save(R/'CURRENT_ACTUAL113_CPU_FORWARD_COMPLETE_AND_FROZEN114_SOURCE_ONLY_WORK_ORDER.json',work)
print(json.dumps(dict(work_order=str(R/'CURRENT_ACTUAL113_CPU_FORWARD_COMPLETE_AND_FROZEN114_SOURCE_ONLY_WORK_ORDER.json'),source114_index=str(idx),source114_index_SHA=work['source114_index_SHA']),ensure_ascii=False))
