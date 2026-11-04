"""Freeze exact three-capacity derivation and six NEW fixture blobs before any parse."""
from pathlib import Path
import ast,difflib,hashlib,importlib.util,json
O=Path(__file__).resolve().parent;R=O.parent
V7=R/'MOD4_DEPLOYMENT_ABI_SCOPE_STATIC_V7';V8=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8';V9=R/'MOD4_DEPLOYMENT_CAPACITY_STATIC_V9'
def record(p,b=None):
 if b is None:b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(name,obj):
 with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 assert not (O/'QA_PREEXEC_01.json').exists() and not (O/'scoped_attrs_v10.py').exists(),'NO_PREP_RESTART'
 old=V7/'scoped_attrs_v7.py';before=record(old)
 assert before['bytes']==11176 and before['SHA']=='0d4784fc36059a49fc434da44f93f354b9d786e8e65c184f4a0246798ed7d1e3'
 data=old.read_bytes();pairs=[(b'MAX_OBJECT=65536',b'MAX_OBJECT=1048576'),(b'MAX_SECTIONS=256',b'MAX_SECTIONS=4096'),(b'table[5]//16<=1024',b'table[5]//16<=16384')]
 new=data
 for a,b in pairs:assert new.count(a)==1;new=new.replace(a,b)
 inverse=new
 for a,b in reversed(pairs):assert inverse.count(b)==1;inverse=inverse.replace(b,a)
 assert inverse==data
 tree=ast.parse(new.decode('utf-8'));reverse_values={1048576:65536,4096:256,16384:1024};count=[0]
 class Reverse(ast.NodeTransformer):
  def visit_Constant(self,node):
   if type(node.value) is int and node.value in reverse_values:
    count[0]+=1;return ast.copy_location(ast.Constant(value=reverse_values[node.value]),node)
   return node
 reverted=Reverse().visit(tree)
 assert count[0]==3 and ast.dump(reverted)==ast.dump(ast.parse(data.decode('utf-8')))
 with (O/'scoped_attrs_v10.py').open('xb') as f:f.write(new)
 with (O/'CAPACITY_ONLY.patch').open('x',encoding='utf-8',newline='\n') as f:f.write(''.join(difflib.unified_diff(data.decode().splitlines(True),new.decode().splitlines(True),fromfile='sealed_V7_reader',tofile='new_V10_reader')))
 spec=importlib.util.spec_from_file_location('new_capacity_fixture_generator',O/'new_boundary_fixtures.py');gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
 cases=gen.fixture_cases();assert len(cases)==6
 d=O/'fixtures';d.mkdir(exist_ok=False);plan=[]
 for item in cases:
  path=d/(item['name']+'.elfbin')
  with path.open('xb') as f:f.write(item['blob'])
  plan.append(dict(name=item['name'],blob=record(path,item['blob']),expected_positive=item['positive'],expected_error=item['expected_error'],construction=item['construction'],parse_count_budget=1))
 assert [x['blob']['bytes'] for x in plan[:2]]==[1048576,1048577]
 assert [x['construction']['section_count'] for x in plan[2:4]]==[4096,4097]
 assert [x['construction']['symbol_count_including_null'] for x in plan[4:]]==[16384,16385]
 gate_path=V8/'compile_v8_once.py';gate_bytes=gate_path.read_bytes();assert hashlib.sha256(gate_bytes).hexdigest()=='5ba3874d0929150fe56858c772ad09df3c46e059af832ab20c658813ddced7ab'
 gate_nodes=[n for n in ast.parse(gate_bytes.decode()).body if isinstance(n,ast.FunctionDef) and n.name=='gate'];assert len(gate_nodes)==1
 gate_AST_SHA=hashlib.sha256(ast.dump(gate_nodes[0]).encode()).hexdigest()
 expected=dict(ELF_class=1,ELF_data=1,ELF_type=1,ELF_machine=40,CPU_arch=13,CPU_profile=77,THUMB_ISA_use=2,FP_arch=6,ABI_HardFP_use=1,ABI_VFP_args=1,ABI_FP_denormal=[1,2])
 diag=load(V9/'HEADER_DIAG_01.json');obj=diag['producer_object_pin'];assert obj['bytes']==58720 and obj['SHA']=='8e01341b4c39ce543c2c114a1bddcba11371731ec87bcb4865f6285263a0e1a0'
 for p in [O/'run_study_once.py',O/'new_boundary_fixtures.py',Path(__file__).resolve()]:ast.parse(p.read_bytes().decode('utf-8'))
 refs=[record(p) for p in [O/'PARENT_SCOPE.json',O/'METHOD.md',old,gate_path,V9/'HEADER_DIAG_01.json',V9/'CAPACITY_PROPOSAL_01.json',O/'new_boundary_fixtures.py',O/'run_study_once.py',Path(__file__).resolve(),O/'scoped_attrs_v10.py']]
 assert record(old)==before
 derivation={'status':'EXACT_THREE_CAPACITY_CONSTANTS_ONLY_NO_SEMANTIC_CHANGE','old':before,'new':record(O/'scoped_attrs_v10.py'),'byte_inverse_exact':inverse==data,'AST_inverse_exact':True,'AST_changed_integer_constant_count':count[0],'literal_substitutions':[{'old':a.decode(),'new':b.decode()} for a,b in pairs],'old_reader_unchanged':record(old)==before,'all_other_caps_and_semantics_unchanged':True,'new_parent_policy_not_actual_TU40_need':True,'old_minimal304_proposal_not_applied':True,'ARM_native_calls':0,'reader_parse_calls':0}
 save('DERIVATION_01.json',derivation)
 save('QA_PREEXEC_01.json',{'status':'FROZEN_BEFORE_FIRST_PARSE','source_refs':refs,'reader':derivation['new'],'gate_definition_source':record(gate_path),'gate_AST_SHA':gate_AST_SHA,'expected_non_type_gate_unchanged':expected,'fixture_plan':plan,'actual_object_pin':obj,'fixture_parses_max':6,'actual_object_new_parses_max':1,'ARM_native_calls':0,'old_objects38_and_main_read':0,'old_V8_history':{'new_compiler_success':39,'new_scope_accepted':38,'capacity_stop_TU':40,'unstarted_C':122,'unstarted_ASM':1}})
 print(json.dumps({'status':'FROZEN_THREE_CONSTANTS_AND_SIX_NEW_BOUNDARY_FIXTURES','reader':derivation['new'],'preexec':record(O/'QA_PREEXEC_01.json'),'fixture_count':len(plan),'fixture_total_bytes':sum(x['blob']['bytes'] for x in plan),'byte_AST_inverse_exact':True,'parser_calls':0,'native_calls':0},ensure_ascii=False))
if __name__=='__main__':main()
