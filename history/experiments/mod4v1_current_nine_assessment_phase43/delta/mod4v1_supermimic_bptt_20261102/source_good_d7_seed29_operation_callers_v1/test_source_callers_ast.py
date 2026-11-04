"""Eight SOURCE-only AST/text checks. Never import or execute any caller."""
from pathlib import Path
import ast,copy,hashlib,json,sys,time,unittest
D=Path(__file__).resolve().parent;R=D.parent
PAIRS=(('upload_preflight_good_holdout_d7_case_final_seed20260930_once.py','upload_preflight_good_holdout_d7_case_final_seed20260929_once.py'),('stage_good_holdout_d7_seed20260930_after_preflight_once.py','stage_good_holdout_d7_seed20260929_after_preflight_once.py'),('read_good_holdout_d7_seed30_prelaunch_resources_once.py','read_good_holdout_d7_seed29_prelaunch_resources_once.py'),('dispatch_good_holdout_d7_seed30_original_parent_once.py','dispatch_good_holdout_d7_seed29_original_parent_once.py'),('collect_good_holdout_d7_seed30_closed_metadata_once.py','collect_good_holdout_d7_seed29_closed_metadata_once.py'),('summarize_good_holdout_d7_seed30_qualified_once.py','summarize_good_holdout_d7_seed29_qualified_once.py'))
H=lambda b:hashlib.sha256(b).hexdigest()
COUNTERS=dict(actual_report_or_metadata_open=0,model_raw_C_lock_or_SDK_open=0,caller_execution_or_import=0,process_network_or_signal=0,outside_source_output_write=0)
FORBIDDEN_NAMES={name for pair in PAIRS for name in pair}
def audit(event,args):
 if event=='open':
  value=args[0]
  if isinstance(value,(str,bytes,Path)):
   text=str(value).replace('\\','/');lower=text.lower();mode=args[1]if len(args)>1 else None;flags=args[2]if len(args)>2 else 0;writing=(isinstance(mode,str)and any(c in mode for c in 'wax+'))or(isinstance(flags,int)and flags&0x503!=0)
   if '/reports/'in lower or '/paper_aligned_rebuild_20261103/'in lower or lower.endswith('/closed_result.json'):
    COUNTERS['actual_report_or_metadata_open']+=1;raise AssertionError('No actual published metadata reads in SOURCE checks')
   if lower.endswith(('.pt','.pth','.ckpt','.npy','.npz','.safetensors'))or(lower.startswith('c:')and not Path(text).resolve().is_relative_to(Path(sys.base_prefix).resolve()))or '/locks/'in lower or '/budget' in lower:
    COUNTERS['model_raw_C_lock_or_SDK_open']+=1;raise AssertionError('No model/raw/C/resource reads in SOURCE checks')
   if writing and not Path(text).resolve().is_relative_to(D.resolve()):
    COUNTERS['outside_source_output_write']+=1;raise AssertionError('Only NEW SOURCE report may be written')
 if event=='exec'and args and Path(getattr(args[0],'co_filename','')).name in FORBIDDEN_NAMES:
  COUNTERS['caller_execution_or_import']+=1;raise AssertionError('Caller AST only, no exec/import')
 if event=='import'and args and(str(args[0]).split('.')[0]in {'torch','omni','isaacsim','isaacgym','paramiko','project_connector'}or any(Path(str(x)).name in FORBIDDEN_NAMES for x in args[:2]if isinstance(x,str))):
  COUNTERS['caller_execution_or_import']+=1;raise AssertionError('No connector/native/caller import')
 if event.startswith(('subprocess.','socket.','os.exec','os.spawn'))or event in ('os.system','os.kill','os.killpg'):
  COUNTERS['process_network_or_signal']+=1;raise AssertionError('No process/network/signal operations')
sys.addaudithook(audit)
def load(name):
 raw=(R/name).read_bytes();return raw.decode('utf8'),ast.parse(raw,filename=name),dict(path=str(R/name).replace('\\','/'),bytes=len(raw),SHA256=H(raw))
