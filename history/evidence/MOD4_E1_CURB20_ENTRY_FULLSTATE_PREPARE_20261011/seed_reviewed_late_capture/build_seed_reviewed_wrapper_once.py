from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'seed_reviewed_payload';P.mkdir(exist_ok=True)
out=P/'supervise_curb20_entry_seed_reviewed_once.py';assert not out.exists()
old=D/'payload/supervise_curb20_entry_fullstate_once.py';text=old.read_text(encoding='utf8')
start=text.index('def fresh_same_scope(big):');end=text.index('def main():',start)
fresh=text[start:end]
fresh=fresh.replace("'--num_envs','20000','--max_iterations','0'","'--num_envs','20000','--seed','20260928','--max_iterations','0'")
assert "'--seed','20260928'" in fresh
source='''"""Reuse actual409 SDK/small/big; only seed-correct fresh and bounded formal."""
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

'''+fresh+'''
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
'''
ast.parse(source);out.write_text(source,encoding='utf8')
p=R/'ENTRY_SEED_WRAPPER_PREPARED.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),source=str(out.resolve()),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),old409_source_retained=True,actual_fresh_failure_seed42_vs_required20260928=True,no_DR_validator_relaxation=True,valid_SDK_small_big_native_not_replayed=True,new_CPU_and_dispatch_pending=True,record_ID_length_error_before_commit_tag_retained=True),ensure_ascii=False,indent=2),encoding='utf8')
