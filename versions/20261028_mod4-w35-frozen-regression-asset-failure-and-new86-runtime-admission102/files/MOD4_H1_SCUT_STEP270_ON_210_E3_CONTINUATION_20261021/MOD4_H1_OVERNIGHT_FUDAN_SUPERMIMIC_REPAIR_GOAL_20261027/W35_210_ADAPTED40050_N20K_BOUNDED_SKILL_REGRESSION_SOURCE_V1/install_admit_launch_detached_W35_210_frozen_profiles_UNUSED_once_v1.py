"""NEW W35 source210 install+actual SDK CPU+detached finite frozen regression."""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v1/w35'
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
OWNER="\nfrom pathlib import Path\nimport hashlib,json,psutil,time\nC=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);expected=v['owner'];go=v['go']\nassert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'\nassert c['remaining_training_seconds']>86412.86069250107 and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]\na=c['active_segment'];active=a is not None\nif active:\n assert a['owner_parent_pid']==expected['pid'] and set(a['experts'])<=set(go)\n p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert actual==expected\nelse:\n candidates=[x for x in c['completed_segments'] if x['owner_parent_pid']==expected['pid'] and set(x['experts'])==set(go) and all(x['experts'][k]['started_epoch']==go[k]['learning_started_epoch'] for k in go)]\n assert len(candidates)==1 and candidates[0].get('ended_epoch') is not None\nprint(json.dumps(dict(passed=True,epoch=time.time(),canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),generation=c['authority_generation'],known_original_owner=expected,known_original_GO=go,original_known_owner_active=active,known_original_closed_if_not_active=not active,remaining_snapshot=c['remaining_training_seconds'],no_authority_copy_lock_or_write=True,no_second_writer_or_new_GO=True)))\n"
PRE="\nfrom pathlib import Path\nimport json,subprocess,shutil,psutil,time\nJ=Path(v['job']);mount=Path('/mnt/mod4_linux_durable_20261013');assert mount.is_mount() and not J.parent.exists() and J.resolve().is_relative_to(mount.resolve())\nm=json.loads(subprocess.check_output(['findmnt','--json','--target',str(mount),'-o','UUID,OPTIONS'],text=True))['filesystems'][0];assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')\napps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert v['GPU'] not in apps,'selected GPU compute busy: left untouched'\nline=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669\nassert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(mount).free>25*1024**3\nJ.mkdir(parents=True,mode=0o700);print(json.dumps(dict(passed=True,epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=0,no_unknown_PID_or_argv_read=True,mount=m,job=str(J))))\n"
RUN="\nfrom pathlib import Path\nimport base64,fcntl,hashlib,importlib.metadata as md,importlib.util,json,math,os,psutil,subprocess,time\nos.environ['CUDA_VISIBLE_DEVICES']='';J=Path(v['job']);lockpath=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')\ndef H(p):\n with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()\ndef put(n,x):\n with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)\nfor row in v['files']:\n p=(J/row['relative']).resolve();assert p.is_relative_to(J) and not p.is_symlink() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']\nversions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}\nrsl=Path(importlib.util.find_spec('rsl_rl').origin).parent;lab=Path(importlib.util.find_spec('isaaclab').origin).parent\nfor row in v['RSL_sources']:assert (rsl/row['relative']).stat().st_size==row['bytes'] and H(rsl/row['relative'])==row['SHA']\nassert H(lab/'utils/math.py')==v['SDK_math_SHA']\nassert (J/'runtime/assets/import_contract.json').read_bytes()==(J/'runtime/isaac/mod4/import_contract.json').read_bytes()\nfrom pxr import Usd,UsdPhysics\nstage=Usd.Stage.Open(str(J/'runtime/assets/robot.usd'));assert stage\nfor name in ['left_gas_slide','right_gas_slide']:\n p=stage.GetPrimAtPath('/Robot/joints/'+name);d=UsdPhysics.DriveAPI.Get(p,'linear');q=UsdPhysics.PrismaticJoint(p)\n assert d.GetStiffnessAttr().Get()==2000 and d.GetDampingAttr().Get()==3 and math.isclose(q.GetUpperLimitAttr().Get(),.020639440248416612,abs_tol=1e-8)\ncpu=dict(passed=True,epoch=time.time(),scope='new target SDK source metadata and USD CPU, existing W35 final78 wholeCPU reused; no policy model decode',versions=versions,RSL_source_bytes_exact=True,SDK_math_source_bytes_exact=True,asset_parent_contract_route_exact=True,nominal400_USD_composition=True,source_model_GPU_fullrestore_still_pending=True)\nput('ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',cpu)\n\ntask=dict(kind='MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1',source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',num_envs=20000,controls=1200,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_source210_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=False,canonical72_known_owner_readonly_passed=v['authority']['passed'],known72_readonly_authority=v['authority'],actual_source210_python=v['python'],full_WM_tap_included=False)\nput('FROZEN_CASE_TASK_TEMPLATE.json',task)\nenv=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1');argv=[v['python'],'-u','-B',str(J/'detached_W35_frozen_eval_private210_supervisor_once_v1.py'),'--job-root',str(J)]\nwith (J/'FROZEN_W35_SUPERVISOR_COMPLETE_STDOUT_STDERR.log').open('xb') as log:p=subprocess.Popen(argv,env=env,cwd=J,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)\nq=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd());assert p.poll() is None\nput('ACTUAL_FROZEN_W35_FINITE_SUPERVISOR_DETACHED.json',dict(epoch=time.time(),identity=identity,actual_detached=True,worker_maximum_seconds=1680,original_child_wait_seconds=1800,source_SDK_CPU_passed=True,actual_GPU_fullrestore_native24_and_profiles_pending=True,no_optimizer_budget_or_new_GO=True))\nprint(json.dumps(dict(passed_source_admission_and_detached_only=True,epoch=time.time(),identity=identity,job_root=str(J),source_SDK_CPU=cpu,actual_GPU_fullrestore_native24_and_profile_coverage_pending=True,no_policy_training_or_skill_graduation_claim=True)))\n"

