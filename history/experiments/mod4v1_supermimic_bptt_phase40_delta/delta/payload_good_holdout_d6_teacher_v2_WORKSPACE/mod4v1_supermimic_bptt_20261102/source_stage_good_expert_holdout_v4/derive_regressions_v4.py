"""Derive NEW D4 stdlib/FAKE regressions from pinned D3 text, not old tests.
No materializer prepare/preflight/stage/main or parent/worker is called.
"""
from pathlib import Path
import ast
import hashlib
import sys
import json
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_stage_good_expert_holdout_v3'
OLD_PIN=(37330,'faf1fa3b82e43083431e56f19fa08928cfab7d67dddacac5d6a8e70074e37c7e')
TEST15='''    def test_15_exact_three_function_D4_whitelist_rest_complete_AST(self):
        first=funcs(R/'source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py')
        old=funcs(R/'source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py')
        new=funcs(HERE/'stage_good_expert_holdout_v4.py')
        changed={n for n in old if AST(old[n])!=AST(new[n])}
        self.assertEqual(changed,{'prepare','preflight_summary','stage'});self.assertEqual(len(old)-len(changed),28)
        self.assertEqual(set(new),set(old))
        original_changed={n for n in first if AST(first[n])!=AST(new[n])}
        self.assertEqual(original_changed,{'prepare','preflight_summary','stage'});self.assertEqual(len(first)-len(original_changed),22)
        for name in ('main','metadata_validate','native_boundary','producer_final','put_once','validate_preservation','retain_originals','derive_materialized_runtime_plan','source_mappings'):
            self.assertEqual(AST(old[name]),AST(new[name]))
        self.assertIn('262144',ast.unparse(new['prepare']))
'''
EXTRA='''    def wire_guard_probe(self,raw,decoded=None):
        # Execute ONLY the two pure identity assertions from SOURCE AST, not prepare.
        # Full original metadata_validate elsewhere is imported/exercised whole.
        prepare=funcs(HERE/'stage_good_expert_holdout_v4.py')['prepare']
        messages={'fixed original GROUP_PLAN wire bytes differ','fixed original GROUP_PLAN decoded canonical identity differs'}
        guards=[n for n in prepare.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
            and isinstance(n.value.func,ast.Name) and n.value.func.id=='need' and len(n.value.args)==2
            and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value in messages]
        self.assertEqual(len(guards),2)
        scope=dict(old_raw=raw,old=json.loads(raw) if decoded is None else decoded,json=json,H=self.s.H,need=self.s.need,
            ORIGINAL_PLAN_PIN=self.s.ORIGINAL_PLAN_PIN,ORIGINAL_PLAN_CANONICAL_SHA256=self.s.ORIGINAL_PLAN_CANONICAL_SHA256)
        exec(compile(ast.Module(body=copy.deepcopy(guards),type_ignores=[]),'D4_SOURCE_TWO_PURE_GUARD_EXPRESSIONS','exec'),scope)
        return True
    def test_33_exact_wire_and_published_SOURCE_are_separate(self):
        w=WIRE_PATH.read_bytes();p=PLAN_PATH.read_bytes();d=DIAG_PATH.read_bytes()
        self.assertEqual((len(w),H(w)),(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1'))
        self.assertEqual((len(p),H(p)),self.s.PUBLISHED_ORIGINAL_PLAN_PIN);self.assertNotEqual(self.s.ORIGINAL_PLAN_PIN,self.s.PUBLISHED_ORIGINAL_PLAN_PIN)
        canonical=lambda b:json.dumps(json.loads(b),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
        self.assertEqual(json.loads(w),json.loads(p));self.assertEqual(H(canonical(w)),self.s.ORIGINAL_PLAN_CANONICAL_SHA256)
        self.assertEqual(H(canonical(p)),self.s.ORIGINAL_PLAN_CANONICAL_SHA256)
        self.assertEqual(p.replace(b'\\r\\n',b'\\n'),w);self.assertEqual(p.count(b'\\r\\n'),273)
        self.assertEqual((len(d),H(d)),(1459,'673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38'))
        diag=json.loads(d);self.assertTrue(diag['whole_decoded_values_equal']);self.assertEqual(diag['differences_first30'],[])
        self.assertTrue(self.wire_guard_probe(w))
    def test_34_equal_canonical_nonfixed_wires_rejected_not_repaired(self):
        wire=WIRE_PATH.read_bytes();canonical=json.dumps(json.loads(wire),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
        for raw in (PLAN_PATH.read_bytes(),wire+b'\\n',wire.replace(b'\\n',b'\\r\\n'),canonical):
            with self.subTest(bytes=len(raw),SHA=H(raw)):
                self.assertEqual(json.loads(raw),json.loads(wire));self.assertNotEqual((len(raw),H(raw)),self.s.ORIGINAL_PLAN_PIN)
                with self.assertRaisesRegex(ValueError,'wire bytes differ'):self.wire_guard_probe(raw)
        self.assertEqual(WIRE_PATH.read_bytes(),wire)
    def test_35_prepare_only_one_extra_canonical_guard_and_no_relaxed_pin(self):
        old=funcs(R/'source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py')['prepare']
        new=copy.deepcopy(funcs(HERE/'stage_good_expert_holdout_v4.py')['prepare'])
        extra=[n for n in new.body if 'ORIGINAL_PLAN_CANONICAL_SHA256' in ast.unparse(n)]
        self.assertEqual(len(extra),1);new.body.remove(extra[0])
        for node in ast.walk(new):
            if isinstance(node,ast.Constant) and node.value=='fixed original GROUP_PLAN wire bytes differ':
                node.value='fixed published original GROUP_PLAN bytes differ'
        self.assertEqual(AST(old),AST(new))
        wire=WIRE_PATH.read_bytes();decoded=json.loads(wire);decoded['asset_SHA']='0'*64
        with self.assertRaisesRegex(ValueError,'decoded canonical identity differs'):self.wire_guard_probe(wire,decoded)
        self.assertNotIn('ORIGINAL_PLAN_PIN = (14385', (HERE/'stage_good_expert_holdout_v4.py').read_text(encoding='utf-8').split('PUBLISHED_ORIGINAL_PLAN_PIN')[0])
    def test_36_fixed27_from_actual_wire_and_two_seed_whole_metadata(self):
        wire=json.loads(WIRE_PATH.read_bytes())
        self.assertEqual(self.s.original_dependency_map(wire['worker_files'],INDEX),self.s.original_dependency_map(PLAN['worker_files'],INDEX))
        self.assertEqual(len(wire['worker_files']),27)
        for seed in (20260929,20260930):
            p,o,f=self.materialized_fixture(seed);self.assertEqual(p['original_plan_SHA'],self.s.ORIGINAL_PLAN_PIN[1])
            q,raw,check=self.publication_probe(p,o,f)
            self.assertTrue(check['passed']);self.assertEqual(check['seed'],seed)
            self.assertEqual(dict(q['plan'],enabled=False,staged=False),p['plan'])
            self.assertFalse(p['new_root'].exists())
'''


