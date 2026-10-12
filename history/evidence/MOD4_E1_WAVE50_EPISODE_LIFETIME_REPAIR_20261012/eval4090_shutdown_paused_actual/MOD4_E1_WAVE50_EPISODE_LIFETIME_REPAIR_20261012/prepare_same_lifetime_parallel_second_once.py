from pathlib import Path
import ast,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload_second_parallel'
CONTROLLER='''from pathlib import Path
import ast,json,time,os,subprocess,argparse,traceback,hashlib,torch
import supervise_wave50_lifetime_async_reviewed_once as parent
prior=parent.prior;D=parent.D;R=parent.R;CODE=parent.CODE;s=parent.s;read=parent.read;identity=parent.identity
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012');INIT_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
from wave50_lifetime_fullsave_cpu import fullsave
def source():
 p=Path(read(R/'SAME_LIFETIME_SOURCE_SELECTED.json')['path']);assert s.q.base.sha(p)==INIT_SHA and fullsave(p)['finite_tensors']==107;return p
def verify():
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==459 and len(f)==462 and all(f[k]==v for k,v in old.items())
 for k,v in f.items():assert s.q.base.sha(D/k)==v
 assert read(R/'SAME_LIFETIME_CPU_PASSED.json')['passed'];b=read(s.q.ctl.CANONICAL);assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'];rev=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
 assert read(R/'HUMAN_PARALLEL_SECOND_SCOPE_ADMISSION.json')['human_train_eval_parallel_authorized']
 for row in read(R/'REUSED_LIFETIME_ACTUAL_CONTRACTS.json')['indices']:assert s.q.base.sha(Path(row['path']))==row['sha256']
def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');passed=read(OLD/'reports/e1_WAVE50_episode_lifetime_observation_PASSED.json');assert st['phase']=='E1_WAVE50_episode_lifetime_saved_review_ready' and st['child'] is None and passed['checkpoint']['sha256']==INIT_SHA and len(passed['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=3447391,start_ticks=96006274)):
  p=identity(loc['pid']);assert not p or p['state']=='Z' or p['start_ticks']!=loc['start_ticks']
 assert not prior.trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
initial=ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text())
name=next(x for x in initial.body if isinstance(x,ast.FunctionDef) and x.name=='train')
class SameIdentity(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str):
   for a,b in {'train_wave50_route_resume_ppo.py':'train_wave50_lifetime_same_scope_resume_ppo.py','train_wave50_route_fresh_preflight_ppo.py':'train_wave50_lifetime_fresh_preflight_ppo.py','bounded_E1_WAVE50_route_lifecycle_learning':'bounded_E1_WAVE50_lifetime_parallel_second_learning'}.items():n.value=n.value.replace(a,b)
  if n.value=='25':n.value='10'
  return n
 def visit_Assert(self,n):
  text=ast.unparse(n.test)
  if "not terrain['terrain_state_restored_exact']" in text:return ast.parse("assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_WAVE50_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and not terrain['explicit_G2_to_G3_geometry_transition']").body[0]
  for var,newfield,predfield,roundtrip in (('direction','explicit_new_episode_direction_scope','predecessor_direction_state_restored_exact','actual_CUDA_direction_disk_roundtrip_exact'),('route','explicit_new_route_lifecycle_scope','predecessor_route_state_restored_exact','actual_CUDA_route_disk_roundtrip_exact'),('entryproof','explicit_new_entry_scope','same_entry_identity_restored_exact','actual_entry_terrain_command_CUDA_disk_roundtrip_exact')):
   if var+"['"+newfield+"']" in text:return ast.parse("assert "+var+"['passed'] and not "+var+"['"+newfield+"'] and "+var+"['"+predfield+"'] and "+var+"['"+roundtrip+"'] and "+var+"['saved_source_episode_plus_one_verified']").body[0]
  return self.generic_visit(n)
node=SameIdentity().visit(name)
for n in ast.walk(node):
 if isinstance(n,ast.If) and ast.unparse(n.test)=='count == 20000' and any('E1_TERRAIN_RESUME_STARTUP_VERIFIED' in ast.unparse(s) for s in n.body):
  n.body.extend(ast.parse("lifetime=read(run/'E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json')\nassert lifetime['passed'] and lifetime['predecessor_lifetime_state_restored_exact'] and not lifetime['explicit_new_episode_lifetime_scope'] and lifetime['actual_CUDA_lifetime_disk_roundtrip_exact'] and lifetime['saved_source_episode_plus_one_verified']").body)
prior.SOURCE_SHA=INIT_SHA;prior.verify=verify;prior.wait_existing=wait_existing;prior.source=source;prior.fullsave=fullsave;prior.__file__=__file__;prior.s.verify=verify
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(__file__)+'#strict-same-lifetime-train','exec'),vars(prior))
for n in ast.walk(initial):
 if isinstance(n,ast.FunctionDef) and n.name=='guardian':
  class Guard(ast.NodeTransformer):
   def visit_Constant(self,n):
    if n.value=='train_wave50_route_resume_ppo.py':n.value='train_wave50_lifetime_same_scope_resume_ppo.py'
    return n
  exec(compile(ast.fix_missing_locations(ast.Module(body=[Guard().visit(n)],type_ignores=[])),str(__file__)+'#own-second-guardian','exec'),vars(prior))
def main():
 torch.set_num_threads(1);assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source();s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 admission=read(R/'HUMAN_PARALLEL_SECOND_SCOPE_ADMISSION.json');prior.write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_WAVE50',target_seconds=admission['target_seconds'],same_lifetime_scope=True,human_parallel_with_frozen_evaluation_authorized=True,max_two_blocks=True,no_GPU_preflight_replay=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 prior.write('E1_GUARDIAN_STARTED.json',identity(g.pid));saved,row=prior.train(init,20000,10000,min(admission['target_seconds'],s.left()),'e1_WAVE50_lifetime_parallel_second_observation',False);assert s.q.base.sha(init)==INIT_SHA
 prior.write('E1_WAVE50_ASYNC_PUBLICATION_PENDING.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],independent4090_backend_required=True,no_global_candidate_number_claimed=True,normal_training_not_blocked_by_3060=True));prior.write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),all_courses_finished=False,max2_lifetime_blocks_complete=True,requires_actual_full_fourcase_and_trace_review=True));prior.phase('E1_WAVE50_lifetime_parallel_second_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],no_blind_resume=True));raise
'''
def main():
 assert not P.exists();P.mkdir();(P/'isaac/mod4').mkdir(parents=True)
 original=D/'payload/isaac/mod4/train_wave50_lifetime_resume_ppo.py';s=original.read_text();s=s.replace("manifest['new_episode_lifetime_axis']=True","manifest['new_episode_lifetime_axis']=False\n    manifest['same50_entry_direction_route_lifetime_fullstate_continuation']=True")
 for before,after in (("manifest['new_route_lifecycle_axis']=True","manifest['new_route_lifecycle_axis']=False"),("manifest['new_episode_direction_axis']=True","manifest['new_episode_direction_axis']=False"),("manifest['explicit_G3_to_WAVE50_geometry_transition']=True","manifest['explicit_G3_to_WAVE50_geometry_transition']=False"),("manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=True","manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=False")):
  assert before in s;s=s.replace(before,after)
 ast.parse(s);(P/'isaac/mod4/train_wave50_lifetime_same_scope_resume_ppo.py').write_text(s,encoding='utf8',newline='\n');ast.parse(CONTROLLER);(P/'supervise_wave50_lifetime_parallel_second_once.py').write_text(CONTROLLER,encoding='utf8',newline='\n')
 guard="from pathlib import Path\nimport json,hashlib\ndef verify_source(path,sha):\n from wave50_lifetime_fullsave_cpu import fullsave\n assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha\n v=fullsave(path);assert v['finite_tensors']==107 and v['lifetime_state_verified'];return v\n"
 (P/'same_lifetime_source_guard.py').write_text(guard,encoding='utf8',newline='\n');files={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in P.rglob('*') if p.is_file()};assert len(files)==3
 p=R/'PARALLEL_SECOND_COMPONENTS_PREPARED.json';assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),passed=True,files=files,actual_source459_sameidentity_inherited=True,new_source_count=462,worker_same_identity_manifest_truthful=True,all_startup_predicates_AST_replaced_not_literal_string=True,periodic_save_interval10_for_frozen_eval_snapshots_no_PPO_change=True,resource_and_CPU_and_dispatch_pending=True),indent=2).encode());print(json.dumps(dict(prepared=True,source_count=462)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('PARALLEL_SECOND_BUILDER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU=True),indent=2));raise
