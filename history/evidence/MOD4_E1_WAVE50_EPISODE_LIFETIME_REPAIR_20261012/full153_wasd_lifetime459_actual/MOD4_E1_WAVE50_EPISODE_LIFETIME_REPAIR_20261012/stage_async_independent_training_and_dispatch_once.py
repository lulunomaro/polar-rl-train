from pathlib import Path
import os,json,time,hashlib,ast,traceback
import stage_lifetime_target_CPU_once as old
D=old.D;R=old.R;ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
CONTROLLER='''from pathlib import Path
import ast,json,time,os,argparse,traceback
import supervise_wave50_lifetime_once as parent
prior=parent.prior;D=parent.D;R=parent.R;CODE=parent.CODE;s=parent.s;read=parent.read;identity=parent.identity
def publish_or_pending(saved):
 p=R/'CANDIDATE_JOB_UNUSED_ACTUAL.json'
 if not p.exists():
  prior.write('E1_WAVE50_ASYNC_PUBLICATION_PENDING.json',dict(epoch=time.time(),own_checkpoint=prior.fullsave(saved),reason='3060 SSH unavailable before dispatch; fresh twohost unused-number admission still required',no_number_claimed=True,no_job_published=True,normal_training_not_blocked_by_eval_transport=True))
  return False
 admission=read(p);assert admission['actual_bothhost_unused'] and admission['number'] is not None
 prior.publish(saved);return True
def candidate_metadata():
 p=R/'CANDIDATE_JOB_UNUSED_ACTUAL.json';return read(p) if p.exists() else dict(number=None,actual_bothhost_unused=False)
node=next(x for x in ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='main')
class PendingPublish(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str):
   for a,b in parent.replacements.items():n.value=n.value.replace(a,b)
  return n
 def visit_Call(self,n):
  n=self.generic_visit(n)
  if isinstance(n.func,ast.Name) and n.func.id=='publish':n.func=ast.Name(id='publish_or_pending',ctx=ast.Load())
  if isinstance(n.func,ast.Name) and n.func.id=='read' and n.args and 'CANDIDATE_JOB_UNUSED_ACTUAL.json' in ast.unparse(n.args[0]):return ast.Call(func=ast.Name(id='candidate_metadata',ctx=ast.Load()),args=[],keywords=[])
  return n
prior.publish_or_pending=publish_or_pending;prior.candidate_metadata=candidate_metadata;prior.__file__=__file__
exec(compile(ast.fix_missing_locations(ast.Module(body=[PendingPublish().visit(node)],type_ignores=[])),str(__file__)+'#training-independent-of-eval-transport','exec'),vars(prior))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],original_failure_retained=True,no_blind_resume=True));raise
'''
def main():
 assert not (R/'ASYNC_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').exists();p=D/'payload_async_reviewed';assert not p.exists();p.mkdir();file=p/'supervise_wave50_lifetime_async_reviewed_once.py';ast.parse(CONTROLLER);file.write_text(CONTROLLER,encoding='utf8',newline='\n')
 n,w=old.connect_linux_only()
 try:
  raw=CONTROLLER.encode();v=old.run(n,r'''from pathlib import Path
import sys,json,time,torch,shutil,hashlib,fcntl
P=Path(CPU_ROOT_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(P),str(P/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_lifetime_once as previous
previous.verify();previous.wait_existing();assert not (P/'controller.log').exists() and not (P/'reports/E1_DISPATCH_STARTED.json').exists() and not D.exists()
f=previous.read(P/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==458
for name,sha in f.items():assert previous.s.q.base.sha(P/name)==sha
resource=json.loads(RESOURCE_JSON_TOKEN);assert shutil.disk_usage(P).free>resource['actual_resource']['required_bytes']
for p in (previous.s.q.P/'autonomy_controller.lock',previous.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as h:fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(h,fcntl.LOCK_UN)
D.mkdir();(D/'reports').mkdir()
for name,sha in f.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,p);assert previous.s.q.base.sha(p)==sha
for p in (P/'reports').iterdir():
 if p.is_file() and p.name not in ('SOURCE_FREEZE.json','WAVE50_TARGET_CPU_PASSED.json'):shutil.copy2(p,D/'reports'/p.name)
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=f,source458_CPU_complete_zero_GPU_and_no_dispatch=True,new_training_independent_eval_transport_controller_only=True)))
'''.replace('CPU_ROOT_TOKEN',repr(old.ROOT)).replace('ROOT_TOKEN',repr(ROOT)).replace('RESOURCE_JSON_TOKEN',repr((R/'OLD449_FINAL_BOUNDARY_RESOURCE_ACTUAL.json').read_text())))
  old.save('SOURCE458_CPU_ONLY_ASYNC_STAGE_BOUNDARY.json',v);freeze=dict(v['oldfreeze']);freeze[file.name]=hashlib.sha256(raw).hexdigest()
  with n.open_sftp() as f:
   with f.open(ROOT+'/'+file.name,'wb') as out:out.write(raw)
   with f.open(ROOT+'/reports/SOURCE_FREEZE.json','wb') as out:out.write(json.dumps(dict(epoch=time.time(),sha256=freeze,all458_oldbytes_exact=True,new_files=[file.name],only_eval_publication_wait_metadata_not_training_axis=True),indent=2).encode())
  result=old.run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,subprocess,fcntl,ast
D=Path(ROOT_TOKEN);P=Path(CPU_ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_lifetime_async_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cpu=j(P/'reports/WAVE50_TARGET_CPU_PASSED.json');assert cpu['passed'] and cpu['source_count']==458 and cpu['actual_full_lifetime_CPU_fixture_finite_tensors']==107
info=own.parent.fullsave(D/'reports/LIFETIME_FULLSTATE_CPU_FIXTURE.pt');assert info['finite_tensors']==107 and info['lifetime_state_verified']
cpu.update(epoch=time.time(),root=str(D),source_count=459,original458_target_CPU_exact_reused=dict(path=str(P/'reports/WAVE50_TARGET_CPU_PASSED.json'),sha256=h(P/'reports/WAVE50_TARGET_CPU_PASSED.json')),source458_CPU_not_GPU=True,new_no_number_claim_or_publish_without_twohost_admission=True,new_async_controller_import_main_Popen_guardian_path_exact=True)
(D/'reports/WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2));own.parent.verify();own.parent.wait_existing();assert own.prior.__file__==str(D/'supervise_wave50_lifetime_async_reviewed_once.py') and own.prior.D==D and own.s.D==D
assert 'train_wave50_lifetime_resume_ppo.py' in str(own.prior.train.__code__.co_consts) and 'native_e1_wave50_lifetime_scope_probe.py' in str(own.prior.native_contract.__code__.co_consts)
for p in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_lifetime_async_reviewed_once.py')];assert not (D/'controller.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=459,controller=loc,argv=args,actual_target_CPU107_and_Popen_verified=True,first_formal_seconds=300,only_physical_training_Wave_timeout20to40s_other20s=True,initial_source_SHA=own.parent.SOURCE_SHA,no_candidate_number_claimed_or_published_yet=True,3060_transport_failure_before_original_dispatch_preserved=True,formal_requires_newscope_actualSDK_native_smallbig_fresh_pass=True,no_GPU_preflight_replay_or_budget_extension=True)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CPU_ROOT_TOKEN',repr(old.ROOT)).replace('ROOT_TOKEN',repr(ROOT)))
  old.save('ASYNC_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json',result);print(json.dumps(result))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:old.save('ASYNC_REVIEWED_STAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_actual_unexecuted_steps_may_continue=True));raise
