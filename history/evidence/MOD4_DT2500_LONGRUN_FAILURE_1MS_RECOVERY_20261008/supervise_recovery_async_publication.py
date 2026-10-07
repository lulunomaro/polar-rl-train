"""CPU-only healthy own-save publication; no GPU, budget or launch authority."""
from pathlib import Path
import sys,time,json,shutil,os,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
TRAIN=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008')
sys.path.insert(0,str(TRAIN));import supervise_validated_1ms_runtime_review as w
s=w.s;read=s.q.w.read
def write(n,v):s.q.base.atomic_json(R/n,v)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'STARTED.json').exists();w.verify()
 original=read(s.q.ER/'SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json');package=original['package'];assert s.q.base.sha(Path(package['path']))==package['sha256']=='f00729ce80a8fb0e64d40e0fb3c6bfd9e9a090603abee5eae0afb8c7ee2ac967'
 write('STARTED.json',dict(epoch=time.time(),owner=s.identity(os.getpid()),training_root=str(TRAIN),runtime_package=package,only_original1ms_frozen_inference_reused=True,no_GPU_no_canonical_write_no_training_launch=True))
 for block in range(1,4):
  path=TRAIN/'reports'/('validated1ms_recovery_block'+str(block)+'_PASSED.json')
  while not path.exists():
   if (TRAIN/'reports/SOLVER32_ATTENTION.json').exists():raise AssertionError('Training attention: candidate not published')
   owner=read(TRAIN/'reports/RECOVERY_STARTED.json')['owner'];actual=s.identity(owner['pid'])
   if not actual or actual['state']=='Z' or actual['start_ticks']!=owner['start_ticks']:
    write('SAVED_WINDOW_ENDED.json',dict(epoch=time.time(),waiting_block=block,no_bad_candidate_published=True,all_course_finished=False));return
   write('STATE.json',dict(epoch=time.time(),phase='waiting_own_healthy_complete_save',block=block));time.sleep(5)
  row=read(path);assert w.learning_health_pass(row['health']) and row['health']['physics_dt_s']==.001
  ck=row['checkpoint'];source=Path(ck['path']);assert s.fullsave(source)==ck;run=Path(row['run']);rec=read(run/'latest_complete.json')
  assert rec==row['own_PID_bound_receipt'] and read(run/'rolling_source_freeze.json')['sha256']==read(TRAIN/'reports/SOURCE_FREEZE.json')['sha256']
  m=read(run/'run_manifest.json');assert m['source_map']==read(TRAIN/'reports/SOURCE_FREEZE.json')['sha256']
  for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
  seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==rec['pid']];assert len(seg)==1 and seg==row['unique_completed_segment']
  E=s.q.ER.parent;target=E/'artifacts'/('validated1ms-recovery-'+ck['sha256']+'.pt');assert not target.exists()
  shutil.copyfile(source,str(target)+'.partial');assert s.q.base.sha(Path(str(target)+'.partial'))==ck['sha256'];os.replace(str(target)+'.partial',target)
  checkpoint=dict(path=str(target),bytes=target.stat().st_size,sha256=ck['sha256']);a=read(s.q.ER/'PLAN_APPROVAL.json');jobs=[]
  for kind in ('flat','spin','world'):
   job='clk1000-recovery-b'+str(block)+'-'+kind;dest=E/'eval_queue'/(job+'.json');assert not dest.exists()
   item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Own healthy complete1ms fallback source; compare with already-evaluated24827 on same1ms platform',physics_dt_s=.001,control_dt_s=.01,solver_position=16,solver_velocity=4,protocol='Original202 immutable1ms frozen inference exact; 218health classifier not in frozen inference path. Prior1ms scope reused; new behavior remains to be evaluated, no GPU bitexact/wholeDR graduation claim.',artifacts=dict(runtime=package,checkpoint=checkpoint),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=False)
   s.q.base.atomic_json(dest,item);jobs.append(item)
  write('BLOCK_'+str(block)+'_PUBLISHED.json',dict(epoch=time.time(),jobs=jobs,source=ck,health=row['health'],unique_completed_segment=seg));write('STATE.json',dict(epoch=time.time(),phase='candidate_immutable_published',block=block,source_sha256=ck['sha256']))
 write('COMPLETE.json',dict(epoch=time.time(),three_blocks_published=True,no_GPU_no_canonical_write_no_training_launch=True))
try:main()
except BaseException:
 write('ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_no_canonical_write_no_training_launch=True,bad_candidate_not_published=True));raise