def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m

def read_json(p):return json.loads(Path(p).read_bytes())

def main():
 R.mkdir(exist_ok=True);put('W35_210_FROZEN_PROFILES_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),no_training_GO_or_secondwriter=True))
 parser=argparse.ArgumentParser();parser.add_argument('--known-owner-report',type=Path,default=L/'TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1/reports/TWO101_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json');parser.add_argument('--known-go-report',type=Path,default=L/'TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1/reports/TWO101_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json');args=parser.parse_args();payload=json.loads((B/'W35_FROZEN_PROFILES_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());actual=read_json(args.known_owner_report);first=read_json(args.known_go_report);assert actual['run_id']==next(iter(first['go'].values()))['run_id']
 wrapper=module('E0_frozen_same_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('E0_same_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_W35_SOURCE_ADMISSION_AND_DETACHED_EVAL',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret);secret=None;authority=d.code(client,d.PY72,OWNER,dict(owner=actual['identities']['owner']['exact_identity'],go=first['go']),timeout=30);put('W35_CURRENT101_CANONICAL72_KNOWN_OWNER_READONLY_ADMISSION_ACTUAL.json',authority);client.close();client=None
  client=route.connect();pre=d.code(client,route.PY,PRE,dict(job=JOB,GPU=GPU),timeout=30);put('W35_210_FRESH_UUID_MOUNT_RESOURCE_ACTUAL.json',pre)
  sf=client.open_sftp();sf.get_channel().settimeout(30);made={JOB}
  try:
   for row in payload['files']:
    path=PurePosixPath(JOB)/row['relative'];assert '..' not in path.parts;parents=[];q=path.parent
    while str(q) not in made:parents.append(q);q=q.parent
    for q in reversed(parents):sf.mkdir(str(q),mode=0o700);made.add(str(q))
    with Path(row['local_path']).open('rb') as source,sf.open(str(path),'wx') as out:
     out.set_pipelined(True)
     while True:
      block=source.read(1024**2)
      if not block:break
      out.write(block)
  finally:sf.close()
  value=d.code(client,route.PY,RUN,dict(job=JOB,GPU=GPU,python=route.PY,files=[{k:r[k] for k in ('relative','bytes','SHA')} for r in payload['files']],RSL_sources=payload['RSL_sources'],SDK_math_SHA=payload['SDK_math_SHA'],authority=authority),timeout=120)
  put('W35_210_SOURCE_SDK_AND_FINITE_SUPERVISOR_DETACHED_RETURNED_ACTUAL.json',value);print(json.dumps(value))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous

if __name__=='__main__':
 try:main()
 except BaseException:put('W35_210_FROZEN_PROFILES_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_newwriter_or_oldsource_promotion=True));raise
