from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,traceback
F=Path(__file__).resolve().parent;T=F.parent.parent;B=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/payloads_v4/seed27/source';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def method(path,name):
 tree=ast.parse(path.read_bytes());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='OwnFudanStepMdp');node=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='relative_features');node.name=name;return node
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();rng=torch.get_rng_state().clone()
 phase=module('native106_original_private_phase_source_only',B/'private_phase_frame_v1.py');contract=module('native106_original_dynamic_source_only',B/'static_dynamic_delay_contract_v1.py');ns=dict(torch=torch,decode_private_frame=phase.decode,task_relative_observation=contract.task_relative_observation)
 old=B/'native_fudan_step_adapter_candidate_v2.py';new=F/'native_fudan_step_adapter_candidate_v3_request_clock_aligned.py'
 for p,n in [(old,'old_features'),(new,'new_features')]:exec(compile(ast.fix_missing_locations(ast.Module(body=[method(p,n)],type_ignores=[])),str(p),'exec'),ns)
 ages=torch.arange(500,dtype=torch.long).expand(250,-1);ids=torch.arange(250,dtype=torch.long)[:,None].expand_as(ages);frames=phase.encode(ages,ids);state=(torch.zeros(250,500,3),)
 class Provider:
  def query(self,f):
   age=phase.decode(f)['public_age'];active=age>=200;v=torch.zeros(*f.shape,73);v[...,0]=active*.75;v[...,2]=.3824462629854679+active*.27;return v,torch.zeros_like(v)
 class Self:provider=Provider();step_edge_x_m=.35;platform_top_z_m=.27
 a=ns['old_features'](Self(),state,frames);b=ns['new_features'](Self(),state,frames);expected=((ages>=200)&(ages<500)).float()
 assert a.shape==b.shape==(250,500,7) and torch.equal(b[...,5],expected)
 assert torch.equal(a[...,:5],b[...,:5]) and torch.equal(a[...,6],b[...,6])
 mismatch=(a[...,5]!=expected);assert int(mismatch.sum())==250*380 and int(((a[...,5]==1)&(expected==0)).sum())==250*80 and int(((a[...,5]==0)&(expected==1)).sum())==250*300
 for age in (0,99,100,179,180,199,200,499):assert bool(b[0,age,5])==(200<=age<500)
 invalid_old_rejected=not torch.equal(a[...,5],expected);assert invalid_old_rejected
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed=True,scope='SOURCE-only exhaustive250private-delay by500actual-age grid, no model or SDK',old_helper_request_interval=[100,180],actual_declared_command_request_interval=[200,500],candidate_request_interval=[200,500],old_mismatches_per500ages=380,old_false_positive_per500=80,old_false_negative_per500=300,private_delay_variants=250,candidate_matches_every_grid_entry=True,other5spatial_and_age_features_literal_unchanged=True,old_wrong_clock_negative_rejected=True,RNG_literal_unchanged=True,old_source_SHA=H(old),new_source_SHA=H(new),saved_model_reads=0,policy_WM_critic_forward=False,SDK_CUDA_SSH=False,not_proven_learning_gain_or_unique_cause=True,requires_new_typed_contract_and_actual_target_admission=True)
 with (F/'reports/SOURCE_CPU_REQUEST_CLOCK_250x500_AND_UNCHANGED_FEATURES_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 (F/'HANDOFF.md').open('x',encoding='utf8').write('''Source-only observation-clock repair: existing Fudan physical request and task goal use actual ages200..499, while the inherited task-relative public_request bit used100..179. This exact source candidate replaces only that one of seven relative features; other spatial/time features, all networks/parameters/norms/optimizers/actions/physics/DR/queue/reset/reward/acceptance untouched. Exhaustive250private-delay by500age CPU grid passed, wrong clock negative rejected. New105 actual fixedcase supplies recorded500ages and380 mismatches; it also produced a short genuine lowclearance hop, not20/27cm success. This does NOT prove the clock was the unique cause or that the repair improves learning.
Selected native_fudan_step_adapter_candidate_v3_request_clock_aligned.py is FROZEN/SOURCE_ONLY/NOT_INSTALLED. Next stage requires typed qualified104 source contract and explicit changed-observation clock encoding, producer/source SDK/CPU binding, original allout/solewriter/source/physical resources and actual400/reset/100Hz admission before any new finite learning. Do not hotpatch103/104/105 or modify shared static_dynamic_delay_contract_v1 (other tasks keep their own contracts). Separate extension reward gate .0474 atgroundedzero_vz is a recorded candidate, not changed here. Models/norms/threeopts/normalRSL832460 must be preserved; exact source fullstate witness is already qualified104, never extra PTload for source/Git statistics. No new106payload/owner/GO/GPU learning yet.\n''')
 rows=[dict(path=str(p),relative=p.relative_to(F).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(F.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 with (F/'FROZEN_NATIVE106_REQUEST_CLOCK_SOURCE_AND_CPU_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(status='FROZEN_SOURCE_ONLY_NOT_INSTALLED',epoch=time.time(),files=rows),f,indent=2)
 print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (F/'reports'/('SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_or_remote=True),f,indent=2)
  raise
