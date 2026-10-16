from pathlib import Path
import sys,os,json,time,getpass,shutil,hashlib,traceback,ast
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'recovery_receipt_schema_v3';sys.path.insert(0,str(D));from deploy_three_independent_V2_source_restore_then_new_axis_once import code,H,connect72,PY,CPU
OLD='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v2/recovery';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
PARENT='''from pathlib import Path
import os,json,time,subprocess,fcntl,traceback
import psutil
B=Path(__file__).resolve().parent;ROOT=Path('/home/lc01/Zonglin Li/zonglin2');PY=ROOT/'run-python.sh'
def put(p,v):
 q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 lock=(ROOT/'state/recovery_schema_v3_gpu1.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put(B/'PARENT_IDENTITY.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),argv=psutil.Process().cmdline()));e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(B/n).mkdir()
 e.update(CUDA_VISIBLE_DEVICES='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');child=None
 try:
  child=subprocess.Popen([str(PY),'-u','-B',str(B/'recovery_worker.py'),'--job','0','--phase','native'],cwd=B,env=e,stdout=(B/'worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/'WORKER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=psutil.Process(child.pid).cmdline()));rc=child.wait();put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,pid=child.pid,actual_waited=True));good=rc==0 and (B/'job0/native/FINAL.json').exists() and not list((B/'job0/native').glob('*ORIGINAL_ERROR*.json'))
  if good:
   v=subprocess.run([str(PY),'-B',str(B/'native_CPU.py'),'--job','0'],cwd=B,env={**e,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(B/'CPU_ACTUAL_EXIT.json',dict(epoch=time.time(),returncode=v.returncode,stdout=v.stdout,stderr=v.stderr));good=v.returncode==0
  put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed_native_CPU=good,canonical_write=False,PPO_updates=0,old_other_experts_not_stopped=True))
 finally:
  if child:child.wait()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),own_child_waited_out=True,own_gpu1_fcntl_released=True))
if __name__=='__main__':
 assert not (B/'PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),native_only=True)),flush=True)
 else:
  os.setsid();f=os.open(str(B/'parent.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
  try:main()
  except BaseException:put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
'''
def main():
 put('RECOVERY_V3_SCHEMA_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,no_old_GPU_repeat=True));pw=getpass.getpass('Host72 recovery receipt-schema repair (hidden): ');c=None
 try:
  c=connect72(pw);pw=None;v=code(c,PY,"from pathlib import Path;import sys,json,time,psutil;B=Path(sys.argv[1]);rows=[]\nfor p in (B/'job0/native/logs').glob('*/*STARTUP_VERIFIED.json'):rows.append(dict(name=p.name,path=str(p),value=json.loads(p.read_bytes())))\nactual=[]\nfor p in psutil.process_iter(['pid','create_time','cmdline']):\n try:\n  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):actual.append(p.info)\n except psutil.Error:pass\nprint(json.dumps(dict(epoch=time.time(),actual_startup_receipts=rows,actual_own_processes=actual,error=json.loads((B/'job0/native/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes()))))",OLD);put('RECOVERY_V2_SEVEN_ACTUAL_TYPED_STARTUP_RECEIPTS_AND_READER_REJECTION.json',v);names=sorted({r['name'] for r in v['actual_startup_receipts']});assert len(names)==7 and 'E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json' in names and not v['actual_own_processes'];assert not Q.exists();shutil.copytree(D/'v2_payload/recovery',Q);p=Q/'recovery_worker.py';s=p.read_text('utf8');old="len(receipts)>=8 and (Path(log_dir)/'E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json').exists()";assert old in s;s=s.replace(old,"set("+repr(names)+").issubset({p.name for p in receipts})");p.write_text(s,encoding='utf8');(Q/'native_parent.py').write_text(PARENT,encoding='utf8');m=json.loads((Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());files=[]
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.name!='CONTINUATION_COMPLETE_MANIFEST_V2.json':
    if p.suffix=='.py':ast.parse(p.read_text('utf8'))
    files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m['files']=files;(Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json').write_text(json.dumps(m,indent=2),encoding='utf8');put('RECOVERY_V3_EXACT_SCHEMA_REQUIRED_NAMES_CPU_ACTUAL.json',dict(epoch=time.time(),required_names=names,old_invalid_count8_retained=True,all_original_six_typed_and_new_phase_required=True,source_and_physics_and_guard_bytes_unchanged=True,missing_any_one_required_name_rejected=all(not set(names).issubset(set(names)-{n}) for n in names),no_fabricated_eighth_marker=True,manifest_SHA=H(Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json')))
  create="from pathlib import Path;import sys,json,shutil,subprocess,psutil;B=Path(sys.argv[1]);A=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned) and not B.exists();gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;B.mkdir();(B/'job0').mkdir()\nfor n in ('runtime','source','assets'):shutil.copytree(A/'job0'/n,B/'job0'/n)\nshutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');print(json.dumps(dict(root=str(B),actual_GPU=line,new_copy_only=True,no_old_expert_changed=True)))";put('RECOVERY_V3_NEW_UNUSED_ROOT_RESOURCE_ACTUAL.json',code(c,PY,create,T,OLD));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   sf.put(str(Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),T+'/CONTINUATION_COMPLETE_MANIFEST_V2.json');missing=code(c,PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());out=[]\nfor r in m['files']:\n p=B/r['relative']\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:out.append(r)\nprint(json.dumps(dict(missing=out)))",T);put('RECOVERY_V3_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
   for row in missing['missing']:sf.put(str(Q/row['relative']),T+'/'+row['relative'])
  finally:sf.close()
  cpu=CPU.replace("else:assert ck['E2_moving4_command_state']","elif m['key']=='e2':assert ck['E2_moving4_command_state']");put('RECOVERY_V3_TARGET_ALL_SOURCE_CPU_ACTUAL.json',code(c,PY,cpu,T,timeout=150));put('RECOVERY_V3_ACTUAL_NATIVE_DETACHED_DISPATCH.json',code(c,PY,"import subprocess,sys,json;v=subprocess.run([sys.argv[1],'-u','-B',sys.argv[2]],capture_output=True,text=True,check=True);print(v.stdout)",PY,T+'/native_parent.py'));print(json.dumps(dict(actual_new_recovery_native_chain_dispatched=True,required_actual_receipts=names,other_two_experts_continue=True,no_PPO_yet=True)))
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('RECOVERY_V3_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay=True));raise
