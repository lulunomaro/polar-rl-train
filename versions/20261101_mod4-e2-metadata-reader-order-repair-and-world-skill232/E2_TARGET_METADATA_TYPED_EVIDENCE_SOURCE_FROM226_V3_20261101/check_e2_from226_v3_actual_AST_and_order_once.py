"""New real-source AST and two tiny lexical examples only. No probe execution."""
from pathlib import Path
import ast,hashlib,json,time,traceback

N=Path(__file__).resolve().parent
T=N.parent


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def assignments(tree):
 return {n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)}
def nodes(tree,text):
 key=ast.dump(ast.parse(text,mode='eval').body,include_attributes=False)
 return [n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.dump(n,include_attributes=False)==key]
def order_assert(tree):
 selected=[n for n in ast.walk(tree) if isinstance(n,ast.Assert) and ast.unparse(n.test).startswith('len(hook) == len(invoke) == len(actor) == len(step) == 1')]
 assert len(selected)==1;return selected[0].test


def main():
 purpose=json.loads((N/'reports/CPU_V3_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/CPU_V3_ONCE_CONSUMED.json',dict(ID=purpose['ID'],epoch=time.time()))
 trees={};texts={}
 for row in purpose['sources']:
  b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA']
  name=Path(row['path']).name;trees[name]=ast.parse(b);texts[name]=b.decode('utf8')
 constants=assignments(trees['contract_e2_from226.py'])
 install=json.loads((N/'reports/INSTALL_SOURCE_V3.json').read_bytes())
 probe_name=install['selected_probe']['relative'];expected_name=install['selected_expected']['relative']
 assert hashlib.sha256((N/probe_name).read_bytes()).hexdigest()==constants['PROBE']
 expected_raw=(N/expected_name).read_bytes();expected=json.loads(expected_raw)
 assert hashlib.sha256(expected_raw).hexdigest()==constants['EXPECTED']
 assert expected['kind']==constants['KIND']==install['selected_KIND']
 for key in ('source_rows','installed_rows'):
  row=next(r for r in expected[key] if r['relative']==probe_name);assert row['SHA']==constants['PROBE']
 assert probe_name in expected['AST_selected_rows']
 worker_path=T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/source/evaluate_e2_world213.py'
 raw=worker_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==constants['WORKER']=='91f7e30febee3f4f8910cdedb4739d87f19b01c131f79d4396d335598b1ca6ab'
 worker=ast.parse(raw)
 calls=dict(hook=nodes(worker,'early.install(DirectionalSpinCommand,sensor_resume_contract,e2_command_checkpoint_v1)'),
  invoke=nodes(worker,"ns['main']()"),actor=nodes(worker,'runner.alg.actor(obs,stochastic_output=False)'),step=nodes(worker,'vec.step(action)'))
 positions={k:[dict(lineno=x.lineno,col_offset=x.col_offset,end_lineno=x.end_lineno,end_col_offset=x.end_col_offset) for x in v] for k,v in calls.items()}
 assert {k:len(v) for k,v in calls.items()}==dict(hook=1,invoke=1,actor=1,step=1)
 assert (calls['actor'][0].lineno,calls['actor'][0].col_offset)==(117,32)
 assert (calls['step'][0].lineno,calls['step'][0].col_offset)==(117,124)
 condition=order_assert(trees[probe_name]);code=compile(ast.Expression(condition),'<new V3 order>','eval')
 assert eval(code,{'len':len},calls) is True
 examples=[]
 for label,text,wanted in [('same_line_forward','action=runner.alg.actor(obs,stochastic_output=False);obs=vec.step(action)',True),
                            ('same_line_reverse','obs=vec.step(action);action=runner.alg.actor(obs,stochastic_output=False)',False)]:
  tree=ast.parse(text);test=dict(calls,actor=nodes(tree,'runner.alg.actor(obs,stochastic_output=False)'),step=nodes(tree,'vec.step(action)'))
  result=eval(code,{'len':len},test);assert result is wanted
  examples.append(dict(label=label,passed_new_order=result,expected=wanted,
   actor=[(x.lineno,x.col_offset) for x in test['actor']],step=[(x.lineno,x.col_offset) for x in test['step']]))
 runner=trees['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 child=[ast.literal_eval(n.value) for n in runner.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHILD_CODE' for t in n.targets)]
 assert len(child)==1;ast.parse(child[0])
 for tree in (runner,ast.parse(child[0])):
  for n in ast.walk(tree):
   if isinstance(n,ast.Call):
    name=n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else None
    assert name not in ('terminate','kill','send_signal','signal','killpg','pthread_kill','raise_signal')
 assert expected_name in texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py'] and expected_name in texts['finalize_e2_from226_actual_evidence_ROOT_ONLY.py']
 put(N/'reports/CPU_V3_ACTUAL213_AST_AND_LEXICAL_EXAMPLES_ACTUAL.json',dict(passed=True,ID=purpose['ID'],
  source_AST_count=len(trees),embedded_child_AST_count=1,actual_worker_SHA=constants['WORKER'],actual_call_counts={k:len(v) for k,v in calls.items()},
  actual_call_positions=positions,new_condition_accepts_actual_source=True,synthetic_lexical_examples=examples,
  selected_probe=install['selected_probe'],selected_expected=install['selected_expected'],selected_KIND=constants['KIND'],
  original_worker_modified=False,old_probe_or_fixture_replays=0,actual_probe_invocations=0,
  runner_or_embedded_child_signal_calls=0,model_asset_raw_Torch_SDK_GPU_network_Git_calls=0,
  actual_metadata_Task_E2_24s_case='PENDING_ROOT_NEW_PURPOSE'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/CPU_V3_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
