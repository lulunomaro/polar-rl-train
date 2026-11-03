"""Derive NEW regression source, not import/execute sealed V2 test scripts."""
from pathlib import Path
import ast
import hashlib

HERE=Path(__file__).resolve().parent;R=HERE.parent
SOURCE=R/'source_phase1_capture_materializer_v2/test_materializer_stdlib_v2.py'
V2_SEAL_PIN=(2249,'399b18c25437f2c22d84aa89dbe50805206848f4f1f8751c6a2f1638f1a61e24')

METHOD30='''    def test_30_V3_whitelist_preserves_V2_entire_functions_and_wire_names(self):
        old_path=R/'source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py';new_path=HERE/'stage_phase1_capture_v3.py'
        old=whole_ast(old_path);new=whole_ast(new_path)
        self.assertEqual(set(new)-set(old),{'normalize_B2_source_paths','verify_B2_source_closure'})
        self.assertEqual({n for n in old if old[n]!=new[n]},{'load_sources','metadata_validate','preflight_summary','stage'})
        for name in set(old)-{'load_sources','metadata_validate','preflight_summary','stage'}:self.assertEqual(old[name],new[name],name)
        oldtext=old_path.read_text();newtext=new_path.read_text()
        oldstage=next(n for n in ast.parse(oldtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        newstage=next(n for n in ast.parse(newtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        self.assertEqual(ast.get_source_segment(oldtext,oldstage).replace("kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'"),ast.get_source_segment(newtext,newstage))
        self.assertEqual(m.ROOT_PREFIX,'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
        self.assertEqual(m.COMPLETE_NAME,'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json')
        self.assertEqual(m.SOURCE_DERIVATION_VERSION,3)
'''

EXTRA=r'''
    def mirror(self):
        root=self.root/'ISOLATED_R_SOURCE_MIRROR_NOT_STAGE';paths={Path(p) for p,_ in self.bundle['sources'].values()}
        paths.add(m.reference_path(R,self.bundle['index']['original_index']['path']))
        paths.update(m.reference_path(R,rel) for rel in self.bundle['index']['all_actuation_original_sources'])
        paths.update(m.reference_path(R,row['source_relative']) for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values())
        for path in paths:
            self.assertTrue(path.is_relative_to(R));put(root/path.relative_to(R),path.read_bytes())
        return root

    def mirror_load_no_original_R_fallback(self,root):
        # Actual original API is imported from this mirror and all reads/stats
        # below the original R but outside this mirror are denied for this call.
        old_open,old_io_open,old_stat,old_lstat=builtins.open,io.open,os.stat,os.lstat
        def guard_path(path):
            if isinstance(path,(str,bytes,os.PathLike)):
                path=Path(os.fsdecode(path))
                if path.is_absolute() and path.is_relative_to(R) and not path.is_relative_to(root):
                    raise AssertionError('isolated mirror attempted original R fallback: '+str(path))
        def wrap(function):
            def call(path,*a,**kw):guard_path(path);return function(path,*a,**kw)
            return call
        builtins.open,io.open,os.stat,os.lstat=map(wrap,(old_open,old_io_open,old_stat,old_lstat))
        try:return m.load_sources(root)
        finally:builtins.open,io.open,os.stat,os.lstat=old_open,old_io_open,old_stat,old_lstat

    def test_34_complete_B2_435_155_plus_four_JSON_and_diagnostics(self):
        proof=self.bundle['receipt']['B2_source_closure']
        self.assertEqual(proof['original_source_pin_references'],435);self.assertEqual(proof['actual_original_Python_files'],155)
        self.assertEqual(proof['extra_entry_routing_JSON_files'],4);self.assertEqual(proof['diagnostic_source_references'],4)
        self.assertEqual(proof['diagnostic_final_handoff'],1);self.assertEqual(proof['source_dependency_files'],164)
        self.assertTrue(proof['full_manifest_regenerated_equal_after_explicit_R_source_path_normalization'])
        self.assertFalse(proof['plant_modules_imported']);self.assertEqual(proof['reset_or_adapter_or_SDK_constructor_calls'],0)
        self.assertEqual(proof['actual_runtime_root_binding'],'UNKNOWN')

    def test_35_explicit_source_path_roots_only_no_suffix_repair(self):
        root=self.root/'R_COPY';rel='discovery/source.py'
        for prefix in (R.as_posix(),root.as_posix()):
            result=m.normalize_B2_source_paths({'source_path':prefix+'/'+rel},root)
            self.assertEqual(result,{'source_path':rel})
        for bad in ('/outside/'+m.R_NAME+'/'+rel,'/outside/'+rel,'discovery/source.py',
                    'F:/RMPOLAR-RL/'+m.R_NAME+'/discovery/../source.py',
                    'F:/RMPOLAR-RL/'+m.R_NAME+'/discovery/./source.py',
                    'F:/RMPOLAR-RL/'+m.R_NAME+'/../'+rel):
            with self.subTest(path=bad):
                with self.assertRaises(ValueError):m.normalize_B2_source_paths({'source_path':bad},root)

    def test_36_normalization_changes_only_source_path_not_hash_or_other_fields(self):
        example={'source_path':R.as_posix()+'/discovery/source.py','source_sha256':'a'*64,
                 'module':'original.module','qualname':'Original.reset','signature':'(self, ids)',
                 'freevars':['adapter','original'],'status':'SOURCE_CONFIRMED_LIVE_UNKNOWN','physics_dt':.0025}
        original=copy.deepcopy(example);result=m.normalize_B2_source_paths(example,self.root/'MIRROR')
        self.assertEqual(example,original);expected=copy.deepcopy(original);expected['source_path']='discovery/source.py'
        self.assertEqual(result,expected)
        for key,value in (('source_sha256','b'*64),('module','changed.module'),('qualname','changed'),('physics_dt',.02),('status','PASS')):
            changed=copy.deepcopy(original);changed[key]=value
            self.assertNotEqual(m.normalize_B2_source_paths(changed,self.root/'MIRROR'),result,key)

    def test_37_isolated_complete_R_mirror_rebuilds_actual_B2_no_original_fallback(self):
        root=self.mirror();bundle=self.mirror_load_no_original_R_fallback(root)
        self.assertEqual(bundle['receipt']['worker']['content_root_sha256'],m.WORKER_ROOT_SHA)
        self.assertTrue(bundle['receipt']['B2_source_closure']['full_manifest_regenerated_equal_after_explicit_R_source_path_normalization'])
        self.assertEqual(len(bundle['B2_source_inputs']),164)
        self.assertTrue(all(Path(p).is_relative_to(root) for p,_ in bundle['sources'].values()))

    def test_38_each_missing_E1_routing_JSON_is_hard_missing_dependency(self):
        root=self.mirror()
        for role in m.B2_ENTRY_ROUTING_PINS:
            path=root/'discovery/reward_command_audit_v1'/role/'E1_CANONICAL_SOURCE_METADATA.json';raw=path.read_bytes()
            self.assertTrue(path.is_relative_to(self.root));path.unlink()
            try:
                with self.assertRaises(FileNotFoundError):self.mirror_load_no_original_R_fallback(root)
            finally:put(path,raw)

    def test_39_changed_full_original_Python_source_is_not_normalized_into_pass(self):
        root=self.mirror();rel=next(rel for rel in self.bundle['B2_source_inputs'] if rel.endswith('.py'))
        path=root/rel;put(path,path.read_bytes()+b'\n# CHANGED_FAKE_SOURCE_COPY_ONLY\n')
        with self.assertRaises(ValueError):self.mirror_load_no_original_R_fallback(root)

    def test_40_missing_diagnostic_reference_is_not_optional(self):
        root=self.mirror();row=self.bundle['index']['sensor_reset_diagnostic_source_references']['source_references'][0]
        original=m.reference_path(R,row['path']);path=root/original.relative_to(R)
        self.assertTrue(path.is_relative_to(self.root));path.unlink()
        with self.assertRaises(FileNotFoundError):self.mirror_load_no_original_R_fallback(root)

    def test_41_all_five_V3_candidate_bytes_identical_sealed_V2(self):
        for name in ('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py',
                     'worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py'):
            self.assertEqual((R/m.WORKER_FOLDER/name).read_bytes(),(R/'source_phase1_capture_worker_v2'/name).read_bytes(),name)

    def test_42_original_B2_builder_only_not_new_strict_reset_verifier(self):
        path=HERE/'stage_phase1_capture_v3.py';text=path.read_text();tree=ast.parse(text)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_B2_source_closure')
        body=ast.get_source_segment(text,node)
        self.assertIn('api.build_manifest(root=source_root)',body)
        for forbidden in ('verify_existing_reset_chain(', 'diagnose_reset_chain(', 'reset(', 'capacity_ctor(', 'parent_five_storage('):
            self.assertNotIn(forbidden,body)
        self.assertLess(body.index('sealed B2 manifest raw identity differs'),body.index('normalize_B2_source_paths(manifest'))
'''


