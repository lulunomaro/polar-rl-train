from route_fixture_io import *

def main():
    second=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012';assert not second.exists()
    (second/'reports').mkdir(parents=True);payload=second/'payload';(payload/'isaac/mod4').mkdir(parents=True)
    worker=(D/'payload/isaac/mod4/train_wave50_route_resume_ppo.py').read_text(encoding='utf8')
    changes={"manifest['explicit_G3_to_WAVE50_geometry_transition']=True":"manifest['explicit_G3_to_WAVE50_geometry_transition']=False", "manifest['new_episode_direction_axis']=True":"manifest['new_episode_direction_axis']=False", "manifest['new_route_lifecycle_axis']=True":"manifest['new_route_lifecycle_axis']=False\n    manifest['same50_entry_direction_route_fullstate_continuation']=True"}
    for a,b in changes.items():assert worker.count(a)==1;worker=worker.replace(a,b)
    target=payload/'isaac/mod4/train_wave50_route_same_scope_resume_ppo.py';compile(worker,str(target),'exec');target.write_text(worker,encoding='utf8')
    guard=r'''from pathlib import Path
import json,hashlib
from wave50_route_source_guard import verify_original_records as original
INIT_SHA='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
ORIGINAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'

def verify_original_records(q,D):
 original(q,D);b=q.w.read(q.ctl.CANONICAL);ids=set();total=36000
 for r in b['budget_extensions']:
  assert r['extension_id'] not in ids and r['state']=='applied' and r['authorization_basis']=='explicit_user_request'
  ids.add(r['extension_id']);assert type(r['additional_training_seconds']) is int and r['additional_training_seconds']>0;total+=r['additional_training_seconds']
 assert total==b['authorized_training_seconds']==1188000 and len(ids)==7
 a=q.w.read(D/'reports/COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json')
 assert a['all_four_actual_complete_errorfree_fullraw_reviewed'] and a['full_own_training_trace_reviewed'] and a['default_same_scope_source_SHA']==INIT_SHA
 assert a['forward_complete']==12 and a['reverse_complete']==25 and a['bounded_second1800_justified_after_first300_short_exposure']
 assert a['no_third_blind_block_or70'] and not a['qualified50']
'''
    target=payload/'wave50_route_second_source_guard.py';compile(guard,str(target),'exec');target.write_text(guard,encoding='utf8')
    controller=r'''"""Independent same50-entry-direction-route continuation; no oldmain/preflight replay."""
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
'''
    target=payload/'supervise_wave50_route_second_bounded_once.py';compile(controller,str(target),'exec');target.write_text(controller,encoding='utf8')
    io_source="from pathlib import Path\nimport sys,json,time,traceback\nD=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'\nsys.path.insert(0,str(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'))\nimport route_fixture_io as previous\nio=previous.io;H=previous.H;run=previous.run;OLD=previous.ROOT\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'\nINIT_SHA='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'\nSOURCE='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt'\ndef save(name,value):\n p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p\n"
    (second/'route_second_io.py').write_text(io_source,encoding='utf8')
    rows=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in payload.rglob('*') if p.is_file()]
    assert len(rows)==3
    save('ROUTE_SECOND1800_LOCAL_PAYLOAD_PREPARED.json',dict(epoch=time.time(),passed=True,local_folder=str(second),files=rows,expected_old443_plus3_source_count=446,compiled_only_no_target_CPU_or_GPU_or_dispatch=True,only_same_scope_manifest_argv_strict_restore_and_unique_controller_guard=True,source68401c107_and_35b026_129_ancestor_pinned=True))
    print(json.dumps(dict(prepared=True,new_files=3,local_folder=str(second),no_deployment=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE_SECOND_PAYLOAD_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
