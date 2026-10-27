"""Fix only CLI LR constructor scalar; source checkpoint/optimizer never read."""
from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 old=OLD/'E0_PPO50_gas400_finite_worker_v3_original_resource_exact.py';new=HERE/'E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py'
 raw=old.read_bytes();assert H(raw)=='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
 a=b"'--learning_rate','.0001'";b=b"'--learning_rate','.00038443359375000017'";assert raw.count(a)==1
 fixed=raw.replace(a,b);assert fixed.replace(b,a)==raw and not new.exists();new.write_bytes(fixed)
 changes=[]
 def compare(a,b,path='root'):
  if isinstance(a,ast.AST):
   assert type(a) is type(b)
   for field in a._fields:compare(getattr(a,field),getattr(b,field),path+'.'+field)
  elif isinstance(a,list):
   assert len(a)==len(b)
   for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'['+str(i)+']')
  elif a!=b:changes.append(dict(path=path,before=a,after=b))
 compare(ast.parse(raw),ast.parse(fixed));assert len(changes)==1 and changes[0]['before']=='.0001' and changes[0]['after']=='.00038443359375000017'
 metadata=json.loads((OLD/'reports/E0_W35_ORIGINAL_CHECKPOINT_CPU_METADATA_V1.json').read_bytes())
 source_lr=metadata['sources']['E0']['optimizer_summary']['param_groups'][0]['lr'];assert float('.00038443359375000017')==source_lr
 installed=HERE.parents[2]/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018/actual_installed_RSL72_sources/rsl_rl'
 ppo=installed/'algorithms/ppo.py';runner=installed/'runners/on_policy_runner.py'
 # Metadata source references only: no package import/constructor/model execution.
 tree=ast.parse(ppo.read_bytes());klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PPO')
 load=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='load')
 load_text=ast.get_source_segment(ppo.read_text('utf8'),load);assert 'self.optimizer.load_state_dict' in load_text and 'self.learning_rate' not in load_text
 assert 'self.learning_rate = learning_rate' in ppo.read_text('utf8') and 'param_group["lr"] = self.learning_rate' in ppo.read_text('utf8')
 proof=dict(attempt_id='E0_PPO_INTERNAL_LR_SCALAR_GAP_REPAIRED_BEFORE_GO_V4_20261027',epoch=time.time(),
  source_original_LR=source_lr,V3_retained=dict(path=str(old),SHA=H(raw)),V4=dict(path=str(new),bytes=len(fixed),SHA=H(fixed)),
  only_replacement=dict(before=a.decode(),after=b.decode(),count=1),inverse_entire_V3_bytes_exact=True,AST_one_string_constant_only=changes,
  semantic_gap='PPO constructor sets self.learning_rate from CLI. PPO.load restores optimizer.param_groups but not internal scalar. Adaptive update writes paramgroups from scalar; V3 would silently start internal scalar1e-4 despite loaded optimizer LR. V4 constructs scalar from original recorded source LR.',
  cached_actual_installed_RSL_sources=dict(ppo=dict(path=str(ppo),SHA=H(ppo.read_bytes()),lines=[136,282,294,444,462]),runner=dict(path=str(runner),SHA=H(runner.read_bytes()),lines=[145,158,159,161])),
  no_PT_normalizer_checkpoint_model_GPU_or_SDK_read=True,no_remote_GO_or_ledger_IO=True,
  original_sourceCPU89C_workerV3_witness_retained=True,V4_actual_postcopy_small_source_delta_admission_required=True,
  Git_status='pending_ordinary_supplement_existing89trial_no_new_tag')
 p=HERE/'E0_WORKER_V4_LR_SCALAR_EXACT_SOURCE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(dict(V4=proof['V4'],source_LR=source_lr,only_one_CLI_literal_changed=True,other_bytes_exact=True)))
if __name__=='__main__':main()
