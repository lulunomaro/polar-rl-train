"""New bounded same-scope continuation after complete140 and saved exposure diagnosis."""
from direction_io import *
import ast,traceback

OLDROOT='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_STARTUP_REVIEWED_20261011'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011'

CONTROLLER=r'''"""One900s same-CURB-entry-direction continuation, no admission/physics replay."""
from pathlib import Path
import argparse,json,time,os,subprocess,traceback,inspect
import supervise_curb20_direction_startup_reviewed_once as prior
D=Path(__file__).resolve().parent;R=D/'reports';read=prior.read;write=prior.write
PREVIOUS=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_STARTUP_REVIEWED_20261011')
INIT_SHA='e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16'

# This module belongs only to the new independent root. Original bytes stay intact.
text=inspect.getsource(prior.train)
old="assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_CURB_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
new="assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_CURB_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
assert text.count(old)==1;text=text.replace(old,new)
old="assert terrain['explicit_new_entry_reset_scope'] and not terrain['entry_reset_state_restored_exact']"
new="assert not terrain['explicit_new_entry_reset_scope'] and terrain['entry_reset_state_restored_exact']"
assert text.count(old)==1;text=text.replace(old,new)
old="assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and direction['actual_CUDA_direction_disk_roundtrip_exact']"
new="assert direction['passed'] and not direction['explicit_new_episode_direction_scope'] and direction['predecessor_direction_state_restored_exact'] and direction['actual_CUDA_direction_disk_roundtrip_exact']"
assert text.count(old)==1;text=text.replace(old,new)
exec(compile(text,str(Path(__file__))+'::same_scope_train','exec'),prior.__dict__)

def source():
 row=read(R/'MATCHED_SOURCE_SELECTED.json');p=Path(row['path'])
 assert prior.s.q.base.sha(p)==INIT_SHA and prior.fullsave(p)['finite_tensors']==104
 return p

def boundary():
 st=read(PREVIOUS/'reports/E1_STATE.json');assert st['phase']=='E1_CURB20_direction_repair_saved_review_ready' and st['child'] is None
 passed=read(PREVIOUS/'reports/e1_CURB20_direction_repair_observation_PASSED.json');assert passed['checkpoint']['sha256']==INIT_SHA
 for loc in (st['owner'],read(PREVIOUS/'reports/E1_GUARDIAN_STARTED.json'),passed['own_PID_bound_receipt']):
  a=prior.identity(loc['pid']);assert not a or a['state']=='Z' or a.get('start_ticks')!=loc.get('start_ticks')
 assert not prior.trainers() and prior.s.q.base.budget_state()['active_segment'] is None and not read(prior.s.q.ctl.STATE_PATH).get('active_training')
 assert read(R/'CURB140_COMPLETE_SCOPE_DECISION.json')['allow_one_exposure_duration_only_continuation']
 assert read(R/'MATCHED_REUSE_CPU_PASSED.json')['passed']

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();prior.verify();boundary();init=source()
 prior.s.q.helpers.acquire(prior.s.q.P/'autonomy_controller.lock');prior.s.q.helpers.acquire(prior.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
 before=prior.s.q.ctl.CANONICAL.read_bytes()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=prior.identity(os.getpid()),source=prior.fullsave(init),actual_previous_closeout_and_two_locks_held=True,new_budget_seconds=0))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=prior.identity(os.getpid()),source=prior.fullsave(init),seconds=900,only_training_exposure_duration_axis=True,no_SDK_native_PPO_preflight_fresh_or_clock_replay=True,new_budget_seconds=0))
 assert prior.s.q.ctl.CANONICAL.read_bytes()==before
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([prior.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(prior.identity(os.getpid())['start_ticks'])],cwd=prior.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',prior.identity(g.pid))
 saved,row=prior.train(init,20000,10000,min(900,prior.s.left()),'e1_CURB20_direction_exposure_matched_observation',False)
 assert prior.s.q.base.sha(init)==INIT_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),selected_source_SHA_preserved=True,E0_Wave_SLOPE_not_optimizer_or_save_targets=True))
 prior.publish(saved)
 write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,requires_actual_candidate_fourcase_review=True,automatic_more_PPO_disallowed=True))
 prior.phase('E1_CURB20_direction_exposure_matched_saved_review_ready',child=None)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(prior.s.LIVE and prior.s.LIVE.poll() is None),active_segment=prior.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''

def main():
 reviewpath=sorted(R.glob('CURB140_SCHEMA_REVIEW_[0-9]*.json'))[-1];review=json.loads(reviewpath.read_bytes());diag=json.loads((R/'CURB140_COMPLETE_PREFIX_EXPOSURE_DIAGNOSIS.json').read_bytes())
 assert review['review_complete'] and not review['pending'] and diag['candidate140_ascending_complete']==23
 assert diag['formal_actual_exposure']['histogram_phase_relation_exact']
 decision=dict(epoch=time.time(),trial_id='CURB140-COMPLETE-SCOPE-AND-ONE-EXPOSURE-CONTINUATION-01',complete_review=str(reviewpath),complete_review_SHA=H(reviewpath.read_bytes()),diagnosis=diag,
  qualified_CURB=False,source132_ascending=26,candidate139_ascending=23,candidate140_ascending=23,descending_complete=27,ascending_count=27,
  negative4pi_diagnostic_source7_candidate3_of8=True,E0_frozen_and_gate_not_trained=True,
  allow_one_exposure_duration_only_continuation=True,selected_same_scope_checkpoint=review['own']['checkpoint'],target_seconds_including_load_learn_save_exit=900,
  selection_reason='Select reviewed own423 only for one same-scope continuation. Saved fulltrace proves only1.68s simulated control, reset root offsets.8/1.65m, maximum command integral.504m, and no root center side change. Correct signed/standing coverage did not provide a full-route training window. This is an exposure hypothesis, not proven causal efficacy, graduation or automatic default for new experts.',
  no_more_than_one_new_block_before_full_review=True,no_third_automatic_same_scope_block=True,no_geometry_commands_reward_LR_DR_hardware_change=True,
  exact_CPU_SDK_native_small_big_fresh_clock_geometry_reuse_no_replay=True,no_original_false_prefix_or_cost_relabel=True,no_new_budget_seconds=0)
 save('CURB140_COMPLETE_SCOPE_DECISION.json',decision)
 note=R/'NEXT_DIRECTION_EXPOSURE_MATCHED_WORK_ORDER.md';assert not note.exists();note.write_text('# CURB20 one bounded exposure continuation\n\nComplete140: up23/27, down27/27, ordinary0; original positive cases3/6/15/36 remain valid incomplete turning/lateral prefixes. Negative4pi diagnostic7→3/8 remains. No graduation. Saved formal168control=1.68s, reset.8/1.65m, nominal maxdistance.504m and actual root no center cross; histogram prephysics/after-update endpoints exact. Select own423 e6df fullCPU104 explicitly only for same-scope900s exposure continuation, retaining original source1293c97 and previous false. New root preserves423 bytes plus one unique controller; samegeometry/entry/direction startup must strict exact/CUDAroundtrip/episode+1. Reuse all prior SDK/native/small/big/fresh/clock/DR exactSHA, no repeat. Actual parentguardianchild exit/twoOSlocks/idle unique canonical before dispatch. Own fullsave/PASSED/uniquecloseout then new actual unused fourcase candidate; no more PPO before complete matched review and new fulltraining exposure audit. No shortened approach, extended evaluation window, newcommands/reward/LR/teacher or E0/Wave/SLOPE/gate/player change. Original7extensions budget330h, no newextension or copying. Samehourlyheartbeat quietpending; allsaved evidence Git.\n',encoding='utf8')
 p=D/'exposure_matched_payload/supervise_curb20_direction_exposure_matched_once.py';p.parent.mkdir();ast.parse(CONTROLLER);p.write_bytes(CONTROLLER.encode())
 save('EXPOSURE_MATCHED_LOCAL_PREPARED.json',dict(epoch=time.time(),root=ROOT,controller=str(p),controller_sha256=H(p.read_bytes()),source_checkpoint=review['own']['checkpoint'],CPU_target_and_dispatch_pending=True,new_scope_is_duration_only=True))
 print(json.dumps(dict(decision=str(R/'CURB140_COMPLETE_SCOPE_DECISION.json'),new_controller=str(p),selected_SHA=review['own']['checkpoint']['sha256'],seconds=900,not_qualified=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('EXPOSURE_MATCHED_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
