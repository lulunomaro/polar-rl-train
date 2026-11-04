"""NEW12 narrow SOURCE/AST/in-memory selector tests; never import a materializer or old test."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent
W=HERE.parent.parent
AUDIT=dict(model_raw_bank_IO=0,native_imports=0,process_network_locks=0,out_of_scope_writes=0,forbidden_entry_calls=0)
RECORD=sys.argv[1:]==['--record']
assert sys.argv[1:] in ([],['--record'])
def fail(category,message):
    AUDIT[category]+=1;raise AssertionError(message)
def audit(event,args):
    if event=='import' and args[0].split('.')[0] in ('torch','numpy','warp','omni','isaaclab','pxr','rsl_rl'):
        fail('native_imports','native import attempted')
    if event.startswith(('subprocess.','socket.','os.system','os.fork','os.posix_spawn','fcntl.','msvcrt.locking','os.kill')):
        fail('process_network_locks','process/network/lock operation attempted')
    if event in ('os.mkdir','os.remove','os.rmdir','os.rename','os.link','os.symlink'):
        fail('out_of_scope_writes','filesystem mutation attempted')
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=Path(os.fsdecode(args[0]));name=path.name.lower();suffix=path.suffix.lower()
        if suffix in ('.pt','.pth','.npz','.npy','.usd','.raw','.bin') or 'canonical_ledger' in name or 'canonical_budget' in name:
            fail('model_raw_bank_IO','model/raw/bank/budget IO attempted')
        flags=args[2] or 0;write=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write and not (RECORD and path==HERE/'TEST_REPORT.json'):
            fail('out_of_scope_writes','only NEW TEST_REPORT can be written')
        if not write and path.is_absolute() and path.is_relative_to(W) and suffix not in ('.py','.json','.md'):
            fail('model_raw_bank_IO','workspace non-SOURCE read attempted')
def profile(frame,event,arg):
    if event=='call' and Path(frame.f_code.co_filename).name.startswith('stage_good_expert_holdout_v') and frame.f_code.co_name in ('prepare','main','stage','metadata_validate'):
        fail('forbidden_entry_calls','materializer entry called')
sys.addaudithook(audit)
sys.setprofile(profile)
spec=importlib.util.spec_from_file_location('_NEW_d5_source_packager_only',HERE/'build_source_v5.py')
B=importlib.util.module_from_spec(spec)
# Execute the COMPLETE new stdlib-only packager text; avoid importlib's .pyc probe.
exec(compile((HERE/'build_source_v5.py').read_bytes(),str(HERE/'build_source_v5.py'),'exec'),B.__dict__)
OLD=B.read(B.OLD/'stage_good_expert_holdout_v4.py')
NEW=B.read(HERE/'stage_good_expert_holdout_v5.py')
OF,NF=B.functions(OLD),B.functions(NEW)
ROOT='E1_CANONICAL_SOURCE_METADATA.json'
INNER='runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'
# Compile just these TWO unmodified selector statements and the complete original
# need() helper. This is an explicit FAKE AST probe, not prepare/SDK or full metadata.
selector=next(n for n in ast.walk(NF['prepare']) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='canonical_rel' for t in n.targets))
guard=next(n for n in ast.walk(NF['prepare']) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='need' and any(isinstance(a,ast.Constant) and a.value=='actual selected E1 canonical metadata differs' for a in n.value.args))
PROBE=compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(NF['need']),copy.deepcopy(selector),copy.deepcopy(guard)],type_ignores=[])),'<D5_exact_selector_FAKE_AST>','exec')
def probe(role,entries):
    calls=[]
    def metadata(marker):
        calls.append(marker);value=entries[marker]
        return copy.deepcopy(value),json.dumps(value,allow_nan=False).encode()
    files={k:(k,{'bytes':1,'SHA':'a'*64}) for k in entries}
    ns=dict(role=role,files=files,metadata=metadata)
    exec(PROBE,ns)
    return calls

def keywords(node):return {k.arg:k.value for k in node.keywords}
def constant_fields(node):return {k.arg:k.value.value for k in node.keywords if isinstance(k.value,ast.Constant)}
class SourceOnly(unittest.TestCase):
    def test_01_D4_seal_and_complete_old92(self):
        self.assertEqual(len(B.baseline()['files']),10)
        mirror=json.loads(B.read(B.OLD/'SOURCE_MIRROR_INPUTS.json'))
        self.assertEqual(len(mirror['files']),mirror['files_count']);self.assertEqual(len(mirror['files']),92)
        for row in mirror['files']:B.read(W.joinpath(*Path(row['workspace_relative']).parts),(row['bytes'],row['SHA256']))
    def test_02_exact_three_function_diff_and_whole28(self):
        proof=B.analyse(OLD,NEW)
        self.assertEqual(proof['unchanged_D4_functions'],28)
        self.assertEqual(proof['changed_functions'],['preflight_summary','prepare','stage'])
        self.assertEqual(B.derive(OLD),NEW)
        self.assertTrue(all(x['whole_AST_equal'] for x in proof['whole_function_source_proofs']))
    def test_03_actual_root_metadata_exact_roles(self):
        for role,pin in B.ROOT_PINS.items():
            value=json.loads(B.read(B.ROOTS/(role+'_'+ROOT),pin))
            self.assertEqual(value['canonical'],role);self.assertNotEqual(value['role'],role)
            self.assertIs(type(value['original_env']),dict)
    def test_04_root_only_selects_each_role(self):
        for role in B.ROOT_PINS:self.assertEqual(probe(role,{ROOT:{'canonical':role}}),[ROOT])
    def test_05_inner_decoy_never_read(self):
        for role in B.ROOT_PINS:
            self.assertEqual(probe(role,{ROOT:{'canonical':role},INNER:{'canonical':'DECOY'}}),[ROOT])
    def test_06_inner_only_has_no_fallback(self):
        for role in B.ROOT_PINS:
            with self.assertRaisesRegex(ValueError,'actual selected E1 canonical metadata differs'):probe(role,{INNER:{'canonical':role}})
    def test_07_bad_root_not_rescued_by_valid_inner(self):
        for role in B.ROOT_PINS:
            with self.assertRaises(ValueError):probe(role,{ROOT:{'canonical':'OTHER'},INNER:{'canonical':role}})
    def test_08_strict_canonical_no_alias_case_missing(self):
        for role in B.ROOT_PINS:
            for value in ({},{'canonical':None},{'canonical':role.lower()},{'canonical':'E1_CURB'},{'canonical':'E1_SLOPE'},{'role':role}):
                with self.subTest(role=role,value=value),self.assertRaises(ValueError):probe(role,{ROOT:value})
    def test_09_strict_wire_SOURCE_canonical_constants(self):
        def globals_of(raw):
            return {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('ORIGINAL_PLAN_PIN','PUBLISHED_ORIGINAL_PLAN_PIN','ORIGINAL_PLAN_CANONICAL_SHA256')}
        expected={'ORIGINAL_PLAN_PIN':(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1'),
                  'PUBLISHED_ORIGINAL_PLAN_PIN':(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0'),
                  'ORIGINAL_PLAN_CANONICAL_SHA256':'8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a'}
        self.assertEqual(globals_of(OLD),expected);self.assertEqual(globals_of(NEW),expected)
    def test_10_V5_typed_fields_and_unchanged_publication(self):
        ret=next(n for n in NF['preflight_summary'].body if isinstance(n,ast.Return))
        fields=constant_fields(ret.value)
        self.assertEqual(fields['kind'],'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5');self.assertEqual(fields['source_derivation_version'],5)
        receipt=next(n.value for n in ast.walk(NF['stage']) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='receipt' for t in n.targets))
        out=constant_fields(receipt)
        self.assertEqual(out['kind'],'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5');self.assertEqual(out['source_derivation_version'],5)
        for key in ('source_native_enabled','staged','dispatched'):self.assertIs(fields[key],False);self.assertIs(out[key],False)
        self.assertIn('GROUP_PLAN_bytes',keywords(receipt));self.assertIn('GROUP_PLAN_SHA256',keywords(receipt))
        dump=lambda n:ast.dump(n,include_attributes=False)
        self.assertEqual(dump(NF['derive_materialized_runtime_plan']),dump(OF['derive_materialized_runtime_plan']))
        for name in ('metadata_validate','main','source_mappings','native_boundary','validate_preservation','put_once'):
            self.assertEqual(dump(NF[name]),dump(OF[name]))
    def test_11_actual15_captures_and_diagnostic_are_SOURCE_only(self):
        paths,report=B.input_evidence();x=report['receipt']
        self.assertEqual(B.source_reference('F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/build_source_v5.py'),HERE/'build_source_v5.py')
        with self.assertRaises(ValueError):B.source_reference('G:/other_workspace/unrelated.json')
        self.assertEqual(len(report['local_SOURCE_captures']),15);self.assertEqual(x['status'],'PASS');self.assertEqual(x['errors'],[])
        self.assertEqual(x['Gate1'],'UNKNOWN');self.assertIs(x['stage2_GO'],False)
        self.assertEqual(x['vendor']['actual_names'],['__init__.py','contract.py','geometry.py','learner.py','logging.py','networks.py','replay.py'])
        for role in B.ROOT_PINS:
            g=x['guards'][role]
            for key in ('parent_verified_actual_staged_source','state_dict_snapshot_all_parameters_and_buffers','torch_equal_before_each_complete_save','torch_equal_before_success_FINAL','producer_success_FINAL_and_checkpoint_teacher_unchanged'):
                self.assertIs(g[key],True)
            self.assertEqual(g['mother_checkpoint_stat_open_hash'],0);self.assertEqual(g['A1_checkpoint_stat_open_hash'],0)
            self.assertIs(g['actual_source_module_execution_by_this_verifier'],False)
    def test_12_scope_flags_cache_and_no_old_test_import(self):
        index=json.loads(B.read(B.OLD/'SOURCE_INDEX.json'))
        for key in ('enabled','source_native_enabled','staged','dispatched'):self.assertIs(index[key],False)
        cache=next(ast.literal_eval(n.value) for n in NF['metadata_validate'].body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names' for t in n.targets))
        self.assertEqual(len(cache),12);self.assertIn('embedded_teacher_reference_v1',cache)
        self.assertFalse(any(name.startswith(('test_good_holdout_v4','test_good_holdout_v3','stage_good_expert_holdout_v')) for name in sys.modules))
        self.assertTrue(all(value==0 for value in AUDIT.values()))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceOnly))
    passed=result.wasSuccessful() and all(x==0 for x in AUDIT.values())
    report=dict(kind='GOOD_HOLDOUT_V5_NEW_NARROW_SOURCE_REGRESSION_ONLY',passed=passed,tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),audit=AUDIT,
        old_test_modules_imported_or_replayed=False,full_prepare_invoked=False,full_metadata_validate_executed=False,
        actual_prepare_preflight_stage_dispatch_executed=False,actual_parent_worker_executed=False,
        selector_probe_scope='TWO_ORIGINAL_STATEMENTS_PLUS_WHOLE_NEED_AST_IN_MEMORY_ONLY',
        selector_probe_is_not_full_prepare_or_native=True,actual_root2_pins_checked=True,
        actual_capture15_pins_checked=True,whole_remaining28_function_source_AST_checked=True,
        strict_canonical_and_wire_SOURCE_identities_kept=True,V5_typed_fields_AST_checked=True,
        parent_diagnostic_is_historical_SOURCE_evidence_not_this_child_native_run=True,
        actual_native_binding='UNKNOWN',source_native_enabled=False,staged=False,dispatched=False)
    if RECORD:
        raw=B.encoded(report);path=HERE/'TEST_REPORT.json'
        if path.exists():assert path.read_bytes()==raw,'existing NEW receipt differs'
        else:
            with path.open('xb') as stream:stream.write(raw)
    print(json.dumps(report,indent=2));sys.setprofile(None)
    raise SystemExit(0 if passed else 1)
