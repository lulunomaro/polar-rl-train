"""Reuse actual409 SDK/small/big; only seed-correct fresh and bounded formal."""
from pathlib import Path
import os,time,json,subprocess,argparse,traceback
import supervise_curb20_entry_fullstate_once as own
from supervise_curb20_entry_fullstate_once import fullsave,write,phase,runtime,read,identity
D=own.D;R=own.R;CODE=own.CODE;s=own.s
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011')

def closed_previous():
 st=read(OLD/'reports/E1_STATE.json');attention=read(OLD/'reports/E1_ATTENTION.json')
 assert not attention['own_child_still_alive'] and attention['active_segment'] is None
 for loc in (st['owner'],st['child'],read(OLD/'reports/E1_GUARDIAN_STARTED.json')):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training') and not own.trainers()

def reuse():
 rows={}
 for label in ('entry_discard128','entry_discard20k'):
  v=read(OLD/'reports'/(label+'_PASSED.json'));count=128 if label.endswith('128') else 20000
  c=fullsave(Path(v['checkpoint']['path']),count=count);assert c['sha256']==v['checkpoint']['sha256'] and c['finite_tensors']==102 and v['discarded_preflight']
  assert v['health']['control_steps']==(48 if count==128 else 96) and v['health']['actual_physics_callbacks']==v['health']['control_steps']*4
  seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==v['own_PID_bound_receipt']['pid']];assert len(seg)==1 and seg==v['unique_completed_segment']
  rows[label]=v
 sdk=read(OLD/'reports/ENTRY_ORIGIN_BOUND_SDK10_PASSED.json');assert sdk['passed'] and sdk['actual_CURB_start_environments']==10 and s.q.base.sha(Path(sdk['path']))==sdk['sha256']
 return rows

def fresh_same_scope(big):
 source_ck=big['checkpoint'];fullsave(Path(source_ck['path']))
 write('FRESH_PROCESS_BIG_CORE_VERIFIED.json',dict(epoch=time.time(),checkpoint=source_ck,CPU_fullsave_passed=True))
 log=D/'ENTRY_FRESH_SAME_SCOPE.log';directory=D/'fresh_same_scope';assert not log.exists() and not directory.exists()
 args=[s.q.base.PY,str(CODE/'probe_curb20_entry_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--seed','20260928','--max_iterations','0','--log_root',str(directory),'--init_checkpoint',source_ck['path']]
 e=runtime();e['RM_CURB_FRESH_RESUME_ONLY']='1'
 with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('ENTRY_FRESH_SAME_SCOPE_PID_RECEIPT.json',dict(epoch=time.time(),child=identity(p.pid),argv=args,no_PPO=True));phase('ENTRY_fresh_same_scope_no_PPO',child=identity(p.pid),active_log=str(log));before=s.q.ctl.CANONICAL.read_bytes()
 while p.poll() is None:time.sleep(2)
 assert s.q.ctl.CANONICAL.read_bytes()==before and p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
 v=read(directory/'FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json');assert v['passed'] and v['actual_control_steps']==v['actual_additional_PPO_updates']==0 and v['terrain']['entry_reset_state_restored_exact'] and not v['terrain']['explicit_new_entry_reset_scope']
 write('ENTRY_FRESH_SAME_SCOPE_PASSED.json',v)


def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();own.verify();closed_previous();own.wait_existing();init=own.source();rows=reuse()
 assert read(R/'ENTRY_SEED_REVIEWED_CPU_PASSED.json')['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');closed_previous()
 before=s.q.ctl.CANONICAL.read_bytes()
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source_SHA=own.SOURCE_SHA,original409_fail_preserved=True,seed20260928_explicit=True,only_new_failed_fresh_scope_then_formal=True,oldSDK_small_big_native_exact_reused=True,no_new_budget_seconds=0))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 assert s.q.ctl.CANONICAL.read_bytes()==before
 fresh_same_scope(rows['entry_discard20k'])
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=rows['entry_discard128'],big=rows['entry_discard20k'],old_actual_valid_scope_exact_reused=True,weights_discarded=True,fresh=read(R/'ENTRY_FRESH_SAME_SCOPE_PASSED.json')))
 saved,row=own.train(init,20000,10000,min(300,s.left()),'e1_CURB20_entry_repair_observation',False)
 assert s.q.base.sha(init)==own.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),source_SHA_preserved=True,E0_Wave_SLOPE_not_optimizer_or_save_targets=True))
 own.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_CURB',all_courses_finished=False,requires_actual139_fourcase_review=True,automatic_more_PPO_disallowed=True))
 phase('E1_CURB20_entry_repair_saved_review_ready',child=None)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);args=p.parse_args()
 try:
  if args.guardian:own.guardian(int(args.guardian[0]),int(args.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
