"""Source-specific frozen evaluation call guard, not a universal Python sandbox."""
import ast
DECLARED_ENV_CALL="env.update(RM_MOD4_USD=str(job / 'runtime/assets/robot.usd'), RM_RESCUE_STOP_FILE=str(OUT / 'STOP.json'), RM_RESCUE_DEADLINE=str(deadline))"
ALLOWED_ENV_COMMIT='os.environ.update(env)'
ALLOWED_ORIGINAL_VEC_STEP='vec.step(action)'
def node_key(node):return ast.dump(node,include_attributes=False)
def call_node(source):return ast.parse(source,mode='eval').body
def validate_frozen_worker_calls(tree):
 expected={node_key(call_node(DECLARED_ENV_CALL)):'declared_env_dictionary',node_key(call_node(ALLOWED_ENV_COMMIT)):'environment_commit',node_key(call_node(ALLOWED_ORIGINAL_VEC_STEP)):'original_vec_step'}
 seen={name:0 for name in expected.values()};rejected=('learn','backward','update','step','train','zero_grad')
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call):continue
  name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else None
  if name not in rejected:continue
  key=node_key(node)
  assert key in expected,'Frozen evaluator forbids state-changing call: '+ast.unparse(node)
  seen[expected[key]]+=1
 assert seen=={'declared_env_dictionary':1,'environment_commit':1,'original_vec_step':1},'Exact declaration/commit/original-step source changed or duplicated'
 return dict(passed=True,exact_allowed_source_calls=seen,all_other_learn_backward_update_step_train_zero_grad_calls_forbidden=True,source_specific_AST_guard_not_universal_dynamic_code_sandbox=True)
