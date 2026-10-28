"""Existing actual reports only; no PT/SDK/actor/GPU/network or new experiment."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent
R=B/'reports'
def put(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((R/'E0_210_BOUNDED_FROZEN_REGRESSION_ORIGINAL_RESULT_RETURNED_ACTUAL.json').read_bytes())
q=v['regression'];m=q['all_population_metrics'];assert v['passed'] and v['actual_waited'] and v['returncode']==0 and not v['deadline_terminated']
assert q['controls']==120 and len(m)==120 and m[-1]['physics_tick']==960 and q['no_optimizer_step_no_norm_update']
s=dict(epoch=time.time(),scope='existing actual bounded E0 frozen inference reports only',passed_execution=True,source_SHA=q['source_SHA'],adaptation_updates=82,controls=120,physics_callbacks=960,num_envs=20000,simulated_seconds=2.4,mean_policy=True,new_PPO_updates=0,all17_Adam_steps=641200,actor_critic_STD_optimizer_literal_unchanged=True,termination_events=sum(x['terminated_count'] for x in m),truncation_events=sum(x['truncated_count'] for x in m),whole_horizon_forward_MAE_m_s=sum(x['forward_abs_tracking_error_mean'] for x in m)/120,whole_horizon_yaw_MAE_rad_s=sum(x['yaw_abs_tracking_error_mean'] for x in m)/120,first_control=m[0],last_control=m[-1],trace=q['trace'],trace_selected_transitions=3840,complete_WM_dataset=False,skill_graduation=False,limitations=['Single fixed physical seed and 2.4 simulated seconds; no long-horizon or original graduation protocol executed.','Selected32 prefix records requested/executed actions and terminal-before-autoreset state, but omits full127/xi31/eight-callback queue/DR schema.'],actual_waited_returncode=0,actual_known_own_identity=v['identity'],actual_private_EX_released=v['actual_private_EX_released'],no_budget_or_GO_writer=True,all_full_original_text_count=len(v['full_original_texts']),no_model_reread_for_summary=True)
put(R/'E0_ACTUAL_BOUNDED_FROZEN_CASE_EXISTING_EVIDENCE_SUMMARY_V1.json',s)
h=B/'HANDOFF_ACTUAL_E0_FROZEN_CASE_FINAL_V1.md'
with h.open('x',encoding='utf8') as f:f.write('Actual source210 E0 bounded frozen regression returned PASS/wait0; selected V2 entry and original V1 preseal missing binary dependency evidence are retained. Original N20k/a92/82-adaptation source, all D1-D7 startup restore receipts, 400N/50Hz/8-callback clock, mean policy 120 controls=2.4s. Core/STD/optimizer unchanged; all17 Adam641200; zero PPO or normalization updates. All-population termination/truncation event totals0. Final tracking MAE forward .027568856m/s, yaw .073039234rad/s. This short fixed-seed case is not skill graduation or a complete WM dataset. Actual27 full original UTF8 texts and all local errors/receipts retained. selected32 NPZ is producer metadata only for Git: 930438 bytes /4452c9b008c4e3233c9db386219c9169f1417628488f792e62f60302e4023c88; original remote and local paths in actual result. Global SSH lease returned; no ledger writes/GO/second writer. Source700 USD omission was caught before any V1 network; V2 added existing exact8777269-byte dependency694e9d54, preserving V1 unchanged. No PT was read to summarize or archive.\n')
rows=[]
for p in sorted(B.rglob('*')):
    if not p.is_file() or p.suffix.lower() in ('.npz','.pt','.usd','.whl','.zip'):continue
    rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p)))
put(B/'FROZEN_ACTUAL_E0_SOURCE_CASE_COMPLETE_HANDOFF_INDEX_V1.json',dict(epoch=time.time(),frozen=True,actual_passed=True,not_skill_graduation=True,not_complete_WM_dataset=True,files=rows,retained_large_artifacts=[q['trace']],source_input_complete_manifest='E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json',original_false_and_source_V1_retained=True,no_new_model_read_or_experiment=True))
print(json.dumps(dict(passed=True,summary=s,index=str(B/'FROZEN_ACTUAL_E0_SOURCE_CASE_COMPLETE_HANDOFF_INDEX_V1.json'))))
