"""New human-authorized Linux GPU1 frozen backend; original V3 Windows attempt retained."""
from pathlib import Path
import json,time,hashlib,shutil,ast,traceback,copy
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'h1_fe1709_linux4090_v4/payload';OLD=B/'h1_fe1709_frozen_v3/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CONTRACT='''from pathlib import Path
import hashlib,json
GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
def validate(lease,manifest,case):
 assert lease['target_host']=='10.24.0.72' and lease['execution_backend']=='linux72_GPU1_frozen_only'
 assert lease['GPU_UUID']==GPU and lease['namespace']=='H1_FE1709_LINUX4090_V4_20261018'
 assert lease['GPU_lease_granted_by_root'] is True and lease['actual_selected_GPU_idle_private_lock_free'] is True
 assert lease['checkpoint_sha256']==manifest['source']['SHA']=='fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e'
 assert lease['case_parameters']==case and case['steps'] in (120,1500) and case['num_envs']==80 and case['seed']==20260928
 assert case['kind']=='jump' and case['router_mode']=='single_eval' and case['headless'] and case['device']=='cuda:0'
 assert lease['human_authorized_4090_eval_parallel_training_not_interrupted'] is True
 if case['steps']==1500:assert lease['actual_same_backend_source_native120_allrow_CPU_passed'] is True and lease['native120_actual_exit_childrenout_lockfree'] is True
 return True
