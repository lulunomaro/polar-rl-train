"""Independent same50-entry-direction-route continuation; no oldmain/preflight replay."""
from pathlib import Path
import ast,argparse,time,traceback,subprocess,os,json,sys
import supervise_wave50_route_fixture_reviewed_once as inherited
from wave50_route_second_source_guard import verify_original_records,INIT_SHA,ORIGINAL35_SHA
prior=inherited.prior;D=prior.D;R=prior.R;CODE=prior.CODE;s=prior.s
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012')
ENTRY='train_wave50_route_same_scope_resume_ppo.py'
_verify=prior.verify;_trainers=prior.trainers
read=prior.read;identity=prior.identity;fullsave=prior.fullsave

def verify():
 _verify();verify_original_records(s.q,D)
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==443 and len(f)==446 and all(f[k]==v for k,v in old.items())
 assert read(R/'WAVE50_TARGET_CPU_PASSED.json')['source_count']==446
 for row in read(R/'REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']:assert s.q.base.sha(Path(row['path']))==row['sha256']

def source():
 p=Path(read(R/'MATCHED_SOURCE_SELECTED.json')['path']);a=fullsave(p)
 assert a['sha256']==s.q.base.sha(p)==INIT_SHA and a['finite_tensors']==107 and a['initial_source_and_expert_identity_exact'];return p

def boundary():
 st=read(OLD/'reports/E1_STATE.json');a=read(OLD/'reports/e1_WAVE50_route_lifecycle_observation_PASSED.json')
 assert st['phase']=='E1_WAVE50_route_lifecycle_saved_review_ready' and st['child'] is None and a['checkpoint']['sha256']==INIT_SHA and len(a['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=a['own_PID_bound_receipt']['pid'],start_ticks=93571728)):
  p=identity(loc['pid']);assert not p or p['state']=='Z' or p['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')

def trainers():
 rows=_trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   argv=[v.decode(errors='replace') for v in p.read_bytes().split(b'\0')]
   if any(Path(v).name==ENTRY for v in argv):rows.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return rows

def runtime():
 e=prior.inherited.runtime()
 for k in tuple(e):
  if k.endswith('INITIAL_ADMISSION'):e.pop(k)
 return e

# Compile new-root copies of the original functions with only same-scope proof and argv disclosure.
tree=ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text())
replacements={
 'train_wave50_route_resume_ppo.py':ENTRY,
 "assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G3_to_WAVE50_geometry_transition'] and terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']":"assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_WAVE50_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']",
 "direction['explicit_new_episode_direction_scope'] and not direction['predecessor_direction_state_restored_exact']":"not direction['explicit_new_episode_direction_scope'] and direction['predecessor_direction_state_restored_exact']",
 "route['explicit_new_route_lifecycle_scope'] and not route['predecessor_route_state_restored_exact']":"not route['explicit_new_route_lifecycle_scope'] and route['predecessor_route_state_restored_exact']",
 "entryproof['explicit_new_entry_scope'] and not entryproof['same_entry_identity_restored_exact']":"not entryproof['explicit_new_entry_scope'] and entryproof['same_entry_identity_restored_exact']",
}
for name in ('train','guardian'):
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);text=ast.unparse(node)
 for a,b in replacements.items():
  if a in text:text=text.replace(a,b)
 exec(compile(text,str(__file__)+'#same-scope-'+name,'exec'),vars(prior))
prior.verify=verify;prior.source=source;prior.trainers=trainers;prior.runtime=runtime

def main():
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();boundary();init=source()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');boundary()
 prior.write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_WAVE50',source=fullsave(init),old443_ownsave_unique_actual_exit_two_locks_idle_verified=True,new_budget_seconds=0))
 prior.write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),same_scope_second_bounded_seconds=1800,no_GPU_preflight_replay=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 prior.write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 saved,row=prior.train(init,20000,10000,min(1800,s.left()),'e1_WAVE50_route_second_bounded_observation',False)
 assert s.q.base.sha(init)==INIT_SHA and saved.is_relative_to(D/'learning_logs')
 prior.write('E1_WAVE50_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),source68401c_preserved=True,other_experts_not_optimizer_or_save_targets=True))
 prior.publish(saved);prior.write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,requires_actual_fourcase_review=True,automatic_more_PPO_disallowed=True))
 prior.phase('E1_WAVE50_route_second_bounded_saved_review_ready',child=None)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
