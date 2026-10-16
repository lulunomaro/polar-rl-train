"""A new same-stage E2 source; no new CURB grant, no consumed case replay."""
from pathlib import Path
import sys,os,json,time,getpass,secrets,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';U=D/'e2_from58_plus75_same4_continuation_v2';Q=U/'payload';NAME=U.name;S='/mnt/mod4_linux_durable_20261013/'+D.name+'/'+NAME;T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/'+NAME;PREV='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/e2';sys.path.insert(0,str(D));from deploy_two_exact_source_continuation_native_cohort_once import code,H,connect72,t,PY,CPU,launch
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,hashlib,shutil,subprocess,psutil
B=Path(sys.argv[1]);A=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();src=A/'job0/production/model_update75.pt';assert hashlib.sha256(src.read_bytes()).hexdigest()=='cf53f49934ac9ab9bb700b865c0bca71188d473a654d0f7767def4e78c62260e';g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if 'GPU-16828f91-2b45-b646-8dc0-9481138e2842' in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B.parent).free>25*1024**3
B.mkdir();(B/'job0').mkdir()
for name in ('runtime','source','assets'):shutil.copytree(A/'job0'/name,B/'job0'/name)
shutil.copytree(A/'lib',B/'lib');shutil.copy2(A/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(src,B/'job0/source/E2_final58.pt');print(json.dumps(dict(epoch=time.time(),root=str(B),actual_GPU_line=line,source_predecessor=str(src),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),all_reuse_new_copy_only_no_oldroot_change=True,no_native_or_PPO_yet=True)))
'''
def main():
 proof=json.loads((R/'E2_CLOSED75_SAME4_NEW_NATIVE_ACCOUNTING_CPU_ADMITTED_ACTUAL.json').read_bytes());assert proof['passed_CPU_only'];spec=dict(proof['spec'],remote_root=T);put('E2_CLOSED75_NEW_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),only_actual_alive_exclusive210_72_249_transport_owner=True,source_cf53_new_native_before_bounded_learning=True));pw=getpass.getpass('Host72 new exact E2 closed75 continuation password (hidden): ');c=sf=None;cfg=None
 try:
  c=t.connect();v=code(c,t.PY,"from pathlib import Path;import sys,json,socket;B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013')) and not B.exists();c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment'] is None\nwith socket.socket() as s:s.bind(('10.24.4.210',29739))\nB.mkdir();print(json.dumps(dict(new_original_owner_root=str(B),old_canonical_idle=True,no_GPU_or_budget_write=True)))",S);put('E2_CLOSED75_ORIGINAL_OWNER_NEW_ROOT_ACTUAL.json',v);sf=c.open_sftp();sf.get_channel().settimeout(120)
  for name in ('cohort_exact_prior_template.py','e2_single_original_canonical_owner_node_v2.py'):sf.put(str(Q/name),S+'/'+name)
  sf.close();sf=None;frozen=[dict(name=n,SHA=H(Q/n)) for n in ('cohort_exact_prior_template.py','e2_single_original_canonical_owner_node_v2.py')];v=code(c,t.PY,"from pathlib import Path;import sys,json,ast,hashlib;B=Path(sys.argv[1]);rows=json.loads(sys.argv[2])\nfor r in rows:\n p=B/r['name'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];ast.parse(p.read_text('utf8'))\nprint(json.dumps(dict(owner_source_AST_SHA_exact=True,files=rows)))",S,json.dumps(frozen));put('E2_CLOSED75_OWNER_SOURCE_CPU_ACTUAL.json',v)
 finally:
  if sf:sf.close();sf=None
  t.close(c);c=None
 try:
  c=connect72(pw);put('E2_CLOSED75_NEW_TARGET_EXACT_REUSE_ACTUAL.json',code(c,PY,CREATE,T,PREV));sf=c.open_sftp();sf.get_channel().settimeout(120);mf=Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json';sf.put(str(mf),T+'/'+mf.name);missing=code(c,PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());out=[]\nfor r in m['files']:\n p=B/r['relative']\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:out.append(r)\nprint(json.dumps(dict(missing=out)))",T);put('E2_CLOSED75_NEW_TARGET_MISSING_ONLY_OVERLAY_ACTUAL.json',missing)
  for row in missing['missing']:
   p=Q/row['relative'];assert H(p)==row['SHA'];sf.put(str(p),T+'/'+row['relative'])
  sf.close();sf=None;put('E2_CLOSED75_ALL_TARGET_SOURCE_CPU_ACTUAL.json',code(c,PY,CPU,T,timeout=150))
 finally:
  if sf:sf.close();sf=None
  if c:c.close();c=None
 try:
  c=t.connect();cfg=dict(role='owner',e2=spec,run_id='E2_CLOSED75_SAME4_CONTINUATION_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(c,t.PY,S,'e2_single_original_canonical_owner_node_v2.py',cfg);put('E2_CLOSED75_SOURCE_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_learning_until_own_native_CPU_and_original_locks=True))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;node=launch(c,PY,T,'e2_single_original_canonical_owner_node_v2.py',dict(spec,role='node',run_id=cfg['run_id'],token=cfg['token']));actual=code(c,PY,"import psutil,sys,json,time;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(node['detached_pid']));put('E2_CLOSED75_NEW_SOURCE_NATIVE_CPU_CHAIN_ACTUAL_DISPATCH.json',dict(epoch=time.time(),source_owner=owner,target_node=node,target_actual=actual,SOURCE=S,TARGET=T,source_SHA=spec['source_SHA'],original_canonical_cap2700_after_native_CPU_only=True,CURB_new_learning_not_granted=True,no_native_or_PPO_pass_inferred=True));print(json.dumps(dict(new_E2_source_owner=owner,new_target_node=node,actual_new_native_chain_dispatched=True,not_PPO_yet=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_CLOSED75_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_readonly_before_continuation_no_redeploy=True));raise
