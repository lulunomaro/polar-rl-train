"""Meaningful in-memory accounting test; no canonical file is read or copied."""
from pathlib import Path
import ast,hashlib,json,shutil,time,types,tarfile
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'train_payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=R/'INDEPENDENT_COHORT_SUM_ACTUAL_INTERVALS_IN_MEMORY_CPU_AND_PACKAGE.json';assert not p.exists();source=(D/'independent_expert_cohort_owner_node_v1.py').read_text(encoding='utf8');tree=ast.parse(source);owner=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='owner');fn=next(x for x in owner.body if isinstance(x,ast.FunctionDef) and x.name=='account');fn.body=[ast.Global(names=x.names) if isinstance(x,ast.Nonlocal) else x for x in fn.body];mock=object();now=[10.];ledger=[dict(active_segment=None,authorized_training_seconds=1188000,budget_extensions=[{} for _ in range(7)],remaining_training_seconds=1187900.,charged_training_seconds=100.,completed_segments=[])];go={'1':dict(learning_started_epoch=10.)}
 class Budget:
  def read_bytes(self):return json.dumps(ledger[0]).encode()
 budget=Budget()
 def put(path,value):assert path is budget;ledger[0]=json.loads(json.dumps(value))
 scope=dict(BUDGET=budget,charged=False,active=None,go=go,time=types.SimpleNamespace(time=lambda:now[0],time_ns=lambda:int(now[0]*1e9)),os=types.SimpleNamespace(getpid=lambda:444),put=put)
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<in-memory synthetic accounting fixture>','exec'),scope);f=scope['account'];f({'1':dict(returncode=None)});now[0]=20.;go['2']=dict(learning_started_epoch=20.);f({'1':dict(returncode=None),'2':dict(returncode=None)});now[0]=30.;rows={'1':dict(returncode=0,exit=dict(epoch=25.)),'2':dict(returncode=None)};f(rows);now[0]=40.;f(rows);now[0]=45.;go['0']=dict(learning_started_epoch=45.);f(rows);now[0]=65.;rows['0']=dict(returncode=0,exit=dict(epoch=60.));rows['2']=dict(returncode=0,exit=dict(epoch=55.));f(rows,end=True)
 result=ledger[0];assert result['active_segment'] is None and len(result['completed_segments'])==1 and abs(result['charged_training_seconds']-165)<1e-9;segment=result['completed_segments'][0];assert {k:v['charged_seconds'] for k,v in segment['experts'].items()}=={'1':15.,'2':35.,'0':15.};assert abs(result['charged_training_seconds']+result['remaining_training_seconds']-1188000)<1e-9
 for name in ('expert_independent_worker_v1.py','verify_independent_native_cpu_gate_v1.py','independent_expert_cohort_owner_node_v1.py'):
  data=(D/name).read_bytes();compile(data,name,'exec');shutil.copyfile(D/name,Q/name)
 (Q/'lib').mkdir();launcher=D.parent/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/payload/lib/zonglin2_app_launcher.py';shutil.copyfile(launcher,Q/'lib/zonglin2_app_launcher.py')
 manifest=dict(epoch=time.time(),rows=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]);(Q/'TRAIN_PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 archive=D/'THREE_INDEPENDENT_EXPERT_TASKS_NATIVE_THEN_BOUNDED_PPO_V1.tar.gz';assert not archive.exists()
 with tarfile.open(archive,'x:gz',compresslevel=1) as tf:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:tf.add(p,arcname=p.relative_to(Q).as_posix(),recursive=False)
 v=dict(epoch=time.time(),passed=True,in_memory_only_no_canonical_file_copy_or_write=True,synthetic_distinct_intervals_seconds={'1':15,'2':35,'0':15},synthetic_sum_charge65_wall50_no_duplicate_charge=True,one_active_one_completed_conservation_exact=True,package=dict(path=str(archive),bytes=archive.stat().st_size,SHA=H(archive)),manifest_SHA=H(Q/'TRAIN_PACKAGE_MANIFEST.json'),files=len(manifest['rows']),source_native_PPO_admission_still_actual_required=True);p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
