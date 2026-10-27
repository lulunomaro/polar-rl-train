"""Bounded source, closing-metadata and process-out mocks. No network/models."""
from pathlib import Path
import ast,copy,hashlib,json,sys,tempfile,types
from unittest import mock
D=Path(__file__).resolve().parent;O=D.parent/'native87_available_two_r3_source';T=D.parent.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
sys.path[:0]=[str(D),str(N/('controllers_r4' if (N/'controllers_r4').is_dir() else 'controllers_r3'))]
import native87_available_two_activation_support_v1 as candidate
from native87R4_target_readonly_observer_v1 import observe_target_readonly
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def refuse(fn,name):
 try:fn()
 except (AssertionError,ValueError,KeyError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance '+name)
previous_path=N/'reports'/candidate.PREVIOUS_R3_REPORT;previous=json.loads(previous_path.read_bytes());SHA=hashlib.sha256(previous_path.read_bytes()).hexdigest()
q=dict(launch_remaining_snapshot=576916.5355293751,previousR3costreportSHA=SHA)
yes(candidate.validate_launch_closed_receipt(q,previous,SHA),'actual_saved_R3_failed_GO_allout_original_cost_receipt_bound')
bad=dict(q,launch_remaining_snapshot=577055.9868602753);refuse(lambda:candidate.validate_launch_closed_receipt(bad,previous,SHA),'old_balance_not_current_launch_snapshot')
refuse(lambda:candidate.validate_launch_closed_receipt(q,previous,'a'*64),'wrong_previous_cost_report_SHA_refused')
bad=copy.deepcopy(previous);bad['native_FINAL_present']=True;refuse(lambda:candidate.validate_launch_closed_receipt(q,bad,SHA),'failed_R3_not_reclassified_qualified_FINAL')
bad=copy.deepcopy(previous);bad['original_independent_fees']['h1']=0.;refuse(lambda:candidate.validate_launch_closed_receipt(q,bad,SHA),'actual_original_fee_not_refunded_or_clamped')
bad=copy.deepcopy(previous);bad['canonical_active_segment']={};refuse(lambda:candidate.validate_launch_closed_receipt(q,bad,SHA),'canonical_None_required')
yes(candidate.REMOTE_ACCOUNT.replace('576916.5355293751','577055.9868602753')==candidate.original.REMOTE_ACCOUNT,'REMOTE_ACCOUNT_only_exact_current_balance_literal_change')
yes('86412.86069250107' in candidate.REMOTE_ACCOUNT and "c['active_segment'] is None" in candidate.REMOTE_ACCOUNT,'strict_threshold_and_no_active_segment_retained')
for name in ('three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py','native87_available_two_schedule_v1.py','AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json','native87_install_activate_support_v1.py','native87_observer_protocol_v1.py'):
 yes((D/name).read_bytes()==(O/name).read_bytes(),'original_bytes '+name)
boundary=json.loads((D/'AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json').read_bytes())
yes(boundary['account']['remaining']==577055.9868602753,'historical_resource_snapshot_unchanged_not_current_budget')
# Use the actual approved dispatcher recipe function (AST only), not a guessed
# process identity interface. Files and identities below are explicit fixtures.
dispatch=D.parent/'native87_dispatcher_v4/native87_closed_source_CPU_v1.py';tree=ast.parse(dispatch.read_bytes());defs=[]
names={'PY210','EXE210','WRAPPER72','LOADER72','LIBRARY72','PYTHON72'}
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in node.targets):defs.append(node)
 if isinstance(node,ast.FunctionDef) and node.name=='expected_exec_identity':defs.append(node)