'''
PARENT='''"""One finite frozen child; no training/canonical operations or other process signals."""
from pathlib import Path
import sys,json,os,time,subprocess,psutil
B=Path(__file__).resolve().parent
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def run(cfg):
 A=Path(cfg['attempt']);assert A.resolve().is_relative_to(B.resolve()) and not A.exists();A.mkdir(parents=True)
 lease=cfg['lease'];L=A/'LEASE_ACTUAL.json';put(L,lease)
 e=os.environ.copy();e.update(CUDA_VISIBLE_DEVICES=lease['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
 for key,part in [('HOME','home'),('TMPDIR','tmp'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
  p=A/part;p.mkdir();e[key]=str(p)
 args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-B','-u',str(B/'h1_linux4090_frozen_worker_v1.py'),'--lease',str(L),'--output',str(A/'output')]
 begin=time.time();log=(A/'worker.log').open('xb');p=subprocess.Popen(args,cwd=str(B),env=e,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
 put(A/'DISPATCH_RECEIPT.json',dict(epoch=begin,parent_pid=os.getpid(),parent_creation=psutil.Process().create_time(),child_pid=p.pid,child_creation=psutil.Process(p.pid).create_time(),argv=args,cwd=str(B),GPU_UUID=lease['GPU_UUID'],no_PPO=True,other_GPU_training_not_signalled=True))
 rc=p.wait();log.close();O=A/'output';errors=[n for n in ('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json') if (O/n).exists()]
 put(A/'PARENT_EXIT_RECEIPT.json',dict(epoch=time.time(),parent_pid=os.getpid(),child_pid=p.pid,actual_child_returncode=rc,all_actual_own_children_waited=True,original_errors=errors,complete=(O/'COMPLETE_ACTUAL.json').exists(),no_PPO=True,canonical_budget_written=False,actual_elapsed_seconds=time.time()-begin))
 if rc or errors:raise RuntimeError('Frozen child failed; original error preserved')
if __name__=='__main__':run(json.loads(sys.stdin.readline()))
'''
WORKER='''"""Human-authorized Linux GPU1 evaluation, isolated from GPU0 paid training."""
from pathlib import Path
import sys,json,time,os,argparse,hashlib,traceback,fcntl,subprocess,shutil,psutil,importlib.metadata as metadata
B=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=argparse.ArgumentParser();p.add_argument('--lease',required=True);p.add_argument('--output',required=True);args=p.parse_args();lease=json.loads(Path(args.lease).read_bytes());O=Path(args.output);m=json.loads((B/'H1_FE1709_LINUX4090_MANIFEST_V4.json').read_bytes());case=lease['case_parameters']
from h1_linux_eval_contract_v1 import validate,GPU
validate(lease,m,case);assert lease['worker_sha256']==H(__file__) and lease['source_manifest_sha256']==H(B/'H1_FE1709_LINUX4090_MANIFEST_V4.json')
assert H(B/m['source_relative'])==lease['checkpoint_sha256'] and os.environ['CUDA_VISIBLE_DEVICES']==GPU and not O.exists()
for row in m['files']:
 q=B/row['relative'];assert q.resolve().is_relative_to(B.resolve()) and q.stat().st_size==row['bytes'] and H(q)==row['SHA'],row['relative']
sdk=json.loads((B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json').read_bytes());assert H(B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json')==lease['actual_Linux_backend_SHA']
for n,v in sdk['versions'].items():assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['SHA']
assert sdk['files'] and sdk['native_binding']['SHA'] and H(sdk['native_binding']['path'])==sdk['native_binding']['SHA']
owned=Path('/home/lc01/Zonglin Li/zonglin2');lockpath=owned/'state'/('three_expert_v2_'+GPU+'.lock');lock=lockpath.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(GPU in x for x in compute.splitlines()),compute
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if GPU in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
O.mkdir(parents=True)
def save(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,case=case,GPU_UUID=GPU,actual_private_fcntl_path=str(lockpath),global_validation_only_briefly_checked_not_held=True,compute_snapshot=compute,actual_Linux_backend=sdk,no_PPO=True,other_GPU_training_not_signalled=True))
for k,v in m['env'].items():os.environ[k]=str(v)
L=B/'frozen_shared/runtime';C=L/'isaac/mod4';os.environ.update(RM_MOD4_USD=str(L/'assets/robot.usd'),RM_MILD_DR_PROFILE='white_v3');sys.path[:0]=[str(B),str(C),str(L),str(B/'frozen_shared')];app=None;context={};failure=None
try:
 import torch,numpy as np,tensordict
 torch.set_num_threads(1)
 from h1_closed24_source_guard_v1 import validate_H1_source
 source=torch.load(B/m['source_relative'],map_location='cpu',weights_only=False);validate_H1_source(source);assert not torch.cuda.is_initialized();del source
 from zonglin2_app_launcher import Zonglin2AppLauncher
 app=Zonglin2AppLauncher(headless=True,device='cuda:0').app
 from h1_frozen_witness_v1 import CONTEXT
 context=CONTEXT;context.update(save=save,output_dir=str(O),router_mode='single_eval');a=argparse.Namespace(**case);a.checkpoint=str(B/m['source_relative']);a.checkpoint_sha=m['source']['SHA'];a.case_id=lease['case_id'];a.shared_payload=str(B/'frozen_shared');a.dr_profile='white_v3';a.speed_limit=1.5;a.ramp_suite=False;a.reset_smoke=False;a.max_rate=4.;a.contact_readback=True;a.manual_reference=False;a.output=str(O/'probe.json')
 from h1_frozen_jump_loop_v1 import run_jump
 run_jump(a);app.close();app=None;save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,no_PPO=True))
except BaseException:
 failure=traceback.format_exc();save('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=failure,no_PPO=True,no_qualification_claim=True))
 try:
  from e2_frozen_prefix_guard_v4 import save_failed_prefix
  save_failed_prefix(context,O,save)
 except BaseException:save('FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_failure_preserved=True))
finally:
 if app is not None:
  try:app.close()
  except BaseException:save('APP_CLOSE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if failure:raise RuntimeError('Original frozen evaluation error saved before SDK close')
'''
def main():
 assert not Q.exists();shutil.copytree(OLD,Q,ignore=shutil.ignore_patterns('__pycache__'))
 for n,s in [('h1_linux_eval_contract_v1.py',CONTRACT),('h1_linux4090_frozen_worker_v1.py',WORKER),('h1_linux4090_frozen_parent_v1.py',PARENT)]:ast.parse(s);(Q/n).write_text(s,encoding='utf8')
 shutil.copy2(B/'payload_h1_native/lib/zonglin2_app_launcher.py',Q/'zonglin2_app_launcher.py')
 p=Q/'h1_plane_reference80_v1.py';s=p.read_text('utf8');s=s.replace("if path.suffix.lower() not in ('.dll','.pyd'):continue","if '.so' not in path.name.lower():continue")
 s=s.replace("assert digest==NATIVE_BINDING_SHA256,('Native binding differs from independently completed V7',str(binding),digest)","expected=json.loads((Path(__file__).resolve().parent/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json').read_bytes())['native_binding'];assert str(binding)==expected['path'] and digest==expected['SHA'],('Actual Linux binding differs from its own prelaunch CPU fingerprint',str(binding),digest)")
 s=s.replace("pin_source='Actual independently completed V7 binding fingerprint'","pin_source='Own actual Linux72 prelaunch CPU fingerprint; Windows3060 proof not reused'")
 p.write_text(s,encoding='utf8');ast.parse(s)
 m=json.loads((OLD/'H1_FE1709_FROZEN_COMPLETE_MANIFEST_V3.json').read_bytes());m.update(version=4,execution_backend='linux72_GPU1_frozen_only',human_authorized_4090_eval_parallel_training=True,Windows3060_backend_and_native_binding_not_reused=True)
 changes=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  old=OLD/p.relative_to(Q)
  if not old.exists() or H(old)!=H(p):changes.append(p.relative_to(Q).as_posix())
 assert changes==sorted(changes)
 files=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 m['files']=files;m['package_files_v8']=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in files];(Q/'H1_FE1709_LINUX4090_MANIFEST_V4.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 ns={};exec(CONTRACT,ns);case=dict(router_mode='single_eval',kind='jump',steps=120,num_envs=80,seed=20260928,headless=True,device='cuda:0');lease=dict(target_host='10.24.0.72',execution_backend=m['execution_backend'],GPU_UUID=ns['GPU'],namespace='H1_FE1709_LINUX4090_V4_20261018',GPU_lease_granted_by_root=True,actual_selected_GPU_idle_private_lock_free=True,checkpoint_sha256=m['source']['SHA'],case_parameters=case,human_authorized_4090_eval_parallel_training_not_interrupted=True);assert ns['validate'](lease,m,case)
 bad=[]
 for label,key,value in [('wrong_host','target_host','10.24.4.249'),('wrong_GPU','GPU_UUID','GPU0'),('wrong_backend','execution_backend','windows3060'),('wrong_source','checkpoint_sha256','0'*64),('missing_human','human_authorized_4090_eval_parallel_training_not_interrupted',False),('no_lock_admission','actual_selected_GPU_idle_private_lock_free',False)]:
  v=copy.deepcopy(lease);v[key]=value
  try:ns['validate'](v,m,case)
  except AssertionError:bad.append(label)
  else:raise AssertionError(label)
 full=copy.deepcopy(case);full['steps']=1500;v=copy.deepcopy(lease);v['case_parameters']=full
 try:ns['validate'](v,m,full)
 except KeyError:bad.append('full_before_own_native_CPU')
 else:raise AssertionError('full accepted without native')
 put('H1_FE1709_LINUX4090_V4_PARALLEL_FROZEN_PACKAGE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_package_AST_and7_contract_rejections=True,changes=changes,negative_cases=bad,files=len(files),manifest_SHA=H(Q/'H1_FE1709_LINUX4090_MANIFEST_V4.json'),source=m['source'],Linux_actual_backend_CPU_resource_fcntl_still_required=True,no_target_upload_or_GPU_yet=True,human='3060关机暂无法恢复，任一4090评测且与训练并行，不中断训练',original_physical_reward_command_phase_controller_and_source_bytes_exact_except_readonly_Linux_binding_fingerprint_adapter=True,Windows_V1_timeout_V2_fixture_false_V3_success_all_preserved=True))
 print(json.dumps(dict(Linux4090_frozen_CPU_prepared=True,files=len(files),negative_cases=bad)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LINUX4090_FROZEN_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
