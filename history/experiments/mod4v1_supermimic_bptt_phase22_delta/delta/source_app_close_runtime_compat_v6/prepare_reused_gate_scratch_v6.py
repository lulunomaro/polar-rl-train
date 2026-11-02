"""Copy approved old tests to NEW scratch; run only their 64 behavioral tests."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;ROOT=B.parent;OLD=ROOT/'source_app_close_semantics_v5';S=B/'GATE_SCRATCH_V6'
assert not S.exists(),'new scratch only'
S.mkdir()
source=(OLD/'test_app_close_semantics_v5.py').read_text(encoding='utf-8')
old="ROOT = HERE.parent\n";assert source.count(old)==1;source=source.replace(old,"ROOT = HERE.parent.parent\n",1)
old="sys.path.insert(0, str(OLD))\n";assert source.count(old)==1
source=source.replace(old,old+"sys.path.append(str(ROOT / 'source_app_close_semantics_v5'))\n",1)
old="suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])";assert source.count(old)==1
source=source.replace(old,"suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(value) for value in list(vars(sys.modules[__name__]).values()) if isinstance(value,type) and issubclass(value,unittest.TestCase) and value.__module__==__name__ and value.__name__!='SourceASTTests')",1)
source=source.replace("STDLIB_CPU_FAKE_AND_SOURCE_AST_ONLY_NOT_NATIVE_V5","REUSED_V5_BEHAVIORAL_GATES_V6_NEW_SCRATCH_NOT_NATIVE")
# Same required failure, now V6 rejects the unpublished module before class/SHA.
source=source.replace("'source_bytes' in r or 'actual_class' in r", "'source_bytes' in r or 'actual_class' in r or 'unpublished actual module' in r",1)
(S/'test_reused_v5_gates_v6.py').write_text(source,encoding='utf-8')
(S/'app_close_semantics_v5.py').write_bytes((B/'app_close_semantics_v6.py').read_bytes())
(S/'_synthetic_app_fixture_v5.py').write_bytes((OLD/'_synthetic_app_fixture_v5.py').read_bytes())
assert hashlib.sha256((S/'app_close_semantics_v5.py').read_bytes()).digest()==hashlib.sha256((B/'app_close_semantics_v6.py').read_bytes()).digest()
print(json.dumps(dict(kind='NEW_SCRATCH_NOT_OLD_SEALED_OUTPUT',scratch=str(S),unchanged_old_behavioral_tests=64,excluded_old_worker_source_AST_tests=9,reason='worker/owners unchanged; replacement V6 compares all actual unchanged gate AST directly',original_sources_written=False)))
