"""New one-read causal diagnostic: frozen source drives, final student shadows."""
from pathlib import Path
import ast, hashlib, json, shutil, time
O=Path(__file__).resolve().parent;T=O.parent
N=T/'FROZEN_SOURCE_COUNTERFACTUAL_V289_20261101';N.mkdir(exist_ok=False)
S=N/'source';shutil.copytree(O/'source',S,ignore=shutil.ignore_patterns('__pycache__'))
(N/'reports').mkdir()
for name in ('contract288.py','run288_eval_once.py'):
    text=(O/name).read_text('utf8').replace('288','289')
    if name.startswith('contract'):
        text=text.replace('FROZEN286_FINAL_DEPTH_HELDOUT270_AND_GROUND_EVAL289','FROZEN2135_SOURCE_COUNTERFACTUAL_FINAL286_SHADOW_EVAL289')
    (N/name.replace('288','289')).write_text(text,encoding='utf8')
text=(S/'evaluate288.py').read_text('utf8').replace('288','289')
begin=text.index(" weights={k.removeprefix")
end=text.index(" put('ACTUAL289_FINAL286_ACTOR_ONE_READ.json'",begin)
text=text[:begin]+''' student_weights={k.removeprefix('mlp.'):v for k,v in ck['student']['actor_state_dict'].items()if k.startswith('mlp.')}
 teacher_weights={k.removeprefix('mlp.'):v for k,v in ck['teacher_full_PPO_state']['actor_state_dict'].items()if k.startswith('mlp.')}
 def make_actor(width,weights):
  net=torch.nn.Sequential(torch.nn.Linear(width,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(real.device)
  net.load_state_dict(weights,strict=True);net.eval()
  for parameter in net.parameters():parameter.requires_grad_(False)
  return net
 actor=make_actor(35,teacher_weights);shadow=make_actor(44,student_weights);weights=teacher_weights
 del ck
 shadow_overflow=torch.zeros(80,6,dtype=torch.long,device=real.device);shadow_mse=torch.zeros(80,device=real.device);first_paired_actions=None
'''+text[end:]
text=text.replace("  with torch.inference_mode():action=actor(x)","""  with torch.inference_mode():action=actor(obs['policy']);shadow_action=shadow(x)
  if first_paired_actions is None:first_paired_actions=dict(source=action.cpu().tolist(),student=shadow_action.cpu().tolist(),policy35=obs['policy'].cpu().tolist(),depth9=d.cpu().tolist())
  shadow_overflow.add_((shadow_action.abs()>6)&active[:,None]);shadow_mse.add_(torch.where(active,(shadow_action-action).square().mean(-1),0.))""")
text=text.replace('seconds=(int(counts[i])+1)*.02','seconds=int(counts[i])*.02')
text=text.replace("action6=np.stack", "action6=np.stack")
text=text.replace("results=results,replay=replay,optimizer_steps=0", "results=results,replay=replay,first_paired_actions=first_paired_actions,shadow_overflow=shadow_overflow.cpu().tolist(),shadow_MSE=(shadow_mse/counts.clamp_min(1)).cpu().tolist(),physical_actor='frozen2135 original35',shadow_actor='final286 student44',optimizer_steps=0")
ast.parse(text);(S/'evaluate289.py').write_text(text,encoding='utf8')
contract=(N/'contract289.py').read_bytes();(S/'contract289.py').write_bytes(contract)
task=json.loads((O/'TASK288_FROZEN.json').read_bytes());task['kind']='FROZEN2135_SOURCE_COUNTERFACTUAL_FINAL286_SHADOW_EVAL289'
task['worker_SHA']=hashlib.sha256(text.encode()).hexdigest()
task.update(purpose='Same9137 source physical actor versus final student shadow; diagnose collapse before repair. Separate necessary model read.',physical_actor_obs=35,shadow_actor_obs=44)
(N/'TASK289_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for p in S.rglob('*.py'):ast.parse(p.read_text('utf8'))
(N/'reports/SOURCE289_PROTOCOL.json').write_text(json.dumps(dict(epoch=time.time(),passed_AST=True,source=str(O),physical='source2135',shadow='final286',same_seed9137=True,model_reads_max=1,optimizer_steps=0,account_writes=0,old_once_replayed=False,terminal_seconds_off_by_one_fixed_in_new_source_only=True),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,directory=str(N),worker_SHA=task['worker_SHA'])))
