from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'v9_payload';sys.path.insert(0,str(D));from deploy_two_unused_expert_native_then_original_accounting_once import code,H,connect72,t,PY,CPU,launch
ROOTS=dict(curb='/mnt/mod4_linux_durable_20261013/'+D.name+'/v9/curb',e2='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v9/e2',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v9/recovery')
PREV=dict(curb='/mnt/mod4_linux_durable_20261013/'+D.name+'/v8/curb',e2='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v8/e2',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v8/recovery')
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,subprocess,psutil,socket
B=Path(sys.argv[1]);A=Path(sys.argv[2]);key=sys.argv[3];owned=Path('/mnt/mod4_linux_durable_20261013') if key=='curb' else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();source=A/sys.argv[6];assert hashlib.sha256(source.read_bytes()).hexdigest()==sys.argv[5];snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in snapshot.splitlines() if sys.argv[4] in x);assert (key=='recovery' or int(line.split(',')[-1])>7000) and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if any(str(A)+'/' in s for s in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
if key!='recovery':assert not procs,procs
else:assert all(any('/native_parent.py' in a or '/recovery_worker.py' in a or '/native_CPU.py' in a for a in p['cmdline']) for p in procs),procs
if key=='curb':
 c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment'] is None
 with socket.socket() as s:s.bind(('10.24.4.210',29748))
B.mkdir(parents=True);(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(source,B/'job0/source'/sys.argv[7]);print(json.dumps(dict(epoch=time.time(),root=str(B),source_SHA=sys.argv[5],actual_GPU_line=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,old_all_own_scope_processes_absent=True,new_copy_only_no_oldroot_or_guard_mutation=True)))
'''
def upload(c,py,key):
 root=ROOTS[key];b=Q/key;sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  sf.put(str(b/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),root+'/CONTINUATION_COMPLETE_MANIFEST_V2.json');missing=code(c,py,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());out=[]\nfor r in m['files']:\n p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve())\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:out.append(r)\nprint(json.dumps(dict(missing=out)))",root);put('V9_'+key.upper()+'_MISSING_ONLY_SOURCE_UPLOAD_ACTUAL.json',missing)
  for row in missing['missing']:
   p=b/row['relative'];assert H(p)==row['SHA'];folder=root
   for piece in row['relative'].split('/')[:-1]:
    folder+='/'+piece
    try:sf.stat(folder)
    except FileNotFoundError:sf.mkdir(folder)
   sf.put(str(p),root+'/'+row['relative'])
 finally:sf.close()
 cpu=CPU.replace("else:assert ck['E2_moving4_command_state']","elif m['key']=='e2':assert ck['E2_moving4_command_state']");put('V9_'+key.upper()+'_ALL_TARGET_CPU_AST_SHA_FULLSOURCE_ACTUAL.json',code(c,py,cpu,root,timeout=180))
def main():
 proof=json.loads((R/'V9_FINAL_SOURCE_STATUS_FIX_E3_NATIVE_REUSE_CURB_DEFERRED_CPU_ACTUAL.json').read_bytes());assert proof['passed_CPU_only'];put('THREE_EXPERT_V9_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,three_independent_finite_chains_not_old_once_replay=True));pw=getpass.getpass('Host72 three independent expert deployment (hidden): ');c=None;cfg=None;specs={r['key']:dict(r,python=t.PY if r['key']=='curb' else PY) for r in proof['frozen']}
 try:
  c=t.connect();put('V9_CURB_NEW_ROOT_RESOURCE_SOURCE_REUSE_ACTUAL.json',code(c,t.PY,CREATE,ROOTS['curb'],PREV['curb'],'curb',specs['curb']['GPU_UUID'],specs['curb']['source_SHA'],'job0/production_only/model_update40.pt','CURB140.pt'));upload(c,t.PY,'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw)
  for key,rel in (('e2','job0/production/model_update4.pt'),('recovery','job0/source/E0_full_source.pt')):put('V9_'+key.upper()+'_NEW_ROOT_RESOURCE_SOURCE_REUSE_ACTUAL.json',code(c,PY,CREATE,ROOTS[key],PREV[key],key,specs[key]['GPU_UUID'],specs[key]['source_SHA'],rel,specs[key]['source_filename']));upload(c,PY,key)
 finally:
  if c:c.close();c=None
 try:
  c=t.connect();cfg=dict(role='owner',experts=specs,token=secrets.token_hex(32),run_id='THREE_DISTINCT_CURB_E2_RECOVERY_V9_'+str(time.time_ns()));owner=launch(c,t.PY,ROOTS['curb'],'three_expert_finite_owner_node_v9.py',cfg);put('V9_THREE_EXPERT_SOURCE_OWNER_ACTUAL_DISPATCH.json',dict(epoch=time.time(),owner=owner,native_before_learning=True))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;nodes={}
  for key in ('e2','recovery'):nodes[key]=launch(c,PY,ROOTS[key],'three_expert_finite_owner_node_v9.py',dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('THREE_EXPERT_V9_ACTUAL_DETACHED_NATIVE_TO_FINITE_PPO_DISPATCH.json',dict(epoch=time.time(),owner=owner,nodes=nodes,roots=ROOTS,each_PPO_only_after_own_native_CPU=True,single_original_canonical_summed_distinct_intervals=True,one_expert_failure_does_not_stop_other_experts=True,no_future_native_or_PPO_pass_inferred=True));print(json.dumps(dict(owner=owner,nodes=nodes,three_actual_new_native_chains_dispatched=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_V9_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_readonly_before_unused_continuation=True));raise