def dump(node):return ast.dump(node,include_attributes=False)
def namespace(tree):
 class N(ast.NodeTransformer):
  def visit_Constant(self,node):
   if isinstance(node.value,str):return ast.copy_location(ast.Constant(value=node.value.replace('20260930','20260929').replace('seed30','seed29').replace('SEED30','SEED29')),node)
   if type(node.value)is int and node.value==20260930:return ast.copy_location(ast.Constant(value=20260929),node)
   return node
 return N().visit(copy.deepcopy(tree))
def strip(tree):
 value=copy.deepcopy(tree);value.body=[n for n in value.body if not(isinstance(n,ast.FunctionDef)and n.name=='_require_published_seed30_qualified')and not(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='_require_published_seed30_qualified')];
 if value.body and isinstance(value.body[0],ast.Expr)and isinstance(value.body[0].value,ast.Constant)and isinstance(value.body[0].value.value,str):value.body=value.body[1:]
 return value
OLD={};NEW={};PINS=[]
for old,new in PAIRS:
 OLD[old]=load(old);NEW[new]=load(new);PINS.extend((OLD[old][2],NEW[new][2]))
def assign(tree,name):return next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
def literal(tree,name):
 node=assign(tree,name).value
 if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=='replace':
  while isinstance(node,ast.Call):node=node.func.value
 return ast.literal_eval(node)
