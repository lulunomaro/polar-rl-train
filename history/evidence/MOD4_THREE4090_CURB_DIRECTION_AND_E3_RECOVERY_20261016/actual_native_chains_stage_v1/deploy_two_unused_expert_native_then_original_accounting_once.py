from pathlib import Path
import sys,os,time,json,getpass,secrets,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';OLD=W/'MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016';sys.path.insert(0,str(OLD))
from deploy_two_exact_source_continuation_native_cohort_once import code,H,connect72,t,PY,CPU,launch
S='/mnt/mod4_linux_durable_20261013/'+D.name+'/curb';T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery'
A='/mnt/mod4_linux_durable_20261013/'+OLD.name+'/curb';PREV='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,subprocess,psutil,socket
B=Path(sys.argv[1]);A=Path(sys.argv[2]);key=sys.argv[3];owned=Path('/mnt/mod4_linux_durable_20261013') if key=='curb' else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();src=A/('job0/production_only/model_update147.pt' if key=='curb' else 'job0/source/E0_full_source.pt');assert hashlib.sha256(src.read_bytes()).hexdigest()==sys.argv[5]
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if sys.argv[4] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldworkers=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if any(str(A)+'/' in x for x in p.info['cmdline'] or []):oldworkers.append(p.info)
 except psutil.Error:pass
assert not oldworkers,oldworkers
if key=='curb':
 with socket.socket() as s:s.bind(('10.24.4.210',29742))
B.mkdir(parents=True);(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(src,B/'job0/source'/sys.argv[6]);print(json.dumps(dict(epoch=time.time(),root=str(B),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),actual_GPU_line=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,old_scope_workers_absent=True,old_canonical_may_still_be_E2_owner_no_write=True,new_copy_only=True)))
'''
def upload(c,py,root,key):
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  mf=Q/key/'CONTINUATION_COMPLETE_MANIFEST_V2.json';sf.put(str(mf),root+'/'+mf.name);missing=code(c,py,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());out=[]\nfor r in m['files']:\n p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve())\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:out.append(r)\nprint(json.dumps(dict(missing=out)))",root);put(key.upper()+'_TARGET_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
  for row in missing['missing']:
   p=Q/key/row['relative'];assert H(p)==row['SHA'];folder=root
   for piece in row['relative'].split('/')[:-1]:
    folder+='/'+piece
    try:sf.stat(folder)
    except FileNotFoundError:sf.mkdir(folder)
   sf.put(str(p),root+'/'+row['relative'])
 finally:sf.close()
 cpu=CPU.replace("else:assert ck['E2_moving4_command_state']","elif m['key']=='e2':assert ck['E2_moving4_command_state']");put(key.upper()+'_TARGET_ALL_SOURCE_CPU_ACTUAL.json',code(c,py,cpu,root,timeout=180))
def main():
 proof=json.loads((R/'FINAL_EXECUTABLE_PAYLOAD_MANIFEST_CPU_ACTUAL.json').read_bytes());assert proof['passed_CPU_only'];put('TWO_NEW_EXPERT_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,one_new_CURB_direction_and_E3_recovery_chain=True,no_old_once_replayed=True));pw=getpass.getpass('Host72 new recovery task deployment (hidden): ');c=None;cfg=None;specs={x['key']:dict(x,python=t.PY if x['key']=='curb' else PY) for x in proof['frozen']}
 try:
  c=t.connect();put('CURB_NEW_ROOT_RESOURCE_SOURCE_REUSE_ACTUAL.json',code(c,t.PY,CREATE,S,A,'curb',specs['curb']['GPU_UUID'],specs['curb']['source_SHA'],'CURB140.pt'));upload(c,t.PY,S,'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw);put('RECOVERY_NEW_ROOT_RESOURCE_SOURCE_REUSE_ACTUAL.json',code(c,PY,CREATE,T,PREV,'recovery',specs['recovery']['GPU_UUID'],specs['recovery']['source_SHA'],'E0_full_source.pt'));upload(c,PY,T,'recovery')
 finally:
  if c:c.close();c=None
 try:
  c=t.connect();cfg=dict(role='owner',run_id='CURB35_APPROACH_E3_RECOVERY_'+str(time.time_ns()),token=secrets.token_hex(32),curb=specs['curb'],recovery=specs['recovery']);owner=launch(c,t.PY,S,'cohort_finite.py',cfg);put('CURB_NEW_NATIVE_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,native_before_original_canonical_handoff=True))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;node=launch(c,PY,T,'cohort_finite.py',dict(specs['recovery'],role='node',run_id=cfg['run_id'],token=cfg['token']));actual=code(c,PY,"import sys,json,time,psutil;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(node['detached_pid']));put('TWO_EXPERT_NEW_NATIVE_CHAIN_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),source_owner=owner,target_node=node,target_actual=actual,SOURCE=S,TARGET=T,independent_policy_optimizer=True,actual_native_and_CPU_gate_required_before_PPO=True,existing_E2_owner_untouched_and_original_canonical_wait_handoff=True,no_PPO_or_native_pass_inferred=True));print(json.dumps(dict(source_owner=owner,target_node=node,actual_new_native_chains_dispatched=True,no_PPO_pass_inferred=True)))
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO_EXPERT_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_unknown_mutation_replay=True));raise
