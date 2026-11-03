"""Prepare NEW V4 SOURCE regressions from complete immutable V3 test text.
No old test module import/replay. Run only after exact final worker4 binding and entry derivation.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
R=HERE.parent
V3=R/'source_phase1_capture_materializer_v3'
TEST_PIN=(38903,'1742c0d91bcff4b37782b7484245d7c5933012e21d8b29ccec471552627803ec')


def H(raw):return hashlib.sha256(raw).hexdigest()


def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('one exact V4 regression target required: '+old[:120])
    return text.replace(old,new,1)


def main():
    if not (HERE/'stage_phase1_capture_v4.py').is_file():raise ValueError('PENDING_FINAL_WORKER4_PINS_AND_DERIVED_ENTRY; no tests emitted')
    raw=(V3/'test_materializer_stdlib_v3.py').read_bytes()
    if (len(raw),H(raw))!=TEST_PIN:raise ValueError('immutable complete V3 test source differs')
    text=raw.decode().replace('import stage_phase1_capture_v3 as m','import stage_phase1_capture_v4 as m')
    text=text.replace("HERE/'stage_phase1_capture_v3.py'","HERE/'stage_phase1_capture_v4.py'")
    text=replace(text,"(R/'source_phase1_capture_worker_v3','SOURCE_SEAL.json')):","(R/'source_phase1_capture_worker_v3','SOURCE_SEAL.json'),\n          (R/'source_phase1_capture_materializer_v3','SOURCE_SEAL.json'),\n          (R/'source_stage_good_expert_holdout_v2','SOURCE_SEAL.json'),\n          (R/'source_phase1_capture_worker_v4','SOURCE_SEAL.json')):")
    begin=text.index('    def test_30_V3_whitelist_preserves_V2_entire_functions_and_wire_names')
    end=text.index('    def test_31_worker_main_reuses_actual_bootstrap_before_storage_and_native',begin)
    text=text[:begin]+'''    def test_30_V4_whitelist_preserves_V3_entire_functions_and_wire_names(self):
        old_path=R/'source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py';new_path=HERE/'stage_phase1_capture_v4.py'
        old=whole_ast(old_path);new=whole_ast(new_path)
        self.assertEqual(set(new),set(old))
        self.assertEqual({n for n in old if old[n]!=new[n]},{'load_sources','metadata_validate','preflight_summary','stage'})
        for name in set(old)-{'load_sources','metadata_validate','preflight_summary','stage'}:self.assertEqual(old[name],new[name],name)
        for name in ('normalize_B2_source_paths','verify_B2_source_closure','prepare','native_boundary','retain_originals','validate_preservation','main'):
            self.assertEqual(old[name],new[name],name)
        oldtext=old_path.read_text();newtext=new_path.read_text()
        oldstage=next(n for n in ast.parse(oldtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        newstage=next(n for n in ast.parse(newtext).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        self.assertEqual(ast.get_source_segment(oldtext,oldstage).replace("kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V4'"),ast.get_source_segment(newtext,newstage))
        self.assertEqual(m.ROOT_PREFIX,'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
        self.assertEqual(m.COMPLETE_NAME,'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json')
        self.assertEqual(m.SOURCE_DERIVATION_VERSION,4)

'''+text[end:]
    begin=text.index('    def test_41_all_five_V3_candidate_bytes_identical_sealed_V2')
    end=text.index('    def test_42_original_B2_builder_only_not_new_strict_reset_verifier',begin)
    text=text[:begin]+'''    def test_41_final_worker4_exact_one_existing_bridge_device_change_only(self):
        for name in ('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py',
                     'worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py'):
            old=(R/'source_phase1_capture_worker_v3'/name).read_bytes()
            actual=(R/m.WORKER_FOLDER/name).read_bytes()
            if name=='worker_passive_interface_v1.py':
                before=b'boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)'
                after=b'boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)'
                self.assertEqual(old.count(before),1)
                self.assertEqual(actual,old.replace(before,after,1))
                self.assertIn(b'boundary.after_original_step(state.terminated,state.truncated)',actual)
                self.assertEqual(actual.count(b'boundary.after_original_step('),1)
            else:self.assertEqual(actual,old,name)

'''+text[end:]
    extra='''    def test_43_complete_declared_boundary_SOURCE8_proof_not_runtime_or_CPU(self):
        record=self.bundle['index']['boundary_device_source_contract'];proof=self.bundle['receipt']['boundary_device_source_contract']
        self.assertEqual(proof['members'],8);self.assertEqual(proof['content_root_sha256'],record['seal']['content_root_sha256'])
        self.assertTrue(proof['read_only_fixture_source_not_runtime_dependency']);self.assertTrue(proof['source_contract_unchanged'])
        self.assertEqual(proof['actual_source_references_verified'],3);self.assertEqual(proof['fixture_or_CPU_module_imports'],0)
        self.assertFalse(proof['parent_CPU_report_dependency']);self.assertIsNone(proof['actual_V3_flags_shape_dtype_device'])
        self.assertEqual(proof['actual_native_binding'],'UNKNOWN');self.assertEqual(self.bundle['receipt']['source_mappings'],27)
        self.assertEqual(len([a for a in self.bundle['sources']if a.startswith('phase1_source_proof/boundary_device_source_contract/')]),9)
        self.assertEqual(len([a for a in self.bundle['sources']if a.startswith('phase1_source_proof/boundary_device_references/')]),3)
        self.assertNotIn('boundary_device_contract',sys.modules);self.assertNotIn('torch_cpu_fixture',sys.modules);self.assertNotIn('torch',sys.modules)
        self.assertEqual(record['parent_CPU_result'],'NOT_REPRESENTED_BY_THIS_SOURCE_SEAL')

    def test_44_each_declared_fixture_member_missing_or_changed_is_hard_failure(self):
        root=self.mirror();record=self.bundle['index']['boundary_device_source_contract']['seal']
        original=m.reference_path(R,record['path']);folder=root/original.parent.relative_to(R)
        for relative in ['SOURCE_SEAL.json']+[r['relative']for r in record['members']]:
            path=folder/relative;raw=path.read_bytes()
            self.assertTrue(path.is_relative_to(self.root));path.unlink()
            try:
                with self.subTest(relative=relative,case='missing'):
                    with self.assertRaises(FileNotFoundError):self.mirror_load_no_original_R_fallback(root)
            finally:put(path,raw)
            put(path,raw+b'\\n# CHANGED_FAKE_SOURCE_COPY_ONLY\\n')
            try:
                with self.subTest(relative=relative,case='changed'):
                    with self.assertRaises(ValueError):self.mirror_load_no_original_R_fallback(root)
            finally:put(path,raw)

'''
    text=replace(text,'\ndef main():',extra+'\ndef main():')
    text=replace(text,"AST_ONLY_V3'","AST_ONLY_V4'")
    tree=ast.parse(text);tests=[n.name for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name.startswith('test_')]
    if len(tests)!=44:raise ValueError('complete original42 plus2 SOURCE fixture regressions count differs')
    path=HERE/'test_materializer_stdlib_v4.py';result=text.encode()
    if path.exists():
        if path.read_bytes()!=result:raise ValueError('existing NEW V4 test source differs')
    else:
        with path.open('xb')as stream:stream.write(result)
    print(json.dumps(dict(kind='SOURCE_V4_REGRESSION_TEXT_DERIVED_NOT_EXECUTED',tests=44,bytes=len(result),SHA256=H(result),old_test_scripts_replayed=False)))


if __name__=='__main__':main()
