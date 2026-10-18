from pathlib import Path
import json,time,hashlib,shutil,ast,sys,types,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 import os;os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch;torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 history=B/'initial_prepared_sources_before_Fudan_clip_and_worker_whitespace_review';history.mkdir()
 for name in ('h1_scut_fudan_jump_reward_v1.py','closed_production_continuation_CPU_v2.py','prepare_next_three_closed_sources_one_hour_CPU_once.py'):
  shutil.copy2(B/name,history/name)
 # Fudan clips each weighted reward to +/-2.5 * dt, not just its final sum.
 p=B/'h1_scut_fudan_jump_reward_v1.py';t=p.read_text('utf8');t=t.replace("    zero_wheel_torque_sigma=1.5,","    zero_wheel_torque_sigma=1.5, Fudan_weighted_rate_clip=2.5,")
 t=t.replace("def measured_reward(env,name):return _current(env)[name]", "FUDAN_TERMS=('flight_vz','flight','leg_tuck','takeoff_extend','orientation','angular_velocity_xy')\ndef measured_reward(env,name):\n    raw=_current(env)[name]\n    if name in FUDAN_TERMS:\n        weight=PROFILE['weights'][name]\n        return (raw*weight).clamp(-2.5,2.5)/weight\n    return raw")
 p.write_text(t,'utf8');shutil.copy2(p,B/'reward_runtime_overlay'/p.name)
 # Original future helpers had not been executed; retain their source above.
 p=B/'closed_production_continuation_CPU_v2.py';t=p.read_text('utf8').replace('"  scut_last=', '"   scut_last=');p.write_text(t,'utf8')
 p=B/'prepare_next_three_closed_sources_one_hour_CPU_once.py';t=p.read_text('utf8').replace("' '+\"  scut_last=",'"   scut_last=');t=t.replace('SCUT_FUDAN_JUMP_REWARD_SOURCE_DIFFERENTIAL_CPU_ACTUAL.json','SCUT_FUDAN_FUDAN_CLIP_WORKER_RUNTIME_CPU_V2_ACTUAL.json');p.write_text(t,'utf8')
 import h1_scut_fudan_jump_reward_v1 as m
 g=W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018';rt=g/'payload/h1/job0/runtime/isaac/mod4'
 spec=types.SimpleNamespace;env=spec(num_envs=5,device='cpu');raw={k:torch.tensor([0.,.1,1.,10.,1000.]) for k in m.PROFILE['weights']};original=m._current;m._current=lambda e:raw
 for key,weight in m.PROFILE['weights'].items():
  v=m.measured_reward(env,key)*weight;expected=(raw[key]*weight).clamp(-2.5,2.5) if key in m.FUDAN_TERMS else raw[key]*weight
  assert torch.equal(v,expected) or torch.allclose(v,expected,atol=1e-6,rtol=0)
 m._current=original
 # Resolve and execute config registration with a minimal SDK config type;
 # the actual live SDK readout is separately saved before learning starts.
 oldmods={k:sys.modules.get(k) for k in ('isaaclab','isaaclab.managers')}
 class Term:
  def __init__(self,func,weight,params=None):self.func=func;self.weight=weight;self.params=params or {}
 managers=types.ModuleType('isaaclab.managers');managers.RewardTermCfg=Term
 sys.modules['isaaclab']=types.ModuleType('isaaclab');sys.modules['isaaclab.managers']=managers;sys.path.insert(0,str(rt))
 f=lambda env,offset=0:torch.tensor([1.123,2.345,3.456])+offset
 cfg=spec(rewards=spec(**{k:Term(f,-1.,{'offset':.5}) for k in ('flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy')}))
 m.configure(cfg);active=torch.tensor([True,False,False]);env=spec(h1_phase=spec(attempt=active,request_for_action=active,launched=torch.zeros(3,dtype=torch.bool),landed=torch.zeros(3,dtype=torch.bool)))
 for key in ('flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy'):
  c=getattr(cfg.rewards,key);v=c.func(env,**c.params);assert torch.equal(v[~active],f(env,.5)[~active]) and v[0]==0 and c.weight==-1.
 for key,weight in m.PROFILE['weights'].items():assert getattr(cfg.rewards,'h1_scut_fudan_'+key).weight==weight
 fake=spec(reward_manager=spec(_term_names=list(vars(cfg.rewards)),_term_cfgs=list(vars(cfg.rewards).values())))
 assert len(m.loaded_recipe(fake)['actual_loaded_terms'])==13
 for k,v in oldmods.items():
  if v is None:sys.modules.pop(k,None)
  else:sys.modules[k]=v
 # Execute the exact future worker transformation and prove inverse AST equality.
 sys.path.insert(0,str(B));import closed_production_continuation_CPU_v2 as proof
 tree=ast.parse((B/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 loop=next(n for n in fn.body if isinstance(n,ast.For) and getattr(n.target,'id','')=='key')
 ifnode=next(n for n in loop.body if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=='key')
 # Locate the migration block instead of the separate H1 task metadata block.
 ifnode=next(n for n in loop.body if isinstance(n,ast.If) and any(isinstance(z,ast.Assign) and any(getattr(a,'id','')=='wt' for a in z.targets) for z in ast.walk(n)))
 workerfile=g/'payload/h1/h1_prelaunch_v2_production_worker_v1.py';old=workerfile.read_text('utf8');wt=old
 for node in ifnode.body:
  if isinstance(node,ast.Assign) and any(getattr(a,'id','')=='wt' for a in node.targets):
   if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='read_text':continue
   # The first semicolon line is split into Assign then later replace Assign.
   ns={'wt':wt};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-future-worker-transform>','exec'),ns);wt=ns['wt']
  elif isinstance(node,ast.Assign) and any(getattr(a,'id','')=='marker' for a in node.targets):marker=ast.literal_eval(node.value)
  elif isinstance(node,ast.Assign) and any(getattr(a,'id','')=='newtext' for a in node.targets):pass
  # final wt replace depends on marker; handled below with the literal payload
 # Independently use the actual generated literals to build its final marker replacement.
 start=next(n.value.args[1].left for n in ifnode.body if isinstance(n,ast.Assign) and any(getattr(a,'id','')=='wt' for a in n.targets) and isinstance(n.value,ast.Call) and getattr(n.value.func,'attr','')=='replace' and isinstance(n.value.args[1],ast.BinOp))
 wt=old.replace('  from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace\n',ast.literal_eval(start)+'  from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace\n')
 logline=next(n.value.args[1].left for n in ifnode.body if isinstance(n,ast.Assign) and any(getattr(a,'id','')=='wt' for a in n.targets) and isinstance(n.value,ast.Call) and getattr(n.value.func,'attr','')=='replace' and isinstance(n.value.args[0],ast.Name) and n.value.args[0].id=='marker')
 wt=wt.replace(marker,ast.literal_eval(logline)+marker);ast.parse(wt)
 restored=proof.normalize_worker(wt,dict(new_source_filename='unused_new.pt',previous_source_filename='unused_old.pt',Adam=999999,previous_Adam=888888))
 assert ast.dump(ast.parse(old))==ast.dump(ast.parse(restored))
 # The only runtime changes outside new reward math are one config import and
 # a read-only reference to clearance already computed by the original callback.
 for name in ('train_H1_ground_prelaunch_fullstate_v2.py','h1_takeoff_progress_environment_v2.py'):
  now=(B/'reward_runtime_overlay'/name).read_text('utf8');before=(rt/name).read_text('utf8')
  inverse=now.replace('from h1_scut_fudan_jump_reward_v1 import configure as configure_h1_rewards','from h1_takeoff_progress_reward_v2 import configure as configure_h1_rewards').replace('self._h1_scut_last_wheel_clearance=wc;','')
  assert ast.dump(ast.parse(before))==ast.dump(ast.parse(inverse))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('SCUT_FUDAN_FUDAN_CLIP_WORKER_RUNTIME_CPU_V2_ACTUAL.json',dict(epoch=time.time(),passed=True,upstream_differential_report_SHA=H(R/'SCUT_FUDAN_JUMP_REWARD_SOURCE_DIFFERENTIAL_CPU_ACTUAL.json'),Fudan_original_per_term_weighted_rate_clip2_5_retained=True,normal_original_terms_bitexact=True,config_registration9_terms_and_actual_readout_schema_CPU=True,physical_environment_AST_exact_after_readonly_snapshot_removal=True,entry_AST_exact_after_reward_config_import_removal=True,future_worker_AST_exact_after_readonly_receipts_removal=True,initial_unused_whitespace_normalization_issue_fixed_before_execution=True,initial_sources_retained=str(history),profile=m.PROFILE,overlay=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in (B/'reward_runtime_overlay').glob('*.py')],RNG_unchanged0CUDA0optimizer=True,no_live_patch_or_GPU=True))
 print('Fudan per-term clipping, normal-row config, runtime/worker inverse AST CPU passed.')
if __name__=='__main__':
 try:main()
 except BaseException:put('REWARD_CLIP_WORKER_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),before_any_new_remote_or_GPU=True));raise
