"""Build first Linux E2/E3 observational payloads from sealed source; no reward changes."""
from pathlib import Path
import ast,hashlib,json,time,shutil,sys,zipfile,traceback,os
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPECS={'E2':dict(original=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017/e2_closed112_frozen_prepared_v10/payload',manifest='E2_CLOSED112_FROZEN_COMPLETE_MANIFEST_V10.json',entry='retention_world_native_v8',guard='e2_closed112_source_guard_CPU_v1',validate='validate_E2_source'),'E3':dict(original=W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/e3_closed85_frozen_prepared_v1/payload',manifest='E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1.json',entry='e3_frozen_recovery_loop_v1',guard='recovery_closed85_source_guard_v1',validate='validate_E3_source')}
def main():
 import torch,importlib.util
 rng=torch.get_rng_state().clone();out=[]
 for kind,s in SPECS.items():
  original=s['original'];old=json.loads((original/s['manifest']).read_bytes());Q=B/(kind+'_linux_reward_frame_v1');Q.mkdir();shutil.copytree(original/'frozen_shared',Q/'frozen_shared',ignore=shutil.ignore_patterns('__pycache__'));(Q/'source').mkdir();src=original/old['source_relative'];dst=Q/old['source_relative'];shutil.copy2(src,dst);assert H(dst)==old['source']['SHA'];needed={s['entry'],s['guard'],'e2_frozen_prefix_guard_v4'};done=set()
  while needed-done:
   name=sorted(needed-done)[0];done.add(name);p=original/(name+'.py')
   if not p.is_file():continue
   tree=ast.parse(p.read_text('utf8'));shutil.copy2(p,Q/p.name)
   for node in ast.walk(tree):
    modules=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
    needed.update(n for n in modules if (original/(n+'.py')).is_file())
  for name in ('actual_reward_frame_observer_v1.py','linux_expert_frozen_reward_diagnostic_worker_v1.py','linux_expert_finite_observation_parent_v1.py'):shutil.copy2(B/name,Q/name)
  sp=importlib.util.spec_from_file_location(kind+'_actual_source_guard',Q/(s['guard']+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);ck=torch.load(dst,map_location='cpu',weights_only=False);getattr(m,s['validate'])(ck);del ck
  rows=[]
  for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  manifest=dict(version=1,expert=kind,source_SHA=old['source']['SHA'],source_relative=old['source_relative'],original_sealed_manifest=dict(path=str(original/s['manifest']),SHA=H(original/s['manifest'])),env=old['env'],files=rows,original_root_selected_modules_byteexact=sorted(n for n in done if (original/(n+'.py')).is_file()),only_new_wrapper_and_passive_reward_frame_observer=True,first_Linux_backend_case_not_replay_3060=True,steps=120,no_PPO=True)
  mf=Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));zp=B/(kind+'_linux_reward_frame_v1.zip')
  with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in Q.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(Q).as_posix())
  out.append(dict(expert=kind,payload=str(Q),manifest_SHA=H(mf),source_SHA=old['source']['SHA'],files=len(rows),package=dict(path=str(zp),bytes=zp.stat().st_size,SHA=H(zp)),worker_SHA=H(Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py')))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 with (R/'TWO_EXPERT_LINUX_REWARD_FRAME_SOURCE_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payloads=out,source_guards_actual_CPU_passed=True,selected_original_modules_byteexact=True,RNG_unchanged0CUDA0optimizer=True,no_target_dispatch_yet=True,no_reward_STD_LR_physics_threshold_change=True),f,indent=2)
 print(json.dumps(dict(prepared=[dict(expert=x['expert'],files=x['files'],zip_bytes=x['package']['bytes']) for x in out],CPU_source_passed=True,no_dispatch_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LINUX_EXPERT_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_or_GPU_or_budget_change=True),f,indent=2)
  raise
