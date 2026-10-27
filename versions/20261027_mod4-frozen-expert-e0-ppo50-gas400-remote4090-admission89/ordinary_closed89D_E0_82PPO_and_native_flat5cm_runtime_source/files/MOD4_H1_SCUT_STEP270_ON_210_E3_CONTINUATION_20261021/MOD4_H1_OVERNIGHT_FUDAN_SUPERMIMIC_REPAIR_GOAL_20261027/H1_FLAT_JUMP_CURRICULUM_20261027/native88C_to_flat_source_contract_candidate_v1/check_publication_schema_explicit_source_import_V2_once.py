"""Previously unexecuted schema fixture; explicit source loading after import error."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def main():
 report=HERE/'PUBLICATION_SCHEMA_V1_IMPORT_ORIGINAL_ERROR_ACTUAL.json'
 with report.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),tool_chunk='b7997d',exit_code=1,
  original_error="ModuleNotFoundError: No module named 'native88C_to_flat_migration_v1'",at='V1 checker line5 import before main/try',
  source_SHA=H(HERE/'check_new_flat_publication_schema_CPU_once_v1.py'),fixture_main_executed=False,
  no_PT_or_restore_or_SDK_or_GPU_operation=True,root_cause_not_assumed=True),f,indent=2)
 load('native88C_flat_pins_v1',HERE/'native88C_flat_pins_v1.py')
 load('native88C_to_flat_migration_v1',HERE/'native88C_to_flat_migration_v1.py')
 fixture=load('new_flat_publication_original_fixture_unexecuted',HERE/'check_new_flat_publication_schema_CPU_once_v1.py')
 fixture.main()
if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('EXPLICIT_SOURCE_IMPORT_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