def H(raw):return hashlib.sha256(raw).hexdigest()
def once(text,old,new):
    assert text.count(old)==1,old[:110]
    return text.replace(old,new,1)
def method(text,name,new):
    nodes=[n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name];assert len(nodes)==1
    node=nodes[0];lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])


def main():
    raw=(OLD/'test_good_holdout_v3_source.py').read_bytes();assert (len(raw),H(raw))==OLD_PIN
    text=raw.decode()
    text=once(text,"PLAN_PATH=T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'",
        "PLAN_PATH=T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'\n"
        "WIRE_PATH=R/'discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'\n"
        "DIAG_PATH=R/'reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json'")
    text=once(text,"(R/'source_stage_good_expert_holdout_v2','SOURCE_SEAL.json')]",
        "(R/'source_stage_good_expert_holdout_v2','SOURCE_SEAL.json'),\n        (R/'source_stage_good_expert_holdout_v3','SOURCE_SEAL.json')]")
    text=text.replace("HERE/'stage_good_expert_holdout_v3.py'","HERE/'stage_good_expert_holdout_v4.py'")
    text=text.replace('_good_holdout_source_v3','_good_holdout_source_v4').replace('SOURCE_ONLY_V3_NOT_STAGE_','SOURCE_ONLY_V4_NOT_STAGE_')
    text=once(text,'self.assertEqual((len(raw),H(raw)),self.s.ORIGINAL_PLAN_PIN)','self.assertEqual((len(raw),H(raw)),self.s.PUBLISHED_ORIGINAL_PLAN_PIN)')
    text=method(text,'test_15_exact_two_function_V3_whitelist_rest_complete_AST',TEST15)
    text=once(text,"self.assertEqual(AST(source['prepare']),AST(funcs(R/'source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py')['prepare']))",
        "self.assertEqual(AST(source['source_mappings']),AST(funcs(R/'source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py')['source_mappings']))")
    text=once(text,'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4')
    text=once(text,'\n\ndef main():','\n'+EXTRA+'\n\ndef main():')
    text=once(text,"kind='GOOD_HOLDOUT_V3_NEW_SOURCE_REGRESSION_ONLY'","kind='GOOD_HOLDOUT_V4_NEW_SOURCE_REGRESSION_ONLY'")
    text=once(text,'V2_test_module_imported_or_replayed=False,','V2_test_module_imported_or_replayed=False,D3_test_module_imported_or_replayed=False,')
    text=once(text,"original_assets_vendor7_fullstatic_integrity_actually_tested=False,actual_native_binding='UNKNOWN'",
        "strict_actual_wire_and_canonical_guard_exercised_in_FAKE_fixture=True,full_prepare_invoked=False,\n        canonical_equal_not_treated_as_wire_identity=True,original_assets_vendor7_fullstatic_integrity_actually_tested=False,actual_native_binding='UNKNOWN'")
    cases=[n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')];assert len(cases)==36
    data=text.encode();target=HERE/'test_good_holdout_v4_source.py'
    if target.exists():assert target.read_bytes()==data,'NEW D4 SOURCE tests differ'
    else:
        with target.open('xb')as stream:stream.write(data)
    print(json.dumps(dict(kind='NEW_D4_SOURCE_REGRESSIONS_DERIVED_NOT_OLD_TEST_REPLAY',tests=36,bytes=len(data),SHA256=H(data),actual_prepare_stage_calls=0)))

if __name__=='__main__':main()
