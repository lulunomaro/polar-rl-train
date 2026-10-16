"""Source-bound frozen controller components, not a complete or dispatched3060 package."""
from pathlib import Path
import os,sys,ast,time,json,hashlib,importlib.util,traceback,math
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
F=Path(__file__).resolve().parent;W=F.parent;V=W/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017';S=W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/payload';O=F/'e2_closed109_frozen_components_v2';R=F/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();rng=torch.get_rng_state().clone();torch.set_num_threads(2);recipe=json.loads((V/'E2_CLOSED109_SIGNED4_WORLD_V0P5_FROZEN_RECIPE_CPU_V1.json').read_bytes());source=Path(recipe['source']['path']);assert H(source)==recipe['source']['SHA'];old=S/'s5_single_frozen35_v1.py';tree=ast.parse(old.read_text('utf8'));cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Single35');c=ast.get_source_segment(old.read_text('utf8'),cl)
 before="assert source.get('history_architecture',{}).get('variant','A0')=='A0' and source['E1_terrain_state']['num_envs']==20000";after="assert source.get('history_architecture',{}).get('variant','A0')=='A0';validate_E2_source(source)";assert c.count(before)==1;c=c.replace(before,after)
 out='''"""Frozen E2 closed109: one normal35 tick, actor9 only, whole6 clip and selected reset."""
from pathlib import Path
import hashlib,torch
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
from e2_closed109_source_guard_v1 import validate_E2_source
EXPECTED='bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
'''+c+'\n';ast.parse(out);p=O/'e2_closed109_single35_v2.py';p.write_text(out,encoding='utf8');guard=V/'e2_closed109_frozen35_source_adapter_v1.py';(O/'e2_closed109_source_guard_v1.py').write_bytes(guard.read_bytes());component=S/'hard_top1_frozen_expert_CPU_component_v1.py';(O/component.name).write_bytes(component.read_bytes())
 for method in ('begin','finish','exact'):
  oldm=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name==method);newcl=next(n for n in ast.parse(out).body if isinstance(n,ast.ClassDef));newm=next(n for n in newcl.body if isinstance(n,ast.FunctionDef) and n.name==method);assert ast.dump(oldm,include_attributes=False)==ast.dump(newm,include_attributes=False)
 adapter=S/'s5_retention_single_adapter_v1.py';at=adapter.read_text('utf8');assert at.count('from s5_single_frozen35_v1 import Single35,EXPECTED,sha')==1;at=at.replace('from s5_single_frozen35_v1 import Single35,EXPECTED,sha','from e2_closed109_single35_v2 import Single35,EXPECTED,sha').replace('S5_SINGLE_','E2_CLOSED109_SINGLE_').replace('only_single_W35_actor_executed','only_single_E2_closed109_actor_executed');ast.parse(at);(O/'e2_closed109_retention_single_adapter_v2.py').write_text(at,encoding='utf8')
 # Existing witness has an E1-only source check at finish and an ABC selector.
 # New isolated components bind real E2 metadata instead of fabricating E1 state.
 witness=S/'retention_native_witness_v8.py';wt=witness.read_text('utf8');assert wt.count("assert source['E1_terrain_state']['num_envs']==20000")==1;wt=wt.replace("assert source['E1_terrain_state']['num_envs']==20000","from e2_closed109_source_guard_v1 import validate_E2_source\n  validate_E2_source(source)")
 a="from s5_ABC_evaluation_adapter_v1 import build_frozen_ABC\n return build_frozen_ABC(vec,path,device)";b="from e2_closed109_retention_single_adapter_v2 import build_retention_single\n assert CONTEXT['router_mode']=='single_eval'\n return build_retention_single(vec,path,device)";assert wt.count(a)==1;wt=wt.replace(a,b);assert wt.count("DR_profile='nominal'")==1;wt=wt.replace("DR_profile='nominal'","DR_profile=self.args.dr_profile");ast.parse(wt);(O/'retention_native_witness_v8.py').write_text(wt,encoding='utf8')
 world=S/'retention_world_native_v8.py';w=world.read_text('utf8');oldgroups="[(1.0, 0.0), (-1.0, 0.0), (2.0, 0.0), (-2.0, 0.0), (2.0, math.pi / 2), (-2.0, math.pi / 2), (2.0, math.pi / 3), (-2.0, math.pi / 3)]";newgroups="[(4.0, 0.0), (-4.0, 0.0), (4.0, math.pi / 2), (-4.0, math.pi / 2), (4.0, math.pi / 3), (-4.0, math.pi / 3), (4.0, math.pi), (-4.0, math.pi)]";assert w.count(oldgroups)==1;w=w.replace(oldgroups,newgroups);ast.parse(w);(O/'retention_world_native_v8.py').write_text(w,encoding='utf8')
 sys.path.insert(0,str(O));sp=importlib.util.spec_from_file_location('actual_E2_closed109_single35_CPU',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);ctl=m.Single35(source,88,'cpu');assert ctl.exact();x=torch.zeros(88,35);x[:,28]=1;x[:,:22]=torch.sin(torch.arange(88*22,dtype=torch.float32).reshape(88,22))*.1;provider_calls=[0]
 def provider():provider_calls[0]+=1;return x
 first=ctl.begin(0,provider);assert ctl.begin(0,provider) is first and provider_calls[0]==1;actual=first['clipped_action'].clone();ended=torch.zeros(88,dtype=torch.bool);ended[[2,17,87]]=True;ctl.finish(actual,ended);expected=actual.clone();expected[ended]=0;assert torch.equal(ctl.last,expected)
 rejected=[]
 def bad(name,arr,tick):
  try:ctl.begin(tick,lambda:arr)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Bad interface accepted: '+name)
 x[:,22:28]=expected;wrong=x.clone();wrong[0,22]+=1;bad('previous_action_mismatch',wrong,1);wrong=x.clone();wrong[0,28:35]=torch.tensor([0.,1.,0.,0.,0.,0.,0.]);bad('non_normal35_mode',wrong,1);bad('skipped_tick',x,2);bad('wrong_34dim',x[:,:34],1);wrong=x.clone();wrong[0,0]=float('nan');bad('nonfinite_input',wrong,1)
 second=ctl.begin(1,provider);assert ctl.calls==2 and provider_calls[0]==2;ctl.finish(second['clipped_action'],torch.zeros(88,dtype=torch.bool));assert ctl.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 # Pure kinematic coverage is not a robot/Plane native test.
 t=torch.linspace(0,15,15001,dtype=torch.float64);analytic=[]
 for sign in (-1.,1.):
  yaw=sign*4.;along=.5*t+.5/(2*yaw)*torch.sin(2*yaw*t);cross=.5/(2*yaw)*(1-torch.cos(2*yaw*t));assert float(cross.abs().max())<=.125000000001;analytic.append(dict(signed_yaw=yaw,ideal_along15=float(along[-1]),ideal_cross_max=float(cross.abs().max()),ideal_total_turns=yaw*15/(2*math.pi)))
 runtime=S/'frozen_shared/runtime/isaac/mod4';task=runtime/'mod4_task.py';tt=ast.parse(task.read_text('utf8'));term=next(n for n in tt.body if isinstance(n,ast.ClassDef) and n.name=='TerminationsCfg');terms=ast.get_source_segment(task.read_text('utf8'),term);assert 'rough_route_boundary' not in terms;plane=runtime/'ground_plane_candidate.py';assert "plane.CreateAttribute('width',Sdf.ValueTypeNames.Double).Set(4000.)" in plane.read_text('utf8')
 files=[dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)) for q in O.iterdir() if q.is_file()];report=dict(epoch=time.time(),passed_source_controller_components_CPU_only=True,source=recipe['source'],components=files,old_sources=[dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)) for q in (old,adapter,witness,world,task,plane)],Single35_begin_finish_exact_AST_literal_unchanged=True,real_E2_guard_not_fake_E1_terrain=True,old_V_generic_frozen_adapter_prepared_not_executed_and_retained=True,one_actor9inclSTD_only_no_critic_optimizer_or_gate_loaded_by_controller=True,two_decision_ticks_once_each_selectedreset_rows_only_whole6clip6=True,all9_source_initial_final_literalexact=True,CPU_contract_rejected=rejected,CPU_RNG_unchanged0CUDA0optimizer=True,ideal_kinematic_only=analytic,authored_plane4000_source_base_termination_has_no_rough2m_only_CPU_not_actual_config=True,original_world_boolean_translation_gate_le0p12_for_moving_still_unchanged_diagnostic_only=True,originalquery1e6_COM1e5_mimic01_closure2mm_not_lowered=True,not_complete_target_package_not_native_not_GPU_not_dispatched=True,remaining=['Freeze full exact dependency/runtime/asset/source package and new recipe seed60928 profilewhite_v3 into isolated own3060 namespace; no installed changes.','Bind actual target SDK/DLL/source/sourceCPU/resource/MSVCRT and fresh unused leases/tasks; current desktop identity must be actual.','New worker must durably retain failed valid prefix and enforce mimic.01/nonfinite/missingcallbacks ownsave-stop; do not blindly dispatch old broad termination config or legacy skill booleans.','Actually native120 thenfull1500/6000callbacks and independent allraw action/35/query/contactCOMhardware including reasoncoverage and truncation.','Existing source-derived Plane/type/width and baseAST no2m are not actual authored USD/cookedShapeLocal/terrain query or15s survival.'],incidental_local_read_lookup_miss='An rg search used a Windows payload/* positional pattern and returned invalid path; independent literal payload directory reads succeeded. No runtime command or GPU involved.',all_old_sources_reports_and_booleans_preserved=True)
 with (R/'E2_CLOSED109_FROZEN_CONTROLLER_COMPONENTS_AND_ROUTE_SOURCE_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed_CPU_components=True,source_SHA=recipe['source']['SHA'],interface_negative_cases=len(rejected),GPU_dispatch=False,remaining=report['remaining'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_FROZEN_COMPONENTS_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_target_runtime_mutation=True),f,indent=2)
  raise
