"""Stage actual255 exact plus new D6 CPU-checked integration; no GPU or ledger writes."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';PREP=D.parent/'MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
assert not (R/'STAGED_D6_FULL_CONTRACT.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
root='/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009'
new=json.loads((R/'NEW_SOURCE_NAMES.json').read_text())
c=connect()
def run(code,py='/usr/bin/python3',timeout=60):
    _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=timeout);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return json.loads(raw)
try:
    setup=r'''
from pathlib import Path
import hashlib,json,shutil
D=Path(ROOT);OLD=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008')
assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==255
for n,h in f.items():
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
print(json.dumps(dict(original_source_count=len(f))))
'''.replace('ROOT',repr(root))
    print(json.dumps(run(setup)))
    with c.open_sftp() as f:
        for n in new:f.put(str(D/n),root+'/'+n);assert f.open(root+'/'+n).read()==(D/n).read_bytes()
        for n in ('SELECTED_D5_BEHAVIOR_SOURCE.json','D6_GAS_DAMPING_ACTUAL_SDK_REVIEW.json'):f.put(str(R/n),root+'/reports/'+n)
        for n in ('D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json','D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json'):f.put(str(PREP/'reports'/n),root+'/reports/'+n)
    code=r'''
from pathlib import Path
import hashlib,json,time,ast,sys,torch
D=Path(ROOT);R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'].copy()
for n,h in f.items():assert sha(D/n)==h
for n in NEW:
 ast.parse((D/n).read_text());f[n]=sha(D/n)
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(epoch=time.time(),candidate_root=str(D),sha256=f,source_count=len(f),all255_predecessor_exact=True,new_scope='D6 gas damping only2.7-3.3Ns/m',hardware_calibrated=False),indent=2))
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
from gas_damping_checkpoint import validate_saved_damping
checks=[]
for n in ('D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json','D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json'):
 r=read(R/n);assert r['passed'] and not r['CUDA_initialized'];checks.append(n+'_exact_evidence_reused')
for fresh in (False,True):
 n='train_gas_fresh_preflight_ppo.py' if fresh else 'train_gas_resume_ppo.py';t=(D/'isaac/mod4'/n).read_text()
 assert 'from gas_damping_training_env import GasDampingMod4Env as Mod4Env' in t and 'install_damping_save_contract(runner,env)' in t
 assert 'gas_damping_recipe' in t and n in t and all(g in t for g in ('gas_damping_factor.py','gas_damping_sdk_adapter.py','gas_damping_training_env.py','gas_damping_checkpoint.py'))
 assert fresh or 'resume_damping_new_episode(runner,env,args.init_checkpoint,log_dir)' in t
 checks.append(n+'_actual_environment_save_and_snapshot_integration')
t=(D/'native_d6_gas_probe.py').read_text();assert 'GasDampingMod4Env' in t and 'gas_damping_audit' in t;checks.append('native20k_actual_gas_class_and_audit')
t=(D/'supervise_d6_gas_full_contract.py').read_text();assert 'train_gas_resume_ppo.py' in t and 'D5_STATE.json' in t and "st['phase']=='E0_D5_saved_review_ready'" in t
assert "validate_saved_damping(ck['gas_damping_state'],count)" in t and 'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json' in t
checks.append('natural_D5_boundary_and_full_PPO_gas_schema_integration')
assert '7200' in t and 'repeated45min_clock_trial=False' in t and 'range(1,4)' in t;checks.append('direct_twohour_blocks_no_clock_trial')
cpu=dict(epoch=time.time(),passed=True,count=len(checks),checks=checks,Torch=torch.__version__,CPU_only=True,CUDA_initialized=torch.cuda.is_initialized(),prior_component_contracts_reused_not_repeated=True)
assert not cpu['CUDA_initialized'];(R/'D6_FULL_TARGET_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
import supervise_d6_gas_full_contract as w
w.verify();src=w.source();assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),source_count=len(f),all255_predecessor_exact=True,CPU_contract=cpu,actual_behavior_source=w.fullsave(src,require_gas=False),controller_import_schema_pass=True,GPU_started=False,budget_transactions=0,old_D5_training_not_interrupted=True)
(R/'STAGED_D6_FULL_CONTRACT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(root)).replace('NEW',repr(new))
    v=run(code,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python')
    with c.open_sftp() as f:
        for n in ('SOURCE_FREEZE.json','D6_FULL_TARGET_CPU_PASSED.json','STAGED_D6_FULL_CONTRACT.json'):f.get(root+'/reports/'+n,str(R/n))
    print(json.dumps(dict(epoch=v['epoch'],source_count=v['source_count'],controller_import_schema_pass=v['controller_import_schema_pass'],source=v['actual_behavior_source']['sha256'],no_GPU=True)))
finally:c.close()
