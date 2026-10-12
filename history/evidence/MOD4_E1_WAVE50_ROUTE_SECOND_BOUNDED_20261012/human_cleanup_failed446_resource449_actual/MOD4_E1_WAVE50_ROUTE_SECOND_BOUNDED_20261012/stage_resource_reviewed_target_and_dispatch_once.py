from route_second_io import *
import shlex
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'

def main():
    save('RESOURCE_STAGE_STARTED.json',dict(epoch=time.time(),new_root=NEWROOT,original446_failed_startup_not_replayed=True,only_new_resource_guard_prePPO_exit_worker_controller=True))
    files={p.relative_to(D/'resource_reviewed_payload_v2').as_posix():p.read_bytes() for p in (D/'resource_reviewed_payload_v2').rglob('*') if p.is_file()};assert len(files)==3
    for name,raw in files.items():compile(raw,name,'exec')
    n,w=io.connect_both()
    try:
        admission=run(n,r'''from pathlib import Path
import json,time,sys,torch,hashlib,shutil,subprocess,fcntl
OLD=Path(OLD_TOKEN);D=Path(NEW_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_second_bounded_once as original
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
end=j(OLD/'reports/HUMAN_FAILED_END_BYTE_REVIEWED_ACTUAL.json');assert end['failed_child_ended'] and len(end['completed_own_segments'])==1
for pid in (3340858,3340979,3340947):assert not Path('/proc',str(pid)).exists()
assert not original.trainers();B=original.s.q.ctl.CANONICAL;before=B.read_bytes();budget=j(B);assert budget['active_segment'] is None and not j(original.s.q.ctl.STATE_PATH).get('active_training')
assert [x for x in budget['completed_segments'] if x['pid']==3340979]==end['completed_own_segments']
assert not list((OLD/'learning_logs').rglob('model_*.pt'))
assert j(OLD/'reports/POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json')['passed']
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',original.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
info=original.fullsave(Path(SOURCE_TOKEN));assert info['sha256']==SHA_TOKEN and info['finite_tensors']==107
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==446
for k,v in freeze.items():assert h(OLD/k)==v
reference=OLD.parent/'MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012';whole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());rf=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];refsource=sum((reference/k).stat().st_size for k in rf);current=sum((OLD/k).stat().st_size for k in freeze)+NEWBYTES_TOKEN
required=2*whole+2*1024**3+2*max(0,current-refsource)+2*660000*80;free=shutil.disk_usage(OLD).free
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024
ram_required=int(36639764*1024*1.25)+658725376+337280000+2*1024**3
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip();gpu_free=int(gpu)*1024**2;gpu_required=(2*9940+2048)*1024**2
apps=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip();assert not apps
assert free>required and mem>ram_required and gpu_free>gpu_required and not D.exists(),dict(free=free,required=required,RAM=mem,RAM_required=ram_required,GPU_free=gpu_free,GPU_required=gpu_required)
D.mkdir();(D/'reports').mkdir()
for k,v in freeze.items():p=D/k;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/k,p);assert h(p)==v
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json','COMPLETE151_ROUTE_AXIS_DECISION.json','COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json','MATCHED_SOURCE_SELECTED.json','REUSED_ACTUAL_CONTRACTS.json'):
 shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=freeze,selected=info,original_failed_segment=end['completed_own_segments'],old446_allprocesses_exited=True,two_locks_free=locks,resources=dict(durable_free=free,durable_required=required,RAM_available=mem,RAM_required=ram_required,GPU_free=gpu_free,GPU_required=gpu_required,guards_based_on_actual_peak_and_fail_sizes_not_cause_proof=True),no_OS_setting_change_no_budget_write_no_old_GPU_replay=True)))
'''.replace('OLD_TOKEN',repr(ROOT)).replace('NEW_TOKEN',repr(NEWROOT)).replace('SOURCE_TOKEN',repr(SOURCE)).replace('SHA_TOKEN',repr(INIT_SHA)).replace('NEWBYTES_TOKEN',str(sum(len(x) for x in files.values()))))
        save('RESOURCE_DURABLE_RAM_GPU_ADMISSION_ACTUAL.json',admission);freeze=dict(admission['oldfreeze'])
        with n.open_sftp() as f:
            for name,raw in files.items():assert name not in freeze;io.put(f,NEWROOT+'/'+name,raw);freeze[name]=H(raw)
            io.put(f,NEWROOT+'/reports/SOURCE_FREEZE.json',json.dumps(dict(epoch=time.time(),sha256=freeze,old446_allbytes_exact=True,newfiles=list(files)),indent=2).encode())
            io.put(f,NEWROOT+'/reports/RESOURCE_ADMISSION_ACTUAL.json',json.dumps(admission,indent=2).encode())
        save('RESOURCE_SOURCE_FREEZE.json',dict(epoch=time.time(),root=NEWROOT,sha256=freeze,source_count=449))
        cpu=run(n,r'''from pathlib import Path
import json,time,sys,torch,ast,copy,tempfile
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_startup_resource_reviewed_once as own
own.boundary();p=own.source();info=own.fullsave(p);assert info['sha256']==SHA_TOKEN and info['finite_tensors']==107
ck=torch.load(p,map_location='cpu',weights_only=False);assert ck['E1_WAVE50_initial_source_sha256']==own.ORIGINAL35_SHA
from wave50_route_state import KEY
from retention_command_state import same
reject=[]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'fixture.pt'
 for field in ('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256','bound_episode','spawn_xy','inward_limit_m'):
  bad=copy.deepcopy(ck)
  if field in ('bound_episode','spawn_xy','inward_limit_m'):bad[KEY][field]+=1
  else:bad[KEY][field]='wrong' if field=='profile' else '0'*64
  torch.save(bad,p)
  try:own.fullsave(p)
  except AssertionError:reject.append(field)
  else:raise AssertionError('wrong route accepted '+field)
 torch.save(ck['E1_retained_flat_command_state'],p);assert same(ck['E1_retained_flat_command_state'],torch.load(p,map_location='cpu',weights_only=False))
assert own.D==own.prior.D==D and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
assert own.ENTRY in str(own.prior.train.__code__.co_consts) and own.ENTRY in str(own.prior.guardian.__code__.co_consts)
assert '--seed' in str(own.prior.train.__code__.co_consts) and '20260928' in str(own.prior.train.__code__.co_consts)
worker=(own.CODE/own.ENTRY).read_text();assert '_OWN_PPO_LEARN_STARTED = False' in worker and 'os._exit(1)' in worker and 'app.close()' in worker
before=ast.parse((own.CODE/'train_wave50_route_same_scope_resume_ppo.py').read_text());after=ast.parse(worker)
def funcs(tree):return {x.name:ast.dump(x,include_attributes=False) for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name!='main'}
assert funcs(before)==funcs(after)
main=next(x for x in after.body if isinstance(x,ast.FunctionDef) and x.name=='main');main.body=[x for x in main.body if not isinstance(x,ast.Global)]
for x in ast.walk(main):
 if hasattr(x,'body') and isinstance(x.body,list):x.body=[n for n in x.body if not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_OWN_PPO_LEARN_STARTED' for t in n.targets))]
oldmain=next(x for x in before.body if isinstance(x,ast.FunctionDef) and x.name=='main');assert ast.dump(main,include_attributes=False)==ast.dump(oldmain,include_attributes=False)
assert not torch.cuda.is_initialized()
proof=dict(epoch=time.time(),passed=True,source_count=449,root=str(D),actual_source_CPU107=info,strict_rejected_fields=reject,private_command_disk_exact=True,restore_validators_and_main_except_observer_flag_AST_exact=True,only_prePPO_failed_exit_handling_changed=True,normal_learning_save_exit_unchanged=True,own_import_main_Popen_guardian_worker_root_seed_exact=True,no_CUDA=True,actual_GPU_startup_pending=True)
for name in ('WAVE50_TARGET_CPU_PASSED.json','RESOURCE_TARGET_CPU_PASSED.json'):(D/'reports'/name).write_text(json.dumps(proof,indent=2))
own.verify();print(json.dumps(proof))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('SHA_TOKEN',repr(INIT_SHA)))
        save('RESOURCE_TARGET_CPU_PASSED.json',cpu)
        listings=[]
        with n.open_sftp() as f,w.open_sftp() as g:
            for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
        number=153
        while any(any('episode-d3-'+str(number)+'-' in name for name in names) for host,path,names in listings):number+=1
        unused=dict(epoch=time.time(),number=number,both_host_actual_unused=[dict(host=h,path=p,matches=[]) for h,p,names in listings])
        save('RESOURCE_CANDIDATE_UNUSED_ACTUAL.json',unused)
        with n.open_sftp() as f:io.put(f,NEWROOT+'/reports/CANDIDATE_JOB_UNUSED_ACTUAL.json',json.dumps(unused,indent=2).encode())
        dispatch=run(n,r'''from pathlib import Path
import json,time,sys,subprocess
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_route_startup_resource_reviewed_once as own
own.verify();own.boundary();assert not (D/'reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'controller.log').open('x') as f:p=subprocess.Popen([own.s.q.base.PY,str(D/'supervise_wave50_route_startup_resource_reviewed_once.py')],cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),root=str(D),source_count=449,owner=own.identity(p.pid),unique_dispatch=True,no_resume=True,no_preflight_replay=True)
(D/'reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(NEWROOT)))
        save('RESOURCE_DISPATCH_ACTUAL_RECEIPT.json',dispatch);print(json.dumps(dict(targetCPU_passed=True,dispatch=dispatch)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_actual_partial_root_only_continue_unexecuted_stage_no_replay=True));raise
