"""CPU-only construction: original D7 three-skill probes, no launch or transport."""
from pathlib import Path
import ast, hashlib, json, shutil, time, traceback
D=Path(__file__).resolve().parent;W=D.parent;P=D/'payload';R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not (R/'CPU_PORT_PREPARED.json').exists()
 P.mkdir(exist_ok=True);R.mkdir(exist_ok=True)
 shared=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
 source={
  'flat':W/'MOD4_D7_RESET_PERFORMANCE_REVIEW_20261009/baseline/frozen_history_flat.py',
  'spin':W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/eval4090_original_runtime_source/runtime/isaac/mod4/frozen_history_spin.py',
  'world':W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/eval4090_original_runtime_source/runtime/isaac/mod4/frozen_history_world.py'}
 original=P/'original';original.mkdir(exist_ok=True)
 class NativeRead(ast.NodeTransformer):
  def visit_Attribute(self,n):
   text=ast.unparse(n)
   if text.endswith('.torch') and (text.startswith('robot.data.') or text.startswith('r.data.')):
    return self.visit(n.value)
   n=self.generic_visit(n)
   if isinstance(n.ctx,ast.Load) and isinstance(n.value,ast.Attribute) and n.value.attr=='data':
    base=ast.unparse(n.value.value)
    if base in ('robot','r') or base.startswith('env.scene.sensors['):
     return ast.Call(func=ast.Name(id='tensor',ctx=ast.Load()),args=[n],keywords=[])
   return n
  def visit_Call(self,n):
   n=self.generic_visit(n)
   if isinstance(n.func,ast.Name) and n.func.id=='Mod4Env':
    return ast.Call(func=ast.Name(id='create_observed_env',ctx=ast.Load()),args=[ast.Name(id='args',ctx=ast.Load())],keywords=n.keywords)
   if isinstance(n.func,ast.Name) and n.func.id=='build_frozen_policy':n.func.id='build_observed_frozen_policy'
   if ast.unparse(n.func)=='env.close':
    return ast.Call(func=ast.Name(id='finalize_observer',ctx=ast.Load()),args=[ast.Name(id='env',ctx=ast.Load()),ast.Name(id='result',ctx=ast.Load())],keywords=[])
   return n
 origins=[]
 for kind,path in source.items():
  old=original/(kind+'_original.py');assert not old.exists();shutil.copy2(path,old)
  module=ast.parse(path.read_text(encoding='utf8'))
  fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='main')
  main_before=ast.dump(fn,include_attributes=False)
  fn=NativeRead().visit(fn);fn.name='run_'+kind
  fn.args.args=[ast.arg(arg='args')]
  fn.body.append(ast.Return(value=ast.Name(id='result',ctx=ast.Load())))
  # Only explicit device/capacity metadata for this small frozen evaluation.
  config=ast.parse("cfg.sim.device=args.device\nfor key,value in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,key,value)").body
  idx=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and ast.unparse(t)=='cfg.scene.num_envs' for t in n.targets))
  fn.body[idx+1:idx+1]=config
  header='''from pathlib import Path
import json,os,time,math,numpy as np,torch
import mod4_task as task
from spin_commands import audit
from nominal_parameter_audit import parameter_audit
from contact_geometry import ControlGeometry
from actuator_clip_diagnostics import rating_clipped
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from retention_native_witness_v1 import tensor,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY
'''
  out=P/('retention_'+kind+'_native_v1.py');assert not out.exists()
  body=ast.unparse(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])))
  text=header+'\n'+body+'\n';compile(text,str(out),'exec');out.write_text(text,encoding='utf8',newline='\n')
  # Original numeric old-gate expressions must be text-identical after AST formatting.
  assignments={ast.unparse(n.targets[0]):ast.dump(n.value,include_attributes=False) for n in ast.walk(next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='main')) if isinstance(n,ast.Assign) and len(n.targets)==1 and ast.unparse(n.targets[0]) in ('common','strict','strict_integrated','skill','skill_legacy_reference','physical')}
  adapted={ast.unparse(n.targets[0]):ast.dump(n.value,include_attributes=False) for n in ast.walk(fn) if isinstance(n,ast.Assign) and len(n.targets)==1 and ast.unparse(n.targets[0]) in assignments}
  assert assignments==adapted,(kind,'original numeric gate AST changed')
  origins.append(dict(kind=kind,source=str(path),original_copy=str(old),source_sha256=H(path),port=str(out),port_sha256=H(out),all_original_numeric_gate_AST_exact=True,main_origin_AST_sha256=hashlib.sha256(main_before.encode()).hexdigest()))
 contracts=P/'cpu_contracts';contracts.mkdir(exist_ok=True)
 for name in ('scut_curriculum_gate_v4.py','world_progress_contract.py'):
  src=W/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'/name;dst=contracts/name;assert not dst.exists();shutil.copy2(src,dst)
 for name in ('world_cycle_metrics.py','physics_clock.py'):
  src=shared/'runtime/isaac/mod4'/name;dst=contracts/name;assert not dst.exists();shutil.copy2(src,dst)
 for src in (P/'original').glob('*.py'):compile(src.read_text(encoding='utf8'),str(src),'exec')
 sources={
  'baseline1aa':dict(local_path=str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/ORIGINAL_LINUX20K_OWN_ACTIVE_SAVE/model_32447.pt'),sha256='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'),
  'left_repair2b':dict(local_path=str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'),sha256='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971')}
 for row in sources.values():assert H(row['local_path'])==row['sha256'];row['bytes']=Path(row['local_path']).stat().st_size
 templates=json.loads((W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/reports/WAVE50_FOUR_CASE_TEMPLATES.json').read_bytes())['jobs'][1:]
 assert [(x['kind'],x['num_envs'],x['steps'],x['seed']) for x in templates]==[('flat',80,1500,20261002),('spin',88,1500,20261002),('world',88,1500,20261002)]
 files=[]
 for q in sorted(shared.rglob('*')):
  if q.is_file() and (q.suffix in ('.py','.json','.usd') or q.name=='MOD4_RESET_COLLISION_BANK.npz'):
   files.append(dict(relative=q.relative_to(shared).as_posix(),local_source=str(q),bytes=q.stat().st_size,sha256=H(q)))
 report=dict(epoch=time.time(),trial_id='LEFT_REPAIR_RETENTION_THREE_NATIVE_CPU_PORT_20261014',status='CPU_PREPARED_ONLY',approved_GPU=False,no_SSH_or_GPU_or_PPO=True,source_fullstate_not_restored=True,only_actor_loaded=True,original_source_N=20000,seed=20261002,discarded_seed20260928_instruction_corrected_before_any_file_generation=True,
  sources=sources,origins=origins,shared_payload_local=str(shared),shared_payload_target='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload',shared_source_freeze=files,
  cases=[dict(kind=x['kind'],num_envs=x['num_envs'],steps=1500,seed=20261002,dr_profile='white_v3',max_rate=4*3.141592653589793,speed_limit=1.5,ramp_suite=x['kind']=='flat',contact_readback=x['kind']!='flat',original_template=x) for x in templates],
  fixed=dict(physics_dt_s=.0025,control_dt_s=.01,TGS_position=32,TGS_velocity=4,actor35=35,critic38=38,actions=6,clip6=True,callbacks_full=6000),original_legacy_booleans_retained=True,fullsignedcircle_and_whole_prefix_required=True,new_backend_pass_not_claimed=True,pending=['actual3060 SDK native per case','actual own frozen1500 fullraw/queries/contact/COM/hardware','actual matched baseline1aa vs own2b complete review','root Git archive'])
 (P/'RETENTION_CPU_MANIFEST.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 (R/'CPU_PORT_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(status=report['status'],origins=origins,cases=[{k:x[k] for k in ('kind','num_envs','steps','seed')} for x in report['cases']]),ensure_ascii=False))

if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);q=R/('CPU_PORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');q.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_no_SSH=True),indent=2),encoding='utf8');raise
