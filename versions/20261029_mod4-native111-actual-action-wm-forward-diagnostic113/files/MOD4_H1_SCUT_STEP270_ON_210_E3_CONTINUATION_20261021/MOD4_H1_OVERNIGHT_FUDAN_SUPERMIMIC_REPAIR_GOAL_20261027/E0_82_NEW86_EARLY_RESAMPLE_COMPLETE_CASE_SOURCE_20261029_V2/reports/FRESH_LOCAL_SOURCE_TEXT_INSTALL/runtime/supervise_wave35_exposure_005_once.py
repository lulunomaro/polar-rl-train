"""Independent Wave35 source3c97, one1800s duration-only exposure observation."""
from pathlib import Path
import argparse,json,os,time,subprocess,traceback
import supervise_e1_wave_isolated_revision004_once as inherited
from wave_budget005_source_guard import verify_original_records
m=inherited.m;D=Path(__file__).resolve().parent;R=D/'reports'
SOURCE_SHA=inherited.SOURCE_SHA
CURRENT=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011')
WAVE_OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010')
read=m.read;identity=m.identity;write=m.write;fullsave=m.fullsave
m.verify_original_records=verify_original_records
def verify():
 verify_original_records(m.s.q,D)
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(WAVE_OLD/'reports/SOURCE_FREEZE.json')['sha256']
 assert len(old)==366 and len(f)==368 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert m.s.q.base.sha(D/n)==h,n
 a=read(R/'REVISION_APPROVED.json');assert a['approved'] and a['approved_revision_id']=='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004'
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')==a['approved_revision_json_sha256']
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md')==a['approved_revision_md_sha256']
 c=read(m.s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert c['approved'] and c['active_next_expert']=='E1_WAVE'
 proof=read(R/'REUSED_ACTUAL_CONTRACTS.json');assert proof['passed'] and proof['same35mm_same_commands_same_reset_and_all_learning_modules_exact']
 for row in proof['actual_original_file_indices']:assert m.s.q.base.sha(Path(row['path']))==row['sha256'],row['path']
 assert read(R/'EXPOSURE_DURATION_DECISION.json')['seconds']==1800
 pkg=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime'];assert m.s.q.base.sha(Path(pkg['path']))==pkg['sha256']
 assert read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number']==142
def source():
 row=read(R/'SOURCE_SELECTED.json');p=Path(row['path']);assert m.s.q.base.sha(p)==SOURCE_SHA and fullsave(p)['finite_tensors']==102;return p
def exited(root,phase,label,sha):
 st=read(root/'reports/E1_STATE.json');row=read(root/'reports'/label)
 assert st['phase']==phase and st['child'] is None and row['checkpoint']['sha256']==sha
 for loc in (st['owner'],read(root/'reports/E1_GUARDIAN_STARTED.json'),row['own_PID_bound_receipt']):
  v=identity(loc['pid']);assert not v or v['state']=='Z' or v['start_ticks']!=loc.get('start_ticks',v['start_ticks'])
 assert [v for v in read(m.s.q.ctl.CANONICAL)['completed_segments'] if v['pid']==row['own_PID_bound_receipt']['pid']]==row['unique_completed_segment']
def boundary():
 exited(CURRENT,'E1_CURB20_direction_exposure_matched_saved_review_ready','e1_CURB20_direction_exposure_matched_observation_PASSED.json','7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43')
 exited(WAVE_OLD,'E1_WAVE_G3_isolated_saved_review_ready','e1_wave_G3_isolated_observation_PASSED.json','2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284')
 assert read(m.s.q.ER/'E1_CURB20_DIRECTION141_COMPLETE_OBSERVED_SCOPE_DECISION.json')['accepted_observed_CURB20_mirrored_scope']
 assert not m.trainers() and m.s.q.base.budget_state()['active_segment'] is None and not read(m.s.q.ctl.STATE_PATH).get('active_training')
def phase(name,**kw):
 if name.startswith('bounded_'):name='bounded_E1_WAVE35_exposure_005_learning'
 write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_WAVE',owner=identity(os.getpid()),**kw))
 m.s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='Approved004005 isolatedWave35 source1293c97 one1800s duration-only exposure; unchanged learning math/geometry/commands/reset; other experts frozen',active_expert='E1_WAVE',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
m.verify=verify;m.source=source;m.wait_existing=boundary;m.phase=phase;m.s.verify=verify
m.s.q.verify=m.s.q.w.verify=m.s.q.ctl.verify=lambda:verify_original_records(m.s.q,D)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();boundary();init=source()
 assert read(R/'WAVE_TARGET_CPU_PASSED.json')['passed'] and m.s.left()>1920
 m.s.q.helpers.acquire(m.s.q.P/'autonomy_controller.lock');m.s.q.helpers.acquire(m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
 before=m.s.q.ctl.CANONICAL.read_bytes()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),old_CURB_and_Wave_actual_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),expert='E1_WAVE',seconds=1800,duration_only_axis=True,unchanged20s_episode_and12to16s_command_resampling=True,no_repeated_SDK_native_PPO_preflight_clock=True,new_budget_seconds=0))
 assert before==m.s.q.ctl.CANONICAL.read_bytes()
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([m.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=m.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 saved,row=m.train(init,20000,10000,1800,'e1_WAVE35_exposure_005_observation',False)
 assert m.s.q.base.sha(init)==SOURCE_SHA and saved.is_relative_to(D/'learning_logs') and row['checkpoint']['finite_tensors']==102
 write('E1_WAVE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=fullsave(saved),source_SHA_preserved=True,output_owned_by_this_expert=True,E0_CURB_SLOPE_not_optimizer_or_save_targets=True))
 m.publish(saved,'142-e1-wave35-exposure-repair')
 write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,requires_actual142_fourcase_and_full_exposure_review=True,automatic_more_PPO_disallowed=True,no_automatic_50mm=True))
 phase('E1_WAVE35_exposure_005_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:m.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(m.s.LIVE and m.s.LIVE.poll() is None),active_segment=m.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
