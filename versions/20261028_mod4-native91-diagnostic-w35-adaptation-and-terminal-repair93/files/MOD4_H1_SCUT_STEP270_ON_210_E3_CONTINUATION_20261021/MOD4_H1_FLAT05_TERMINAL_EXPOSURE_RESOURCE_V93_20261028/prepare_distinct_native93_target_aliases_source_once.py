"""Two real target payloads, explicit owner alias versus native worker ABI."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;B=N/'payload';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,'utf8')
base=read(R/'NATIVE93_SOURCE_PREPARED_ACTUAL.json');oldmf=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={x['relative']:x for x in oldmf['files']}
specs={}
for alias,backend,gpu,seed,job,python,lock in [
 ('h1','target72','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',27,'/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TERMINAL_2610v93/h1','/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock'),
 ('h1_210','source210','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',28,'/mnt/mod4_linux_durable_20261013/MOD4_H1_FLAT05_TERMINAL_2610v93/h1_210','/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')]:
 dest=N/'payloads'/alias;assert not dest.exists();dest.mkdir(parents=True)
 for row in oldmf['files']:
  src=B/row['relative'];p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p)
 task=read(dest/'job0/TASK.json');task.update(logical_slot=alias,canonical_worker_key='h1',execution_backend=backend,GPU_UUID=gpu,native_seed=seed)
 guard=dest/'native_flat90_source_guard_v1.py';s=guard.read_text('utf8')
 s=s.replace("task['execution_backend']=='target72'","task['execution_backend']=="+repr(backend)).replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d',gpu)
 needle="return assert_declared_admission('h1',task,go)";assert s.count(needle)==1
 s=s.replace(needle,"require(task.get('logical_slot')=="+repr(alias)+" and task.get('canonical_worker_key')=='h1' and go.get('logical_slot')==task['logical_slot'] and go.get('canonical_worker_key')=='h1','exact physical target alias and native worker ABI')\n "+needle)
 write(guard,s)
 mig=dest/'source/native88C_to_flat_migration_v1.py';s=mig.read_text('utf8');needle="task['native_seed']==27";assert s.count(needle)==1;s=s.replace(needle,"task['native_seed']=="+str(seed),1);write(mig,s)
 cpu=dest/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text('utf8');needle='value=dict(passed=True,kind=KIND';assert s.count(needle)==1;s=s.replace(needle,"value=dict(passed=True,logical_slot=task['logical_slot'],canonical_worker_key=task['canonical_worker_key'],kind=KIND",1);write(cpu,s)
 contract=read(dest/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');contract.update(logical_slot=alias,canonical_worker_key='h1',execution_backend=backend,GPU_UUID=gpu,native_seed=seed)
 contract['approved_python']={p.relative_to(dest).as_posix():H(p) for p in dest.rglob('*.py')};write(dest/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(contract,indent=2))
 task['flat_source_contract_SHA']=H(dest/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(dest/'job0/TASK.json',json.dumps(task,indent=2))
 rows=[]
 for p in sorted(dest.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(dest).as_posix()
  if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):row=oldrows[rel];assert p.stat().st_size==row['bytes']
  else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  rows.append(row)
 manifest=dict(oldmf,files=rows);write(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(manifest,indent=2))
 sp=copy.deepcopy(base['h1_spec_pending_actual_CPU_and_controller']);sp.update(key=alias,logical_slot=alias,canonical_worker_key='h1',GPU_UUID=gpu,execution_backend=backend,private_lock=lock,python=python,job_root=job,native_seed=seed,payload_manifest_SHA=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(dest/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
 for name,rel in [('CPU_path','job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json'),('CPU_proof_path','job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json'),('payload_manifest_path','THREE_SLOT_COMPLETE_MANIFEST_V1.json'),('source_contract_path','FLAT90_SOURCE_CONTRACT_ACTUAL.json')]:sp[name]=job+'/'+rel
 protocol=(N/'controllers/h1_next72_protocol.py').read_text('utf8')
 for a,b in [("KEY='h1'","KEY="+repr(alias)),('GPU-c27eecbd-6838-7290-1cd2-37e34522213d',gpu),('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TERMINAL_2610v93/h1',job),("'target72'",repr(backend)),("s.get('native_seed')==27","s.get('native_seed')=="+str(seed)),("PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'","PYTHON="+repr(python)),("PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'","PRIVATE_LOCK="+repr(lock))]:protocol=protocol.replace(a,b)
 needle="require(s.get('key')==KEY";assert protocol.count(needle)==1;protocol=protocol.replace(needle,"require(s.get('logical_slot')==KEY and s.get('canonical_worker_key')=='h1','explicit owner alias versus native ABI')\n "+needle)
 needle="require(v.get('passed') is True";assert protocol.count(needle)==1;protocol=protocol.replace(needle,"require(v.get('logical_slot')==KEY and v.get('canonical_worker_key')=='h1','actual target CPU alias, no projected foreign proof')\n "+needle)
 needle='flat05_objective_changed_from_native88C=True,';assert protocol.count(needle)==1;protocol=protocol.replace(needle,"logical_slot=KEY,canonical_worker_key='h1',"+needle)
 out=N/'protocols'/alias/'h1_native93_protocol.py';write(out,protocol)
 for p in [*dest.rglob('*.py'),out]:ast.parse(p.read_bytes())
 specs[alias]=dict(spec=sp,payload=str(dest),protocol=str(out),protocol_SHA=H(out),actual_target_CPU_pending=True,source_only=True)
with (R/'NATIVE93_TWO_DISTINCT_TARGET_ALIAS_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,source_only_no_remote_GO_or_CPU=True,each_real_target_requires_separate_actual_SDK_CPU=True,source_native91_models_norms_threeopts_globals_retained=True,source_seed27_distinct_from_fresh_physical_seeds=[27,28],owner_alias_never_projected_by_account_writer=True,node_only_native_worker_slot_projection='h1',targets=specs,epoch=time.time()),f,indent=2)
print(json.dumps(dict(prepared_aliases=list(specs),actual_source_SDK_CPU_pending=True)))
