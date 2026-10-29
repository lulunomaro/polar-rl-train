"""One reviewed same50 fullstate1800s continuation; never a third blind block."""
from pathlib import Path
import argparse,json,os,time,subprocess,traceback,inspect
import supervise_wave50_entry_scope_once_v2 as prior
from wave50_entry_source_guard import verify_original_records as original005
D=Path(__file__).resolve().parent;R=D/'reports';read=prior.read;write=prior.write
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012')
INIT_SHA='ea9fd8558079ec690b0a483e3620c27201ed1afc36cfac56ec2a5c74f42c1f5a'
ORIGINAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
ENTRY='train_wave50_entry_same_scope_resume_ppo.py'
def verify():
 original005(prior.s.q,D)
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==410 and len(f)==412 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert prior.s.q.base.sha(D/n)==h,n
 a=read(prior.s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages']
 rev=read(prior.s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
 decision=read(R/'COMPLETE148_SCOPE_DECISION.json');assert decision['full_four_cases_complete_errorfree_and_raw_reviewed'] and decision['allow_one_second_bounded_same50_entry_scope_exposure_block_under005'] and decision['maximum_additional_block_seconds']==1800 and decision['automatic_third_block_disallowed'] and decision['own_checkpoint_SHA']==INIT_SHA
 reuse=read(R/'REUSED_ACTUAL_CONTRACTS.json');assert reuse['passed'] and reuse['same50_entry_geometry_command_reset_reward_LR_DR']
 for row in reuse['actual_original_file_indices']:assert prior.s.q.base.sha(Path(row['path']))==row['sha256']
 assert read(R/'ENTRY_SECOND_TARGET_CPU_PASSED.json')['passed'] and prior.s.q.base.budget_state()['remaining_training_seconds']>1920
 for t in read(R/'WAVE50_FOUR_CASE_TEMPLATES.json')['jobs']:assert prior.s.q.base.sha(Path(t['artifacts']['runtime']['path']))==t['artifacts']['runtime']['sha256']
def source():
 row=read(R/'MATCHED_SOURCE_SELECTED.json');p=Path(row['path']);assert prior.s.q.base.sha(p)==INIT_SHA and prior.fullsave(p)['finite_tensors']==102
 return p
original_trainers=prior.trainers
def trainers():
 rows=original_trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   argv=[x.decode(errors='replace') for x in p.read_bytes().split(b'\0')]
   if any(Path(x).name==ENTRY for x in argv):rows.append(prior.identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return rows
def boundary():
 st=read(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE50_entry_saved_review_ready' and st['child'] is None
 p=read(OLD/'reports/e1_WAVE50_entry_observation_PASSED.json');assert p['checkpoint']['sha256']==INIT_SHA and len(p['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=90749332)):
  a=prior.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and prior.s.q.base.budget_state()['active_segment'] is None and not read(prior.s.q.ctl.STATE_PATH).get('active_training')
original_runtime=prior.runtime
def runtime():
 e=original_runtime()
 for n in tuple(e):
  if n.endswith('INITIAL_ADMISSION'):e.pop(n)
 return e
def phase(name,**kw):
 if name.startswith('bounded_'):name='bounded_E1_WAVE50_entry_second_bounded_learning'
 write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_WAVE50',owner=prior.identity(os.getpid()),**kw))
 prior.s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='004005 reviewed148 same50entry second1800s exposure, allpreflights exactreuse, no third blindblock',active_expert='E1_WAVE50',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
# Only controller receipt expectations and the worker's truthful manifest change.
text=inspect.getsource(prior.train)
old="assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
new="assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_WAVE50_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']"
assert text.count(old)==1;text=text.replace(old,new)
old="entry='train_wave50_entry_fresh_preflight_ppo_v2.py' if count==128 else 'train_wave50_entry_resume_ppo_v2.py'"
new="entry='train_wave50_entry_fresh_preflight_ppo_v2.py' if count==128 else 'train_wave50_entry_same_scope_resume_ppo.py'"
assert text.count(old)==1;text=text.replace(old,new)
old="assert entryproof['passed'] and entryproof['explicit_new_entry_scope'] and not entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']"
new="assert entryproof['passed'] and not entryproof['explicit_new_entry_scope'] and entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']"
assert text.count(old)==1;text=text.replace(old,new)
exec(compile(text,str(Path(__file__))+'::same50_train','exec'),prior.__dict__)
text=inspect.getsource(prior.guardian);old="('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_entry_resume_ppo_v2.py')";assert text.count(old)==1
text=text.replace(old,"('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_entry_resume_ppo_v2.py','train_wave50_entry_same_scope_resume_ppo.py')")
exec(compile(text,str(Path(__file__))+'::same50_own_guardian','exec'),prior.__dict__)
original_publish=prior.publish
text=inspect.getsource(original_publish);old="'-e1-wave50-entry-repair'";assert text.count(old)==1;text=text.replace(old,"'-e1-wave50-entry-second-bounded'")
exec(compile(text,str(Path(__file__))+'::newcandidate_publish','exec'),prior.__dict__)
prior.verify=verify;prior.source=source;prior.wait_existing=boundary;prior.trainers=trainers;prior.runtime=runtime;prior.phase=phase;prior.s.verify=verify
prior.s.q.verify=prior.s.q.w.verify=prior.s.q.ctl.verify=lambda:original005(prior.s.q,D)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();boundary();init=source()
 prior.s.q.helpers.acquire(prior.s.q.P/'autonomy_controller.lock');prior.s.q.helpers.acquire(prior.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
 before=prior.s.q.ctl.CANONICAL.read_bytes()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=prior.identity(os.getpid()),source=prior.fullsave(init),old410_actual_exit_and_two_locks_held=True,no_budget_extension=True))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=prior.identity(os.getpid()),source=prior.fullsave(init),expert='E1_WAVE50',seconds=1800,second_same50_entry_block=True,only_duration_exposure_axis=True,same50_geometry_command_reward_LR_DR=True,no_SDK_native_small_big_fresh_clock_replay=True,no_automatic_third_block=True,new_budget_seconds=0))
 assert prior.s.q.ctl.CANONICAL.read_bytes()==before
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([prior.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(prior.identity(os.getpid())['start_ticks'])],cwd=prior.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',prior.identity(g.pid))
 saved,row=prior.train(init,20000,10000,1800,'e1_WAVE50_entry_second_bounded_observation',False)
 assert prior.s.q.base.sha(init)==INIT_SHA and saved.is_relative_to(D/'learning_logs') and row['checkpoint']['finite_tensors']==102
 terrain=read(Path(row['run'])/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');command=read(Path(row['run'])/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')
 assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_WAVE50_geometry_transition'] and command['predecessor_command_state_restored_exact'] and not command['explicitly_new_command_scope']
 write('E1_WAVE50_SECOND_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],source_SHA_preserved=True,original35_lineage_SHA=ORIGINAL35_SHA,output_owned_by_this_expert=True,E0_CURB_SLOPE_WAVE35_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,candidate_number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number'],requires_actual_fourcase_and_full_exposure_review=True,automatic_more_PPO_disallowed=True,no_automatic70mm_or_third_block=True))
 phase('E1_WAVE50_entry_second_bounded_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(prior.s.LIVE and prior.s.LIVE.poll() is None),active_segment=prior.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