class SourceChecks(unittest.TestCase):
 def test_01_six_complete_callers_parse_without_execution(self):
  self.assertEqual(len(NEW),6)
  for old,new in PAIRS:
   text,tree,_=NEW[new];self.assertGreater(len(tree.body),10);self.assertIn('from pathlib import Path',text);self.assertNotIn('if __name__',text)
  self.assertTrue(all(v==0 for v in COUNTERS.values()))
 def test_02_four_complete_namespace_only_bodies_and_old_guards(self):
  for i in (0,1,3,4):
   old,new=PAIRS[i];self.assertEqual(dump(strip(namespace(OLD[old][1]))),dump(strip(NEW[new][1])),new)
  old,new=PAIRS[0];a=OLD[old][0];b=NEW[new][0]
  for token in ('GOOD_HOLDOUT_D4_SEED20260929_ACTUAL_PREFLIGHT_V1.json','GOOD_HOLDOUT_D5_SEED20260929_ACTUAL_PREFLIGHT_V1.json','GOOD_HOLDOUT_D6_SEED20260929_CLOSED_FAILURE_FACTS_V1.json','old207_payload_files_preserved_bytewise','source_file_count=len(payload)',"mirror_files']==164","original_complete_source_mapping_passed']==20"):
   if token in a:self.assertIn(token,b)
  self.assertIn("stamp=str(time.time_ns())",b);self.assertIn("'_SOURCE_INPUT'",b);self.assertNotIn('20261104_074235',b)
 def test_03_published_seed30_prerequisite_whole_function_identical_and_early(self):
  functions=[]
  for index in (0,3):
   text,tree,_=NEW[PAIRS[index][1]];fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='_require_published_seed30_qualified');functions.append(ast.get_source_segment(text,fn));call=next(n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id==fn.name);self.assertLess(call.lineno,text.splitlines().index('sys.path.insert(0,str(R.parent/\'mod4v1_experts_fulldr_rm70_20261101\'));from project_connector import connect72')+1 if index==0 else next(n.lineno for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)and n.module=='project_connector'))
   body=ast.get_source_segment(text,fn)
   for token in ('GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json','CLOSED_RESULT.json',"(len(raw),H(raw))==(info['bytes'],info['SHA256'])",'producer_original_source_grade','original_ownchild_actual_waits','original_both_EX_released','independent_outer_actual_Popen_wait','actual_parent_p_wait_returned','original_single_GPU_private_EX_released','original_global_finite_EX_released','canonical_writes'):
    self.assertIn(token,body)
   self.assertNotIn('conditional_original_scope_results',body);self.assertNotIn('observed_counts',body)
  self.assertEqual(functions[0],functions[1]);EVIDENCE['new_full_guard_functions_compared']=2
  summary_fields={keyword.arg for keyword in assign(OLD[PAIRS[5][0]][1],'v').value.keywords};self.assertTrue({'kind','seed','root','closed_metadata','passed_closed_execution','errors','producer_grade_rewritten','gates','own_child_waits','actual_outer_parent_returncode'}<=summary_fields)
  producer_text,producer_tree,producer_pin=load('source_good_holdout_lifecycle_routes_v5/collect_good_holdout_result.py');producer=next(node for node in producer_tree.body if isinstance(node,ast.FunctionDef)and node.name=='summarize');publication=next(node.value for node in producer.body if isinstance(node,ast.Return));producer_fields={keyword.arg for keyword in publication.keywords};self.assertTrue({'kind','seed','root','requested_roles','passed_closed_good_reference_execution','errors','gates','metadata','own_child_waits','actual_outer_parent_returncode'}<=producer_fields);EVIDENCE['seed30_guard_fields_confirmed_from_complete_SOURCE_producers']=dict(summary_template=OLD[PAIRS[5][0]][2],CLOSED_publisher=producer_pin,no_actual_published_metadata_read=True)
 def test_04_original_remote_Popen_and_resource_extraction_literals_identical(self):
  old,new=PAIRS[3];before=literal(OLD[old][1],'code');after=literal(NEW[new][1],'code');self.assertEqual(before,after);self.assertEqual(dump(ast.parse(before)),dump(ast.parse(after)));self.assertIn('subprocess.Popen(ARGV',after);self.assertNotIn('2400',after)
  old,new=PAIRS[2]
  for name in ('source','raw','tree','node','code'):
   self.assertEqual(dump(assign(OLD[old][1],name)),dump(assign(NEW[new][1],name)),name)
  text,tree,pin=load('observe_bound_probe_resources_after_zero_admission_timeout_once.py');observer=literal(tree,'code');ast.parse(observer);self.assertIn('lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0',observer);EVIDENCE['original_resource_observer_source']=pin;EVIDENCE['entire_readonly_code_literal']=dict(bytes=len(observer.encode()),SHA256=H(observer.encode()));EVIDENCE['entire_remote_dispatch_code_literal']=dict(bytes=len(after.encode()),SHA256=H(after.encode()))
 def test_05_future_stage_raw_chain_and_no_reencoding_as_raw_proof(self):
  old,new=PAIRS[1];self.assertIn("s.open(root+'/STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json','rb')",NEW[new][0]);self.assertIn('stage_receipt_bytes=len(raw),stage_receipt_SHA256=H(raw)',NEW[new][0]);self.assertIn('json.loads(raw)==receipt',NEW[new][0])
  text,tree,_=NEW[PAIRS[2][1]];self.assertIn("add_argument('--expected-stage-sha',required=True",text);self.assertIn("stage['stage_receipt_SHA256']==expected_stage_sha",text);self.assertIn("stage['preflight_receipt_SHA256']==hashlib.sha256(pfraw).hexdigest()",text);self.assertIn("stage['root']==receipt['root']==pf['root']",text);self.assertIn("stage['group_id']==receipt['group_id']==pf['group_id']",text);self.assertIn("stage['seed']==receipt['seed']==pf['seed']==20260929",text);self.assertIn('06e82474aa80ec1280cc38aee8a199556ec2ff054189db02394f7f608f30b8f5',text);self.assertNotIn('110fc2eca73a3b5bf25158d648f5b6367f8c2b1801e452ba3a024c5cebe7d6b8',text);self.assertNotIn('json.dumps(receipt',text);self.assertNotIn('approval',ast.get_source_segment(text,assign(tree,'config'))if any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='config'for t in n.targets)for n in ast.walk(tree))else '')
 def test_06_new_closed_pointer_and_non100_data_driven_summary(self):
  old,new=PAIRS[5];a=namespace(OLD[old][1]);text,b,_=NEW[new]
  self.assertIn('GOOD_HOLDOUT_D7_SEED20260929_LATEST_CLOSED_RESULT_PATH.json',text);self.assertIn("p=Path(pointer['result'])",text);self.assertIn("p.resolve().is_relative_to((R/'reports').resolve())",text);self.assertIn("p.name=='CLOSED_RESULT.json'and p.is_file()",text);self.assertIn("q['root']==pointer['root']==stage['root']",text);self.assertIn("q['requested_roles']==['CURB_PROTECTED878','SLOPE135']",text);self.assertIn('CLOSED_GOOD_REFERENCE_SOURCE_GRADE_AND_ACTUAL_WAITS',text);self.assertNotIn('20261104_074235',text)
  for name in ('conditions','expected','v'):self.assertEqual(dump(assign(a,name)),dump(assign(b,name)),name)
  self.assertNotIn("['complete']==27",text);self.assertNotIn("['contact_confirmed']==27",text);self.assertNotIn("['no_failure']==26",text);self.assertNotIn('（100%）',text)
  for token in ("type(value['denominator'])is int and value['denominator']==27","type(value[key])is int and 0<=value[key]<=value['denominator']","type(value['no_failure'])is int and 0<=value['no_failure']<=value['denominator']"):
   self.assertIn(token,text)
  row_template=ast.literal_eval(assign(b,'ROW_TEMPLATE').value);format_call=next(n for n in ast.walk(b)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='ROW_TEMPLATE'and n.func.attr=='format');rendered=[]
  for label,up,up_contact,down,down_contact,stand in(('C878',24,23,25,22,23),('S135',26,24,24,24,25)):
   value=dict(ascending=dict(denominator=27,complete=up,contact_confirmed=up_contact,complete_rate=up/27,contact_confirmed_rate=up_contact/27),descending=dict(denominator=27,complete=down,contact_confirmed=down_contact,complete_rate=down/27,contact_confirmed_rate=down_contact/27),stand=dict(denominator=26,no_failure=stand,no_failure_rate=stand/26),whole_skill_rate=None,new_acceptance_predicate=None,full_expert_graduation=None)
   self.assertTrue(all(type(value[d][k])is int and 0<=value[d][k]<=value[d]['denominator']for d in('ascending','descending')for k in('complete','contact_confirmed')));self.assertTrue(type(value['stand']['no_failure'])is int and 0<=value['stand']['no_failure']<=26)
   arguments={}
   for keyword in format_call.keywords:
    node=keyword.value;keys=[]
    while isinstance(node,ast.Subscript):keys.append(ast.literal_eval(node.slice));node=node.value
    self.assertIsInstance(node,ast.Name);self.assertIn(node.id,('label','value'));actual=label if node.id=='label'else value
    for key in reversed(keys):actual=actual[key]
    arguments[keyword.arg]=actual
   row=row_template.format(**arguments);self.assertIn(f'{up}/27',row);self.assertIn(f'{up_contact}/27',row);self.assertIn(f'{down}/27',row);self.assertIn(f'{down_contact}/27',row);self.assertIn(f'{stand}/26',row);self.assertIn(format(value['ascending']['complete_rate'],'.2%'),row);self.assertIn(format(value['ascending']['contact_confirmed_rate'],'.2%'),row);self.assertNotIn('100%',row);rendered.append(row)
  EVIDENCE['non100_summary_pure_data_string_AST_check']=dict(native_or_caller_executed=False,source_asserts_100_percent=False,complete_and_contact_separate=True,raw_published_rates_preserved=True,synthetic_rows=rendered,qualification_not_recomputed_from_rates=True)
  for token in ('bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()','producer_grade_rewritten=False','prior_seed29_failed_run_promoted=False','multiseed_holdout_completed=False','stage2_GO=False'):
   self.assertIn(token,text)
 def test_07_frozen_CFF_parent_controller_resources_and_payload_pins(self):
  folder=R/'source_good_holdout_lifecycle_routes_v5';raw=(folder/'SOURCE_SEAL.json').read_bytes();self.assertEqual((len(raw),H(raw)),(2446,'ddfa3f19c4be7961003207ac6e6c79f96f8befad97a91a2477e0589c37e0ab6d'));seal=json.loads(raw);self.assertEqual(len(seal['files']),13);self.assertEqual(seal['root_SHA256'],'4ec4589ea395eed235c2690a05b250cdecd9b61a37dcd9ccf49ce0b42a9e3f89')
  for row in seal['files']:
   data=(folder/row['name']).read_bytes();self.assertEqual((len(data),H(data)),(row['bytes'],row['SHA256']))
  EVIDENCE['frozen_CFF13_plus_seal']=dict(path=str(folder).replace('\\','/'),files=13,seal_bytes=len(raw),seal_SHA256=H(raw),root_SHA256=seal['root_SHA256'])
  parent=(R/'source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py').read_bytes();self.assertEqual((len(parent),H(parent)),(9679,'fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff'));controller=(folder/'good_holdout_parent_actual_wait_controller_v1.py').read_bytes();self.assertEqual((len(controller),H(controller)),(5170,'4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0'));self.assertIn(b'child.wait(',controller);self.assertIn(b'+1800',parent);self.assertIn(b'+900',parent);self.assertIn(b'+2400',parent);self.assertIn(b'23500',parent);self.assertIn(b'96*1024**3',parent);self.assertIn(b'25*1024**3',parent)
  EVIDENCE['parent_pin']=dict(bytes=len(parent),SHA256=H(parent));EVIDENCE['controller_pin']=dict(bytes=len(controller),SHA256=H(controller))
 def test_08_new_namespaces_do_not_reuse_old_roots_or_markers(self):
  for index,(old,new)in enumerate(PAIRS):
   text,tree,_=NEW[new];top=strip(tree);strings=[n.value for n in ast.walk(top)if isinstance(n,ast.Constant)and isinstance(n.value,str)]
   allowed_old='GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json'
   self.assertFalse(any('GOOD_HOLDOUT_D7_SEED20260930_'in value and allowed_old not in value for value in strings));self.assertNotIn('GOOD_HOLDOUT_D6_SEED20260929_STAGE_STARTED_ONCE',text)
  self.assertEqual(len({name for _,name in PAIRS}),6);self.assertTrue(all(value==0 for value in COUNTERS.values()));EVIDENCE['unrelated_package_or_old_root_writes']=0
