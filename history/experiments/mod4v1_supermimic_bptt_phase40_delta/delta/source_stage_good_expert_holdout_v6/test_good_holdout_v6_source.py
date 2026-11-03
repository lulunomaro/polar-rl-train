"""Eight NEW SOURCE/AST/in-memory three-dict tests; never consumer or old-test execution."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import sys
import types
import unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R,W=HERE.parent,HERE.parent.parent
REPORT=HERE/'TEST_REPORT.json'
AUDIT=dict(model_or_raw_opens=0,native_imports=0,process_or_network=0,lock_or_budget=0,outside_report_writes=0)
DENIED_IMPORTS={'torch','numpy','warp','isaaclab','isaacsim','rsl_rl','omni'}
def audit(event,args):
    if event=='import' and str(args[0]).split('.')[0] in DENIED_IMPORTS:
        AUDIT['native_imports']+=1;raise AssertionError('native import attempted')
    if event.startswith('subprocess.') or event in ('os.system','os.fork','socket.connect','socket.bind'):
        AUDIT['process_or_network']+=1;raise AssertionError('process or network attempted')
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=Path(os.fsdecode(args[0]));low=str(p).lower().replace('\\','/')
        if p.suffix.lower() in ('.pt','.pth','.pkl','.npy','.npz','.raw','.bin','.sqlite'):
            AUDIT['model_or_raw_opens']+=1;raise AssertionError('model/raw/bank open attempted')
        if 'budget' in low or '/locks/' in low or p.suffix.lower()=='.lock':
            AUDIT['lock_or_budget']+=1;raise AssertionError('budget or lock open attempted')
        mode=args[1] or '';flags=args[2] if len(args)>2 else 0
        writing=(isinstance(mode,str) and any(x in mode for x in ('w','a','x','+'))) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and p.resolve()!=REPORT:
            AUDIT['outside_report_writes']+=1;raise AssertionError('write outside own NEW report attempted')
        if not writing and p.resolve().is_relative_to(W) and p.suffix.lower() not in ('.py','.json','.md'):
            raise AssertionError('workspace non-SOURCE read attempted')
def profile(frame,event,arg):
    if event=='call' and frame.f_code.co_name in ('prepare','metadata_validate','stage','derive_producer_guard','validate_reference_row'):
        raise AssertionError('actual consumer/guard function invoked: '+frame.f_code.co_name)
sys.addaudithook(audit);sys.setprofile(profile)
spec=importlib.util.spec_from_file_location('new_source_v6_packager',HERE/'build_source_v6.py')
B=importlib.util.module_from_spec(spec)
exec(compile((HERE/'build_source_v6.py').read_bytes(),str(HERE/'build_source_v6.py'),'exec'),B.__dict__)
OLD_ENTRY=B.read(B.OLD/'stage_good_expert_holdout_v5.py')
NEW_ENTRY=B.read(HERE/'stage_good_expert_holdout_v6.py')
OLD_GUARD=B.read(B.GUARD,B.GUARD_PIN)
NEW_GUARD=B.read(B.COMP/'producer_teacher_guard_v1.py')
OLD_RUNTIME=B.read(B.BASE/'good_expert_holdout_runtime_v1.py',B.RUNTIME_PIN)
NEW_RUNTIME=B.read(B.COMP/'good_expert_holdout_runtime_v1.py')
OVERLAY_RAW=B.read(B.COMP/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json')
OVERLAY=json.loads(OVERLAY_RAW)
CAPTURES=B.teacher_inputs()['receipt']['roles']
def find_assign(raw,name):
    return next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets))
old_gf,new_gf=B.functions(OLD_GUARD),B.functions(NEW_GUARD)
old_rf=B.functions(OLD_RUNTIME)
pure={}
exec(compile(ast.Module(body=[old_gf['need'],old_gf['teacher_identity'],find_assign(OLD_RUNTIME,'BASELINE_IDENTITIES')],type_ignores=[]),'<complete pure need/identity and baseline constants>','exec'),pure)
def identity_block(raw):
    body=B.functions(raw)['validate_reference_row'].body
    start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='mother' for x in n.targets))
    # Only the exact identity statements, before unchanged actor/container check.
    return compile(ast.Module(body=body[start:-2],type_ignores=[]),'<exact reference identity block, not whole validator>','exec')
NEW_IDENTITY=identity_block(NEW_GUARD);OLD_IDENTITY=identity_block(OLD_GUARD)
body=old_rf['_validate_zero_update_baseline'].body
start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='teacher' for x in n.targets))
RUNTIME_IDENTITY=compile(ast.Module(body=body[start:-1],type_ignores=[]),'<exact original runtime mother identity block>','exec')
def accepts(role,final_teacher,checkpoint_teacher,row_teacher,new=True,runtime=True):
    env=dict(pure,producer={'FINAL':{'teacher':final_teacher}},final={'teacher':final_teacher},checkpoint={'teacher_source':checkpoint_teacher},
        row={'original_bootstrap_teacher':row_teacher},expected=pure['BASELINE_IDENTITIES'][role])
    try:
        if runtime:exec(RUNTIME_IDENTITY,env)
        exec(NEW_IDENTITY if new else OLD_IDENTITY,env)
        return True
    except (ValueError,TypeError,KeyError):return False
class NewSourceTests(unittest.TestCase):
    def test01_immutable_D5_all8_and_complete127(self):
        seal=B.baseline();self.assertEqual(len(seal['files']),8)
        mirror=json.loads(B.read(B.OLD/'SOURCE_MIRROR_INPUTS.json'));self.assertEqual(len(mirror['files']),127)
        for row in mirror['files']:B.read(W/row['workspace_relative'],(row['bytes'],row['SHA256']))
        self.assertEqual(mirror['files_count'],127)
    def test02_exact_component_and_entry_AST_whitelists(self):
        products=B.component_products()
        for name,raw in products.items():self.assertEqual(B.read(B.COMP/name),raw)
        self.assertEqual(len(B.same_functions(OLD_ENTRY,NEW_ENTRY,B.CHANGED)),28)
        self.assertEqual(len(B.same_functions(OLD_RUNTIME,NEW_RUNTIME,set())),len(old_rf))
        B.same_functions(OLD_GUARD,NEW_GUARD,{'validate_reference_row'})
        diff=B.entry_diff(OLD_ENTRY,NEW_ENTRY,OVERLAY_RAW);self.assertTrue(diff['prepare_only_raw_teacher_deepcopy_changed'])
    def test03_actual_two_raw9_strict_predicates_and_original_conflict(self):
        for role,cap in CAPTURES.items():
            final=copy.deepcopy(cap['final_teacher']);checkpoint=copy.deepcopy(cap['checkpoint_teacher_source']);row=copy.deepcopy(final)
            self.assertEqual(set(row),B.KEYS);self.assertEqual(final,checkpoint)
            self.assertTrue(accepts(role,final,checkpoint,row))
            self.assertFalse(accepts(role,final,checkpoint,row,new=False))
            four=cap['current_stager_original_bootstrap_teacher']
            self.assertFalse(accepts(role,final,checkpoint,four))
            self.assertTrue(accepts(role,final,checkpoint,four,new=False,runtime=False))
            self.assertEqual(cap['final_teacher'],final);self.assertEqual(cap['checkpoint_teacher_source'],checkpoint)
    def test04_wrong_mother_path_SHA_bytes_frozen_still_fail_original_predicate(self):
        for role,cap in CAPTURES.items():
            actual=cap['final_teacher']
            for key,bad in (('source_path','/different/mother.pt'),('source_SHA','0'*64),('source_bytes',actual['source_bytes']+1),('teacher_frozen',False)):
                row=copy.deepcopy(actual);row[key]=bad
                self.assertFalse(accepts(role,actual,actual,row))
                # Even coherent but wrong three-dict identities still fail original baseline predicates.
                self.assertFalse(accepts(role,row,copy.deepcopy(row),copy.deepcopy(row)))
    def test05_missing_extra_and_type_spoofed_history_fail_without_defaults(self):
        for role,cap in CAPTURES.items():
            actual=cap['final_teacher']
            for key in B.KEYS:
                row=copy.deepcopy(actual);del row[key];self.assertFalse(accepts(role,actual,actual,row))
                self.assertFalse(accepts(role,row,copy.deepcopy(row),copy.deepcopy(row)))
            row=copy.deepcopy(actual);row['invented_extra']=True
            self.assertFalse(accepts(role,actual,actual,row));self.assertFalse(accepts(role,row,copy.deepcopy(row),copy.deepcopy(row)))
            for key in B.COUNTS:
                for bad in (True,1.0,0,0.0,'1',False,None):
                    row=copy.deepcopy(actual);row[key]=bad
                    self.assertFalse(accepts(role,actual,actual,row));self.assertFalse(accepts(role,row,copy.deepcopy(row),copy.deepcopy(row)))
            for key in B.FLAGS:
                for bad in (False,1,1.0,0,0.0,'True',None):
                    row=copy.deepcopy(actual);row[key]=bad
                    self.assertFalse(accepts(role,actual,actual,row));self.assertFalse(accepts(role,row,copy.deepcopy(row),copy.deepcopy(row)))
    def test06_exact_deepcopy_expression_retains_all_actual_raw_keys(self):
        tree=ast.parse(NEW_ENTRY);matches=[n for n in ast.walk(tree) if isinstance(n,ast.keyword) and n.arg=='original_bootstrap_teacher']
        self.assertEqual(len(matches),1);expr=matches[0].value
        self.assertEqual(ast.unparse(expr),"copy.deepcopy(producers[role]['FINAL']['teacher'])")
        code=compile(ast.Expression(expr),'<exact D6 deepcopy expression only>','eval')
        for role,cap in CAPTURES.items():
            teacher=copy.deepcopy(cap['final_teacher']);before=copy.deepcopy(teacher)
            result=eval(code,dict(copy=copy,producers={role:{'FINAL':{'teacher':teacher}}},role=role))
            self.assertEqual(result,teacher);self.assertIsNot(result,teacher)
            result['source_path']='changed-only-in-copy';self.assertEqual(teacher,before)
    def test07_complete20_two_changes_exact_guard_runtime_index_pins(self):
        old=json.loads(B.read(B.BASE/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json',B.OVERLAY_PIN));new=OVERLAY
        self.assertEqual(len(new['overlay_entries']),20);self.assertEqual(new['kind'],old['kind'])
        changed=[]
        for a,b in zip(old['overlay_entries'],new['overlay_entries']):
            self.assertEqual(a['relative'],b['relative'])
            if a!=b:changed.append(a['relative'])
            raw=B.read(B.source_reference(b['path']),(b['bytes'],b['SHA256']))
            if a['relative']=='producer_teacher_guard_v1.py':self.assertEqual(raw,NEW_GUARD)
            if a['relative']=='good_expert_holdout_runtime_v1.py':self.assertEqual(raw,NEW_RUNTIME)
        self.assertEqual(set(changed),{'producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py'})
        for key,value in old.items():
            if key!='overlay_entries':self.assertEqual(new[key],value)
        self.assertEqual(new['teacher_schema_source_revision']['revision'],2)
        self.assertEqual(ast.literal_eval(find_assign(NEW_ENTRY,'INDEX_PIN').value),(len(OVERLAY_RAW),B.H(OVERLAY_RAW)))
        guard_pin=next(n for n in ast.walk(ast.parse(NEW_RUNTIME)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='_pinned_module' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='producer_teacher_guard_v1')
        self.assertEqual(ast.literal_eval(guard_pin.args[1]),(len(NEW_GUARD),B.H(NEW_GUARD)))
    def test08_remaining_metadata_cache_wire_typed_publication_resources_unchanged(self):
        fa,fb=B.functions(OLD_ENTRY),B.functions(NEW_ENTRY)
        for name in ('metadata_validate','source_mappings','publish_enabled_runtime_plan','main'):
            if name in fa:self.assertEqual(ast.get_source_segment(OLD_ENTRY.decode(),fa[name]),ast.get_source_segment(NEW_ENTRY.decode(),fb[name]))
        for name in ('ORIGINAL_PLAN_PIN','PUBLISHED_ORIGINAL_PLAN_PIN','ORIGINAL_PLAN_CANONICAL_SHA256'):
            self.assertEqual(ast.dump(find_assign(OLD_ENTRY,name),include_attributes=False),ast.dump(find_assign(NEW_ENTRY,name),include_attributes=False))
        metadata=ast.get_source_segment(NEW_ENTRY.decode(),fb['metadata_validate'])
        self.assertIn('producer_teacher_guard_v1',metadata);self.assertIn('embedded_teacher_reference_v1',metadata)
        core=B.read(R/'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py',(37927,'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'))
        self.assertNotIn(b'producer_teacher_guard',core);self.assertNotIn(b'4ea1470d',core)
        self.assertIn(b'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6',NEW_ENTRY)
        self.assertIn(b'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V6',NEW_ENTRY)
        self.assertIn(b"canonical_rel = 'E1_CANONICAL_SOURCE_METADATA.json'",NEW_ENTRY)
        self.assertIn(b"metadata(files[canonical_rel][0])[0].get('canonical') == role",NEW_ENTRY)
        self.assertIn(b'return evidence',NEW_GUARD)
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NewSourceTests))
    sys.setprofile(None)
    receipt=dict(kind='NEW_GOOD_HOLDOUT_V6_EIGHT_SMALL_SOURCE_AST_AND_THREE_DICT_TESTS',passed=result.wasSuccessful(),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),audit=AUDIT,actual_teacher_roles=sorted(CAPTURES),
        executed_only_pure_identity_AST_blocks_and_exact_deepcopy_expression=True,full_prepare_invoked=False,full_metadata_validate_executed=False,
        actual_guard_derive_invoked=False,whole_original_validator_or_reference_function_executed=False,old_test_modules_imported_or_replayed=False,
        original_checkpoint_or_raw_bank_opened=False,actual_preflight_or_native_evaluation=False)
    REPORT.write_bytes(B.encoded(receipt))
    if not result.wasSuccessful() or any(AUDIT.values()):raise SystemExit(1)
