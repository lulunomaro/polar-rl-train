"""One independent Wave expert observation under explicit subdivision revision004."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_e1_command_retention_matched_once as previous
m=previous.m;D=Path(__file__).resolve().parent;R=D/'reports'
OLD365=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010')
SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
read=m.read;identity=m.identity;fullsave=m.fullsave

def verify():
 m.verify_original_records(m.s.q,D)
 a=read(m.s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 revision=read(R/'REVISION_APPROVED.json');assert revision['approved'] and revision['approved_revision_id']=='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004'
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')==revision['approved_revision_json_sha256']
 assert m.s.q.base.sha(R/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md')==revision['approved_revision_md_sha256']
 current=read(m.s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json');assert current['terrain_subexpert_revision004']['approved'] and current['terrain_subexpert_revision004']['active_next_expert']=='E1_WAVE'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD365/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==366 and len(old)==365 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert m.s.q.base.sha(D/n)==h,n
 assert read(R/'CANDIDATE_130_COMPLETE_ACTUAL_REVIEW.json')['review_complete']
 assert read(R/'EXPERT_OWNERSHIP_CPU_PASSED.json')['passed']
 reused=read(R/'REUSED_CONTRACTS.json');assert reused['same_geometry_same_command_scope_all_actual_contracts_exact_reused'] and reused['no_new_math_or_plant_or_reward']
 assert read(R/'SOURCE_SELECTED.json')['sha256']==SOURCE_SHA
 pkg=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime'];assert m.s.q.base.sha(Path(pkg['path']))==pkg['sha256']

def source():
 row=read(R/'SOURCE_SELECTED.json');p=Path(row['path']);assert m.s.q.base.sha(p)==SOURCE_SHA and fullsave(p)['finite_tensors']==102;return p

def wait_existing():
 state=read(OLD365/'reports/E1_STATE.json');row=read(OLD365/'reports/e1_G3_command_retention_matched_PASSED.json')
 assert state['phase']=='E1_G3_command_retention_matched_saved_review_ready' and state['child'] is None and (OLD365/'reports/E1_REVIEW_READY.json').exists()
 assert row['checkpoint']['sha256']=='f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a' and len(row['unique_completed_segment'])==1
 for loc in (state['owner'],read(OLD365/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=79649880)):
  actual=identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 assert len([x for x in read(m.s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']])==1
 assert not m.trainers() and m.s.q.base.budget_state()['active_segment'] is None and not read(m.s.q.ctl.STATE_PATH).get('active_training')

def phase(name,**kw):
 if name.startswith('bounded_'):name='bounded_E1_WAVE_G3_isolated_learning'
 m.write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_WAVE',owner=identity(os.getpid()),**kw))
 m.s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='Approved revision004 independent E1_WAVE same35mm/sameconditionedcommands 300s; E0 frozen; other terrain expert weights never overwritten',active_expert='E1_WAVE',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)

m.verify=verify;m.source=source;m.wait_existing=wait_existing;m.phase=phase;m.s.verify=verify
m.s.q.verify=m.s.q.w.verify=m.s.q.ctl.verify=lambda:m.verify_original_records(m.s.q,D)

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source()
 m.s.q.helpers.acquire(m.s.q.P/'autonomy_controller.lock');m.s.q.helpers.acquire(m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 before=m.s.q.ctl.CANONICAL.read_bytes();initial_SHA=m.s.q.base.sha(init)
 m.write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),revision004_approved=True,old365_all_actual_exited=True,two_original_locks_held=True,active_empty=True,expert='E1_WAVE',new_budget_seconds=0))
 m.write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),expert='E1_WAVE',seconds=300,independent_output_root=str(D),no_repeated_SDK_native_PPO_preflight_clock=True,new_budget_seconds=0))
 assert before==m.s.q.ctl.CANONICAL.read_bytes()
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([m.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=m.s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 m.write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 saved,row=m.train(init,20000,10000,min(300,m.s.left()),'e1_wave_G3_isolated_observation',False)
 assert m.s.q.base.sha(init)==initial_SHA==SOURCE_SHA
 assert Path(row['run']).is_relative_to(D/'learning_logs') and saved.is_relative_to(D/'learning_logs')
 m.write('E1_WAVE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),expert='E1_WAVE',own_checkpoint=fullsave(saved),immutable_warmstart_SHA_unchanged=True,output_owned_by_this_expert=True,E0_and_other_expert_weights_not_update_targets=True,all_saved_old_source_files_verified=True))
 m.publish(saved,'131-e1-wave-g3-isolated')
 m.write('E1_REVIEW_READY.json',dict(epoch=time.time(),expert='E1_WAVE',own_saved_source=str(saved),all_courses_finished=False,requires_full131_route_review=True,inherited_flat_skills_diagnostic_not_E0_replacement=True,automatic_more_PPO_disallowed=True,other_expert_branches_require_their_own_contracts=True))
 phase('E1_WAVE_G3_isolated_saved_review_ready',child=None)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);a=parser.parse_args()
 try:
  if a.guardian:m.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  m.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(m.s.LIVE and m.s.LIVE.poll() is None),active_segment=m.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
