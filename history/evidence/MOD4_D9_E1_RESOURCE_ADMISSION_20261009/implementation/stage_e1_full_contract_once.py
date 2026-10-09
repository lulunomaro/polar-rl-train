"""Isolate actual277 D7 bytes +18 E1 files; target CPU, source schema, no GPU."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009'
assert not (R/'E1_STAGED_FULL_CONTRACT.json').exists();new=json.loads((R/'NEW_SOURCE_NAMES.json').read_text(encoding='utf8'));assert len(new)==18
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
def run(code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=120);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return json.loads(raw)
try:
 setup=r'''
from pathlib import Path
import hashlib,json,shutil
D=Path(ROOT);OLD=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009');assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==277
for name,h in f.items():
 assert hashlib.sha256((OLD/name).read_bytes()).hexdigest()==h
 p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,p)
print(json.dumps(dict(original_source_count=277)))
'''.replace('ROOT',repr(root))
 print(json.dumps(run(setup)))
 with c.open_sftp() as sf:
  for name in new:
   parent=root+'/'+str(Path(name).parent).replace('\\','/')
   try:sf.stat(parent)
   except FileNotFoundError:
    # Only pinned_source is a genuinely new nested directory here.
    assert name.startswith('isaac/mod4/pinned_source/');sf.mkdir(parent)
   sf.put(str(D/name),root+'/'+name);assert sf.open(root+'/'+name).read()==(D/name).read_bytes()
  for name in ('SELECTED_E0_FOR_E1_BEHAVIOR_SOURCE.json','E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','NEXT_S3_E1_FULL_LEARNING_WORK_ORDER.json','D9_RETENTION18_ACTUAL_REVIEW.json'):
   sf.put(str(R/name),root+'/reports/'+name)
 code=r'''
from pathlib import Path
import ast,json,time,hashlib,sys,torch
D=Path(ROOT);R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'].copy()
for name,h in f.items():assert sha(D/name)==h
for name in NEW:
 if name.endswith('.py'):ast.parse((D/name).read_text())
 f[name]=sha(D/name)
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(epoch=time.time(),candidate_root=str(D),sha256=f,source_count=len(f),all277_predecessor_exact=True,new_scope='Independent E1 gentle terrain with inherited D0-D7',masterSHA_unchanged=True),indent=2))
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));from test_e1_terrain_state_cpu import main
v=main();assert v['passed'] and v['count']==9 and not v['CUDA_initialized']
for name in ('train_e1_terrain_resume_ppo.py','train_e1_terrain_fresh_preflight_ppo.py'):
 text=(D/'isaac/mod4'/name).read_text();assert 'E1TerrainLearningEnv as Mod4Env,configure_intro' in text and 'configure_intro(cfg)' in text and 'install_e1_save_contract(runner,env)' in text and 'E1_terrain_identity' in text
 if 'fresh' not in name:assert 'resume_e1_new_episode(runner,env,args.init_checkpoint,log_dir)' in text
ctl=(D/'supervise_e1_gentle_full_contract.py').read_text();assert "'S3' in a['allowed_stages']" in ctl and "st['phase']=='E0_D7_saved_review_ready'" in ctl and "'e1_first_gentle_block'" in ctl and '2700' in ctl and "active_expert='E1'" in ctl
v.update(inherited_DR_CPU_and_SDK_exact_reused=True,actual_ground_interface_accepted=read(R/'E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json')['actual_interface_scope_accepted'],new_complete_checkpoint_CPU_is_schema_not_actual_CUDA=True)
(R/'E1_FULL_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
import supervise_e1_gentle_full_contract as w
w.verify();source=w.source();info=w.fullsave(source,require_e1=False);assert not torch.cuda.is_initialized()
row=dict(epoch=time.time(),source_count=len(f),all277_predecessor_exact=True,target_CPU=v,source=info,controller_import_schema_pass=True,GPU_started=False,PPO_and_budget_transactions=0,new_scope_native_then_complete_PPO_required=True)
(R/'E1_STAGED_FULL_CONTRACT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''.replace('ROOT',repr(root)).replace('NEW',repr(new))
 v=run(code,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python')
 with c.open_sftp() as sf:
  for name in ('SOURCE_FREEZE.json','E1_FULL_TARGET_CPU_PASSED.json','E1_STAGED_FULL_CONTRACT.json'):sf.get(root+'/reports/'+name,str(R/name))
 print(json.dumps(dict(source_count=v['source_count'],target_CPU=v['target_CPU']['count'],source=v['source']['sha256'],GPU_started=False)))
finally:c.close()
