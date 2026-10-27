"""No remote operations: source AST, literal derivation, one tiny ownerout mock."""
from pathlib import Path
import ast,contextlib,hashlib,io,json,sys,tempfile,types
D=Path(__file__).resolve().parent;O=D.parent/'native87_available_two_schedule_source';checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
for p in D.glob('*.py'):ast.parse(p.read_bytes());checks.append('AST '+p.name)
for name in ('native87_install_activate_support_v1.py','native87_available_two_schedule_v1.py','three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py','native87_observer_protocol_v1.py','AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json'):
 yes((D/name).read_bytes()==(O/name).read_bytes(),'byteexact '+name)
for name in ('native87_available_two_activation_support_v1.py','activate_available_two_H1_native87R3_sole72_after_actual_CPU_unused_once.py'):
 oldname=name.replace('native87R3','native87R2')
 expected=(O/oldname).read_text('utf8').replace('native87R2','native87R3').replace('NATIVE87R2','NATIVE87R3').replace('native_2610v87r2','native_2610v87r3').replace('controllers_r2','controllers_r3').replace('payloads_r2','payloads_r3').replace('R2','R3')
 yes((D/name).read_text('utf8')==expected,name+' only R3 namespace reports controller paths')
source=(D/'observe_available_two_H1_native87R3_first_GO_policy_finite_unused_once.py').read_text('utf8')
tree=ast.parse(source)
def constant(tree,name):return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
yes(constant(tree,'TARGET_READ')==constant(ast.parse((O/'observe_available_two_H1_native87R2_first_GO_policy_finite_unused_once.py').read_bytes()),'TARGET_READ'),'target_reader_exact_original_not_reexecuted')
code=constant(tree,'OWNER_READ');class_error=type('NoSuchProcess',(Exception,),{})
def missing(pid):raise class_error(pid)
saved=sys.modules.get('psutil');sys.modules['psutil']=types.SimpleNamespace(Process=missing,NoSuchProcess=class_error)
try:
 with tempfile.TemporaryDirectory(prefix='native87_ownerout_metadata_fixture_') as temp:
  root=Path(temp);(root/'OWNER_CURRENT.json').write_text(json.dumps(dict(rows={},go={})),encoding='utf8')
  (root/'OWNER_EXIT_ACTUAL.json').write_text(json.dumps(dict(original_cost_settled=True)),encoding='utf8')
  output=io.StringIO()
  with contextlib.redirect_stdout(output):
   try:exec(code,{'v':dict(owner_root=str(root),owner_identity=dict(pid=123,creation=1))})
   except SystemExit as exc:yes(exc.code==0,'ownerout remote helper returns clean text process')
  value=json.loads(output.getvalue())
  yes(value['owner_actual_out'] and value['first_positive_not_proven'] and 'OWNER_EXIT_ACTUAL.json' in value['existing_own_small_receipts'],'NoSuchProcess preserved ownerout receipts no Pi claim')
finally:
 if saved is None:sys.modules.pop('psutil',None)
 else:sys.modules['psutil']=saved
yes("owner.get('owner_actual_out') or owner.get('owner_observation_error')" in source,'local observer commits false summary on preserved owner error')
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,source_and_mock_only=True,actual_owner_or_node_query=False,actual_activation_or_model_or_network=False),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))
