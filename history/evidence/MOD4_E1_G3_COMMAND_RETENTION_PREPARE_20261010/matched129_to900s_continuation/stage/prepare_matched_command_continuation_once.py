"""Prepare a separate same-scope900s controller. Preserve every364 source byte."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
def main():
 decision=json.loads((R/'COMMAND129_COMPLETE_RETENTION_DECISION.json').read_bytes());assert decision['continuation_admitted']
 v=json.loads(sorted(R.glob('CANDIDATE_129_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1].read_bytes());assert v['review_complete']
 folder=D/'matched_continuation_payload';assert not folder.exists();folder.mkdir()
 source=r'''"""One same35mm/samecommand continuation after actual129; no repeatedpreflights."""
from pathlib import Path
import argparse,inspect,json,os,subprocess,time,traceback
import supervise_e1_command_retention_episode_reviewed_once as m
D=Path(__file__).resolve().parent;R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010')
read=m.read;identity=m.identity;fullsave=m.fullsave;SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
old_runtime=m.runtime
def runtime():
 e=old_runtime()
 for k in ('RM_E1_INITIAL_ADMISSION','RM_E1_G3_INITIAL_ADMISSION','RM_E1_COMMAND_RETENTION_INITIAL_ADMISSION'):e.pop(k,None)
 return e
def verify():
 m.verify_original_records(m.s.q,D)
 approval=read(m.s.q.ER/'PLAN_APPROVAL.json');assert approval['approved'] and 'S3' in approval['allowed_stages'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==365 and len(old)==364 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert m.s.q.base.sha(D/n)==h,n
 a=read(R/'COMMAND129_COMPLETE_RETENTION_DECISION.json');assert a['continuation_admitted'] and a['selected_next_source']['sha256']==SOURCE_SHA and a['no_next50mm_admission']
 assert read(R/'COMMAND129_COMPLETE_ACTUAL_REVIEW.json')['review_complete'] and read(R/'COMMAND129_SELECTED_SOURCE_MATCHED_REVIEW.json')['review_complete']
 assert read(R/'REUSED_CONTRACTS.json')['same_scope_CPU_SDK_native_complete_PPO_clock_D0_D7_reused_exact']
 pkg=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime'];assert m.s.q.base.sha(Path(pkg['path']))==pkg['sha256']
def source():
 row=read(R/'COMMAND129_COMPLETE_RETENTION_DECISION.json');p=Path(row['selected_next_source']['path']);assert m.s.q.base.sha(p)==SOURCE_SHA
 ck=fullsave(p);assert ck['finite_tensors']==102
 return p
def wait_existing():
 state=read(OLD/'reports/E1_STATE.json');passed=read(OLD/'reports/e1_G3_command_retention_observation_PASSED.json');assert state['phase']=='E1_G3_command_retention_saved_review_ready' and state['child'] is None and (OLD/'reports/E1_REVIEW_READY.json').exists()
 assert passed['checkpoint']['sha256']==SOURCE_SHA and len(passed['unique_completed_segment'])==1
 for locator in (state['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=2302440_START)):
  v=identity(locator['pid']);assert not v or v['state']=='Z' or v['start_ticks']!=locator['start_ticks']
 assert len([x for x in read(m.s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==passed['own_PID_bound_receipt']['pid']])==1
 assert not m.trainers() and m.s.q.base.budget_state()['active_segment'] is None and not read(m.s.q.ctl.STATE_PATH).get('active_training')
def phase(name,**kw):
 m.write('E1_STATE.json',dict(epoch=time.time(),phase=name,owner=identity(os.getpid()),**kw))
 m.s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='S3 E1 G3 same35mm/sameclearplane conditioned commands matched900s from actual129 ownfullsave; allfixedcontracts unchanged',active_expert='E1',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
m.verify=verify;m.source=source;m.wait_existing=wait_existing;m.phase=phase;m.runtime=runtime;m.s.verify=verify
m.s.q.verify=m.s.q.w.verify=m.s.q.ctl.verify=lambda:m.verify_original_records(m.s.q,D)
# Only outer startup assertions change from first-G2transition to actual same-G3
# and same retained command restore. The entire trainer, physics and checkpoints
# remain the verified364 bytes.
text=inspect.getsource(m.train)
old="assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G2_to_G3_geometry_transition'] and terrain['explicitly_new_E1_terrain']"
new="assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G2_to_G3_geometry_transition'] and not terrain['explicitly_new_E1_terrain']"
assert text.count(old)==1;text=text.replace(old,new)
needle="v=read(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert v['saved_source_episode_plus_one_verified']"
assert text.count(needle)==1;text=text.replace(needle,"v=read(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert v['predecessor_command_state_restored_exact'] and not v['explicitly_new_command_scope'];assert v['saved_source_episode_plus_one_verified']")
text=text.replace("'bounded_E1_G3_command_retention_learning'","'bounded_E1_G3_command_retention_matched_continuation'")
exec(compile(text,str(Path(__file__)), 'exec'),m.__dict__)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source()
 m.s.q.helpers.acquire(m.s.q.P/'autonomy_controller.lock');m.s.q.helpers.acquire(m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 before=m.s.q.ctl.CANONICAL.read_bytes()
 m.write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),actual129_complete_review_admitted=True,actual364_parent_guardian_child_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0))
 m.write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),same_scope_matched_seconds=900,no_repeated_SDK_native_PPO_preflight_clock=True,new_budget_seconds=0))
 assert before==m.s.q.ctl.CANONICAL.read_bytes()
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([m.s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=m.s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 m.write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 init,row=m.train(init,20000,10000,min(900,m.s.left()),'e1_G3_command_retention_matched',False)
 m.publish(init,'130-e1-g3-command-retention-matched')
 m.write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),all_courses_finished=False,matched900s_complete=True,needs_actual130_route_and_old_skill_review=True,automatic_more_PPO_disallowed=True))
 phase('E1_G3_command_retention_matched_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);args=p.parse_args()
 try:
  if args.guardian:m.guardian(int(args.guardian[0]),int(args.guardian[1]))
  else:main()
 except BaseException:
  m.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(m.s.LIVE and m.s.LIVE.poll() is None),active_segment=m.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''.replace('2302440_START','79446206')
 ast.parse(source);name='supervise_e1_command_retention_matched_once.py';p=folder/name;p.write_bytes(source.encode())
 report=dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-900S-DEPLOY-01',new_file_count=1,sha256={name:H(p.read_bytes())},old364_allbytes_preserved=True,new_source_count=365,same_geometry_same_command_scope=True,only_controller_restore_assertions_and_matched_duration_changed=True,no_SDK_native_PPO_preflight_clock_replay=True,new_budget_seconds=0)
 p=R/'COMMAND_MATCHED_PREPARED.json';assert not p.exists();p.write_bytes(json.dumps(report,indent=2).encode());print(json.dumps(report))
if __name__=='__main__':main()
