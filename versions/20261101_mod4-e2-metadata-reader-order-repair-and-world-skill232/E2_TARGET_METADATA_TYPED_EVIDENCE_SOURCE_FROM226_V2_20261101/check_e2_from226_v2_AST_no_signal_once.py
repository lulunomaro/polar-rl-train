"""New V2 static check only. No child,old fixture,SDK or actual timeout case."""
from pathlib import Path
import ast,hashlib,json,time,traceback

N=Path(__file__).resolve().parent
V1=N.parent/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V1_20261101'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 purpose=json.loads((N/'reports/CPU_V2_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/CPU_V2_ONCE_CONSUMED.json',dict(ID=purpose['ID'],epoch=time.time()))
 trees={};texts={}
 for row in purpose['sources']:
  b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA']
  name=Path(row['path']).name;trees[name]=ast.parse(b);texts[name]=b.decode('utf8')
 runner=trees['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 forbidden=[]
 for node in ast.walk(runner):
  if isinstance(node,ast.Call):
   name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else None
   if name in ('terminate','kill','send_signal','signal','killpg','pthread_kill','raise_signal'):forbidden.append(name)
 assert forbidden==[]
 child=[ast.literal_eval(n.value) for n in runner.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHILD_CODE' for t in n.targets)]
 assert len(child)==1;child_tree=ast.parse(child[0])
 for node in ast.walk(child_tree):
  if isinstance(node,ast.Call):
   name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else None
   assert name not in ('terminate','kill','send_signal','signal','killpg','pthread_kill','raise_signal')
 timeout=[n for n in ast.walk(runner) if isinstance(n,ast.ExceptHandler) and isinstance(n.type,ast.Attribute) and n.type.attr=='TimeoutExpired']
 assert len(timeout)==1
 calls=[n for n in ast.walk(timeout[0]) if isinstance(n,ast.Call)]
 assert any(isinstance(n.func,ast.Attribute) and n.func.attr=='communicate' and not n.args and not n.keywords for n in calls)
 assert 'actual_waited=False,all_own_children_waited=False' in texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 assert 'FREE_or_EX_release_claimed=False' in texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 assert 'and not timed_out' in texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 for name in ('contract_e2_from226.py','finalize_e2_from226_actual_evidence_ROOT_ONLY.py'):
  assert (N/name).read_bytes()==(V1/name).read_bytes()
 assert "if child is not None:child.wait()" in texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 put(N/'reports/CPU_V2_SOURCE_AST_NO_SIGNAL_ACTUAL.json',dict(passed=True,ID=purpose['ID'],
  source_AST_count=len(trees),embedded_child_AST_count=1,runner_signal_call_count=0,embedded_child_signal_call_count=0,
  timeout_original_false_before_continued_communicate_wait=True,FREE_before_actual_wait_claimed=False,
  timeout_never_promoted_to_pass=True,contract_finalizer_byte_identical=True,
  actual_child_or_probe_invocations=0,old_fixture_replays=0,
  model_asset_raw_Torch_SDK_GPU_network_Git_calls=0,actual_E2_24s_skill='PENDING_ROOT'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/CPU_V2_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
