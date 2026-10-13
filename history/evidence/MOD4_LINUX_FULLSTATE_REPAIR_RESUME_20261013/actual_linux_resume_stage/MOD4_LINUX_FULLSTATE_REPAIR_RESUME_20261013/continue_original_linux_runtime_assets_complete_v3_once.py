"""New scope fills original non-code runtime assets omitted by the code-only copier."""
import json,os
from pathlib import Path
from deploy_original_linux20k_formal_once import S as BASE,PY,D,O as ORIGINAL
from read_linux_resume_boundary_actual import connect_linux_only
OLD=BASE.replace('_v1','_EULA_environment_v2');S=BASE.replace('_v1','_runtime_assets_complete_v3')
c=connect_linux_only()
try:
    src=r'''
from pathlib import Path
import json,hashlib,shutil,fcntl,subprocess,time
P=Path;old=P(OLD);R=P(S);original=P(ORIGINAL);assert not R.exists()
e=json.loads((old/'formal/EXIT_RECEIPT.json').read_bytes());assert e['child_actually_absent']
assert b'MOD4_RESET_COLLISION_BANK.npz' in (old/'formal/worker_stdout.log').read_bytes()
assert not list((old/'formal/learning_logs').glob('*/latest_complete.json'))
B=P('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(B.read_bytes())['active_segment'] is None
assert not subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
R.mkdir();m=json.loads((old/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());rows={}
for x in m['sourcefreeze']:
 p=P(x['path']);rel=p.relative_to(old);q=R/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[str(rel)]=dict(x,path=str(q))
# Complete original runtime trees, including reset-bank NPZ assets. No installed SDK changes.
assets=[]
for tree in ('isaac','train'):
 for p in (original/tree).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(original);q=R/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  h=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(q.read_bytes()).hexdigest()==h
  x=dict(path=str(q),origin=str(p),bytes=q.stat().st_size,sha256=h);rows[str(rel)]=x
  if p.suffix not in ('.py','.json'):assets.append(x)
assert (R/'isaac/mod4/MOD4_RESET_COLLISION_BANK.npz').exists()
m.update(scope=S,sourcefreeze=list(rows.values()),original_runtime_asset_tree_complete=True,prior_missing_asset_failure_preserved=str(old/'formal/EXIT_RECEIPT.json'))
(R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').write_text(json.dumps(m,indent=2))
shutil.copy2(old/'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json',R/'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json')
proof=dict(epoch=time.time(),passed=True,complete_original_runtime_assets=assets,source_files=len(rows),no_RL_parameter_or_state_changes=True)
(R/'ORIGINAL_RUNTIME_ASSETS_BYTEEXACT_ACTUAL.json').write_text(json.dumps(proof,indent=2))
argv=[PY,'-u',str(R/'original_linux_formal_parent.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=int((P('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split()[19]),argv=argv,cwd=S,complete_original_runtime_assets=True,PPO_claimed=False)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(dict(dispatch=receipt,asset_proof=proof)))
'''
    si,so,se=c.exec_command('python3 -',timeout=60);si.write('OLD='+repr(OLD)+'\nS='+repr(S)+'\nPY='+repr(PY)+'\nORIGINAL='+repr(ORIGINAL)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();p=D/'reports/ORIGINAL_LINUX20K_RUNTIME_ASSETS_COMPLETE_V3_DISPATCH_ACTUAL.json';p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);print(out.decode()[:2200])
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
