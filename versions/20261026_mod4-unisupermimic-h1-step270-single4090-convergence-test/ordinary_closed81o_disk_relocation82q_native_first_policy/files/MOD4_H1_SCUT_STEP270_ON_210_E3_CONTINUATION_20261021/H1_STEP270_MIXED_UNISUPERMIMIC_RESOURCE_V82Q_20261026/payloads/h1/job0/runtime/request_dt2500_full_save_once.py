from pathlib import Path
import sys,time,json,re,traceback
P=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2500_PRACTICAL_20261007');sys.path.insert(0,str(P));import continue_selected_practical_clock_once as q
R=P/'reports';q.verify()
assert not (R/'DT2500_PPO_PHYSICAL_REJECTION.json').exists()
log=q.P/'auto_0397_clock20k_discard_cap12.5664_white_v3.log';text=log.read_text(errors='replace')
rates=[float(x) for x in re.findall(r'Episode_Termination/closure:\s*([0-9.]+)',text)];assert rates and max(rates)>0
q.write('DT2500_PPO_PHYSICAL_REJECTION.json',dict(epoch=time.time(),actual_closure_termination_observed=True,rounded_reported_rates=rates,
 log=str(log),log_sha256=q.base.sha(log),original_PPO_success_receipt_retained=True,physical_adoption_revoked=True,
 reason='Short frozen readback healthy, but complete stochastic20kPPO triggers actual closure terminations. Reject2.5ms; do not relax2mm contract. Preserve all weights and settle current own-save boundary once.',next_candidate_dt=.001,no_budget_mutation=True))
for _ in range(720):
 a=q.base.budget_state()['active_segment'];ident=q.helpers.identity(689795)
 assert a and a['pid']==689795 and ident and ident['state']!='Z' and ident['start_ticks']==46916056
 try:run=q.w.rate.trainer_run(q.P/'logs',689795);manifest=q.w.read(run/'run_manifest.json')
 except (AssertionError,FileNotFoundError):time.sleep(2);continue
 assert manifest['init_checkpoint_sha256']==q.SHA and manifest['env']['RM_PHYSICS_DT_S']=='.0025' or manifest['init_checkpoint_sha256']==q.SHA and float(manifest['env']['RM_PHYSICS_DT_S'])==.0025
 stop=run/'STOP_AFTER_SAVE';assert not stop.exists();stop.write_text('S0P actual2.5msPPO closure failure: preserve own full checkpoint and exit. Next1ms candidate waits actual owner accounting and two-lock boundary.\n')
 q.write('DT2500_OWN_SAVE_REQUESTED.json',dict(epoch=time.time(),trainer=ident,run=str(run),stop_path=str(stop),source_sha=q.SHA,no_forced_kill=True,no_new_GPU_or_budget_mutation=True));break
else:raise RuntimeError('Own run manifest not available within bounded wait')