def main():
    raw=SOURCE.read_bytes();text=raw.decode()
    # The sealed source pin is checked through the immutable V2 seal, not guessed.
    seal_raw=(SOURCE.parent/'SOURCE_SEAL.json').read_bytes()
    if (len(seal_raw),hashlib.sha256(seal_raw).hexdigest())!=V2_SEAL_PIN:raise ValueError('immutable V2 materializer seal changed')
    seal=__import__('json').loads(seal_raw)
    row=next(r for r in seal['files'] if r['relative']==SOURCE.name)
    if (len(raw),hashlib.sha256(raw).hexdigest())!=(row['bytes'],row['SHA256']):raise ValueError('sealed V2 regression text changed')
    tree=ast.parse(text);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SourceTests')
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='test_30_V2_whitelist_preserves_V1_entire_functions_and_wire_names')
    lines=text.splitlines(keepends=True);lines[method.lineno-1:method.end_lineno]=[METHOD30]
    text=''.join(lines).replace('import stage_phase1_capture_v2 as m','import stage_phase1_capture_v3 as m').replace("HERE/'stage_phase1_capture_v2.py'","HERE/'stage_phase1_capture_v3.py'")
    text=text.replace("(R/'source_phase1_capture_worker_v2','SOURCE_SEAL.json')):","(R/'source_phase1_capture_worker_v2','SOURCE_SEAL.json'),\n          (R/'source_phase1_capture_materializer_v2','SOURCE_SEAL.json'),\n          (R/'source_phase1_capture_worker_v3','SOURCE_SEAL.json')):")
    text=text.replace("\n\ndef main():",'\n'+EXTRA+'\n\ndef main():',1)
    text=text.replace('PHASE1_MATERIALIZER_SOURCE_REAL_TEXT_PIN_WHOLE_BOOTSTRAP_FAKE_STATIC_AST_ONLY_V2','PHASE1_MATERIALIZER_SOURCE_REAL_B2_MANIFEST_MIRROR_BOOTSTRAP_FAKE_STATIC_AST_ONLY_V3')
    ast.parse(text);target=HERE/'test_materializer_stdlib_v3.py';out=text.encode()
    if target.exists():
        if target.read_bytes()!=out:raise ValueError('existing NEW V3 regression differs')
    else:
        with target.open('xb') as stream:stream.write(out)
    print('NEW_V3_REGRESSION_SOURCE_DERIVED_NO_TEST_EXECUTION')

if __name__=='__main__':main()
