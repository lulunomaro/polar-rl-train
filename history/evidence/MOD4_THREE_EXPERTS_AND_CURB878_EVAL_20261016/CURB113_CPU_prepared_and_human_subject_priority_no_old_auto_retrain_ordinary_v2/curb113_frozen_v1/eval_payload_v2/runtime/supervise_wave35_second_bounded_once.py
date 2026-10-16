"""One reviewed same-G3 same-command second1800s block; no automatic third."""
from pathlib import Path
import argparse,json,os,time,subprocess,traceback
import supervise_wave35_exposure_005_once as prior
m=prior.m;D=Path(__file__).resolve().parent;R=D/'reports'
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_EXPOSURE_REPAIR_20261011')
SOURCE_SHA='7f1032ad33b87671dcb6450f19c15122de45e3d76a8700d92ab5dcd8be3ee0e4'
read=m.read;write=m.write;identity=m.identity;fullsave=m.fullsave
def verify():
 prior.verify_original_records(m.s.q,D)
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
 assert len(old)==368 and len(f)==369 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert m.s.q.base.sha(D/n)==h,n
 a=read(R/'REVISION_APPROVED.json');assert a['approved'] and a['approved_revision_id']=='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004'
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')==a['approved_revision_json_sha256']
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md')==a['approved_revision_md_sha256']
 c=read(m.s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert c['approved'] and c['active_next_expert']=='E1_WAVE'
 decision=read(R/'COMPLETE142_SCOPE_DECISION.json')
 assert decision['full_four_cases_complete_errorfree_and_raw_reviewed'] and decision['allow_one_additional_bounded_same_scope_block_under005']
 assert decision['own_checkpoint_SHA']==SOURCE_SHA and decision['maximum_additional_block_seconds']==1800 and decision['automatic_third_block_disallowed']
 for row in read(R/'REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']:assert m.s.q.base.sha(Path(row['path']))==row['sha256'],row['path']
 reuse=read(R/'REUSED_ACTUAL_CONTRACTS.json');assert reuse['passed'] and reuse['same35mm_same_commands_same_reset_and_all_learning_modules_exact']
 assert read(R/'SECOND_BOUNDING_DECISION.json')['seconds']==1800
 pkg=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime'];assert m.s.q.base.sha(Path(pkg['path']))==pkg['sha256']
 job=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json');assert job['actual_both_hosts_queue_results_jobs_unused'] and job['number']>142
def source():
 row=read(R/'SOURCE_SELECTED.json');p=Path(row['path']);assert m.s.q.base.sha(p)==SOURCE_SHA and fullsave(p)['finite_tensors']==102;return p
def boundary():
 prior.exited(OLD,'E1_WAVE35_exposure_005_saved_review_ready','e1_WAVE35_exposure_005_observation_PASSED.json',SOURCE_SHA)
 assert not m.trainers() and m.s.q.base.budget_state()['active_segment'] is None and not read(m.s.q.ctl.STATE_PATH).get('active_training')
def phase(name,**kw):
 if name.startswith('bounded_'):name='bounded_E1_WAVE35_second_bounded_learning'
 write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_WAVE',owner=identity(os.getpid()),**kw))
 m.s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='Approved004005 Wave35 reviewed second1800s sameG3samecommand block from own3687f; full142 reviewed; no automaticthird; other experts frozen',active_expert='E1_WAVE',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
m.verify=verify;m.source=source;m.wait_existing=boundary;m.phase=phase;m.s.verify=verify
m.s.q.verify=m.s.q.w.verify=m.s.q.ctl.verify=lambda:prior.verify_original_records(m.s.q,D)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();boundary();init=source()
 assert read(R/'SECOND_TARGET_CPU_PASSED.json')['passed'] and m.s.left()>1920
 m.s.q.helpers.acquire(m.s.q.P/'autonomy_controller.lock');m.s.q.helpers.acquire(m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
 before=m.s.q.ctl.CANONICAL.read_bytes()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),old368_actual_parent_guardian_child_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),expert='E1_WAVE',seconds=1800,second_same_repair_scope_block=True,no_automatic_third_block=True,same_geometry_reset_command_reward_LR_DR=True,no_repeated_SDK_native_PPO_preflight_clock=True,new_budget_seconds=0))
 assert before==m.s.q.ctl.CANONICAL.read_bytes()
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([m.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=m.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 saved,row=m.train(init,20000,10000,1800,'e1_WAVE35_second_bounded_observation',False)
 assert m.s.q.base.sha(init)==SOURCE_SHA and saved.is_relative_to(D/'learning_logs') and row['checkpoint']['finite_tensors']==102
 write('E1_WAVE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=fullsave(saved),source_SHA_preserved=True,output_owned_by_this_expert=True,E0_CURB_SLOPE_not_optimizer_or_save_targets=True))
 number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number'];m.publish(saved,str(number)+'-e1-wave35-second-bounded')
 write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,candidate_number=number,requires_actual_fourcase_and_full_exposure_review=True,automatic_more_PPO_disallowed=True,no_automatic_50mm_or_third_block=True))
 phase('E1_WAVE35_second_bounded_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:m.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(m.s.LIVE and m.s.LIVE.poll() is None),active_segment=m.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
