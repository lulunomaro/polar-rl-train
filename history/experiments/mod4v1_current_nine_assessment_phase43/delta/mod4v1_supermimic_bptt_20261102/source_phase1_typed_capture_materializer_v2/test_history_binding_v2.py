"""Six new AST/pure-memory cases. No old suites or materializer execution."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import unittest
from historical_b2_binding_v2 import verify_published_B2_handoff

HERE=Path(__file__).resolve().parent
R=HERE.parent
V1=R/'source_phase1_typed_capture_materializer_v1'
H=lambda raw:hashlib.sha256(raw).hexdigest()


def member_rows(raw, folder):
    rows=[]
    for row in json.loads(raw)['files']:
        actual=(folder/row['relative']).read_bytes()
        assert (len(actual),H(actual))==(row['bytes'],row['sha256'])
        rows.append(dict(relative=row['relative'],bytes=len(actual),SHA256=H(actual)))
    return rows


class HistoryBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((R/'source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json').read_bytes())
        cls.handoff=json.loads((R/'source_phase1_sensor_reset_identity_diagnosis_v1/FINAL_SOURCE_HANDOFF_RECEIPT.json').read_bytes())
        cls.b2_raw=(R/'source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json').read_bytes()
        cls.b4_raw=(R/'source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json').read_bytes()
        cls.actual13=member_rows(cls.b2_raw,R/'source_phase1_passive_sensor_capture_v2')

    def data(self):
        return copy.deepcopy(self.index),copy.deepcopy(self.handoff),self.b2_raw,copy.deepcopy(self.actual13)

    def test_01_complete_function_and_active_guards_unchanged(self):
        old=(V1/'stage_phase1_typed_capture_v1.py').read_text(encoding='utf-8')
        new=(HERE/'stage_phase1_typed_capture_v2.py').read_text(encoding='utf-8')
        a={n.name:n for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
        b={n.name:n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(list(a),list(b));self.assertEqual(len(a),14)
        for name,node in a.items():
            other=b[name]
            same=ast.dump(node,include_attributes=False)==ast.dump(other,include_attributes=False)
            self.assertEqual(same,name!='verify_B2_source_closure')
            if same:self.assertEqual(ast.get_source_segment(old,node),ast.get_source_segment(new,other))
        assignments={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(new).body
                     if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
                     and n.targets[0].id in ('DEPENDENCY_SEALS','ROOT_PREFIX','MATERIALIZER_SOURCE_PUBLICATION')}
        self.assertEqual(assignments['DEPENDENCY_SEALS']['sensor'],(21,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3'))
        self.assertEqual(assignments['ROOT_PREFIX'],'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
        self.assertEqual(assignments['MATERIALIZER_SOURCE_PUBLICATION'],2)
        closure=ast.get_source_segment(new,b['verify_B2_source_closure'])
        self.assertNotIn("DEPENDENCY_SEALS['sensor']",closure)
        self.assertIn("verify_package(historical_path.parent,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a',13)",closure)
        self.assertLess(closure.index('verify_package(historical_path.parent'),closure.index('verify_published_B2_handoff('))
        self.assertIn('historical_B2_reference_binding=historical_binding',closure)
        derivation=ast.parse((HERE/'derive_history_binding_v2.py').read_bytes())
        text_constants={n.targets[0].id:ast.literal_eval(n.value) for n in derivation.body
                        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('OLD','NEW')}
        restored=new.replace(text_constants['NEW'],text_constants['OLD'],1)
        restored=restored.replace('from historical_b2_binding_v2 import verify_published_B2_handoff\n','',1)
        restored=restored.replace('MATERIALIZER_SOURCE_PUBLICATION=2\n','',1)
        restored=restored.replace('        historical_B2_reference_binding=historical_binding,\n','',1)
        self.assertEqual(restored,old)
        for name in ('static_source_helpers_v1.py','typed_source_support_v1.py','SOURCE_MIRROR_INPUTS.json'):
            self.assertEqual((HERE/name).read_bytes(),(V1/name).read_bytes())
        self.assertEqual(len([n for n in ast.parse((HERE/'static_source_helpers_v1.py').read_bytes()).body if isinstance(n,ast.FunctionDef)]),17)
        for name,pin in [('PRODUCER_ABI.json',(9441,'e805ecb63aa61c81324c62488981a49973a99381dc14cc4d37b911c4a70f696a')),
                         ('FINITE_SOURCE_BUNDLE.json',(11663,'5b633338090b8801282e8b2ee824d74d413495efa39f93708cda44bff2222155')),
                         ('SOURCE_SEAL.json',(3503,'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966'))]:
            raw=(R/'source_phase1_typed_native_capture_v1'/name).read_bytes();self.assertEqual((len(raw),H(raw)),pin)
        finite=json.loads((R/'source_phase1_typed_native_capture_v1/FINITE_SOURCE_BUNDLE.json').read_bytes())
        self.assertEqual(len(finite['full_module_files']),34)
        source=ast.parse((HERE/'historical_b2_binding_v2.py').read_bytes())
        selector=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='verify_published_B2_handoff')
        self.assertFalse(any(isinstance(n,ast.Name) and n.id=='DEPENDENCY_SEALS' for n in ast.walk(selector)))

    def test_02_published_B2_passes_with_distinct_active_B4(self):
        index,handoff,raw,actual=self.data()
        self.assertNotEqual(index['original_B2_reference_seal']['SHA256'],index['dependency_seals']['sensor']['SHA256'])
        result=verify_published_B2_handoff(index,handoff,raw,actual)
        self.assertEqual(result['raw_seal_SHA256'],'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a')
        self.assertEqual(result['complete_members'],13);self.assertIsNone(result['original_content_root_sha256'])
        self.assertIs(result['active_sensor_used_as_expected'],False)
        independent=copy.deepcopy(index);independent.pop('dependency_seals')
        self.assertEqual(verify_published_B2_handoff(independent,handoff,raw,actual),result)

    def test_03_active_successor_is_not_historical_reference(self):
        for variant in ('index','handoff','raw'):
            with self.subTest(variant=variant):
                index,handoff,raw,actual=self.data();active=index['dependency_seals']['sensor']
                if variant=='index':index['original_B2_reference_seal']=copy.deepcopy(active)
                elif variant=='handoff':
                    handoff['B2_source_seal']=dict(path=active['path'],bytes=active['bytes'],sha256=active['SHA256'])
                    handoff['B2_members']=copy.deepcopy(json.loads(self.b4_raw)['files'])
                else:raw=self.b4_raw
                with self.assertRaises(ValueError):verify_published_B2_handoff(index,handoff,raw,actual)

    def test_04_claims_cannot_generate_expected_raw_pin(self):
        index,handoff,raw,actual=self.data();forged=json.loads(raw)
        forged['files'][0]['sha256']='0'*64
        fake_raw=(json.dumps(forged,indent=2)+'\n').encode();fake_sha=H(fake_raw)
        index['original_B2_reference_seal'].update(bytes=len(fake_raw),SHA256=fake_sha)
        handoff['B2_source_seal'].update(bytes=len(fake_raw),sha256=fake_sha)
        actual[0]['SHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'fixed independently published raw seal pin differs'):
            verify_published_B2_handoff(index,handoff,fake_raw,actual)
        index,handoff,raw,actual=self.data();index['original_B2_reference_seal']['SHA256']='0'*64
        with self.assertRaises(ValueError):verify_published_B2_handoff(index,handoff,raw,actual)

    def test_05_all_13_sourceproof_members_are_required(self):
        variants=('missing_actual','duplicate_actual','changed_actual','extra_actual','missing_index','changed_handoff','bool_proof','float_size')
        for variant in variants:
            with self.subTest(variant=variant):
                index,handoff,raw,actual=self.data()
                if variant=='missing_actual':actual.pop()
                elif variant=='duplicate_actual':actual[-1]=copy.deepcopy(actual[0])
                elif variant=='changed_actual':actual[0]['SHA256']='0'*64
                elif variant=='extra_actual':actual.append(copy.deepcopy(actual[0]))
                elif variant=='missing_index':index['original_B2_reference_seal']['members'].pop()
                elif variant=='changed_handoff':handoff['B2_members'][0]['bytes']+=1
                elif variant=='bool_proof':actual=True
                else:actual[0]['bytes']=float(actual[0]['bytes'])
                with self.assertRaises(ValueError):verify_published_B2_handoff(index,handoff,raw,actual)

    def test_06_no_fallback_null_repair_or_origin_drift(self):
        variants=('absent_reference','wrong_status','wrong_handoff_path','relative_claim','index_float_bytes','handoff_float_bytes','root_false','claim_without_members')
        for variant in variants:
            with self.subTest(variant=variant):
                index,handoff,raw,actual=self.data()
                if variant=='absent_reference':index.pop('original_B2_reference_seal')
                elif variant=='wrong_status':handoff['status']='UNKNOWN'
                elif variant=='wrong_handoff_path':handoff['B2_source_seal']['path']=handoff['B2_source_seal']['path'].replace('capture_v2','capture_v4')
                elif variant=='relative_claim':handoff['B2_source_seal']['path']='source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json'
                elif variant=='index_float_bytes':index['original_B2_reference_seal']['bytes']=2909.0
                elif variant=='handoff_float_bytes':handoff['B2_source_seal']['bytes']=2909.0
                elif variant=='root_false':index['original_B2_reference_seal']['content_root_sha256']=False
                else:handoff.pop('B2_members')
                with self.assertRaises(ValueError):verify_published_B2_handoff(index,handoff,raw,actual)
