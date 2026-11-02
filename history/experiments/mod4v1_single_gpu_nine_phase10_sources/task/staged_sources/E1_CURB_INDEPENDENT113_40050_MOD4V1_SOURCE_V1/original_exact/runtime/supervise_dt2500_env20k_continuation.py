"""New unique approved S2 continuation. Original211 runtime remains byte exact."""
from pathlib import Path
import os,time,sys,subprocess,traceback,argparse
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D))
import supervise_dt2500_solver32_training_test as s
F=Path('/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007')
H=Path('/home/egde/rl_candidates/MOD4_ENV25000_MATERIAL_POOL_REVIEW_20261007')
SOURCE_SHA='4a4456efce65f238e8b02c7a65aa17236b5dcf97754604d54103359dede1c641'
original_phase=s.phase
def continuation_phase(name,**kw):
 if name=='bounded_solver32_formal_training_test':name='bounded_S2_E0_dt2500_env20k_learning'
 original_phase(name,**kw)
 s.q.base.status(plan_stage='S2 E0 D1+D2 stable continuation',num_envs=20000,active_code_root=str(D))
s.phase=continuation_phase

def verify_continuation():
 s.verify()
 own=s.q.w.read(R/'SOURCE_FREEZE.json')['sha256'];prior=s.q.w.read(F/'reports/SOURCE_FREEZE.json')['sha256']
 assert len(prior)==211 and len(own)==213
 for n,h in prior.items():assert s.q.base.sha(F/n)==h and own[n]==h,n
 a=s.q.w.read(R/'KEEP20K_CONTINUE_AUTHORIZATION.json')
 assert a['human_message']=='保留2w开始继续推进任务吧' and a['num_envs']==20000 and a['new_budget_seconds']==0
 assert a['source_sha256']==SOURCE_SHA and a['master_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert s.q.w.read(R/'CONTINUATION_CONTROLLER_CPU_CONTRACT.json')['passed']
 assert s.q.w.read(R/'SOURCE25211_RESUME_CPU_CONTRACT.json')['passed']

def old_authorities_exited():
 for root,names in [(F,('SOLVER32_STARTED.json','SOLVER32_GUARDIAN_STARTED.json')),(H,('SCALING_STARTED.json','SCALING_GUARDIAN_STARTED.json'))]:
  for n in names:
   p=root/'reports'/n
   if not p.exists():continue
   i=s.q.w.read(p);i=i.get('owner',i);a=s.identity(i['pid'])
   assert not a or a['state']=='Z' or a['start_ticks']!=i['start_ticks'],(p,a)

def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'CONTINUATION_STARTED.json').exists();verify_continuation()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock')
 s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert not s.trainers() and s.q.base.budget_state()['active_segment'] is None
 assert not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training');old_authorities_exited()
 formal=s.q.w.read(F/'reports/solver32_formal45_PASSED.json');init=Path(formal['checkpoint']['path'])
 assert s.q.base.sha(init)==SOURCE_SHA;info=s.fullsave(init)
 health=formal['health']
 assert health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['max_closure_error_m']<=.002
 assert health['actual_physics_callbacks']==health['expected_physics_callbacks']
 segment=[x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==formal['own_PID_bound_receipt']['pid']]
 assert segment==formal['unique_completed_segment'] and len(segment)==1
 pre=s.q.w.read(F/'reports/SOLVER32_COMPLETE_PPO_PREFLIGHT_PASSED.json')
 assert pre['weights_discarded'] and pre['full_1920000_environment_steps']
 before=s.q.ctl.CANONICAL.read_bytes()
 s.write('CONTINUATION_INSTALL_BOUNDARY.json',dict(epoch=time.time(),source=info,prior_segment_exact=segment,original211_byte_exact=True,two_original_locks_held=True,actual_old_authorities_exited=True,noactive=True,new_budget_seconds=0,no_new_range_PPO_preflight=True,benchmark_weights_discarded=True,prior25211_behavior_pending=True))
 s.write('CONTINUATION_STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),source=info,plan_stage='S2 E0 D1+D2',num_envs=20000,physics_dt_s=.0025,solver_position=32,solver_velocity=4,planned_seconds=7200,new_budget_seconds=0,original211_byte_exact=True,parallel_evaluation_required=True,D3_installed=False))
 with (D/'guardian.log').open('x') as f:
  g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(s.identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 s.write('SOLVER32_GUARDIAN_STARTED.json',s.identity(g.pid));assert before==s.q.ctl.CANONICAL.read_bytes()
 p,row=s.train(init,20000,10000,7200,'env20k_S2_D1D2_stable2h',False)
 # The new 2.5ms/solver32 platform is not the old1ms worker scope.
 # This CPU-only request is a durable exact-source handoff, not an executable GPU job.
 s.write('NEXT_ASYNC_FROZEN_REQUEST.json',dict(epoch=time.time(),source=row['checkpoint'],runtime_root=str(D),runtime_source_freeze=str(R/'SOURCE_FREEZE.json'),physics_dt_s=.0025,solver=[32,4],requested_kinds=['flat','spin','world'],clean_and_noise_pairing_required=True,immutable_package_and_platform_scope_required=True,old1ms_worker_must_not_execute=True,request_not_job_or_completed_evidence=True))
 s.write('SOLVER32_REVIEW_READY.json',dict(epoch=time.time(),formal=row,own_saved_source=p.as_posix(),new_policy_behavior_pending=True,next='Review same-clock clean/noisy old skills in parallel; validate D3 SDK/sample-age/cache/reset before approved new-range PPO and new unique safe handover.',num_envs=20000,all_courses_finished=False,new_budget_seconds=0))
 s.phase('S2_E0_dt2500_env20k_stable_saved_review_ready',child=None,source=row['checkpoint'])

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:s.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:
  s.write('SOLVER32_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
