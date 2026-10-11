from slope_io import *
import ast
Q=D/'snapshot_reviewed_payload'
def main():
 assert not Q.exists();Q.mkdir();(Q/'isaac/mod4').mkdir(parents=True)
 worker=D/'payload/isaac/mod4/train_slope5_full_resume_ppo.py';old=worker.read_text();assert 'slope5_command_migration_environment_view.py' in old
 new=old.replace('slope5_command_migration_environment_view.py','slope5_command_migration.py');assert new!=old
 p=Q/'isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py';compile(new,str(p),'exec');p.write_bytes(new.encode())
 src=(D/'payload/supervise_slope5_independent_scope_once.py').read_text();tree=ast.parse(src);functions={x.name:ast.get_source_segment(src,x) for x in tree.body if isinstance(x,ast.FunctionDef)}
 train=functions['train'].replace("'train_slope5_full_resume_ppo.py'","'train_slope5_snapshot_reviewed_resume_ppo.py'")
 guardian=functions['guardian'].replace("'train_slope5_full_resume_ppo.py'","'train_slope5_snapshot_reviewed_resume_ppo.py'")
 header='''"""Unique snapshot-list repair; old402 failures retained, no SDK/native/small replay."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_slope5_independent_scope_once as prior
from clock_training_health import learning_health_pass
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=prior.s
read=prior.read;write=prior.write;identity=prior.identity;freeze_run=prior.freeze_run;fullsave=prior.fullsave;verify=prior.verify;runtime=prior.runtime;phase=prior.phase
OLD402=Path('/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011')
def trainers():
 found=prior.trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   if any(Path(x.decode(errors='replace')).name=='train_slope5_snapshot_reviewed_resume_ppo.py' for x in p.read_bytes().split(b'\\0')):found.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return found
def wait_existing():
 prior.wait_existing();st=read(OLD402/'reports/E1_STATE.json');att=read(OLD402/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 for loc in (st['owner'],st['child'],read(OLD402/'reports/E1_GUARDIAN_STARTED.json')):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None
'''
 main='''def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 small=read(R/'REUSED_SLOPE_SMALL128.json');assert small['discarded_preflight'] and small['actual_updates']==2 and small['actual_environment_steps']==6144
 for row in read(R/'REUSED_SLOPE_NATIVE.json')['results'].values():assert row['passed'] and row['no_PPO'] and s.q.base.sha(Path(row['path']))==row['sha256']
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_SLOPE',new_snapshot_list_literal_repair=True,SDK_native_small_exact_reused=True,old402_failed_before_PPO_retained=True,formal_seconds=300,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 _,big=train(init,20000,4,900,'slope_snapshot_reviewed_discard20k',True)
 fresh=prior.fresh_resume(big)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=small,big=big,fresh_same_scope=fresh,weights_discarded=True,SDK_native_small_exact_reused=True,old402_failed_snapshot_literal_preserved=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_SLOPE5_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_SLOPE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_CURB_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_SLOPE',all_courses_finished=False,requires_actual135_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_SLOPE5_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''
 text=header+train+'\n'+guardian+'\n'+main;p=Q/'supervise_slope5_snapshot_reviewed_once.py';compile(text,str(p),'exec');p.write_bytes(text.encode())
 save('SNAPSHOT_LITERAL_ERROR_REVIEW.json',dict(epoch=time.time(),trial_id='SLOPE402-BIG-PRELEARN-SNAPSHOT-LITERAL-REJECTION-01',old_worker_SHA=H(worker.read_bytes()),new_worker_SHA=H(new.encode()),original_error='FileNotFoundError slope5_command_migration_environment_view.py in src_snapshot list before bounded_learn',actual_old_full_CUDA_startup_receipts_passed=True,old_no_PPO_updates=True,old_source_errors_fullstate_and_unique_cost_preserved=True,new_unique_root_required=True,no_hotpatch_or_old_once_replay=True,native_small_reuse_required=True))
 print(json.dumps(dict(new_payload_files=2,only_snapshot_literal_repaired=True,no_GPU_launch=True)))
if __name__=='__main__':main()
