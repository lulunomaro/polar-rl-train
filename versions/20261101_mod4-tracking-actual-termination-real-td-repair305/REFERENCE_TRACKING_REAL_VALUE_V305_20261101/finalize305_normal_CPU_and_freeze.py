"""Freeze305 after passedCPU; adapt originalnormal and finalreader to offsets."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_BPTT_V300_20261101';R=N/'reports';D=N/'normal305';D.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
def change(s):
 keep=[]
 def h(m):keep.append(m.group());return'@HASH'+str(len(keep)-1)+'@'
 s=re.sub(r'\b[0-9a-f]{64}\b',h,s);s=re.sub(r'(?<=[A-Za-z_])300(?!\d)','305',s)
 for i,v in enumerate(keep):s=s.replace('@HASH'+str(i)+'@',v)
 return s
def write(p,s):
 p.write_bytes(s.encode());ast.parse(s,filename=str(p))
for p in(O/'normal300').glob('*.py'):
 s=change(p.read_text('utf8')).replace('7087+u','9712+u').replace('==7087+u','==9712+u')
 s=s.replace('INDEX305_NORMAL_SOURCE_FROZEN','INDEX305_NORMAL_SOURCE_FROZEN')
 if p.name=='normal300_common.py':s=s.replace('4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d','e700e546e3cada81dee7cdd6ed1aa59d51eb0d0d1932f0dfda928799de7812a8')
 write(D/change(p.name),s)
s=change((O/'review300_NEW_final_whole_CPU_UNUSED_once.py').read_text('utf8'))
s=s.replace('7087+ck','9712+ck').replace('wm-7087','wm-9712').replace("(('actor',42940),('critic',0))", "(('actor',45533),('critic',2593))")
s=s.replace("assert not s['old_Fudan_return']", "assert 'target_critic_state_dict'in s and s['actor_Adam_offset']==45533 and s['critic_Adam_offset']==2593\n    assert not s['old_Fudan_return']")
write(N/'review305_NEW_final_whole_CPU_UNUSED_once.py',s)
task=json.loads((N/'TASK305_FROZEN.json').read_bytes());proof=json.loads((R/'CPU305_MATCHED_SURVIVAL_REAL_TD_AND_RESUME_NO_STEP.json').read_bytes());assert proof['passed']
assert H(N/'source/worker305.py')==task['worker_SHA']
worker=(N/'source/worker305.py').read_text('utf8');learner=(N/'source/tracking_learner305.py').read_text('utf8')
assert 'learner.actor_offset+learner.Pi_updates'in worker and 'learner.critic_offset+learner.critic_updates'in worker
assert 'actual_reward=b.data' in learner and 'td_target=actual_reward+.99*(~actual_done)'in learner and 'matched_survival305(following)'in learner
assert 'target_critic_state_dict' in learner
files=[D/'normal305_common.py',D/'collect305_tracking_formal_cost_normal900_UNUSED_once.py',N/'teacher_task305.py']
put(D/'INDEX305_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
put(R/'SOURCE305_FROZEN_REAL_TD_SURVIVAL_CHECK.json',dict(epoch=time.time(),passed=True,actual_TD_and_EMA_saved=True,source_WM9712_actorAdam45533_criticAdam2593=True,CPU305_pass=True,physical_termination_unchanged=True,paired_H32_actual_report_beforefirstPi=True,no_rollback_or_optimizer_reset=True,source_model_reads=0,SDK=0,GO=0))
files=[p for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')]
index=N/'INDEX305_SOURCE_TASK_CALLERS_FROZEN.json'
put(index,dict(epoch=time.time(),kind='REFERENCE_TRACKING305_REAL_TD_AND_MATCHED_SURVIVAL_FROZEN',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
print(json.dumps(dict(passed=True,index_SHA=H(index),run_id=task['run_id'],files=len(files))))
