"""Stage new fullDR80 model-free integration from immutable W35 runtime plus v2 overlay."""
from pathlib import Path
import ast,json,hashlib,time,datetime,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;OVER=R/'staged_sources/W35_MOD4V1_SOURCE_V2_FINAL';A=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets');BASE='/home/lc01/Zonglin Li/zonglin2'
SRC=BASE+'/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');job=BASE+'/tasks/MOD4V1_W35_FRESH80_FULLDR_V2_'+stamp+'_'+str(time.time_ns())
sup=R/'fresh80_supervisor_v2.py';assert not sup.exists()
s=(R/'native_probe_supervisor_v3.py').read_text(encoding='utf-8').replace("'asset':str(B/'assets/robot.usd')","'asset':str(B/'runtime/assets/robot.usd'),'runtime_job':str(B)").replace("d/'NATIVE_DATA_COMPLETE.json'","d/'FRESH80_FULLDR_NATIVE24_COMPLETE.json'")
s=s.replace("'canonical_before':None","'canonical_before_active_owner_pid':(budget['active_segment'] or {}).get('owner_parent_pid')")
ast.parse(s);sup.write_text(s,encoding='utf-8')
files=[('native_mod4v1_probe.py',R/'probe_w35_fresh80_full_dr_v2.py'),('native_probe_supervisor.py',sup),('runtime/assets/robot.usd',A/'robot.usd'),('runtime/assets/import_contract.json',A/'import_contract.json')]
for p in OVER.rglob('*'):
 if p.is_file():files.append((p.relative_to(OVER).as_posix(),p))
getter=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\REFERENCE_TRACKING_BPTT_V300_20261101\source\actual_DR_memory_getter272.py');files.append(('runtime/isaac/mod4/actual_DR_memory_getter272.py',getter))
for _,p in files:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
plan={'kind':'MOD4V1_FRESH80_FULLDR_NO_PT','new_remote_job':job,'gpus':[{'label':'gpu0','uuid':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}],'asset_sha256':H(A/'robot.usd'),'contract_sha256':H(A/'import_contract.json'),'worker_sha256':H(R/'probe_w35_fresh80_full_dr_v2.py'),'files':[{'relative':rel,'bytes':p.stat().st_size,'sha256':H(p)} for rel,p in files],'source_PT_opens':0,'no_production_GO_or_canonical_write':True}
prepare="""import pathlib,shutil,json,hashlib
B=pathlib.Path(%r);S=pathlib.Path(%r);assert not B.exists();B.mkdir()
def ignore(path,names):return [n for n in names if n=='__pycache__' or pathlib.Path(n).suffix.lower() in ('.pt','.pth','.pyc')]
shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)
shutil.copy2(S/'original_run_manifest.json',B/'original_run_manifest.json')
for relative in ['W35_PPO50_gas400_finite_worker_v1.py', 'W35_target_source_SDK_CPU_admission_v1.py', 'contract227.py', 'original_field/assets/arena_collision.usdc', 'original_field/data/arena_collision.npz', 'original_run_manifest.json', 'worker227.py', 'worker_full227.py']:
 source=S/relative
 if source.is_file():
  destination=B/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)

rows=[]
for rel,sha in [('assets/arena_collision.usdc','9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'),('data/arena_collision.npz','f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954')]:
 p=B/'original_field'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(S/'original_field'/rel,p);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;rows.append({'relative':rel,'bytes':len(raw),'SHA':sha})
(B/'RM70_BINARY_INSTALL_ACTUAL.json').write_text(json.dumps({'actual_postcopy_fullSHA_verified':True,'files':rows,'model_opens':0},indent=2))
print(json.dumps({'new_root':str(B),'source_runtime_copied_without_PT':True,'field_binary_hashes_verified':rows}))
"""%(job,SRC)
c=connect72();sf=c.open_sftp();result={'plan':plan,'status':'STAGING'}
try:
 i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(prepare),timeout=180);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);result['runtime_prepare']=json.loads(out)
 for rel,p in files:
  parent=job+'/'+str(Path(rel).parent).replace('\\','/')
  current=''
  for part in parent.split('/'):
   if not part:continue
   current+='/'+part
   try:sf.mkdir(current)
   except OSError:sf.stat(current)
  sf.put(str(p),job+'/'+rel)
 with sf.open(job+'/PLAN.json','wx')as f:f.write(json.dumps(plan,indent=2))
 code="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'native_probe_supervisor.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);q=psutil.Process(p.pid);print(json.dumps({'pid':p.pid,'creation':q.create_time(),'root':str(B),'dispatched_only':True}))"%(job,BASE+'/run-python.sh')
 i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);result.update(status='PARENT_DISPATCHED',parent=json.loads(out),stderr=err)
finally:sf.close();c.close()
p=R/'reports'/('fullDR80_dispatch_'+stamp+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(result,ensure_ascii=False,indent=2))
