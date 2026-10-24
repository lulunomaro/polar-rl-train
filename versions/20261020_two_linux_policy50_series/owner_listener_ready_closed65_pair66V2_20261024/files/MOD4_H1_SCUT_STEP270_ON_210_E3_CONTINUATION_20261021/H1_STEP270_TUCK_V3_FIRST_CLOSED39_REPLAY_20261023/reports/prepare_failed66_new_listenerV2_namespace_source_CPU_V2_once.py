from pathlib import Path
import ast,hashlib,json,shutil,time
O=Path(__file__).resolve().parent.parent;T=O.parent;P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=read(P/'reports/FAILED66_LISTENER_V2_NO_NODES_NO_GO_TWOHOST_ALL_OUT_ACTUAL.json');assert proof['passed'] and proof['no_actual_GO_or_fee'] and proof['canonical_unchanged_no_new_segment_or_charge']
assert not N.exists();scripts={}
names=('collect_selected_H1_final_unused_once.py','collect_selected_H1_first_PPO_unused_once.py','collect_selected_pair_finals_unused_once.py','collect_selected_pair_first_PPO_unused_once.py','deploy_selected_H1_only_unused_once.py','deploy_selected_pair_unused_once.py','prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py','read_E3_resource_only_after_actual_H1_closed_CPU_once.py','relocate_selected_H1_closed_forensics_unused_once.py','relocate_selected_pair_closed_forensics_unused_once.py','review_selected_H1_model_unused_once.py','review_selected_pair_models_unused_once.py')
for name in names:
 s=(P/name).read_text('utf8').replace('H1step270_reward_tuckclear4_2410v66','H1step270_reward_tuckclear4_2410v66listenerv2');ast.parse(s);scripts[name]=s
needle="with socket.create_connection(('10.24.4.210',29754),timeout=5):pass"
wait="while True:\n try:\n  with socket.create_connection(('10.24.4.210',29754),timeout=5):pass\n  break\n except ConnectionRefusedError:\n  assert time.monotonic()<until,'Own owner listener not ready within original20second readiness boundary'\n  time.sleep(.1)"
for name in ('deploy_selected_pair_unused_once.py','deploy_selected_H1_only_unused_once.py'):
 # Only the selected paired path changes. The unused H1-only alternative retains its existing implementation.
 if name!='deploy_selected_pair_unused_once.py':continue
 tree=ast.parse(scripts[name]);calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='code' and len(n.args)>2 and isinstance(n.args[2],ast.Constant) and isinstance(n.args[2].value,str) and needle in n.args[2].value];assert len(calls)==1
 oldcode=calls[0].args[2].value;newcode=oldcode.replace(needle,wait);ast.parse(newcode)
 # Replace the literal token by its AST source span, preserving every other deployed statement.
 literal=calls[0].args[2];lines=scripts[name].splitlines(keepends=True);assert literal.lineno==literal.end_lineno;i=literal.lineno-1;lines[i]=lines[i][:literal.col_offset]+repr(newcode)+lines[i][literal.end_col_offset:];scripts[name]=''.join(lines);ast.parse(scripts[name])
 class Clock:
  def __init__(self):self.now=0.
  def monotonic(self):return self.now
  def sleep(self,seconds):self.now+=seconds
 class Connection:
  def __enter__(self):return self
  def __exit__(self,*a):pass
 class Socket:
  def __init__(self,failures):self.failures=failures;self.calls=0
  def create_connection(self,*a,**kw):
   self.calls+=1
   if self.calls<=self.failures:raise ConnectionRefusedError('synthetic readiness window')
   return Connection()
 cases=[]
 for failures in (0,2,100000):
  clock=Clock();sock=Socket(failures);expired=False
  try:exec(wait,dict(socket=sock,time=clock,until=20))
  except AssertionError:expired=True
  assert expired==(failures==100000) and (sock.calls==failures+1 if not expired else clock.now>=20 and clock.now<20.2)
  cases.append(dict(synthetic_refusals=failures,calls=sock.calls,bounded_expiry=expired,passed=True))
N.mkdir();(N/'reports').mkdir()
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(P/folder,N/folder)
for name,s in scripts.items():(N/name).write_text(s,'utf8')
assert not any((N/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
report=dict(epoch=time.time(),passed_source_AST_and_three_synthetic_CPU_cases=True,original_failed_namespace=P.name,new_namespace=N.name,old_deployer_SHA=H(P/'deploy_selected_pair_unused_once.py'),new_deployer_SHA=H(N/'deploy_selected_pair_unused_once.py'),exact_old_remote_ready_code=oldcode,exact_new_remote_ready_code=newcode,only_paired_deployer_listener_refusal_wait_within_original20s=True,original_owner_accounting_and_nodes_unchanged=True,owner_identity_written_before_socket_bind_source_observed=True,actual_old_owner_expired_unregistered_no_GO_and_canonical_unchanged=True,old_error_reader_schema_correction_all_retained=True,CPU_cases=cases,no_network_policy_physics_GPU_or_training_execution=True,no_NEW_GO_or_budget_write_yet=True)
with (N/'reports/LISTENER_READY_RACE_SOURCE_AND_SYNTHETIC_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,new_namespace=N.name,CPU_cases=3,no_GO=True)))
