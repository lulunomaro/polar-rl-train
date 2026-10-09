"""Stage265 actual D6 bytes plus12 new files, target CPU/schema only; once."""
from pathlib import Path
import json,shlex,sys
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009'
assert not (R/'STAGED_D7_FULL_CONTRACT.json').exists();new=json.loads((R/'NEW_SOURCE_NAMES.json').read_text());assert len(new)==12
assert json.loads((R/'D7_COM_PD_ACTUAL_SDK_REVIEW.json').read_text())['COM_PD_separate_actual_SDK_scope_accepted']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
def run(code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return json.loads(raw)
try:
 setup=r'''
from pathlib import Path
import hashlib,json,shutil
D=Path(ROOT);OLD=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==265
for n,h in f.items():
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h,n
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
print(json.dumps(dict(original_source_count=len(f))))
'''.replace('ROOT',repr(root))
 print(json.dumps(run(setup)))
 with c.open_sftp() as sf:
  for n in new:sf.put(str(D/n),root+'/'+n);assert sf.open(root+'/'+n).read()==(D/n).read_bytes()
  for n in ('SELECTED_D6_BEHAVIOR_SOURCE.json','D7_COM_PD_ACTUAL_SDK_REVIEW.json','D6_ACTUAL_BASELINE_SCOPE_REVIEW.json'):sf.put(str(R/n),root+'/reports/'+n)
 code=r'''
from pathlib import Path
import hashlib,json,time,ast,sys,torch
D=Path(ROOT);R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'].copy()
for n,h in f.items():assert sha(D/n)==h
for n in NEW:ast.parse((D/n).read_text());f[n]=sha(D/n)
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(epoch=time.time(),candidate_root=str(D),sha256=f,source_count=len(f),all265_predecessor_exact=True,new_scope='D7 chassis-only COM5mm and explicit PD095-105',hardware_calibrated=False),indent=2))
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));from test_chassis_pd_checkpoint_cpu import main
cpu=main();assert cpu['passed'] and cpu['count']==13 and not cpu['CUDA_initialized']
checks=[]
for name in ('train_chassis_pd_resume_ppo.py','train_chassis_pd_fresh_preflight_ppo.py'):
 t=(D/'isaac/mod4'/name).read_text();assert 'from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env' in t and 'install_chassis_pd_save_contract(runner,env)' in t
 assert name in t and 'chassis_PD_recipe' in t and 'chassis_pd_checkpoint.py' in t
 if 'fresh' not in name:assert 'resume_chassis_pd_new_episode(runner,env,args.init_checkpoint,log_dir)' in t
 checks.append(name)
t=(D/'native_d7_chassis_pd_probe.py').read_text();assert 'ChassisPDMod4Env' in t and "report['chassis_PD_audit']=env.chassis_pd_audit()" in t;checks.append('actual_native_COM_PD_readback')
t=(D/'supervise_d7_chassis_pd_full_contract.py').read_text();assert 'D6_STATE.json' in t and "st['phase']=='E0_D6_saved_review_ready'" in t and 'train_gas_resume_ppo.py' in t and 'train_chassis_pd_resume_ppo.py' in t
assert 'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json' in t and 'validate_saved_chassis_pd' in t and 'range(1,4)' in t and 'repeated45min_clock_trial=False' in t;checks.append('safe_boundary_fullresume_direct_stable_contract')
cpu.update(integration_checks=checks,existing_COM_PD_group_CPU_and_actual_SDK_evidence_exact_reused=True)
(R/'D7_FULL_TARGET_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
import supervise_d7_chassis_pd_full_contract as w
w.verify();source=w.source();info=w.fullsave(source,require_d7=False);assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),source_count=len(f),all265_predecessor_exact=True,CPU_contract=cpu,actual_behavior_source=info,controller_import_schema_pass=True,GPU_started=False,budget_transactions=0,old_D6_training_not_interrupted=True)
(R/'STAGED_D7_FULL_CONTRACT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(root)).replace('NEW',repr(new))
 v=run(code,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','D7_FULL_TARGET_CPU_PASSED.json','STAGED_D7_FULL_CONTRACT.json'):sf.get(root+'/reports/'+n,str(R/n))
 print(json.dumps(dict(source_count=v['source_count'],source=v['actual_behavior_source']['sha256'],target_CPU=v['CPU_contract']['count'],GPU_started=False)))
finally:c.close()