ns={};exec(compile(ast.Module(body=defs,type_ignores=[]),'<approved_dispatcher_recipe>','exec'),ns)
saved=sys.modules.get('native87_closed_source_CPU_v1');sys.modules['native87_closed_source_CPU_v1']=types.SimpleNamespace(expected_exec_identity=ns['expected_exec_identity'])
import psutil
class Missing(psutil.NoSuchProcess):pass
try:
 with tempfile.TemporaryDirectory(prefix='native87R4_observer_source_fixture_') as temp:
  B=Path(temp);(B/'source').mkdir();(B/'job0/production').mkdir(parents=True)
  real_entry=D.parent/'native87_encoder_actual_SDK_API_fix_v1/native_own_fudan87_training.py'
  (B/'native87_closed_source_CPU_v1.py').write_bytes(dispatch.read_bytes());(B/'source/native_own_fudan87_training.py').write_bytes(real_entry.read_bytes())
  manifest=dict(files=[dict(relative=n,SHA=hashlib.sha256((B/n).read_bytes()).hexdigest()) for n in ('native87_closed_source_CPU_v1.py','source/native_own_fudan87_training.py')])
  mraw=json.dumps(manifest).encode();(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_bytes(mraw)
  spec=dict(key='recovery',execution_backend='target72',python=ns['WRAPPER72'],production_script='h1_native_own87_worker_v1.py',seed=29,manifest_SHA=hashlib.sha256(mraw).hexdigest())
  ne=ns['expected_exec_identity'](spec,[spec['python'],'-u','-B',str(B/'three_slot_finite_node_v1.py')],B)
  record=dict(pid=42,creation=1.,argv=ne['argv'],root=ne['root']);(B/'NODE_IDENTITY.json').write_text(json.dumps(record))
  logical=[spec['python'],'-u','-B',str(B/spec['production_script']),'--slot','recovery','--phase','production','--num-envs','4096','--seed','29','--source-scope','policy_only_fresh_environment']
  we=ns['expected_exec_identity'](spec,logical,B);worker=dict(pid=43,creation=1.,argv=we['argv'],root=we['root'])
  (B/'job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').write_text(json.dumps(dict(error='SYNTHETIC_PRIMARY_FAILURE')))
  v=dict(root=str(B),spec=spec,row=dict(worker=worker),run_id='SYNTHETIC_NOT_ACTUAL')
  def missing(pid):raise psutil.NoSuchProcess(pid)
  with mock.patch.object(psutil,'Process',side_effect=missing),mock.patch('subprocess.check_output') as gpu:
   value=observe_target_readonly(v)
   yes(value['node_identity']['actual_out'] and value['worker_identity']['actual_out'] and not value['passed_live_identity'],'node_and_worker_out_return_metadata_not_NoSuchProcess')
   yes(any('SYNTHETIC_PRIMARY_FAILURE' in str(x) for x in value['existing_small_errors'].values()),'primary_error_preserved_before_process_query')
   yes(gpu.call_count==0,'no_GPU_query_for_out_processes')
  class NodeOnly:
   def __init__(self,pid):
    if pid==43:raise psutil.NoSuchProcess(pid)
    self.pid=pid
   def create_time(self):return 1.
   def cmdline(self):return ne['argv']
   def exe(self):return ne['exe']
   def cwd(self):return ne['root']
  with mock.patch.object(psutil,'Process',NodeOnly):
   value=observe_target_readonly(v);yes(value['node_identity']['passed'] and value['worker_identity']['actual_out'],'live_node_dead_worker_preserves_primary_error')
  touched=[]
  class Recycled(NodeOnly):
   def __init__(self,pid):self.pid=pid
   def create_time(self):return 99.
   def cmdline(self):touched.append('cmdline');raise AssertionError('foreign recycled pid queried')
   def exe(self):touched.append('exe');raise AssertionError('foreign recycled pid queried')
  with mock.patch.object(psutil,'Process',Recycled):
   value=observe_target_readonly(v);yes(value['node_identity']['status']=='pid_creation_mismatch' and not touched,'recycled_pid_creation_mismatch_does_not_query_foreign_exe_argv')
finally:
 if saved is None:sys.modules.pop('native87_closed_source_CPU_v1',None)
 else:sys.modules['native87_closed_source_CPU_v1']=saved
observer=(D/'observe_available_two_H1_native87R4_first_GO_policy_finite_unused_once.py').read_text('utf8')
yes("if owner.get('owner_actual_out') or owner.get('owner_observation_error')" in observer and "targets['h1']=d.code" in observer,'ownerout_still_collects_both_target_primary_receipts')
for p in D.glob('*.py'):ast.parse(p.read_bytes())
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,source_and_synthetic_metadata_only=True,
 previous_R3_cost_report_SHA=SHA,actual_model_SDK_network_GPU_or_budget_operation=False),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))
