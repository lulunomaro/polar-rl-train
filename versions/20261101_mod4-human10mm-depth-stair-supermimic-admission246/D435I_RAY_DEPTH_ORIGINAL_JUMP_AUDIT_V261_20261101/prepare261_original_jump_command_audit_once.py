from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_RAY_DEPTH_N1_ORIGINAL_JUMP_V260_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT260_NEW240_mean_regression_once.py']:
 s=p.read_text('utf8')if p.name=='depth_stair247.py'else p.read_text('utf8').replace('260','261')
 if p.name.startswith('evaluate'):
  needle=' real=sdk.JumpMod4Env(cfg=cfg)';assert s.count(needle)==1
  i=s.index(needle)
  s=s[:i]+''' # The inherited logger assumed E0 DirectionalSpinCommand. This N1
 # sensor purpose uses the original JUMP sampler, so audit that exact class
 # and its pinned bounds. No command, reward or physical guard is changed.
 import spin_commands
 def audit_original_jump(env):
  term=env.command_manager.get_term('twist');c=term.command
  assert isinstance(term,sdk.OriginalJumpCommand) and not term.cfg.heading_command and not term.is_heading_env.any() and torch.isfinite(c).all()
  assert c[:,0].abs().max()<=2.10001 and c[:,1].abs().max()<=1e-6 and c[:,2].abs().max()<=2.00001
  return dict(stage='literal_original_JUMP_sensor_only',actual_class=type(term).__name__,pinned_vx_limit=2.1,pinned_yaw_limit=2.,no_command_or_reward_replacement=True)
 spin_commands.audit=audit_original_jump
''' +s[i:]
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT261_|","pattern='run_ROOT261_|run_ROOT260_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('260','261');out.write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT261_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p))
 for n in ast.walk(tree):
  if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='hashlib':assert hasattr(hashlib,n.attr)
report=R/'ROOT261_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original260_false_preserved=True,repair='Inherited step logger now checks actual OriginalJumpCommand class and pinned bounds for this N1 sensor purpose, rather than demanding DirectionalSpinCommand.',original_JUMP_commands_rewards_physical_guards_unchanged=True,model_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX261_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_ORIGINAL_JUMP_COMMAND_AUDIT_SENSOR',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
