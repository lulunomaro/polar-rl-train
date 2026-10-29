"""Execute only target CPU's actual guard statements on fresh source AST."""
from pathlib import Path
import ast,hashlib,json,sys
from e2_frozen_worker_call_guard_v3 import validate_frozen_worker_calls,DECLARED_ENV_CALL
B=Path(__file__).resolve().parent
def main():
 worker=B/'evaluate_E2_adapted93_new86_frozen900_once_v1.py';raw=worker.read_bytes();tree=ast.parse(raw);cpu=ast.parse((B/'E2_new86_target_source_SDK_metadata_admission_v1.py').read_bytes());main=next(n for n in cpu.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 actual=[]
 for n in main.body:
  if isinstance(n,ast.ImportFrom) and n.module=='e2_frozen_worker_call_guard_v3':actual.append(n)
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='guard' for t in n.targets):actual.append(n)
 assert len(actual)==2;scope=dict(tree=tree);exec(compile(ast.Module(body=actual,type_ignores=[]),'<actual new target CPU AST statements only>','exec'),scope);assert scope['guard']['passed'];checks=['actual target CPU guard statements accept exact selected worker AST']
 old_predicate=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('learn','backward','update') for n in ast.walk(tree));assert old_predicate;checks.append('old blanket predicate reproduces exact legitimate update false')
 negatives=['runner.alg.update()','runner.alg.optimizer.step()','optimizer.step()','actor.train()','actor.train(False)','loss.backward()','runner.learn(1)','normalizer.update(obs)','os.environ.update({"x":1})','env.update(RM_JUMP_SCRIPT_PROB="1")','env.update(**more)','vec.step(other_action)','update()','optimizer.zero_grad()',DECLARED_ENV_CALL]
 rejected=[]
 for source in negatives:
  trial=ast.parse(raw);trial.body.extend(ast.parse(source).body)
  try:validate_frozen_worker_calls(trial)
  except AssertionError:rejected.append(source)
  else:raise AssertionError('Forbidden/duplicated call accepted: '+source)
 assert len(rejected)==len(negatives);checks.append('fifteen learner/backward/update/step/train/mutation/duplicate negatives rejected')
 assert scope['guard']['exact_allowed_source_calls']=={'declared_env_dictionary':1,'environment_commit':1,'original_vec_step':1}
 old=B.parent/'E2_93_NEW86_FROZEN_PROFILE_DOMAIN_PATH_REPAIR_SOURCE_20261029_V2';assert raw==(old/worker.name).read_bytes();checks.append('selected worker exact bytes unchanged versus actual failed V2')
 for name in ('e2_profile_domain_telemetry_v1.py','lossless_snapshot_pinned75d683.py','e2_original_profile_catalog_candidate_v1.py','detached_E2_new86_frozen_profile_supervisor_once_v1.py','project_clone_launch_helpers_v1.py'):assert (B/name).read_bytes()==(old/name).read_bytes()
 checks.append('metric/queue-related hooks/supervisor/clone environment exact unchanged bytes')
 parsed=[]
 for p in B.glob('*.py'):ast.parse(p.read_bytes());parsed.append(p.name)
 for n in ('E2_frozen_actual_receipts_readonly_CODE_v3.py',):
  code=next(ast.literal_eval(x.value) for x in ast.parse((B/n).read_bytes()).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in x.targets));ast.parse(code)
 checks.append('all selected sources and embedded readonly CODE AST passed')
 with (B/'reports/V3_ACTUAL_TARGET_CPU_GUARD_SELECTED_SOURCE_POSITIVE_NEGATIVE_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,checks=checks,negative_cases_rejected=rejected,selected_worker_SHA=hashlib.sha256(raw).hexdigest(),actual_target_CPU_guard_AST=ast.dump(ast.Module(body=actual,type_ignores=[]),include_attributes=False),allowed=scope['guard'],parsed=parsed,no_PT_raw_binary_model_SDK_GPU_remote_or_credentials=True),f,indent=2)
 print(json.dumps(dict(passed=True,negative_cases=len(rejected),actual_target_CPU_section_executed_locally_on_source_AST=True)))
if __name__=='__main__':main()
