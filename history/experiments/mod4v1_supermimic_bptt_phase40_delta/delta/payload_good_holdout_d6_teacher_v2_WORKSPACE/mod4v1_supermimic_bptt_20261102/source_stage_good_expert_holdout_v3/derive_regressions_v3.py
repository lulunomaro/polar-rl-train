"""Derive NEW SOURCE regressions from pinned V2 test text, never import/replay old tests.
Only NEW helper + whole unchanged metadata_validate run with synthetic producers.
No old/new prepare, preflight, stage, main, parent, worker or controller is executed.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_stage_good_expert_holdout_v2'
PIN=(24656,'a89a962d453035bf34cef6bc06d3126d5cd07be3335bcc8a360355e01199b8c3')

TEST15='''    def test_15_exact_two_function_V3_whitelist_rest_complete_AST(self):
        first=funcs(R/'source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py')
        old=funcs(R/'source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py')
        new=funcs(HERE/'stage_good_expert_holdout_v3.py')
        changed={n for n in old if AST(old[n])!=AST(new[n])}
        self.assertEqual(changed,{'preflight_summary','stage'});self.assertEqual(len(old)-len(changed),28)
        self.assertEqual(set(new)-set(old),{'derive_materialized_runtime_plan'})
        original_changed={n for n in first if AST(first[n])!=AST(new[n])}
        self.assertEqual(original_changed,{'prepare','preflight_summary','stage'})
        self.assertEqual(len(first)-len(original_changed),22)
        for name in ('prepare','main','metadata_validate','native_boundary','producer_final','put_once','validate_preservation','retain_originals'):
            self.assertEqual(AST(old[name]),AST(new[name]))
        self.assertIn('262144',ast.unparse(new['prepare']))
'''

TEST17='''    def test_17_stage_AST_stream_metadata_before_runtime_plan_publication(self):
        stage=funcs(HERE/'stage_good_expert_holdout_v3.py')['stage'];text=ast.unparse(stage)
        self.assertIn('observed=written',text);self.assertIn('originals=prepared[',text)
        self.assertIn('root / ORIGINAL_PRESERVATION_NAME',text)
        self.assertLess(text.index('outgoing.flush()'),text.index('derive_materialized_runtime_plan('))
        self.assertLess(text.index('os.fsync('),text.index('derive_materialized_runtime_plan('))
        self.assertLess(text.index('validate_preservation('),text.index('derive_materialized_runtime_plan('))
        self.assertLess(text.index('derive_materialized_runtime_plan('),text.index('metadata_validate(runtime_prepared, actual_root=root)'))
        self.assertLess(text.index('metadata_validate(runtime_prepared, actual_root=root)'),text.index("root / 'GROUP_PLAN.json'"))
        self.assertIn("put_once(root / 'GROUP_PLAN.json', runtime_bytes)",text)
        self.assertNotIn('Popen',text)
'''

NEW_METHODS='''    def materialized_fixture(self,seed):
        # These observations are SYNTHETIC metadata, never actual stage evidence.
        # The two original asset identities are read from allowed fixed plan JSON;
        # their symbolic paths are NEVER created/stat'ed/opened. No raw bytes used.
        p=self.prepared(seed);s=self.s
        required=s.original_dependency_map(PLAN['worker_files'],INDEX);originals=dict(p['originals'])
        for row in PLAN['worker_files']:
            if row['relative'].startswith('pinned_assets/'):
                originals[row['relative']]=(self.case/'UNOPENED_FAKE_ASSET_METADATA_ONLY'/row['relative'],dict(bytes=row['bytes'],SHA=row['SHA']))
        materials,proof=s.retain_originals(originals,self.sources,original_root='SYNTHETIC_ORIGINAL_ROOT_NOT_ADMISSION',
            original_plan_SHA=s.ORIGINAL_PLAN_PIN[1],native_root='SYNTHETIC_NATIVE_ROOT_NOT_ADMISSION',required=required)
        aliases=set(self.sources)|set(required)|set(proof['baseline_provenance']['source_to_retained'].values())
        p['plan']['worker_files']=[dict(relative=rel,**materials[rel][1]) for rel in sorted(aliases)]
        p.update(materials=materials,originals=originals,original_preservation=proof,original_dependency_files=required)
        p['encoded_plan']=json.dumps(p['plan'],indent=2,allow_nan=False).encode()
        observed={rel:copy.deepcopy(info) for rel,(_,info) in materials.items()}
        proof=copy.deepcopy(proof);proof['installed']=[dict(relative=row['relative'],**observed[row['relative']]) for row in proof['baseline']]
        proof['installed_status']='ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES'  # Synthetic branch fixture only.
        return p,observed,proof
    def encode_source(self,p):
        p['encoded_plan']=json.dumps(p['plan'],indent=2,allow_nan=False).encode()
    def helper(self,p,observed,proof):
        return self.s.derive_materialized_runtime_plan(p['plan'],p['encoded_plan'],p['materials'],observed,
            originals=p['originals'],preservation=proof,required=p['original_dependency_files'])
    def publication_probe(self,p,observed,proof):
        # Own in-memory fake IO harness, NOT s.stage and not a copied executable stage.
        plan,raw=self.helper(p,observed,proof);q=dict(p,plan=plan,encoded_plan=raw)
        if plan['group_id']!=p['new_root'].name:raise ValueError('runtime plan/root identity differs before publication')
        check=self.validate(q)  # Entire unchanged real metadata function, no schema stub.
        self.emitted.append(dict(name='GROUP_PLAN.json',raw=raw))  # Memory only, no target root/file.
        return q,raw,check
    def assert_no_emit_failure(self,p,observed,proof):
        self.emitted=[]
        with self.assertRaises((ValueError,AssertionError,KeyError,TypeError)):
            self.publication_probe(p,observed,proof)
        self.assertEqual(self.emitted,[]);self.assertFalse(p['new_root'].exists())
    def test_19_new_true_plan_seed29_unmodified_whole_metadata(self):
        p,observed,proof=self.materialized_fixture(20260929);before=copy.deepcopy(p['plan']);encoded=p['encoded_plan']
        q,raw,check=self.publication_probe(p,observed,proof)
        self.assertIs(q['plan']['enabled'],True);self.assertIs(q['plan']['staged'],True)
        self.assertIs(q['plan']['source_native_enabled'],False);self.assertIs(q['plan']['dispatched'],False)
        self.assertEqual(dict(q['plan'],enabled=False,staged=False),before)
        self.assertEqual(p['plan'],before);self.assertEqual(p['encoded_plan'],encoded)
        self.assertEqual(json.loads(raw),q['plan']);self.assertLessEqual(len(raw),262144)
        self.assertTrue(check['passed']);self.assertEqual(check['seed'],20260929)
        self.assertEqual(len(self.emitted),1);self.assertFalse(p['new_root'].exists())
    def test_20_new_true_plan_seed30_unmodified_whole_metadata(self):
        p,observed,proof=self.materialized_fixture(20260930);q,raw,check=self.publication_probe(p,observed,proof)
        self.assertTrue(check['passed']);self.assertEqual(check['purpose'],'GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1')
        self.assertEqual(len(check['task_checks']),2);self.assertTrue(check['full_modules_not_AST_cropped_or_stubbed'])
        self.assertTrue(all(row['cross_seed_pose_rejected'] for row in check['task_checks']))
        self.assertEqual({r['role'] for r in q['plan']['roles']},set(self.s.ROLES));self.assertNotIn('H1_normal',self.s.ROLES)
        self.assertFalse(p['new_root'].exists())
    def test_21_wrong_seed_purpose_member_and_pose_no_emit(self):
        mutations=[lambda p:p['plan'].update(seed=20260928),lambda p:p['plan'].update(seed=20260930),
            lambda p:p['plan'].update(batch_purpose='GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1'),
            lambda p:p['plan']['holdout_protocol'].update(seed=20260930),
            lambda p:p['plan'].update(paired_reset_protocol=self.s.paired_plan(20260930)),
            lambda p:next(r for r in p['plan']['roles'] if r['role']=='SLOPE135').update(seed=20260930)]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                p,o,f=self.materialized_fixture(20260929);mutation(p);self.encode_source(p);self.assert_no_emit_failure(p,o,f)
    def test_22_missing_or_extra_observation_no_emit(self):
        for extra in (False,True):
            p,o,f=self.materialized_fixture(20260929)
            if extra:o['NOT_AN_ACTUAL_MATERIAL.txt']=dict(bytes=1,SHA='f'*64)
            else:o.pop('resume_runtime_contracts_v3.py')
            self.assert_no_emit_failure(p,o,f)
    def test_23_observation_hash_count_or_boolean_tamper_no_emit(self):
        for alias,field,value in [('good_expert_holdout_runtime_v1.py','SHA','0'*64),
            ('single_gpu_group_supervisor.py','bytes',1),('resume_runtime_contracts_v3.py','bytes',True)]:
            p,o,f=self.materialized_fixture(20260929);o[alias][field]=value;self.assert_no_emit_failure(p,o,f)
    def test_24_independent_origin_and_retained_forgery_no_emit(self):
        for field in ('origin','retained','equal_arrays'):
            p,o,f=self.materialized_fixture(20260929)
            if field=='origin':f['baseline_provenance']['original_logical_rows'][0]['input_path']='SPOOFED_SOURCE'
            elif field=='retained':f['baseline_provenance']['source_to_retained'].pop(next(iter(f['baseline_provenance']['source_to_retained'])))
            else:f['baseline'].pop();f['installed']=copy.deepcopy(f['baseline']);f['baseline_SHA']=self.s.preservation_digest(f['baseline'])
            self.assert_no_emit_failure(p,o,f)
    def test_25_SOURCE_flags_original_encoded_and_old_stage_no_activation(self):
        old=funcs(R/'source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py')
        self.assertIn("put_once(root / 'GROUP_PLAN.json', prepared['encoded_plan'])",ast.unparse(old['stage']))
        self.assertNotIn('derive_materialized_runtime_plan',ast.unparse(old['stage']))
        for key in ('enabled','staged','source_native_enabled','dispatched'):
            p,o,f=self.materialized_fixture(20260929);p['plan'][key]=True;self.encode_source(p);self.assert_no_emit_failure(p,o,f)
        self.assertEqual(self.emitted,[])
    def test_26_planned_or_missing_copy_proof_does_not_publish(self):
        for status in ('PLANNED_HASH_IDENTITIES_NOT_ACTUAL_MATERIALIZATION','TEST_SOURCE_READ_HASH_NOT_STAGE',None):
            p,o,f=self.materialized_fixture(20260929);f['installed_status']=status;self.assert_no_emit_failure(p,o,f)
    def test_27_fixed27_missing_asset_dependency_or_pin_tamper_no_emit(self):
        for missing in (True,False):
            p,o,f=self.materialized_fixture(20260929);key=next(k for k in p['original_dependency_files'] if k.startswith('pinned_assets/'))
            if missing:p['original_dependency_files'].pop(key)
            else:p['original_dependency_files'][key]=(1,'f'*64)
            self.assert_no_emit_failure(p,o,f)
    def test_28_changed_SOURCE_bytes_and_original_bound_no_emit(self):
        p,o,f=self.materialized_fixture(20260929);p['encoded_plan']+=b' ';self.assert_no_emit_failure(p,o,f)
        p,o,f=self.materialized_fixture(20260929);p['plan']['SOURCE_ONLY_TEST_OVERSIZE']='x'*262145;self.encode_source(p);self.assert_no_emit_failure(p,o,f)
    def test_29_original_metadata_guard_failure_precedes_fake_emit(self):
        p,o,f=self.materialized_fixture(20260929)
        next(r for r in p['plan']['roles'] if r['role']=='CURB_PROTECTED878')['a1_producer']['FINAL']['checkpoint']['SHA']='0'*64
        self.encode_source(p)
        # Helper verifies material/seed/flags, but never replaces the full producer/cache schema.
        plan,raw=self.helper(p,o,f);self.assertTrue(plan['enabled'])
        self.assert_no_emit_failure(p,o,f)
    def test_30_pure_helper_no_approval_IO_native_or_hidden_activation(self):
        helper=funcs(HERE/'stage_good_expert_holdout_v3.py')['derive_materialized_runtime_plan']
        names=[a.arg for a in helper.args.args+helper.args.kwonlyargs]
        self.assertEqual(names,['source_plan','source_plan_bytes','materials','observed','originals','preservation','required'])
        text=ast.unparse(helper)
        for forbidden in ('approved','Popen','.open(','.read_bytes(','.write_bytes(','metadata_validate(','os.fsync','SDK','GPU_GO'):
            self.assertNotIn(forbidden,text)
        self.assertFalse(any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(helper)))
        source=funcs(HERE/'stage_good_expert_holdout_v3.py')
        self.assertEqual(AST(source['prepare']),AST(funcs(R/'source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py')['prepare']))
        self.assertIn('source_native_enabled=False, staged=False, dispatched=False, materialized=False',ast.unparse(source['preflight_summary']))
    def test_31_receipt_exact_new_hash_fields_and_original_root_rules(self):
        stage=funcs(HERE/'stage_good_expert_holdout_v3.py')['stage'];receipt=next(n.value for n in ast.walk(stage) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='receipt' for t in n.targets))
        fields={k.arg:ast.unparse(k.value) for k in receipt.keywords}
        self.assertEqual(fields['kind'],"'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3'")
        self.assertEqual(fields['GROUP_PLAN_bytes'],'len(runtime_bytes)');self.assertEqual(fields['GROUP_PLAN_SHA256'],'H(runtime_bytes)')
        self.assertEqual(fields['original_plan_SHA'],"prepared['original_plan_SHA']")
        for key in ('source_native_enabled','staged','dispatched'):self.assertEqual(fields[key],'False')
        self.assertEqual(self.s.COMPLETE_NAME,'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
        p,o,f=self.materialized_fixture(20260929);p['new_root']=self.case/'WRONG_SEED_ROOT';self.assert_no_emit_failure(p,o,f)
    def test_32_copy_hash_fsync_loop_and_parent_close_AST_unchanged(self):
        before=funcs(R/'source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py')['stage']
        after=funcs(HERE/'stage_good_expert_holdout_v3.py')['stage']
        a=next(n for n in ast.walk(before) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
        b=next(n for n in ast.walk(after) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
        self.assertEqual(AST(a),AST(b))
        self.assertIn("runtime_plan['group_id'] == root.name",ast.unparse(after))
        self.assertEqual(H((R/'source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py').read_bytes()),'4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f')
'''


def H(raw):return hashlib.sha256(raw).hexdigest()
def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)
def method(text,name,new):
    nodes=[n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name];assert len(nodes)==1
    node=nodes[0];lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])


def main():
    raw=(OLD/'test_good_holdout_v2_source.py').read_bytes();assert (len(raw),H(raw))==PIN
    text=raw.decode('utf-8')
    text=once(text,"(R/'source_good_expert_holdout_subset_v1','GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json')]",
        "(R/'source_good_expert_holdout_subset_v1','GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'),\n        (R/'source_stage_good_expert_holdout_v2','SOURCE_SEAL.json')]")
    text=text.replace("HERE/'stage_good_expert_holdout_v2.py'","HERE/'stage_good_expert_holdout_v3.py'")
    text=text.replace('_good_holdout_source_v2','_good_holdout_source_v3').replace('SOURCE_ONLY_V2_NOT_STAGE_','SOURCE_ONLY_V3_NOT_STAGE_')
    text=once(text,'self.case.mkdir();self.fake_paths={}','self.case.mkdir();self.fake_paths={};self.emitted=[]')
    text=method(text,'test_15_exact_three_function_whitelist_rest_complete_AST',TEST15)
    text=method(text,'test_17_stage_AST_binds_actual_stream_and_sidecar_separate_from_plan',TEST17)
    text=once(text,'\n\ndef main():','\n'+NEW_METHODS+'\n\ndef main():')
    text=once(text,"kind='GOOD_HOLDOUT_V2_NEW_SOURCE_REGRESSION_ONLY'","kind='GOOD_HOLDOUT_V3_NEW_SOURCE_REGRESSION_ONLY'")
    text=once(text,'old18_tests_replayed=False,actual_prepare_preflight_stage_dispatch_executed=False,actual_parent_worker_executed=False,',
        'old18_tests_replayed=False,V2_test_module_imported_or_replayed=False,actual_prepare_preflight_stage_dispatch_executed=False,actual_parent_worker_executed=False,\n        true_plan_two_seed_whole_metadata_passed=True,publication_probe_is_own_in_memory_fake_IO_not_stage=True,negative_publication_probes_emit_nothing=True,')
    parsed=ast.parse(text);cases=[n for n in ast.walk(parsed) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')];assert len(cases)==32
    target=HERE/'test_good_holdout_v3_source.py';result=text.encode()
    if target.exists():assert target.read_bytes()==result,'existing NEW test SOURCE differs'
    else:
        with target.open('xb')as stream:stream.write(result)
    print(json.dumps(dict(kind='NEW_V3_SOURCE_TEST_TEXT_DERIVED_NOT_OLD_TEST_REPLAY',tests=32,bytes=len(result),SHA256=H(result),actual_stage_calls=0)))

if __name__=='__main__':main()