EVIDENCE={}
if __name__=='__main__':
 start=time.monotonic();suite=unittest.defaultTestLoader.loadTestsFromTestCase(SourceChecks);result=unittest.TextTestRunner(verbosity=2).run(suite);report=dict(kind='SOURCE_ONLY_D7_SEED29_THIN_CALLERS_EIGHT_AST_CHECKS_V1',passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_seconds=round(time.monotonic()-start,6),caller_import_exec_or_main_executed=False,actual_prepare_preflight_stage_parent_SDK=0,automatic_stage_or_dispatch=False,source_enabled=False,source_staged=False,source_files=PINS,evidence=EVIDENCE,independent_operation_counters=COUNTERS,limitations=['AST/text/source-byte checks only; no caller execution or future metadata read','Future stage raw SHA must be supplied from actual stage publication and rechecked by unchanged controller','No new native/quality/closed-seed29 evidence; old D6 failure unchanged'],failure_details=[dict(test=str(t),traceback=detail)for t,detail in result.failures+result.errors]);path=D/'AST_CHECK_REPORT.json'
 with path.open('w',encoding='utf8',newline='\n')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:report[k]for k in('passed','tests','failures','errors','elapsed_seconds','independent_operation_counters')},indent=2));raise SystemExit(0 if result.wasSuccessful()else 1)
